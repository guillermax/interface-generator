"""Integration test: generate_interface pipeline with mock LLM (LLM_MODE=mock)."""
import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Ensure mock mode for all tests in this module
os.environ.setdefault("LLM_MODE", "mock")

from app.services.generator import generate_interface
from app.services.llm_client import get_llm_client

pytestmark = pytest.mark.asyncio(loop_scope="session")

_engine = create_async_engine(os.environ["DATABASE_URL"], echo=False, poolclass=NullPool)
_SessionFactory = async_sessionmaker(_engine, expire_on_commit=False, autocommit=False, autoflush=False)


@pytest.fixture(scope="session")
def engine():
    return _engine


@pytest_asyncio.fixture(autouse=True)
async def clean_db(engine):
    async with engine.begin() as conn:
        await conn.execute(
            text("TRUNCATE components_log, generation_results, requests RESTART IDENTITY CASCADE")
        )


@pytest_asyncio.fixture
async def db_session():
    async with _SessionFactory() as session:
        yield session


# ─────────────────────────── helper ──────────────────────────────────────────

async def _get_component_log(request_id: str) -> list[tuple]:
    """Fetch (component_type, generation_method) rows for a request."""
    async with _engine.begin() as conn:
        rows = await conn.execute(
            text("""
                SELECT cl.component_type, cl.generation_method
                FROM components_log cl
                JOIN generation_results gr ON gr.result_id = cl.result_id
                WHERE gr.request_id = CAST(:rid AS uuid)
                ORDER BY cl.log_id
            """),
            {"rid": request_id},
        )
        return rows.fetchall()


# ─────────────────────────── tests ───────────────────────────────────────────

async def test_login_form_generates_html(db_session: AsyncSession):
    """Template path: LoginForm → HTML contains <form>."""
    get_llm_client.cache_clear()
    os.environ["LLM_MODE"] = "mock"

    result = await generate_interface("форма входа с email и паролем", db_session)

    assert result["html"]
    assert "<form" in result["html"]
    assert result["request_id"]


async def test_login_form_all_components_use_template(db_session: AsyncSession):
    """All components in a login form are template-based."""
    get_llm_client.cache_clear()
    os.environ["LLM_MODE"] = "mock"

    result = await generate_interface("форма входа с email и паролем", db_session)
    entries = await _get_component_log(result["request_id"])

    assert len(entries) > 0
    methods = {row[1] for row in entries}
    assert methods == {"template"}


async def test_landing_renders_full_page(db_session: AsyncSession):
    """Landing page pipeline: HTML contains header, hero section, footer."""
    get_llm_client.cache_clear()
    os.environ["LLM_MODE"] = "mock"

    result = await generate_interface("лендинг страница", db_session)

    assert result["html"]
    assert "<header" in result["html"]
    assert 'class="hero"' in result["html"]
    assert "<footer" in result["html"]


async def test_multiple_roots_compose_correctly(db_session: AsyncSession):
    """Two components in one request both appear in the single HTML document."""
    get_llm_client.cache_clear()
    os.environ["LLM_MODE"] = "mock"

    result = await generate_interface("навигационное меню и форма входа", db_session)

    assert result["html"]
    assert 'class="nav"' in result["html"]
    assert "<form" in result["html"]


async def test_slider_generates_html(db_session: AsyncSession):
    """LLM path: ImageSlider → mock HTML contains image-slider markup."""
    get_llm_client.cache_clear()
    os.environ["LLM_MODE"] = "mock"

    result = await generate_interface("слайдер с тремя картинками", db_session)

    assert result["html"]
    assert "image-slider" in result["html"]
    assert result["request_id"]


async def test_slider_logs_template_method(db_session: AsyncSession):
    """ImageSlider now has a Jinja2 template → generation_method must be 'template'."""
    get_llm_client.cache_clear()
    os.environ["LLM_MODE"] = "mock"

    result = await generate_interface("слайдер с тремя картинками", db_session)
    entries = await _get_component_log(result["request_id"])

    template_types = [row[0] for row in entries if row[1] == "template"]
    assert "ImageSlider" in template_types
