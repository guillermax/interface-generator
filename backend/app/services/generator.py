"""
Сервис генерации интерфейса — реальный конвейер.

Цепочка обработки:
NLP-модуль → AMI Builder → Template Engine → CSS Builder → Validator → Storage
"""
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.nlp import NLPModule
from app.services.ami_builder import AMIBuilder
from app.services.template_engine import TemplateEngine
from app.services.css_builder import CSSBuilder
from app.services.validator import Validator
from app.services.storage import StorageService


# Синглтоны без состояния — инициализируются один раз при импорте
_nlp = NLPModule()
_ami_builder = AMIBuilder()
_template_engine = TemplateEngine()
_css_builder = CSSBuilder()
_validator = Validator()


def generate(text: str) -> dict:
    """
    Синхронный конвейер генерации.
    Используется напрямую в тестах и как ядро generate_interface.
    """
    start = time.perf_counter()

    entities = _nlp.predict(text)
    graph = _ami_builder.build(entities)
    html = _template_engine.render(graph)
    css = _css_builder.build(graph)
    html, validation_issues = _validator.validate(html)

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    return {
        "html": html,
        "css": css,
        "generation_time_ms": elapsed_ms,
        "ami": graph,
        "validation_issues": validation_issues,
        "_entities": entities,          # используется только внутри generate_interface
    }


async def generate_interface(text: str, db: AsyncSession) -> dict:
    """
    Асинхронный фасад: запускает конвейер и сохраняет результат в БД.
    request_id берётся из БД.
    """
    storage = StorageService(db)
    request_id = await storage.save_request(text)

    try:
        result = generate(text)

        entities = result.pop("_entities")
        nlp_result = [e.model_dump() for e in entities]
        ami_dict = result["ami"].model_dump()

        await storage.save_result(
            request_id=request_id,
            html=result["html"],
            css=result["css"],
            ami_graph=ami_dict,
            generation_time_ms=result["generation_time_ms"],
            nlp_result=nlp_result,
        )

        result["request_id"] = str(request_id)
        return result

    except Exception as exc:
        await storage.mark_error(request_id, str(exc))
        raise
