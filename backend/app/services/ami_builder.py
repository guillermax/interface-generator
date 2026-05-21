from app.schemas.ami import AMINode, AMIGraph, Entity


class AMIValidationError(Exception):
    """Исключение при нарушении валидности AMI-графа"""
    pass


class AMIBuilder:
    """Построение и валидация AMI-графа"""
    
    KNOWN_TYPES = {
        # Atoms
        'Input', 'Button', 'Text', 'Image', 'Label', 'Heading',
        # Molecules
        'LoginForm', 'RegistrationForm', 'ProductCard', 'SearchBar', 'NavItem',
        # Organisms
        'Nav', 'Header', 'Footer', 'Sidebar', 'CardGrid',
        # LLM-only organisms (no Jinja2 template — routed to LLM fallback)
        'ImageSlider', 'Modal', 'Accordion',
        # Generic
        'Container',
    }
    
    def build(self, entities: list[Entity]) -> AMIGraph:
        """
        Превращает список Entity в AMIGraph.
        Устанавливает связи родитель–потомок и валидирует.
        """
        if not entities:
            return AMIGraph(components=[])
        
        # Создать словарь для быстрого доступа по ID
        entity_map = {e.entity_id: e for e in entities}
        
        # Валидировать типы
        for entity in entities:
            if entity.entity_type not in self.KNOWN_TYPES:
                raise AMIValidationError(
                    f"Unknown entity type: {entity.entity_type}"
                )
        
        # Построить AMINode для каждой Entity
        node_map: dict[str, AMINode] = {}
        for entity in entities:
            node = AMINode(
                node_id=entity.entity_id,
                type=entity.entity_type,
                attributes=entity.attributes,
                children=[]
            )
            node_map[entity.entity_id] = node
        
        # Установить связи родитель–потомок
        for entity in entities:
            if entity.parent_id and entity.parent_id in node_map:
                parent_node = node_map[entity.parent_id]
                child_node = node_map[entity.entity_id]
                parent_node.children.append(child_node)
        
        # Найти корневые узлы (без родителей)
        root_nodes = [
            node_map[e.entity_id] for e in entities
            if e.parent_id is None
        ]
        
        # Валидировать глубину и циклы
        for root in root_nodes:
            self._validate_depth(root)
            self._validate_cycles(root, set())
        
        graph = AMIGraph(components=root_nodes)
        return graph
    
    def _validate_depth(self, node: AMINode, depth: int = 0, max_depth: int = 8):
        """Валидирует, что глубина графа не превышает max_depth"""
        if depth > max_depth:
            raise AMIValidationError(
                f"Graph depth exceeds maximum of {max_depth}"
            )
        for child in node.children:
            self._validate_depth(child, depth + 1, max_depth)
    
    def _validate_cycles(self, node: AMINode, visited: set[str]):
        """DFS для проверки циклов"""
        if node.node_id in visited:
            raise AMIValidationError(
                f"Cycle detected in AMI graph at node {node.node_id}"
            )
        
        # Добавить текущий узел в посещенные
        visited_copy = visited.copy()
        visited_copy.add(node.node_id)
        
        # Рекурсивно проверить детей
        for child in node.children:
            self._validate_cycles(child, visited_copy)
