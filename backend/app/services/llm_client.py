"""LLM Fallback Client — generates HTML components for types without Jinja2 templates.

Architecture:
  LLMFallbackClient (ABC)
  ├── MockLLMClient          — pre-built fixtures, used in dev/CI (LLM_MODE=mock)
  ├── GigaChatLLMClient      — Sber GigaChat via two-step OAuth (LLM_PROVIDER=gigachat)
  └── OpenAICompatibleLLMClient — OpenAI / Qwen / OpenRouter (LLM_PROVIDER=openai_compatible)

Factory:
  get_llm_client() — reads env vars, returns a cached singleton.
"""
import abc
import asyncio
import functools
import logging
import os
import re
import time
import uuid
import warnings
from typing import Any

import html5lib
import httpx

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when required LLM configuration is missing or invalid."""


# ──────────────────────────────────────────────────── Abstract base ───────────

class LLMFallbackClient(abc.ABC):
    """Common interface for all LLM component generators."""

    @abc.abstractmethod
    async def generate_component(
        self,
        node_type: str,
        attributes: dict,
        styles: dict,
        parent_type: str | None,
    ) -> tuple[str, int]:
        """
        Generate an HTML fragment for *node_type*.
        Returns (html_fragment, attempts_count).
        """

    def _build_prompt(
        self,
        node_type: str,
        attributes: dict,
        styles: dict,
        parent_type: str | None,
    ) -> list[dict]:
        """Build a two-message OpenAI-compatible prompt (shared by all real providers)."""
        system = (
            "Ты — генератор HTML-компонентов. "
            "Возвращай только валидный HTML5-фрагмент, без markdown-обёрток и пояснений. "
            "Используй семантическую разметку и ARIA-атрибуты по WCAG 2.1."
        )
        user = (
            f"Сгенерируй HTML-компонент. "
            f"Тип: {node_type}. "
            f"Атрибуты: {attributes}. "
            f"Стили: {styles}. "
            f"Родительский элемент: {parent_type}. "
            f"Требования: HTML5, ARIA-атрибуты (role, aria-label), БЭМ-классы."
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    @staticmethod
    def _clean_response(text: str) -> str:
        """Strip markdown code fences (```html … ``` or ``` … ```) and whitespace."""
        text = re.sub(r"```html\s*", "", text)
        text = re.sub(r"```\s*", "", text)
        return text.strip()

    @staticmethod
    def _validate_html_fragment(html: str) -> bool:
        """Return True if *html* is a non-empty parseable HTML5 fragment."""
        if not html.strip():
            return False
        try:
            html5lib.parseFragment(html)
            return True
        except Exception:
            return False


# ─────────────────────────────────────────────────────── Mock client ──────────

MOCK_RESPONSES: dict[str, str] = {
    "ImageSlider": (
        '<section class="image-slider" role="region" aria-label="Image Slider">\n'
        '  <div class="image-slider__track">\n'
        '    <div class="image-slider__slide">\n'
        '      <img src="https://picsum.photos/800/400?random=1" alt="Slide 1" class="image-slider__image">\n'
        '    </div>\n'
        '    <div class="image-slider__slide">\n'
        '      <img src="https://picsum.photos/800/400?random=2" alt="Slide 2" class="image-slider__image">\n'
        '    </div>\n'
        '    <div class="image-slider__slide">\n'
        '      <img src="https://picsum.photos/800/400?random=3" alt="Slide 3" class="image-slider__image">\n'
        '    </div>\n'
        '  </div>\n'
        '  <button class="image-slider__prev" aria-label="Previous slide" type="button">&#8592;</button>\n'
        '  <button class="image-slider__next" aria-label="Next slide" type="button">&#8594;</button>\n'
        '</section>'
    ),
    "Modal": (
        '<div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">\n'
        '  <div class="modal__overlay"></div>\n'
        '  <div class="modal__content">\n'
        '    <h2 id="modal-title" class="modal__title">Заголовок</h2>\n'
        '    <p class="modal__body">Содержимое модального окна.</p>\n'
        '    <button class="modal__close" aria-label="Close modal" type="button">&times;</button>\n'
        '  </div>\n'
        '</div>'
    ),
    "Accordion": (
        '<div class="accordion" role="list">\n'
        '  <div class="accordion__item" role="listitem">\n'
        '    <button class="accordion__trigger" aria-expanded="false" aria-controls="panel-1" type="button">\n'
        '      <h3 class="accordion__heading">Section 1</h3>\n'
        '    </button>\n'
        '    <div id="panel-1" class="accordion__panel" hidden>\n'
        '      <p class="accordion__content">Content here.</p>\n'
        '    </div>\n'
        '  </div>\n'
        '</div>'
    ),
}


class MockLLMClient(LLMFallbackClient):
    """Returns pre-built HTML fixtures. Used in development and CI (LLM_MODE=mock)."""

    async def generate_component(
        self,
        node_type: str,
        attributes: dict,
        styles: dict,
        parent_type: str | None,
    ) -> tuple[str, int]:
        await asyncio.sleep(0.05)
        html = MOCK_RESPONSES.get(
            node_type,
            f'<div role="region" aria-label="{node_type}">{node_type} component</div>',
        )
        logger.debug("MockLLMClient generated %s", node_type)
        return html, 1


# ─────────────────────────────────────────────────── GigaChat client ──────────

class GigaChatLLMClient(LLMFallbackClient):
    """
    Two-step OAuth + OpenAI-compatible chat completions for Sber GigaChat.

    Step 1: POST Authorization Key (base64) → access_token (lives 30 min).
    Step 2: POST /chat/completions with Bearer token.

    # TODO для продакшна: установить сертификаты Минцифры в системный truststore
    # или использовать verify="/path/to/russiantrustedca.pem" вместо verify=False.
    """

    def __init__(
        self,
        auth_key: str,
        scope: str,
        model: str,
        oauth_url: str,
        api_url: str,
        max_attempts: int = 3,
        timeout: float = 30.0,
        _http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.auth_key = auth_key
        self.scope = scope
        self.model = model
        self.oauth_url = oauth_url
        self.api_url = api_url.rstrip("/")
        self.max_attempts = max_attempts
        self.timeout = timeout

        self._token: str | None = None
        self._token_expires_at: float = 0.0

        if _http_client is not None:
            self._http = _http_client
        else:
            try:
                import urllib3
                warnings.filterwarnings(
                    "ignore", category=urllib3.exceptions.InsecureRequestWarning
                )
            except ImportError:
                pass
            self._http = httpx.AsyncClient(verify=False, timeout=timeout)

    async def _get_access_token(self) -> str:
        """Return cached token, or fetch a new one if expired / missing."""
        now = time.time()
        if self._token and now < self._token_expires_at - 60:
            return self._token

        response = await self._http.post(
            self.oauth_url,
            content=f"scope={self.scope}".encode(),
            headers={
                "Authorization": f"Basic {self.auth_key}",
                "RqUID": str(uuid.uuid4()),
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        response.raise_for_status()
        data = response.json()
        self._token = data["access_token"]
        self._token_expires_at = data["expires_at"] / 1000.0
        return self._token

    async def generate_component(
        self,
        node_type: str,
        attributes: dict,
        styles: dict,
        parent_type: str | None,
    ) -> tuple[str, int]:
        messages = self._build_prompt(node_type, attributes, styles, parent_type)
        start = time.perf_counter()

        for attempt in range(1, self.max_attempts + 1):
            try:
                token = await self._get_access_token()
                response = await self._http.post(
                    f"{self.api_url}/chat/completions",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.3,
                        "max_tokens": 500,
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )

                if response.status_code == 401:
                    logger.warning("GigaChat 401 — resetting token cache (attempt %d)", attempt)
                    self._token = None
                    self._token_expires_at = 0.0
                    if attempt < self.max_attempts:
                        await asyncio.sleep(2 ** (attempt - 1))
                    continue

                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
                html = self._clean_response(content)

                if self._validate_html_fragment(html):
                    elapsed = int((time.perf_counter() - start) * 1000)
                    logger.info(
                        "GigaChat generated %s in %d attempt(s), %dms",
                        node_type, attempt, elapsed,
                    )
                    return html, attempt

                logger.warning(
                    "GigaChat returned invalid HTML for %s (attempt %d/%d)",
                    node_type, attempt, self.max_attempts,
                )

            except Exception as exc:
                logger.warning(
                    "GigaChat attempt %d/%d failed for %s: %s",
                    attempt, self.max_attempts, node_type, exc,
                )

            if attempt < self.max_attempts:
                await asyncio.sleep(2 ** (attempt - 1))

        logger.error("GigaChat exhausted all %d attempts for %s", self.max_attempts, node_type)
        return (
            f'<div role="region" aria-label="{node_type}">Component generation failed</div>',
            self.max_attempts,
        )


# ─────────────────────────────────────── OpenAI-compatible client (future) ────

class OpenAICompatibleLLMClient(LLMFallbackClient):
    """
    Minimal OpenAI-compatible client for OpenAI, Qwen, OpenRouter, etc.
    No two-step OAuth — uses Authorization: Bearer {api_key} directly.

    To switch from GigaChat:
      LLM_PROVIDER=openai_compatible
      LLM_API_BASE_URL=https://api.openai.com/v1
      LLM_API_KEY=sk-...
      LLM_MODEL=gpt-4o
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        max_attempts: int = 3,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.max_attempts = max_attempts
        self.timeout = timeout
        self._http = httpx.AsyncClient(timeout=timeout)

    async def generate_component(
        self,
        node_type: str,
        attributes: dict,
        styles: dict,
        parent_type: str | None,
    ) -> tuple[str, int]:
        messages = self._build_prompt(node_type, attributes, styles, parent_type)
        start = time.perf_counter()

        for attempt in range(1, self.max_attempts + 1):
            try:
                response = await self._http.post(
                    f"{self.base_url}/chat/completions",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.3,
                        "max_tokens": 500,
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
                html = self._clean_response(content)

                if self._validate_html_fragment(html):
                    elapsed = int((time.perf_counter() - start) * 1000)
                    logger.info(
                        "OpenAI-compatible generated %s in %d attempt(s), %dms",
                        node_type, attempt, elapsed,
                    )
                    return html, attempt

            except Exception as exc:
                logger.warning(
                    "OpenAI-compatible attempt %d/%d failed for %s: %s",
                    attempt, self.max_attempts, node_type, exc,
                )

            if attempt < self.max_attempts:
                await asyncio.sleep(2 ** (attempt - 1))

        logger.error(
            "OpenAI-compatible exhausted all %d attempts for %s",
            self.max_attempts, node_type,
        )
        return (
            f'<div role="region" aria-label="{node_type}">Component generation failed</div>',
            self.max_attempts,
        )


# ──────────────────────────────────────────────────────────── Factory ──────────

@functools.lru_cache(maxsize=1)
def get_llm_client() -> LLMFallbackClient:
    """
    Read LLM_MODE / LLM_PROVIDER from environment and return a cached client.
    Call get_llm_client.cache_clear() to force re-creation (needed in tests).
    """
    mode = os.environ.get("LLM_MODE", "mock").lower()

    if mode == "mock":
        logger.info("LLM client: MockLLMClient (LLM_MODE=mock)")
        return MockLLMClient()

    if mode != "real":
        raise ConfigurationError(
            f"LLM_MODE must be 'mock' or 'real', got '{mode}'"
        )

    provider = os.environ.get("LLM_PROVIDER", "gigachat").lower()

    if provider == "gigachat":
        auth_key = os.environ.get("GIGACHAT_AUTH_KEY", "")
        if not auth_key:
            raise ConfigurationError(
                "LLM_MODE=real with LLM_PROVIDER=gigachat requires GIGACHAT_AUTH_KEY to be set"
            )
        logger.info("LLM client: GigaChatLLMClient")
        return GigaChatLLMClient(
            auth_key=auth_key,
            scope=os.environ.get("GIGACHAT_SCOPE", "GIGACHAT_API_PERS"),
            model=os.environ.get("GIGACHAT_MODEL", "GigaChat"),
            oauth_url=os.environ.get(
                "GIGACHAT_OAUTH_URL",
                "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            ),
            api_url=os.environ.get(
                "GIGACHAT_API_URL",
                "https://gigachat.devices.sberbank.ru/api/v1",
            ),
            max_attempts=int(os.environ.get("LLM_MAX_ATTEMPTS", "3")),
            timeout=float(os.environ.get("LLM_TIMEOUT_SECONDS", "30")),
        )

    if provider == "openai_compatible":
        api_key = os.environ.get("LLM_API_KEY", "")
        base_url = os.environ.get("LLM_API_BASE_URL", "")
        if not api_key:
            raise ConfigurationError(
                "LLM_MODE=real with LLM_PROVIDER=openai_compatible requires LLM_API_KEY"
            )
        if not base_url:
            raise ConfigurationError(
                "LLM_MODE=real with LLM_PROVIDER=openai_compatible requires LLM_API_BASE_URL"
            )
        logger.info("LLM client: OpenAICompatibleLLMClient (base_url=%s)", base_url)
        return OpenAICompatibleLLMClient(
            base_url=base_url,
            api_key=api_key,
            model=os.environ.get("LLM_MODEL", ""),
            max_attempts=int(os.environ.get("LLM_MAX_ATTEMPTS", "3")),
            timeout=float(os.environ.get("LLM_TIMEOUT_SECONDS", "30")),
        )

    raise ConfigurationError(
        f"Unknown LLM_PROVIDER '{provider}'. Supported: gigachat, openai_compatible"
    )
