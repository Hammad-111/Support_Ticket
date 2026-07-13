import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ALGORITHM"] = "HS256"
os.environ["REDIS_URL"] = "memory://"

import pytest
from httpx import ASGITransport, AsyncClient

import app.models.reply
import app.models.ticket
import app.models.user
from app.db.database import SessionLocal, engine, get_db
from app.core.rate_limit import limiter
from app.main import app
from app.models.base import Base

limiter.enabled = False


async def override_get_db():
    async with SessionLocal() as session:
        yield session


@pytest.fixture
async def client():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
