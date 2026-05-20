"""Тесты Validator — проверка WCAG 2.1 AA правил и автоисправлений."""
import pytest
from app.services.validator import Validator
from app.services.nlp import NLPModule
from app.services.ami_builder import AMIBuilder
from app.services.template_engine import TemplateEngine


def _page(body: str, lang: str = 'lang="ru"') -> str:
    """Минимальный HTML-документ для изолированного тестирования правил."""
    return f'<!DOCTYPE html><html {lang}><head></head><body>{body}</body></html>'


@pytest.fixture
def validator():
    return Validator()


@pytest.fixture
def pipeline():
    return NLPModule(), AMIBuilder(), TemplateEngine()


class TestValidator:

    # ------------------------------------------------------------------ rule 1

    def test_img_alt_added_when_missing(self, validator):
        html = _page('<img src="photo.jpg">')
        fixed, issues = validator.validate(html)

        assert any(i.rule == "img_alt_missing" for i in issues)
        assert 'alt=""' in fixed

    def test_img_alt_not_flagged_when_present(self, validator):
        html = _page('<img src="photo.jpg" alt="A nice photo">')
        _, issues = validator.validate(html)

        assert not any(i.rule == "img_alt_missing" for i in issues)

    # ------------------------------------------------------------------ rule 2

    def test_input_aria_label_added_when_missing(self, validator):
        html = _page('<input type="email">')
        fixed, issues = validator.validate(html)

        assert any(i.rule == "interactive_label_missing" for i in issues)
        assert 'aria-label=' in fixed

    def test_input_inside_label_not_flagged(self, validator):
        html = _page('<label>Email<input type="email"></label>')
        _, issues = validator.validate(html)

        assert not any(i.rule == "interactive_label_missing" for i in issues)

    # ------------------------------------------------------------------ rule 3

    def test_heading_hierarchy_skip_flagged(self, validator):
        html = _page('<h1>Title</h1><h3>Section</h3>')
        _, issues = validator.validate(html)

        skip_issues = [i for i in issues if i.rule == "heading_hierarchy_skip"]
        assert len(skip_issues) == 1
        assert skip_issues[0].severity == "error"
        assert "h1" in skip_issues[0].description
        assert "h3" in skip_issues[0].description

    def test_heading_sequence_not_flagged(self, validator):
        html = _page('<h1>Title</h1><h2>Section</h2><h3>Sub</h3>')
        _, issues = validator.validate(html)

        assert not any(i.rule == "heading_hierarchy_skip" for i in issues)

    # ------------------------------------------------------------------ rule 4

    def test_header_role_added_when_missing(self, validator):
        html = _page('<header><h1>Site</h1></header>')
        fixed, issues = validator.validate(html)

        assert any(i.rule == "semantic_role_missing" for i in issues)
        assert 'role="banner"' in fixed

    def test_nav_role_added_when_missing(self, validator):
        html = _page('<nav><a href="#">Home</a></nav>')
        fixed, issues = validator.validate(html)

        assert any(i.rule == "semantic_role_missing" for i in issues)
        assert 'role="navigation"' in fixed

    def test_semantic_role_not_duplicated_when_present(self, validator):
        html = _page('<nav role="navigation"><a href="#">Home</a></nav>')
        _, issues = validator.validate(html)

        assert not any(i.rule == "semantic_role_missing" for i in issues)

    # ------------------------------------------------------------------ rule 5

    def test_html_lang_added_when_missing(self, validator):
        html = _page('<p>Hello</p>', lang='')
        fixed, issues = validator.validate(html)

        assert any(i.rule == "html_lang_missing" for i in issues)
        assert 'lang="ru"' in fixed

    def test_html_lang_not_flagged_when_present(self, validator):
        html = _page('<p>Hello</p>')
        _, issues = validator.validate(html)

        assert not any(i.rule == "html_lang_missing" for i in issues)

    # ------------------------------------------------------------------ rule 6

    def test_tabindex_removed_from_button(self, validator):
        html = _page('<button aria-label="Submit" tabindex="-1">Click</button>')
        fixed, issues = validator.validate(html)

        assert any(i.rule == "tabindex_negative" for i in issues)
        assert 'tabindex="-1"' not in fixed

    def test_tabindex_not_flagged_when_absent(self, validator):
        html = _page('<button aria-label="Submit">Click</button>')
        _, issues = validator.validate(html)

        assert not any(i.rule == "tabindex_negative" for i in issues)

    # ------------------------------------------------------------------ combined

    def test_valid_html_produces_no_issues(self, validator):
        html = _page(
            '<nav role="navigation" aria-label="Main">'
            '<a href="#">Home</a>'
            '</nav>'
            '<button aria-label="Submit">Submit</button>'
            '<img src="photo.jpg" alt="A photo">'
            '<input type="text" aria-label="Name">'
        )
        _, issues = validator.validate(html)

        assert issues == []

    # ------------------------------------------------------------------ integration

    def test_integration_login_form_zero_issues(self, validator, pipeline):
        nlp, builder, engine = pipeline
        entities = nlp.predict("форма входа с email и паролем")
        graph = builder.build(entities)
        html = engine.render(graph)
        _, issues = validator.validate(html)

        assert issues == [], (
            f"Expected 0 issues for login form template, got {len(issues)}: "
            + "; ".join(f"{i.rule}: {i.description}" for i in issues)
        )
