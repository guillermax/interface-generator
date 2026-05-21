"""
Generation pipeline:
NLP → AMI Builder → Template Engine (+ LLM Fallback) → CSS Builder → Validator → Storage
"""
import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.nlp import NLPModule
from app.services.ami_builder import AMIBuilder
from app.services.template_engine import TemplateEngine
from app.services.css_builder import CSSBuilder
from app.services.validator import Validator
from app.services.storage import StorageService
from app.services.llm_client import get_llm_client

logger = logging.getLogger(__name__)

_nlp = NLPModule()
_ami_builder = AMIBuilder()
_template_engine = TemplateEngine()
_css_builder = CSSBuilder()
_validator = Validator()


async def generate_interface(text: str, db: AsyncSession) -> dict:
    """
    Full async pipeline: NLP → AMI → Template/LLM → CSS → Validate → persist → return.
    """
    storage = StorageService(db)
    request_id = await storage.save_request(text)

    try:
        start = time.perf_counter()

        entities = _nlp.predict(text)
        graph = _ami_builder.build(entities)

        llm_client = get_llm_client()
        html, components_log = await _template_engine.render(graph, llm_client)

        css = _css_builder.build(graph)
        html, validation_issues = _validator.validate(html)

        elapsed_ms = int((time.perf_counter() - start) * 1000)

        ami_dict = graph.model_dump()
        nlp_result = [e.model_dump() for e in entities]

        await storage.save_result(
            request_id=request_id,
            html=html,
            css=css,
            ami_graph=ami_dict,
            generation_time_ms=elapsed_ms,
            nlp_result=nlp_result,
            components_log=components_log,
        )

        logger.info(
            "Generated interface for '%s' in %dms (%d components)",
            text[:50], elapsed_ms, len(components_log),
        )

        return {
            "request_id": str(request_id),
            "html": html,
            "css": css,
            "generation_time_ms": elapsed_ms,
            "ami": graph,
            "validation_issues": validation_issues,
        }

    except Exception as exc:
        await storage.mark_error(request_id, str(exc))
        raise
