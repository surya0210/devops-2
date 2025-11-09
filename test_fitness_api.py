import pytest
from ACEest_Fitness_API import app

# Use Flask’s test client (doesn't need the server running)
@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_home(client):
    """Check if the API home route works"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert "ACEest Fitness API" in data["message"]

def test_save_user_info(client):
    """Test saving user information"""
    payload = {
        "name": "Kalaiarasan",
        "age": 28,
        "gender": "M",
        "height": 175,
        "weight": 70
    }
    response = client.post('/user_info', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "user_info" in data
    assert data["user_info"]["bmi"] > 0

def test_add_workout(client):
    """Test adding a workout"""
    payload = {
        "category": "Workout",
        "exercise": "Push-ups",
        "duration": 30
    }
    response = client.post('/add_workout', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "Push-ups" in data["message"]

def test_get_workouts(client):
    """Test fetching all workouts"""
    response = client.get('/workouts')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, dict)
    assert "Workout" in data

def test_get_summary(client):
    """Test getting summary"""
    response = client.get('/summary')
    assert response.status_code == 200
    data = response.get_json()
    assert "total_minutes" in data
    assert "total_calories" in data
    assert data["total_minutes"] >= 0

def test_export_pdf(client):
    """Test PDF export"""
    response = client.get('/export_pdf')
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
