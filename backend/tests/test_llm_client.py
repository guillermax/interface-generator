"""Tests for LLM Fallback Client (MockLLMClient, GigaChatLLMClient, factory)."""
import asyncio
import os
import time

import httpx
import pytest
from pytest_httpx import HTTPXMock

from app.services.llm_client import (
    ConfigurationError,
    GigaChatLLMClient,
    MockLLMClient,
    get_llm_client,
)

# ──────────────────────────────────────────── MockLLMClient ───────────────────

@pytest.mark.asyncio
async def test_mock_returns_image_slider():
    client = MockLLMClient()
    html, attempts = await client.generate_component("ImageSlider", {}, {}, None)
    assert "image-slider" in html
    assert 'role="region"' in html
    assert attempts == 1


@pytest.mark.asyncio
async def test_mock_returns_modal():
    client = MockLLMClient()
    html, attempts = await client.generate_component("Modal", {}, {}, None)
    assert "modal" in html
    assert 'role="dialog"' in html
    assert attempts == 1


@pytest.mark.asyncio
async def test_mock_returns_accordion():
    client = MockLLMClient()
    html, attempts = await client.generate_component("Accordion", {}, {}, None)
    assert "accordion" in html
    assert "aria-expanded" in html
    assert attempts == 1


@pytest.mark.asyncio
async def test_mock_returns_fallback_for_unknown():
    client = MockLLMClient()
    html, attempts = await client.generate_component("UnknownWidget", {}, {}, None)
    assert 'role="region"' in html
    assert "UnknownWidget" in html
    assert attempts == 1


# ─────────────────────────── _clean_response ─────────────────────────────────

def test_clean_response_strips_html_markdown():
    result = MockLLMClient._clean_response("```html\n<div>hello</div>\n```")
    assert result == "<div>hello</div>"


def test_clean_response_strips_plain_backticks():
    result = MockLLMClient._clean_response("```\n<div>hello</div>\n```")
    assert result == "<div>hello</div>"


def test_clean_response_leaves_plain_html():
    html = "<div>hello</div>"
    assert MockLLMClient._clean_response(html) == html


# ──────────────────────────── _validate_html_fragment ─────────────────────────

def test_validate_html_fragment_valid():
    assert MockLLMClient._validate_html_fragment("<div>hello</div>") is True


def test_validate_html_fragment_empty_string():
    assert MockLLMClient._validate_html_fragment("") is False


def test_validate_html_fragment_whitespace_only():
    assert MockLLMClient._validate_html_fragment("   ") is False


# ───────────────────────── GigaChatLLMClient helpers ─────────────────────────

OAUTH_URL = "https://gigachat.test/oauth"
API_URL = "https://gigachat.test/api/v1"


def _make_client(http: httpx.AsyncClient, max_attempts: int = 3) -> GigaChatLLMClient:
    return GigaChatLLMClient(
        auth_key="dGVzdA==",
        scope="GIGACHAT_API_PERS",
        model="GigaChat",
        oauth_url=OAUTH_URL,
        api_url=API_URL,
        max_attempts=max_attempts,
        timeout=5.0,
        _http_client=http,
    )


def _token_resp() -> dict:
    return {
        "access_token": "test_access_token",
        "expires_at": int(time.time() * 1000) + 1_800_000,
    }


def _chat_resp(html: str) -> dict:
    return {"choices": [{"message": {"content": html}}]}


# ─────────────────────────── GigaChat tests ───────────────────────────────────

@pytest.mark.asyncio
async def test_gigachat_fetches_token_on_first_call(httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=OAUTH_URL, json=_token_resp())
    httpx_mock.add_response(
        url=f"{API_URL}/chat/completions", json=_chat_resp("<div>ok</div>")
    )

    async with httpx.AsyncClient() as http:
        client = _make_client(http)
        html, attempts = await client.generate_component("Button", {}, {}, None)

    assert "<div>" in html
    assert attempts == 1
    oauth_reqs = [r for r in httpx_mock.get_requests() if OAUTH_URL in str(r.url)]
    assert len(oauth_reqs) == 1


@pytest.mark.asyncio
async def test_gigachat_uses_cached_token(httpx_mock: HTTPXMock):
    """Second generate_component call must NOT trigger a second OAuth request."""
    httpx_mock.add_response(url=OAUTH_URL, json=_token_resp())
    httpx_mock.add_response(
        url=f"{API_URL}/chat/completions", json=_chat_resp("<div>first</div>")
    )
    httpx_mock.add_response(
        url=f"{API_URL}/chat/completions", json=_chat_resp("<div>second</div>")
    )

    async with httpx.AsyncClient() as http:
        client = _make_client(http)
        await client.generate_component("Button", {}, {}, None)
        await client.generate_component("Input", {}, {}, None)

    oauth_reqs = [r for r in httpx_mock.get_requests() if OAUTH_URL in str(r.url)]
    assert len(oauth_reqs) == 1


@pytest.mark.asyncio
async def test_gigachat_refreshes_token_on_401(httpx_mock: HTTPXMock, monkeypatch):
    async def _fast_sleep(_): pass
    monkeypatch.setattr(asyncio, "sleep", _fast_sleep)

    httpx_mock.add_response(url=OAUTH_URL, json=_token_resp())
    httpx_mock.add_response(url=f"{API_URL}/chat/completions", status_code=401)
    httpx_mock.add_response(url=OAUTH_URL, json=_token_resp())
    httpx_mock.add_response(
        url=f"{API_URL}/chat/completions", json=_chat_resp("<section>ok</section>")
    )

    async with httpx.AsyncClient() as http:
        client = _make_client(http)
        html, attempts = await client.generate_component("Nav", {}, {}, None)

    assert "<section>" in html
    oauth_reqs = [r for r in httpx_mock.get_requests() if OAUTH_URL in str(r.url)]
    assert len(oauth_reqs) == 2


@pytest.mark.asyncio
async def test_gigachat_request_body(httpx_mock: HTTPXMock):
    import json as _json

    httpx_mock.add_response(url=OAUTH_URL, json=_token_resp())
    httpx_mock.add_response(
        url=f"{API_URL}/chat/completions", json=_chat_resp("<div>ok</div>")
    )

    async with httpx.AsyncClient() as http:
        client = _make_client(http)
        await client.generate_component("Button", {"label": "Click"}, {"color": "blue"}, "Form")

    chat_req = next(
        r for r in httpx_mock.get_requests() if "chat/completions" in str(r.url)
    )
    body = _json.loads(chat_req.content)
    assert body["model"] == "GigaChat"
    assert body["temperature"] == 0.3
    assert body["max_tokens"] == 500
    assert len(body["messages"]) == 2
    assert body["messages"][0]["role"] == "system"
    assert body["messages"][1]["role"] == "user"


@pytest.mark.asyncio
async def test_gigachat_retries_on_http_error(httpx_mock: HTTPXMock, monkeypatch):
    async def _fast_sleep(_): pass
    monkeypatch.setattr(asyncio, "sleep", _fast_sleep)

    httpx_mock.add_response(url=OAUTH_URL, json=_token_resp())
    httpx_mock.add_response(url=f"{API_URL}/chat/completions", status_code=500)
    httpx_mock.add_response(url=f"{API_URL}/chat/completions", status_code=500)
    httpx_mock.add_response(
        url=f"{API_URL}/chat/completions", json=_chat_resp("<article>ok</article>")
    )

    async with httpx.AsyncClient() as http:
        client = _make_client(http)
        html, attempts = await client.generate_component("Nav", {}, {}, None)

    assert "<article>" in html
    assert attempts == 3


@pytest.mark.asyncio
async def test_gigachat_returns_fallback_on_exhaustion(httpx_mock: HTTPXMock, monkeypatch):
    async def _fast_sleep(_): pass
    monkeypatch.setattr(asyncio, "sleep", _fast_sleep)

    httpx_mock.add_response(url=OAUTH_URL, json=_token_resp())
    for _ in range(3):
        httpx_mock.add_response(url=f"{API_URL}/chat/completions", status_code=503)

    async with httpx.AsyncClient() as http:
        client = _make_client(http, max_attempts=3)
        html, attempts = await client.generate_component("Accordion", {}, {}, None)

    assert 'role="region"' in html
    assert "generation failed" in html.lower() or "Accordion" in html
    assert attempts == 3


# ──────────────────────────── Factory tests ───────────────────────────────────

def test_factory_returns_mock_client(monkeypatch):
    get_llm_client.cache_clear()
    monkeypatch.setenv("LLM_MODE", "mock")
    client = get_llm_client()
    assert isinstance(client, MockLLMClient)
    get_llm_client.cache_clear()


def test_factory_raises_on_missing_gigachat_key(monkeypatch):
    get_llm_client.cache_clear()
    monkeypatch.setenv("LLM_MODE", "real")
    monkeypatch.setenv("LLM_PROVIDER", "gigachat")
    monkeypatch.delenv("GIGACHAT_AUTH_KEY", raising=False)

    with pytest.raises(ConfigurationError, match="GIGACHAT_AUTH_KEY"):
        get_llm_client()

    get_llm_client.cache_clear()
