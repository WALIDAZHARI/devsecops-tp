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
    assert b'Product Service is healthy' in response.data

def test_create_product(client):
    data = {
        'name': 'Test Product',
        'description': 'A test product',
        'price': 99.99,
        'stock': 100
    }
    response = client.post('/products', json=data)
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert 'id' in response_data
    assert response_data['name'] == data['name']
    assert response_data['price'] == data['price']

def test_get_products(client):
    response = client.get('/products')
    assert response.status_code == 200
    products = json.loads(response.data)
    assert isinstance(products, list)

def test_get_product(client):
    # First create a product
    data = {
        'name': 'Get Product',
        'description': 'A product to get',
        'price': 49.99,
        'stock': 50
    }
    create_response = client.post('/products', json=data)
    product_id = json.loads(create_response.data)['id']
    
    # Then get the product
    response = client.get(f'/products/{product_id}')
    assert response.status_code == 200
    product = json.loads(response.data)
    assert product['name'] == data['name']
    assert product['price'] == data['price']
