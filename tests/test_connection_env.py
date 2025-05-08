import pytest




from src.settings.config import MODE_ENV

@pytest.mark.parametrize("mode, expectation",
                         [
                            ("PROD", False),
                            ("DEV", False),
                            ("TEST", True)
                          ]
                         )
def test_settings_config(mode, expectation):
    assert (MODE_ENV.MODE == mode) == expectation

