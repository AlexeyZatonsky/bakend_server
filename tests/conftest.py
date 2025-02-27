import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

@pytest.fixture(scope='session', autouse=True)
def faker_session_locale():
    return ['ru_RU']