"""
CSS Builder — генерация CSS-файла на основе AMI-графа.

Для каждого узла графа собирает CSS-правила с БЭМ-именованием классов,
добавляет адаптивные медиа-запросы для трёх контрольных точек.
"""
from app.schemas.ami import AMIGraph, AMINode


# Базовые CSS-стили для каждого типа компонента
DEFAULT_STYLES = {
    "button": """.button {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    background: #667eea;
    color: white;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
}
.button:hover {
    background: #5568d3;
}
.button--submit {
    width: 100%;
    margin-top: 0.5rem;
}""",

    "input": """.input__wrapper {
    display: block;
    margin-bottom: 1rem;
}
.input__label {
    display: block;
    margin-bottom: 0.25rem;
    color: #555;
    font-size: 0.9rem;
}
.input__field {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 1rem;
    box-sizing: border-box;
}
.input__field:focus {
    outline: none;
    border-color: #667eea;
}""",

    "heading": """.heading {
    color: #1a1a2e;
    margin: 0 0 1rem 0;
}
.heading--level-1 { font-size: 1.75rem; }
.heading--level-2 { font-size: 1.5rem; }
.heading--level-3 { font-size: 1.25rem; }""",

    "label": """.label {
    display: block;
    margin-bottom: 0.5rem;
    color: #555;
    font-size: 0.9rem;
}""",

    "image": """.image {
    max-width: 100%;
    height: auto;
    display: block;
}""",

    "login_form": """.login-form {
    background: white;
    padding: 2.5rem;
    border-radius: 12px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
    width: 100%;
    max-width: 400px;
    margin: 2rem auto;
}
.login-form__title {
    margin: 0 0 1.5rem 0;
    font-size: 1.75rem;
    color: #1a1a2e;
}
.login-form__fields {
    display: flex;
    flex-direction: column;
}
/* Градиент применяется только к фону формы входа */
body:has(.login-form), body:has(.registration-form) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}""",

    "image_slider": """.image-slider {
    position: relative;
    max-width: 800px;
    margin: 2rem auto;
    border-radius: 12px;
    overflow: hidden;
    background: #1a1a2e;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}
.image-slider__track {
    display: flex;
    overflow: hidden;
}
.image-slider__track .image {
    width: 100%;
    min-width: 100%;
    height: 400px;
    object-fit: cover;
    flex-shrink: 0;
    display: block;
}
.image-slider__nav {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: rgba(255, 255, 255, 0.9);
    border: none;
    border-radius: 50%;
    width: 44px;
    height: 44px;
    font-size: 1.5rem;
    line-height: 1;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    transition: background 0.2s, transform 0.2s;
    z-index: 2;
}
.image-slider__nav:hover {
    background: white;
    transform: translateY(-50%) scale(1.05);
}
.image-slider__nav--prev { left: 12px; }
.image-slider__nav--next { right: 12px; }
.image-slider__dots {
    position: absolute;
    bottom: 14px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 8px;
    z-index: 2;
}
.image-slider__dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.5);
    transition: background 0.2s;
}
.image-slider__dot--active {
    background: white;
}""",

    "registration_form": """.registration-form {
    background: white;
    padding: 2.5rem;
    border-radius: 12px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
    width: 100%;
    max-width: 480px;
    margin: 2rem auto;
}
.registration-form__title {
    margin: 0 0 1.5rem 0;
    font-size: 1.75rem;
    color: #1a1a2e;
}""",

    "product_card": """.product-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.product-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}
.product-card__image {
    width: 100%;
    height: 200px;
    object-fit: cover;
}
.product-card__body {
    padding: 1rem;
}
.product-card__title {
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
}
.product-card__price {
    font-weight: bold;
    color: #667eea;
    font-size: 1.25rem;
    margin: 0.5rem 0;
}
.product-card__description {
    color: #666;
    font-size: 0.9rem;
    margin: 0;
}""",

    "search_bar": """.search-bar {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    padding: 0.5rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.search-bar__label {
    position: absolute;
    left: -9999px;
}
.search-bar__input {
    flex: 1;
    padding: 0.5rem 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}
.search-bar__button {
    padding: 0.5rem 1rem;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}""",

    "nav": """.nav {
    background: #1a1a2e;
    padding: 1rem 2rem;
}
.nav__list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    gap: 1.5rem;
}""",

    "nav_item": """.nav-item__link {
    color: white;
    text-decoration: none;
    font-size: 1rem;
    transition: opacity 0.2s;
}
.nav-item__link:hover {
    opacity: 0.7;
}""",

    "header": """.header {
    background: white;
    padding: 1.5rem 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.header__title {
    margin: 0;
    color: #1a1a2e;
}""",

    "footer": """.footer {
    background: #1a1a2e;
    color: white;
    padding: 2rem;
    text-align: center;
}
.footer__copyright {
    margin: 1rem 0 0 0;
    opacity: 0.7;
    font-size: 0.9rem;
}""",

    "sidebar": """.sidebar {
    background: #f5f5f7;
    padding: 1.5rem;
    border-radius: 8px;
    min-width: 240px;
}""",

    "card_grid": """.card-grid__container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
    padding: 1.5rem;
}""",
}


BASE_STYLES = """* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #f5f5f7;
    min-height: 100vh;
    color: #1a1a2e;
    line-height: 1.5;
}
"""


MEDIA_QUERIES = """
@media (max-width: 1280px) {
    body { padding: 1rem; }
}
@media (max-width: 768px) {
    .card-grid__container { grid-template-columns: repeat(2, 1fr); }
    .login-form, .registration-form { padding: 1.5rem; }
}
@media (max-width: 320px) {
    .card-grid__container { grid-template-columns: 1fr; }
    .login-form, .registration-form { padding: 1rem; }
    .nav__list { flex-direction: column; gap: 0.5rem; }
}
"""


class CSSBuilder:
    """Собирает CSS-файл на основе типов компонентов в AMI-графе."""

    def build(self, graph: AMIGraph) -> str:
        """
        Собирает CSS-документ для всех компонентов в графе.

        Параметры:
            graph: AMIGraph с компонентами

        Возвращает:
            строку с CSS-кодом
        """
        used_types = set()
        for node in graph.components:
            self._collect_types(node, used_types)

        rules = [BASE_STYLES]

        for type_name in used_types:
            snake = self._to_snake_case(type_name)
            style = DEFAULT_STYLES.get(snake)
            if style:
                rules.append(style)

        rules.append(MEDIA_QUERIES)

        return "\n\n".join(rules)

    def _collect_types(self, node: AMINode, types: set) -> None:
        """Рекурсивно собирает все типы из графа."""
        types.add(node.type)
        for child in node.children:
            self._collect_types(child, types)

    @staticmethod
    def _to_snake_case(name: str) -> str:
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append("_")
            result.append(char.lower())
        return "".join(result)