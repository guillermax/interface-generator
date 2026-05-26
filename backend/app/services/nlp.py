"""NLP module — rule-based entity recognition.

Architecture:
  1. PAGE_PATTERNS checked first (mutually exclusive page compositions).
  2. If no page pattern matches, RULES are applied independently and accumulated.
  3. If all rules return empty → fallback Container.
"""
import uuid
from app.schemas.ami import Entity


def _uid() -> str:
    return uuid.uuid4().hex[:8]


# ─────────────────────────── atom / molecule helpers ─────────────────────────

def _nav_entities(parent_id: str, items: list[tuple[str, str]] | None = None) -> list[Entity]:
    """Return a Nav entity + NavItem children parented to *parent_id*."""
    nav_id = _uid()
    if items is None:
        items = [("Главная", "#home"), ("О нас", "#about"), ("Контакты", "#contact")]
    entities = [
        Entity(entity_id=nav_id, entity_type="Nav", text="Navigation",
               attributes={"label": "Навигация"}, parent_id=parent_id, confidence=0.95),
    ]
    for label, href in items:
        entities.append(Entity(
            entity_id=_uid(), entity_type="NavItem", text=label,
            attributes={"label": label, "href": href},
            parent_id=nav_id, confidence=0.95,
        ))
    return entities


def _header_with_nav() -> list[Entity]:
    """Return Header (root) + Nav + 3 NavItems."""
    header_id = _uid()
    header = Entity(entity_id=header_id, entity_type="Header", text="Header",
                    attributes={"title": "Interface Generator", "label": "Шапка сайта"},
                    parent_id=None, confidence=0.95)
    return [header, *_nav_entities(header_id)]


def _footer() -> Entity:
    return Entity(entity_id=_uid(), entity_type="Footer", text="Footer",
                  attributes={"copyright": "© 2024. Все права защищены."},
                  parent_id=None, confidence=0.95)


# ──────────────────────────── page-level builders ────────────────────────────

# Each builder returns (header_entities, middle_entities, footer_entities).
# This ensures Footer is always last even when component rules add extra items.

def _build_landing() -> tuple[list[Entity], list[Entity], list[Entity]]:
    header = _header_with_nav()

    hero_id = _uid()
    middle: list[Entity] = [Entity(
        entity_id=hero_id, entity_type="Hero", text="Hero",
        attributes={
            "title": "Создавайте интерфейсы из текста",
            "subtitle": "Опишите нужный компонент — система сгенерирует HTML и CSS автоматически",
            "cta_label": "Начать", "cta_href": "#",
        },
        parent_id=None, confidence=0.95,
    )]

    features_id = _uid()
    middle.append(Entity(
        entity_id=features_id, entity_type="Features", text="Features",
        attributes={"label": "Преимущества"},
        parent_id=None, confidence=0.95,
    ))
    for label in ["Быстро", "Просто", "Качественно"]:
        middle.append(Entity(
            entity_id=_uid(), entity_type="Text", text=label,
            attributes={"label": label, "content": label},
            parent_id=features_id, confidence=0.95,
        ))

    return header, middle, [_footer()]


def _build_ecommerce() -> tuple[list[Entity], list[Entity], list[Entity]]:
    header = _header_with_nav()

    search_id = _uid()
    middle: list[Entity] = [Entity(
        entity_id=search_id, entity_type="SearchBar", text="Search Bar",
        attributes={"label": "Поиск товаров", "placeholder": "Найти товар..."},
        parent_id=None, confidence=0.95,
    )]
    middle.append(Entity(
        entity_id=_uid(), entity_type="Button", text="Найти",
        attributes={"label": "Найти", "type": "submit"},
        parent_id=search_id, confidence=0.95,
    ))

    grid_id = _uid()
    middle.append(Entity(
        entity_id=grid_id, entity_type="CardGrid", text="Product Grid",
        attributes={"label": "Каталог товаров"},
        parent_id=None, confidence=0.95,
    ))
    for i, name in enumerate(["Товар 1", "Товар 2", "Товар 3"], 1):
        card_id = _uid()
        middle.append(Entity(
            entity_id=card_id, entity_type="ProductCard", text=name,
            attributes={"label": name},
            parent_id=grid_id, confidence=0.95,
        ))
        middle.append(Entity(
            entity_id=_uid(), entity_type="Image", text=f"Product {i}",
            attributes={"alt": name, "src": f"https://placehold.co/300x200/e2e8f0/64748b?text={name}"},
            parent_id=card_id, confidence=0.95,
        ))
        middle.append(Entity(
            entity_id=_uid(), entity_type="Text", text=f"Цена: {i * 999} ₽",
            attributes={"label": f"Цена: {i * 999} ₽"},
            parent_id=card_id, confidence=0.95,
        ))

    return header, middle, [_footer()]


def _build_blog() -> tuple[list[Entity], list[Entity], list[Entity]]:
    header = _header_with_nav()

    sidebar_id = _uid()
    middle: list[Entity] = [Entity(
        entity_id=sidebar_id, entity_type="Sidebar", text="Sidebar",
        attributes={"label": "Рубрики"},
        parent_id=None, confidence=0.95,
    )]
    middle.extend(_nav_entities(sidebar_id, [
        ("Технологии", "#tech"), ("Новости", "#news"), ("Обзоры", "#reviews"),
    ]))

    middle.append(Entity(
        entity_id=_uid(), entity_type="Heading", text="Заголовок статьи",
        attributes={"level": 1, "text": "Заголовок статьи"},
        parent_id=None, confidence=0.95,
    ))
    middle.append(Entity(
        entity_id=_uid(), entity_type="Text", text="Содержание статьи",
        attributes={"label": "Содержание", "content": "Текст публикации..."},
        parent_id=None, confidence=0.95,
    ))

    return header, middle, [_footer()]


def _build_dashboard() -> tuple[list[Entity], list[Entity], list[Entity]]:
    header = _header_with_nav()

    sidebar_id = _uid()
    middle: list[Entity] = [Entity(
        entity_id=sidebar_id, entity_type="Sidebar", text="Sidebar",
        attributes={"label": "Меню администратора"},
        parent_id=None, confidence=0.95,
    )]
    middle.extend(_nav_entities(sidebar_id, [
        ("Дашборд", "#dashboard"), ("Пользователи", "#users"), ("Настройки", "#settings"),
    ]))

    grid_id = _uid()
    middle.append(Entity(
        entity_id=grid_id, entity_type="CardGrid", text="Stats",
        attributes={"label": "Статистика"},
        parent_id=None, confidence=0.95,
    ))
    for label in ["Пользователи: 1 024", "Заказы: 256", "Выручка: 512 000 ₽"]:
        card_id = _uid()
        middle.append(Entity(
            entity_id=card_id, entity_type="ProductCard", text=label,
            attributes={"label": label},
            parent_id=grid_id, confidence=0.95,
        ))
        middle.append(Entity(
            entity_id=_uid(), entity_type="Text", text=label,
            attributes={"label": label},
            parent_id=card_id, confidence=0.95,
        ))

    return header, middle, [_footer()]


# Page patterns: (matcher, builder). Checked in order; first match wins.
_PAGE_PATTERNS: list[tuple] = [
    (lambda t: any(k in t for k in ["лендинг", "landing", "одностраничник"]), _build_landing),
    (lambda t: any(k in t for k in ["интернет-магазин", "магазин", "ecommerce", "онлайн магазин"]), _build_ecommerce),
    (lambda t: any(k in t for k in ["блог", "blog"]), _build_blog),
    (lambda t: any(k in t for k in ["админ-панель", "админка", "dashboard", "admin panel"]), _build_dashboard),
]


# ─────────────────────────── component rules ─────────────────────────────────
# Each rule accepts `exclude`: a set of entity_types already added by a page
# pattern. If the rule's primary type is in exclude it returns [] immediately,
# preventing duplicate components on full-page layouts.

def _recognize_login_form(t: str, exclude: frozenset = frozenset()) -> list[Entity]:
    if "LoginForm" in exclude:
        return []
    if not any(k in t for k in ["форма входа", "login form", "авторизац", "вход"]):
        return []
    form_id = _uid()
    return [
        Entity(entity_id=form_id, entity_type="LoginForm", text="Login Form",
               attributes={"label": "Login Form"}, parent_id=None, confidence=0.95),
        Entity(entity_id=_uid(), entity_type="Input", text="Email Input",
               attributes={"type": "email", "placeholder": "Enter your email"},
               parent_id=form_id, confidence=0.95),
        Entity(entity_id=_uid(), entity_type="Input", text="Password Input",
               attributes={"type": "password", "placeholder": "Enter your password"},
               parent_id=form_id, confidence=0.95),
        Entity(entity_id=_uid(), entity_type="Button", text="Sign In",
               attributes={"label": "Sign In", "type": "submit"},
               parent_id=form_id, confidence=0.95),
    ]


def _recognize_registration_form(t: str, exclude: frozenset = frozenset()) -> list[Entity]:
    if "RegistrationForm" in exclude:
        return []
    if not any(k in t for k in ["форма регистрации", "registration form", "регистрац", "signup", "sign up"]):
        return []
    form_id = _uid()
    return [
        Entity(entity_id=form_id, entity_type="RegistrationForm", text="Registration Form",
               attributes={"label": "Registration Form"}, parent_id=None, confidence=0.95),
        Entity(entity_id=_uid(), entity_type="Input", text="Email Input",
               attributes={"type": "email", "placeholder": "Enter your email"},
               parent_id=form_id, confidence=0.95),
        Entity(entity_id=_uid(), entity_type="Input", text="Password Input",
               attributes={"type": "password", "placeholder": "Enter your password"},
               parent_id=form_id, confidence=0.95),
        Entity(entity_id=_uid(), entity_type="Input", text="Confirm Password",
               attributes={"type": "password", "placeholder": "Confirm your password"},
               parent_id=form_id, confidence=0.95),
        Entity(entity_id=_uid(), entity_type="Button", text="Sign Up",
               attributes={"label": "Sign Up", "type": "submit"},
               parent_id=form_id, confidence=0.95),
    ]


def _recognize_product_card(t: str, exclude: frozenset = frozenset()) -> list[Entity]:
    if "ProductCard" in exclude:
        return []
    if not any(k in t for k in ["карточка товара", "product card", "товар", "card"]):
        return []
    card_id = _uid()
    return [
        Entity(entity_id=card_id, entity_type="ProductCard", text="Product Card",
               attributes={"label": "Product Card"}, parent_id=None, confidence=0.95),
        Entity(entity_id=_uid(), entity_type="Image", text="Product Image",
               attributes={"alt": "Product"}, parent_id=card_id, confidence=0.95),
        Entity(entity_id=_uid(), entity_type="Text", text="Product Title",
               attributes={"label": "Product Title"}, parent_id=card_id, confidence=0.95),
        Entity(entity_id=_uid(), entity_type="Text", text="Price",
               attributes={"label": "Price"}, parent_id=card_id, confidence=0.95),
    ]


def _recognize_nav(t: str, exclude: frozenset = frozenset()) -> list[Entity]:
    if "Nav" in exclude:
        return []
    if not any(k in t for k in ["навигац", "navbar", "меню", "navigation", "menu"]):
        return []
    nav_id = _uid()
    entities = [
        Entity(entity_id=nav_id, entity_type="Nav", text="Navigation",
               attributes={"label": "Navigation"}, parent_id=None, confidence=0.95),
    ]
    for label, href in [("Home", "#home"), ("About", "#about"), ("Contact", "#contact")]:
        entities.append(Entity(
            entity_id=_uid(), entity_type="NavItem", text=label,
            attributes={"label": label, "href": href},
            parent_id=nav_id, confidence=0.95,
        ))
    return entities


def _recognize_slider(t: str, exclude: frozenset = frozenset()) -> list[Entity]:
    if "ImageSlider" in exclude:
        return []
    if not any(k in t for k in ["слайдер", "карусель", "slider", "carousel"]):
        return []
    slider_id = _uid()
    entities = [
        Entity(entity_id=slider_id, entity_type="ImageSlider", text="Image Slider",
               attributes={"label": "Image Slider", "slide_count": 3},
               parent_id=None, confidence=0.9),
    ]
    for i in range(1, 4):
        entities.append(Entity(
            entity_id=_uid(), entity_type="Image", text=f"Slide {i}",
            attributes={"alt": f"Slide {i}", "src": f"https://picsum.photos/800/400?random={i}"},
            parent_id=slider_id, confidence=0.9,
        ))
    return entities


def _recognize_modal(t: str, exclude: frozenset = frozenset()) -> list[Entity]:
    if "Modal" in exclude:
        return []
    if not any(k in t for k in ["модальное окно", "всплывающее окно", "modal", "диалог"]):
        return []
    modal_id = _uid()
    return [
        Entity(entity_id=modal_id, entity_type="Modal", text="Modal",
               attributes={"label": "Modal Dialog"}, parent_id=None, confidence=0.9),
        Entity(entity_id=_uid(), entity_type="Heading", text="Заголовок",
               attributes={"level": 2, "text": "Заголовок"},
               parent_id=modal_id, confidence=0.9),
        Entity(entity_id=_uid(), entity_type="Button", text="Close",
               attributes={"label": "Close", "type": "button"},
               parent_id=modal_id, confidence=0.9),
    ]


def _recognize_search_bar(t: str, exclude: frozenset = frozenset()) -> list[Entity]:
    if "SearchBar" in exclude:
        return []
    if not any(k in t for k in ["поиск", "поисковая строка", "search bar", "search field"]):
        return []
    bar_id = _uid()
    return [
        Entity(entity_id=bar_id, entity_type="SearchBar", text="Search Bar",
               attributes={"label": "Поиск", "placeholder": "Поиск..."},
               parent_id=None, confidence=0.9),
        Entity(entity_id=_uid(), entity_type="Button", text="Найти",
               attributes={"label": "Найти", "type": "submit"},
               parent_id=bar_id, confidence=0.9),
    ]


def _recognize_accordion(t: str, exclude: frozenset = frozenset()) -> list[Entity]:
    if "Accordion" in exclude:
        return []
    if not any(k in t for k in ["аккордеон", "accordion", "развёртываемый список"]):
        return []
    acc_id = _uid()
    return [
        Entity(entity_id=acc_id, entity_type="Accordion", text="Accordion",
               attributes={"label": "Accordion"}, parent_id=None, confidence=0.9),
        Entity(entity_id=_uid(), entity_type="Heading", text="Section 1",
               attributes={"level": 3, "text": "Section 1"},
               parent_id=acc_id, confidence=0.9),
    ]


# Ordered list of component rules.
_RULES = [
    _recognize_login_form,
    _recognize_registration_form,
    _recognize_product_card,
    _recognize_nav,
    _recognize_slider,
    _recognize_modal,
    _recognize_search_bar,
    _recognize_accordion,
]


# ─────────────────────────── public API ──────────────────────────────────────

class NLPModule:
    """NLP module for entity recognition (rule-based)."""

    def predict(self, text: str) -> list[Entity]:
        t = text.lower()
        header_entities: list[Entity] = []
        middle_entities: list[Entity] = []
        footer_entities: list[Entity] = []

        # 1. First matching page pattern splits into positional groups.
        #    Footer always stays last regardless of what rules add below.
        for matcher, builder in _PAGE_PATTERNS:
            if matcher(t):
                h, m, f = builder()
                header_entities.extend(h)
                middle_entities.extend(m)
                footer_entities.extend(f)
                break

        # 2. All component rules run independently, appending to middle so they
        #    appear between header and footer. Pass already-added types to prevent
        #    duplicates (e.g. Nav inside Header won't be added again).
        already_added = frozenset(
            e.entity_type for e in header_entities + middle_entities + footer_entities
        )
        for rule in _RULES:
            middle_entities.extend(rule(t, exclude=already_added))

        entities = header_entities + middle_entities + footer_entities

        # 3. Fallback when nothing matched
        if not entities:
            entities.append(Entity(
                entity_id=_uid(), entity_type="Container", text=text,
                attributes={"label": "Container"}, parent_id=None, confidence=0.85,
            ))

        return entities
