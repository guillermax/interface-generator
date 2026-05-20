"""
Template Engine — детерминированная генерация HTML из AMI-графа.

Обходит граф в ширину (BFS) и для каждого узла ищет Jinja2-шаблон
в директории templates/{level}/{type}.html. Если шаблон не найден,
используется fallback-шаблон.
"""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.schemas.ami import AMIGraph, AMINode


# Маппинг типов компонентов на уровни Atomic Design
COMPONENT_LEVELS = {
    # Atoms
    "Button": "atoms",
    "Input": "atoms",
    "Label": "atoms",
    "Heading": "atoms",
    "Image": "atoms",
    "Text": "atoms",
    # Molecules
    "LoginForm": "molecules",
    "RegistrationForm": "molecules",
    "ProductCard": "molecules",
    "SearchBar": "molecules",
    "NavItem": "molecules",
    # Organisms
    "Nav": "organisms",
    "Header": "organisms",
    "Footer": "organisms",
    "Sidebar": "organisms",
    "CardGrid": "organisms",
}


class TemplateEngine:
    """Рендерит HTML-документ на основе AMI-графа."""

    def __init__(self, templates_dir: str | None = None):
        if templates_dir is None:
            templates_dir = str(Path(__file__).parent.parent / "templates")

        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(["html"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, graph: AMIGraph, title: str = "Сгенерированный интерфейс") -> str:
        """
        Рендерит HTML из AMI-графа.

        Параметры:
            graph: построенный AMIGraph
            title: заголовок страницы (тег <title>)

        Возвращает:
            строку с готовым HTML-документом
        """
        body_parts = [self._render_node(node) for node in graph.components]
        body = "\n".join(body_parts)

        page = self.env.get_template("page.html")
        return page.render(body=body, title=title, lang="ru")

    def _render_node(self, node: AMINode) -> str:
        """Рекурсивно рендерит узел и его потомков."""
        # Сначала рендерим всех детей
        children_html = "\n".join(self._render_node(child) for child in node.children)

        # Ищем шаблон по уровню и типу
        level = COMPONENT_LEVELS.get(node.type)
        template_name = None

        if level:
            # camelCase → snake_case для имени файла
            file_name = self._to_snake_case(node.type)
            template_name = f"{level}/{file_name}.html"

        try:
            if template_name:
                template = self.env.get_template(template_name)
                return template.render(
                    attrs=node.attributes,
                    styles=node.styles,
                    children=children_html,
                )
        except Exception:
            pass

        # Fallback для неизвестных типов
        template = self.env.get_template("_fallback.html")
        return template.render(
            attrs={**node.attributes, "label": node.type},
            children=children_html,
        )

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """LoginForm → login_form, ProductCard → product_card."""
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append("_")
            result.append(char.lower())
        return "".join(result)