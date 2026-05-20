"""Тесты Template Engine."""
import pytest
from app.services.nlp import NLPModule
from app.services.ami_builder import AMIBuilder
from app.services.template_engine import TemplateEngine


@pytest.fixture
def engine():
    return TemplateEngine()


@pytest.fixture
def nlp():
    return NLPModule()


@pytest.fixture
def builder():
    return AMIBuilder()


class TestTemplateEngine:

    def test_login_form_renders_form_tag(self, engine, nlp, builder):
        entities = nlp.predict("форма входа с email и паролем")
        graph = builder.build(entities)
        html = engine.render(graph)

        assert "<form" in html
        assert 'class="login-form"' in html

    def test_login_form_has_email_input(self, engine, nlp, builder):
        entities = nlp.predict("форма входа с email и паролем")
        graph = builder.build(entities)
        html = engine.render(graph)

        assert 'type="email"' in html

    def test_login_form_has_password_input(self, engine, nlp, builder):
        entities = nlp.predict("форма входа")
        graph = builder.build(entities)
        html = engine.render(graph)

        assert 'type="password"' in html

    def test_login_form_has_submit_button(self, engine, nlp, builder):
        entities = nlp.predict("форма входа")
        graph = builder.build(entities)
        html = engine.render(graph)

        assert "<button" in html
        assert 'type="submit"' in html

    def test_html_has_doctype(self, engine, nlp, builder):
        entities = nlp.predict("форма входа")
        graph = builder.build(entities)
        html = engine.render(graph)

        assert "<!DOCTYPE html>" in html
        assert 'lang="ru"' in html

    def test_unknown_type_renders_fallback(self, engine, nlp, builder):
        entities = nlp.predict("случайный непонятный текст")
        graph = builder.build(entities)
        html = engine.render(graph)

        # Должен отрендериться хотя бы page.html
        assert "<!DOCTYPE html>" in html
        assert "<body>" in html