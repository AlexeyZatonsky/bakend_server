import pytest
import pytest_asyncio
import sys
import asyncio
from pathlib import Path
import time
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import delete
from httpx import AsyncClient, ASGITransport

from typing import AsyncGenerator


import sys, pathlib
root_dir = pathlib.Path(__file__).resolve().parents[1]   #  …/bakend_server
sys.path.insert(0, str(root_dir)) 

from src.database import get_async_session
from src.app import app
from settings.config import settings

from src.auth.models import UsersORM, SecretInfoORM




if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

pytestmark = pytest.mark.asyncio(loop_scope="session")

# ---------- единственный loop на все тесты ----------
@pytest.fixture(scope="session")
def event_loop():
    """Глобальный event-loop, общий для всех тестов."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()



@pytest.fixture( autouse=True)
def verify_test_environment():
    if settings.MODE != "TEST":
        pytest.skip("Skipping tests for non-test environment")



@pytest.fixture()
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client



@pytest.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    agen = get_async_session()            
    session = await anext(agen)           
    try:
        yield session                    
    finally:
        await session.close()
        await agen.aclose()               


# ---------- очистка таблиц ----------
@pytest_asyncio.fixture(autouse=True)
async def clean_tables() -> None:
    yield                                 

    agen = get_async_session()
    session = await anext(agen)
    try:
        await session.execute(delete(UsersORM))
        await session.execute(delete(SecretInfoORM))
        await session.commit()
    finally:
        await session.close()

def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        default="chrome",
        choices=("chrome", "firefox"),
        help="Browser for testing"
    )
    parser.addoption(
        "--run-slow",
        default="false",
        choices=("true", "false"),
        help="Run slow tests"
    )

@pytest.fixture
def browser(request):
    return request.config.getoption("--browser")

def test_browser(browser):
    print(browser)
    
@pytest.mark.skipif('config.getoption("--run-slow") == "false"')
def test_slow():
    time.sleep(3)
    
def test_fast():
    pass



