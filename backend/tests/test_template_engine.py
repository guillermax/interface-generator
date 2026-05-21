"""Tests for Template Engine (async render)."""
import pytest
from app.services.llm_client import MockLLMClient
from app.services.nlp import NLPModule
from app.services.ami_builder import AMIBuilder
from app.services.template_engine import TemplateEngine

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(scope="session")
def engine():
    return TemplateEngine()


@pytest.fixture(scope="session")
def nlp():
    return NLPModule()


@pytest.fixture(scope="session")
def builder():
    return AMIBuilder()


@pytest.fixture(scope="session")
def llm():
    return MockLLMClient()


async def test_login_form_renders_form_tag(engine, nlp, builder, llm):
    entities = nlp.predict("форма входа с email и паролем")
    graph = builder.build(entities)
    html, _ = await engine.render(graph, llm)

    assert "<form" in html
    assert 'class="login-form"' in html


async def test_login_form_has_email_input(engine, nlp, builder, llm):
    entities = nlp.predict("форма входа с email и паролем")
    graph = builder.build(entities)
    html, _ = await engine.render(graph, llm)

    assert 'type="email"' in html


async def test_login_form_has_password_input(engine, nlp, builder, llm):
    entities = nlp.predict("форма входа")
    graph = builder.build(entities)
    html, _ = await engine.render(graph, llm)

    assert 'type="password"' in html


async def test_login_form_has_submit_button(engine, nlp, builder, llm):
    entities = nlp.predict("форма входа")
    graph = builder.build(entities)
    html, _ = await engine.render(graph, llm)

    assert "<button" in html
    assert 'type="submit"' in html


async def test_html_has_doctype(engine, nlp, builder, llm):
    entities = nlp.predict("форма входа")
    graph = builder.build(entities)
    html, _ = await engine.render(graph, llm)

    assert "<!DOCTYPE html>" in html
    assert 'lang="ru"' in html


async def test_unknown_type_renders_fallback(engine, nlp, builder, llm):
    entities = nlp.predict("случайный непонятный текст")
    graph = builder.build(entities)
    html, _ = await engine.render(graph, llm)

    assert "<!DOCTYPE html>" in html
    assert "<body>" in html


async def test_slider_uses_llm_path(engine, nlp, builder, llm):
    """ImageSlider has no template — must go through LLM, log says 'llm'."""
    entities = nlp.predict("слайдер с тремя картинками")
    graph = builder.build(entities)
    html, log = await engine.render(graph, llm)

    # HTML contains mock slider markup
    assert "image-slider" in html
    # At least one log entry has generation_method='llm' for ImageSlider
    llm_entries = [(t, m) for t, m, _ in log if m == "llm"]
    assert any(t == "ImageSlider" for t, _ in llm_entries)


async def test_template_log_entries(engine, nlp, builder, llm):
    """Template-based components produce 'template' log entries."""
    entities = nlp.predict("форма входа")
    graph = builder.build(entities)
    _, log = await engine.render(graph, llm)

    methods = {m for _, m, _ in log}
    assert "template" in methods
    assert "llm" not in methods
