import pytest
from contextlib import nullcontext as does_not_raise



from src.settings.config import settings

@pytest.mark.parametrize("mode, expectation",
                         [
                            ("PROD", False),
                            ("DEV", False),
                            ("TEST", True)
                          ]
                         )
def test_settings_config(mode, expectation):
    assert (settings.MODE == mode) == expectation

