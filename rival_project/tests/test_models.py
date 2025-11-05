from app.models.company import Company
from app.models.event import Event
from app.models.user import User
from app.models.watchlist import Watchlist
import pytest

@pytest.fixture
def sample_company():
    return Company(name="Test Company", description="A company for testing.")

@pytest.fixture
def sample_event():
    return Event(title="Test Event", date="2023-01-01", company_id=1)

@pytest.fixture
def sample_user():
    return User(username="testuser", email="test@example.com", password="password")

@pytest.fixture
def sample_watchlist(sample_user):
    return Watchlist(user_id=sample_user.id, company_id=1)

def test_company_creation(sample_company):
    assert sample_company.name == "Test Company"
    assert sample_company.description == "A company for testing."

def test_event_creation(sample_event):
    assert sample_event.title == "Test Event"
    assert sample_event.date == "2023-01-01"

def test_user_creation(sample_user):
    assert sample_user.username == "testuser"
    assert sample_user.email == "test@example.com"

def test_watchlist_creation(sample_watchlist):
    assert sample_watchlist.user_id == sample_watchlist.user_id
    assert sample_watchlist.company_id == 1