"""Tests for StorageService — requires a live PostgreSQL on DATABASE_URL (port 5433)."""
import os
import uuid

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from app.services.storage import StorageService

pytestmark = pytest.mark.asyncio(loop_scope="session")

_SIMPLE_AMI = {
    "components": [
        {
            "type": "LoginForm",
            "children": [
                {"type": "Input", "children": []},
                {"type": "Button", "children": []},
            ],
        }
    ]
}


@pytest.fixture(scope="session")
def engine():
    return create_async_engine(os.environ["DATABASE_URL"], echo=False, poolclass=NullPool)


@pytest.fixture(scope="session")
def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False, autocommit=False, autoflush=False)


@pytest_asyncio.fixture(autouse=True)
async def clean_db(engine):
    async with engine.begin() as conn:
        await conn.execute(
            text("TRUNCATE components_log, generation_results, requests RESTART IDENTITY CASCADE")
        )


@pytest_asyncio.fixture
async def db_session(session_factory):
    async with session_factory() as session:
        yield session


# ─────────────────────────── save_request ────────────────────────────────────

async def test_save_request_returns_uuid(db_session):
    storage = StorageService(db_session)
    rid = await storage.save_request("Форма входа")
    assert isinstance(rid, uuid.UUID)


async def test_save_request_status_pending(db_session):
    storage = StorageService(db_session)
    rid = await storage.save_request("Карточка товара")
    history = await storage.get_history()
    assert any(str(rid) == item["request_id"] and item["status"] == "pending" for item in history)


# ─────────────────────────── save_result ─────────────────────────────────────

async def test_save_result_marks_done(db_session):
    storage = StorageService(db_session)
    rid = await storage.save_request("Тест")
    await storage.save_result(
        request_id=rid,
        html="<div></div>",
        css=".x{}",
        ami_graph=_SIMPLE_AMI,
        generation_time_ms=42,
        nlp_result=[],
    )
    history = await storage.get_history()
    record = next(i for i in history if str(rid) == i["request_id"])
    assert record["status"] == "done"


async def test_save_result_logs_components(db_session):
    storage = StorageService(db_session)
    rid = await storage.save_request("Тест компонентов")
    await storage.save_result(
        request_id=rid,
        html="<div></div>",
        css="",
        ami_graph=_SIMPLE_AMI,
        generation_time_ms=10,
        nlp_result=None,
    )
    full = await storage.get_full_result(str(rid))
    assert full is not None
    assert full["ami_graph"] == _SIMPLE_AMI


# ─────────────────────────── mark_error ──────────────────────────────────────

async def test_mark_error_sets_status(db_session):
    storage = StorageService(db_session)
    rid = await storage.save_request("Сломанный запрос")
    await storage.mark_error(rid, "something went wrong")
    history = await storage.get_history()
    record = next(i for i in history if str(rid) == i["request_id"])
    assert record["status"] == "error"


# ─────────────────────────── get_history ─────────────────────────────────────

async def test_get_history_returns_newest_first(db_session):
    storage = StorageService(db_session)
    r1 = await storage.save_request("Первый")
    r2 = await storage.save_request("Второй")
    history = await storage.get_history()
    ids = [h["request_id"] for h in history]
    assert ids.index(str(r2)) < ids.index(str(r1))


async def test_get_history_respects_limit(db_session):
    storage = StorageService(db_session)
    for i in range(5):
        await storage.save_request(f"Запрос {i}")
    history = await storage.get_history(limit=3)
    assert len(history) == 3


# ─────────────────────────── get_full_result ─────────────────────────────────

async def test_get_full_result_returns_html_css(db_session):
    storage = StorageService(db_session)
    rid = await storage.save_request("Полный результат")
    await storage.save_result(
        request_id=rid,
        html="<main></main>",
        css=".main{}",
        ami_graph=_SIMPLE_AMI,
        generation_time_ms=55,
        nlp_result=[{"entity": "LoginForm"}],
    )
    full = await storage.get_full_result(str(rid))
    assert full is not None
    assert full["html"] == "<main></main>"
    assert full["css"] == ".main{}"
    assert full["generation_time_ms"] == 55


async def test_get_full_result_unknown_id_returns_none(db_session):
    storage = StorageService(db_session)
    result = await storage.get_full_result(str(uuid.uuid4()))
    assert result is None


async def test_get_full_result_invalid_uuid_returns_none(db_session):
    storage = StorageService(db_session)
    result = await storage.get_full_result("not-a-uuid")
    assert result is None
