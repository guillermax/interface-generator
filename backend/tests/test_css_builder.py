"""Тесты CSS Builder."""
import pytest
from app.services.nlp import NLPModule
from app.services.ami_builder import AMIBuilder
from app.services.css_builder import CSSBuilder


@pytest.fixture
def builder():
    return CSSBuilder()


@pytest.fixture
def nlp():
    return NLPModule()


@pytest.fixture
def ami_builder():
    return AMIBuilder()


class TestCSSBuilder:

    def test_css_has_base_styles(self, builder, nlp, ami_builder):
        entities = nlp.predict("форма входа")
        graph = ami_builder.build(entities)
        css = builder.build(graph)

        assert "body {" in css
        assert "box-sizing: border-box" in css

    def test_login_form_has_bem_classes(self, builder, nlp, ami_builder):
        entities = nlp.predict("форма входа")
        graph = ami_builder.build(entities)
        css = builder.build(graph)

        assert ".login-form" in css
        assert ".login-form__title" in css

    def test_media_queries_present(self, builder, nlp, ami_builder):
        entities = nlp.predict("форма входа")
        graph = ami_builder.build(entities)
        css = builder.build(graph)

        assert "@media (max-width: 320px)" in css
        assert "@media (max-width: 768px)" in css
        assert "@media (max-width: 1280px)" in css

    def test_button_styles_included(self, builder, nlp, ami_builder):
        entities = nlp.predict("форма входа")
        graph = ami_builder.build(entities)
        css = builder.build(graph)

        assert ".button" in css