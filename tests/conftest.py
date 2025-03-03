import pytest
import sys
from pathlib import Path
import time
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.database import get_async_session
from src.app import app
from typing import AsyncGenerator
import asyncio
from httpx import AsyncClient, ASGITransport

sys.path.append(str(Path(__file__).parent.parent))

@pytest.fixture(scope="session", autouse=True)
def faker_session_locale():
    return ["ru_RU"]

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    """
    Создает асинхронный клиент для тестов
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture(scope="session")
async def session() -> AsyncGenerator[AsyncSession, None]:
    """
    Создает сессию для тестов
    """
    async for session in get_async_session():
        yield session

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

