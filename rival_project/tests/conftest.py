import pytest
from app import create_app
from app.config import Config

class TestConfig(Config):
    TESTING = True

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        yield app
