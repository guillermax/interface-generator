import pytest
from app.services.nlp import NLPModule


class TestNLPModule:
    
    def setup_method(self):
        """Инициализация NLPModule для каждого теста"""
        self.nlp = NLPModule()
    
    def test_login_form_recognition(self):
        """Тестирует распознавание формы входа"""
        text = "форма входа с email и паролем"
        entities = self.nlp.predict(text)
        
        # Должна быть LoginForm
        assert any(e.entity_type == 'LoginForm' for e in entities)
        
        # Должны быть Input для email и password
        assert any(e.entity_type == 'Input' and 'email' in e.attributes.get('type', '').lower() for e in entities)
        assert any(e.entity_type == 'Input' and 'password' in e.attributes.get('type', '').lower() for e in entities)
        
        # Должен быть Button для submit
        assert any(e.entity_type == 'Button' for e in entities)
    
    def test_login_form_alternative_keyword(self):
        """Тестирует распознавание с альтернативным ключевым словом 'login form'"""
        text = "Create a login form"
        entities = self.nlp.predict(text)
        
        assert any(e.entity_type == 'LoginForm' for e in entities)
    
    def test_registration_form_recognition(self):
        """Тестирует распознавание формы регистрации"""
        text = "форма регистрации с email и паролем"
        entities = self.nlp.predict(text)
        
        # Должна быть RegistrationForm
        assert any(e.entity_type == 'RegistrationForm' for e in entities)
        
        # Должны быть Input для email и password
        assert any(e.entity_type == 'Input' and 'email' in e.attributes.get('type', '').lower() for e in entities)
        assert any(e.entity_type == 'Input' and 'password' in e.attributes.get('type', '').lower() for e in entities)
        
        # Должен быть Button для submit
        assert any(e.entity_type == 'Button' for e in entities)
    
    def test_registration_form_alternative_keyword(self):
        """Тестирует распознавание с альтернативным ключевым словом 'registration form'"""
        text = "Create a registration form"
        entities = self.nlp.predict(text)
        
        assert any(e.entity_type == 'RegistrationForm' for e in entities)
    
    def test_product_card_recognition(self):
        """Тестирует распознавание карточки товара"""
        text = "карточка товара"
        entities = self.nlp.predict(text)
        
        assert any(e.entity_type == 'ProductCard' for e in entities)
        assert any(e.entity_type == 'Image' for e in entities)
        assert any(e.entity_type == 'Text' for e in entities)
    
    def test_navbar_recognition(self):
        """Тестирует распознавание навигационного меню"""
        text = "навигационное меню"
        entities = self.nlp.predict(text)
        
        assert any(e.entity_type == 'Nav' for e in entities)
        assert any(e.entity_type == 'NavItem' for e in entities)
    
    def test_search_bar_recognition(self):
        """Тестирует распознавание поисковой строки"""
        text = "поисковая строка"
        entities = self.nlp.predict(text)

        assert any(e.entity_type == 'SearchBar' for e in entities)
        search_bar = next(e for e in entities if e.entity_type == 'SearchBar')
        assert any(
            e.entity_type == 'Button'
            and e.attributes.get('type') == 'submit'
            and e.parent_id == search_bar.entity_id
            for e in entities
        )

    def test_landing_page_recognition(self):
        """'лендинг' → page pattern returns Header, Hero, Footer."""
        entities = self.nlp.predict("лендинг")
        types = {e.entity_type for e in entities}
        assert "Header" in types
        assert "Hero" in types
        assert "Footer" in types

    def test_ecommerce_page_recognition(self):
        """'интернет-магазин' → page pattern returns Header, SearchBar, CardGrid, Footer."""
        entities = self.nlp.predict("интернет-магазин")
        types = {e.entity_type for e in entities}
        assert "Header" in types
        assert "SearchBar" in types
        assert "CardGrid" in types
        assert "Footer" in types

    def test_multiple_components_in_one_request(self):
        """'навигационное меню и форма входа' → both Nav and LoginForm returned."""
        entities = self.nlp.predict("навигационное меню и форма входа")
        types = {e.entity_type for e in entities}
        assert "Nav" in types
        assert "LoginForm" in types

    def test_landing_with_extra_component(self):
        """Landing page + extra rule: 'лендинг со слайдером' adds ImageSlider to base structure."""
        entities = self.nlp.predict("лендинг страница со слайдером")
        root_types = [e.entity_type for e in entities if e.parent_id is None]
        assert "Header" in root_types
        assert "Hero" in root_types
        assert "Features" in root_types
        assert "Footer" in root_types
        assert "ImageSlider" in root_types
        # Only one Nav (inside Header, not as extra root)
        assert root_types.count("Nav") == 0

    def test_landing_with_slider_correct_order(self):
        """'лендинг со слайдером' → Header first, Footer last, ImageSlider in between."""
        entities = self.nlp.predict("лендинг со слайдером")
        root_types = [e.entity_type for e in entities if e.parent_id is None]
        assert root_types[0] == "Header"
        assert root_types[-1] == "Footer"
        assert "ImageSlider" in root_types[1:-1]

    def test_unknown_text_recognition(self):
        """Тестирует обработку неизвестного текста"""
        text = "Какой-то случайный текст"
        entities = self.nlp.predict(text)
        
        # Должен быть Container
        assert any(e.entity_type == 'Container' for e in entities)
    
    def test_entity_hierarchy(self):
        """Тестирует иерархию сущностей (parent_id)"""
        text = "форма входа"
        entities = self.nlp.predict(text)
        
        # Найти LoginForm
        login_form = next((e for e in entities if e.entity_type == 'LoginForm'), None)
        assert login_form is not None
        
        # Все Input и Button должны иметь parent_id, указывающий на LoginForm
        inputs_and_buttons = [e for e in entities if e.entity_type in ['Input', 'Button']]
        for entity in inputs_and_buttons:
            assert entity.parent_id == login_form.entity_id
    
    def test_confidence_score(self):
        """Тестирует что confidence установлен корректно"""
        text = "форма входа"
        entities = self.nlp.predict(text)
        
        for entity in entities:
            assert 0 < entity.confidence <= 1
            assert entity.confidence >= 0.85
