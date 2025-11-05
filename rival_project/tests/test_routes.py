from flask import url_for
import pytest

@pytest.fixture
def client(app):
    return app.test_client()

def test_index(client):
    response = client.get(url_for('main.index'))
    assert response.status_code == 200
    assert b'Welcome' in response.data  # Adjust based on actual content in index.html

# Add more tests as needed for other routes and functionalities.