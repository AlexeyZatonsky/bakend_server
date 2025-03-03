import pytest
import sys
from pathlib import Path
import time
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.database import get_async_session
from src.app import app
from typing import AsyncGenerator

from httpx import AsyncClient, ASGITransport

from src.settings.config import settings


sys.path.append(str(Path(__file__).parent.parent))

@pytest.fixture(scope="session", autouse=True)
def verify_test_environment():
    if settings.MODE != "TEST":
        pytest.skip("Skipping tests for non-test environment")


@pytest.fixture(scope="function")
async def ac() -> AsyncGenerator[AsyncClient, None]:

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_session():
        yield session
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

