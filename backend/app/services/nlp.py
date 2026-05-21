from app.schemas.ami import Entity


class NLPModule:
    """NLP модуль для распознавания сущностей (rule-based заглушка)"""
    
    def predict(self, text: str) -> list[Entity]:
        """
        Анализирует текст и возвращает список распознанных сущностей.
        Rule-based парсер по ключевым словам.
        """
        text_lower = text.lower()
        entities = []
        
        # Логин форма
        if any(keyword in text_lower for keyword in ['форма входа', 'login form', 'авторизац', 'вход']):
            login_form_id = __import__('uuid').uuid4().hex[:8]
            
            form_entity = Entity(
                entity_id=login_form_id,
                entity_type='LoginForm',
                text='Login Form',
                attributes={'label': 'Login Form'},
                parent_id=None,
                confidence=0.95
            )
            entities.append(form_entity)
            
            # Дети формы
            email_input = Entity(
                entity_id=__import__('uuid').uuid4().hex[:8],
                entity_type='Input',
                text='Email Input',
                attributes={'type': 'email', 'placeholder': 'Enter your email'},
                parent_id=login_form_id,
                confidence=0.95
            )
            entities.append(email_input)
            
            password_input = Entity(
                entity_id=__import__('uuid').uuid4().hex[:8],
                entity_type='Input',
                text='Password Input',
                attributes={'type': 'password', 'placeholder': 'Enter your password'},
                parent_id=login_form_id,
                confidence=0.95
            )
            entities.append(password_input)
            
            submit_button = Entity(
                entity_id=__import__('uuid').uuid4().hex[:8],
                entity_type='Button',
                text='Sign In',
                attributes={'label': 'Sign In', 'type': 'submit'},
                parent_id=login_form_id,
                confidence=0.95
            )
            entities.append(submit_button)
        
        # Форма регистрации
        elif any(keyword in text_lower for keyword in ['форма регистрации', 'registration form', 'регистрац', 'signup', 'sign up']):
            registration_form_id = __import__('uuid').uuid4().hex[:8]
            
            form_entity = Entity(
                entity_id=registration_form_id,
                entity_type='RegistrationForm',
                text='Registration Form',
                attributes={'label': 'Registration Form'},
                parent_id=None,
                confidence=0.95
            )
            entities.append(form_entity)
            
            # Дети формы
            email_input = Entity(
                entity_id=__import__('uuid').uuid4().hex[:8],
                entity_type='Input',
                text='Email Input',
                attributes={'type': 'email', 'placeholder': 'Enter your email'},
                parent_id=registration_form_id,
                confidence=0.95
            )
            entities.append(email_input)
            
            password_input = Entity(
                entity_id=__import__('uuid').uuid4().hex[:8],
                entity_type='Input',
                text='Password Input',
                attributes={'type': 'password', 'placeholder': 'Enter your password'},
                parent_id=registration_form_id,
                confidence=0.95
            )
            entities.append(password_input)
            
            confirm_password_input = Entity(
                entity_id=__import__('uuid').uuid4().hex[:8],
                entity_type='Input',
                text='Confirm Password Input',
                attributes={'type': 'password', 'placeholder': 'Confirm your password'},
                parent_id=registration_form_id,
                confidence=0.95
            )
            entities.append(confirm_password_input)
            
            submit_button = Entity(
                entity_id=__import__('uuid').uuid4().hex[:8],
                entity_type='Button',
                text='Sign Up',
                attributes={'label': 'Sign Up', 'type': 'submit'},
                parent_id=registration_form_id,
                confidence=0.95
            )
            entities.append(submit_button)
        
        # Карточка товара
        elif any(keyword in text_lower for keyword in ['карточка товара', 'product card', 'товар', 'card']):
            product_card_id = __import__('uuid').uuid4().hex[:8]
            
            card_entity = Entity(
                entity_id=product_card_id,
                entity_type='ProductCard',
                text='Product Card',
                attributes={'label': 'Product Card'},
                parent_id=None,
                confidence=0.95
            )
            entities.append(card_entity)
            
            # Дети карточки
            image = Entity(
                entity_id=__import__('uuid').uuid4().hex[:8],
                entity_type='Image',
                text='Product Image',
                attributes={'alt': 'Product'},
                parent_id=product_card_id,
                confidence=0.95
            )
            entities.append(image)
            
            title = Entity(
                entity_id=__import__('uuid').uuid4().hex[:8],
                entity_type='Text',
                text='Product Title',
                attributes={'label': 'Product Title'},
                parent_id=product_card_id,
                confidence=0.95
            )
            entities.append(title)
            
            price = Entity(
                entity_id=__import__('uuid').uuid4().hex[:8],
                entity_type='Text',
                text='Price',
                attributes={'label': 'Price'},
                parent_id=product_card_id,
                confidence=0.95
            )
            entities.append(price)
        
        # Навигационное меню
        elif any(keyword in text_lower for keyword in ['навигац', 'navbar', 'меню', 'navigation', 'menu']):
            nav_id = __import__('uuid').uuid4().hex[:8]

            nav_entity = Entity(
                entity_id=nav_id,
                entity_type='Nav',
                text='Navigation',
                attributes={'label': 'Navigation'},
                parent_id=None,
                confidence=0.95
            )
            entities.append(nav_entity)

            # Три пункта меню
            for i, item in enumerate(['Home', 'About', 'Contact'], 1):
                menu_item = Entity(
                    entity_id=__import__('uuid').uuid4().hex[:8],
                    entity_type='NavItem',
                    text=item,
                    attributes={'label': item, 'href': f'#{item.lower()}'},
                    parent_id=nav_id,
                    confidence=0.95
                )
                entities.append(menu_item)

        # Слайдер / карусель изображений
        elif any(keyword in text_lower for keyword in ['слайдер', 'карусель', 'slider', 'carousel']):
            slider_id = __import__('uuid').uuid4().hex[:8]

            slider_entity = Entity(
                entity_id=slider_id,
                entity_type='ImageSlider',
                text='Image Slider',
                attributes={'label': 'Image Slider', 'slide_count': 3},
                parent_id=None,
                confidence=0.9,
            )
            entities.append(slider_entity)

            for i in range(1, 4):
                slide = Entity(
                    entity_id=__import__('uuid').uuid4().hex[:8],
                    entity_type='Image',
                    text=f'Slide {i}',
                    attributes={
                        'alt': f'Slide {i}',
                        'src': f'https://picsum.photos/800/400?random={i}',
                    },
                    parent_id=slider_id,
                    confidence=0.9,
                )
                entities.append(slide)

        # Модальное / всплывающее окно
        elif any(keyword in text_lower for keyword in ['модальное окно', 'всплывающее окно', 'modal', 'диалог']):
            modal_id = __import__('uuid').uuid4().hex[:8]

            modal_entity = Entity(
                entity_id=modal_id,
                entity_type='Modal',
                text='Modal',
                attributes={'label': 'Modal Dialog'},
                parent_id=None,
                confidence=0.9,
            )
            entities.append(modal_entity)

            heading = Entity(
                entity_id=__import__('uuid').uuid4().hex[:8],
                entity_type='Heading',
                text='Заголовок',
                attributes={'level': 2, 'text': 'Заголовок'},
                parent_id=modal_id,
                confidence=0.9,
            )
            entities.append(heading)

            close_btn = Entity(
                entity_id=__import__('uuid').uuid4().hex[:8],
                entity_type='Button',
                text='Close',
                attributes={'label': 'Close', 'type': 'button'},
                parent_id=modal_id,
                confidence=0.9,
            )
            entities.append(close_btn)

        # Аккордеон / развёртываемый список
        elif any(keyword in text_lower for keyword in ['аккордеон', 'accordion', 'развёртываемый список']):
            accordion_id = __import__('uuid').uuid4().hex[:8]

            accordion_entity = Entity(
                entity_id=accordion_id,
                entity_type='Accordion',
                text='Accordion',
                attributes={'label': 'Accordion'},
                parent_id=None,
                confidence=0.9,
            )
            entities.append(accordion_entity)

            heading = Entity(
                entity_id=__import__('uuid').uuid4().hex[:8],
                entity_type='Heading',
                text='Section 1',
                attributes={'level': 3, 'text': 'Section 1'},
                parent_id=accordion_id,
                confidence=0.9,
            )
            entities.append(heading)

        # Если ничего не распознано
        else:
            container_id = __import__('uuid').uuid4().hex[:8]
            container = Entity(
                entity_id=container_id,
                entity_type='Container',
                text=text,
                attributes={'label': 'Container'},
                parent_id=None,
                confidence=0.85
            )
            entities.append(container)
        
        return entities
