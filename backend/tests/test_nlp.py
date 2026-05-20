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
