import pytest
from src.app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'User Service is healthy' in response.data

def test_create_user(client):
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepass123'
    }
    response = client.post('/users', json=data)
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert 'id' in response_data
    assert response_data['username'] == data['username']
    assert response_data['email'] == data['email']

def test_get_users(client):
    response = client.get('/users')
    assert response.status_code == 200
    users = json.loads(response.data)
    assert isinstance(users, list)

def test_get_user(client):
    # First create a user
    data = {
        'username': 'getuser',
        'email': 'get@example.com',
        'password': 'securepass123'
    }
    create_response = client.post('/users', json=data)
    user_id = json.loads(create_response.data)['id']
    
    # Then get the user
    response = client.get(f'/users/{user_id}')
    assert response.status_code == 200
    user = json.loads(response.data)
    assert user['username'] == data['username']
    assert user['email'] == data['email']
