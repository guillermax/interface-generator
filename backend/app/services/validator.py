"""
HTML Validator — проверка на соответствие HTML5 и WCAG 2.1 AA.

Применяет шесть правил последовательно, автоматически исправляя нарушения
там, где правка безопасна (severity="fix"), и только фиксируя остальные
(severity="error").
"""
from typing import Literal

from bs4 import BeautifulSoup
from pydantic import BaseModel


class ValidationIssue(BaseModel):
    rule: str
    element: str
    severity: Literal["error", "fix"]
    description: str


class Validator:
    SEMANTIC_ROLES: dict[str, str] = {
        "header": "banner",
        "nav": "navigation",
        "main": "main",
        "footer": "contentinfo",
        "aside": "complementary",
    }
    INTERACTIVE_TAGS: frozenset[str] = frozenset({"input", "button", "select", "textarea"})

    def validate(self, html: str) -> tuple[str, list[ValidationIssue]]:
        """
        Парсит HTML, применяет правила WCAG 2.1 AA и возвращает
        исправленный HTML вместе со списком найденных нарушений.
        """
        soup = BeautifulSoup(html, "html5lib")
        issues: list[ValidationIssue] = []

        self._rule_img_alt(soup, issues)
        self._rule_interactive_labels(soup, issues)
        self._rule_heading_hierarchy(soup, issues)
        self._rule_semantic_roles(soup, issues)
        self._rule_html_lang(soup, issues)
        self._rule_tabindex(soup, issues)

        return str(soup), issues

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _tag_repr(el) -> str:
        """Возвращает строку открывающего тега без содержимого, макс. 120 символов."""
        attrs = "".join(
            f' {k}="{" ".join(v) if isinstance(v, list) else v}"'
            for k, v in el.attrs.items()
        )
        return f"<{el.name}{attrs}>"[:120]

    # ------------------------------------------------------------------ rules

    def _rule_img_alt(self, soup: BeautifulSoup, issues: list[ValidationIssue]) -> None:
        """WCAG 1.1.1: все изображения должны иметь атрибут alt."""
        for img in soup.find_all("img"):
            if img.get("alt") is None:
                original = self._tag_repr(img)
                img["alt"] = ""
                issues.append(ValidationIssue(
                    rule="img_alt_missing",
                    element=original,
                    severity="fix",
                    description='<img> без атрибута alt; установлен alt="" (декоративное изображение)',
                ))

    def _rule_interactive_labels(self, soup: BeautifulSoup, issues: list[ValidationIssue]) -> None:
        """WCAG 1.3.1 / 4.1.2: интерактивные элементы должны иметь доступное имя."""
        for el in soup.find_all(self.INTERACTIVE_TAGS):
            if el.get("aria-label"):
                continue
            el_id = el.get("id")
            if el_id and soup.find("label", attrs={"for": el_id}):
                continue
            if el.find_parent("label"):
                continue
            original = self._tag_repr(el)
            label_value = (
                el.get("placeholder")
                or el.get("name")
                or el.get("type", "field")
            )
            el["aria-label"] = label_value
            issues.append(ValidationIssue(
                rule="interactive_label_missing",
                element=original,
                severity="fix",
                description=f'Интерактивный элемент без доступного имени; добавлен aria-label="{label_value}"',
            ))

    def _rule_heading_hierarchy(self, soup: BeautifulSoup, issues: list[ValidationIssue]) -> None:
        """WCAG 1.3.1: иерархия заголовков должна быть последовательной."""
        prev_level = 0
        for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            level = int(heading.name[1])
            if prev_level > 0 and level > prev_level + 1:
                issues.append(ValidationIssue(
                    rule="heading_hierarchy_skip",
                    element=str(heading)[:120],
                    severity="error",
                    description=f"Иерархия заголовков пропускает уровень: h{prev_level} → h{level}",
                ))
            prev_level = level

    def _rule_semantic_roles(self, soup: BeautifulSoup, issues: list[ValidationIssue]) -> None:
        """WCAG 1.3.6: семантические элементы должны иметь явный ARIA role."""
        for tag, role in self.SEMANTIC_ROLES.items():
            for el in soup.find_all(tag):
                if not el.get("role"):
                    original = self._tag_repr(el)
                    el["role"] = role
                    issues.append(ValidationIssue(
                        rule="semantic_role_missing",
                        element=original,
                        severity="fix",
                        description=f'<{tag}> без атрибута role; добавлен role="{role}"',
                    ))

    def _rule_html_lang(self, soup: BeautifulSoup, issues: list[ValidationIssue]) -> None:
        """WCAG 3.1.1: корневой элемент <html> должен указывать язык документа."""
        html_tag = soup.find("html")
        if html_tag and not html_tag.get("lang"):
            html_tag["lang"] = "ru"
            issues.append(ValidationIssue(
                rule="html_lang_missing",
                element="<html>",
                severity="fix",
                description='<html> без атрибута lang; установлен lang="ru"',
            ))

    def _rule_tabindex(self, soup: BeautifulSoup, issues: list[ValidationIssue]) -> None:
        """WCAG 2.1.1: интерактивные элементы не должны иметь tabindex="-1"."""
        for el in soup.find_all(self.INTERACTIVE_TAGS):
            if el.get("tabindex") == "-1":
                original = self._tag_repr(el)
                del el["tabindex"]
                issues.append(ValidationIssue(
                    rule="tabindex_negative",
                    element=original,
                    severity="fix",
                    description=f'<{el.name}> с tabindex="-1" исключён из навигации клавиатурой; атрибут удалён',
                ))
