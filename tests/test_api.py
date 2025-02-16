import pytest
from flask import url_for
import json
from src.app import app
from src.services.auth_service import auth_service

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_token():
    # Create a test user and get auth token
    user_data = {
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    token = auth_service.create_token(user_data)
    return token

def test_market_data_endpoint(client, auth_token):
    response = client.get(
        '/api/market-data',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'nifty' in data
    assert 'banknifty' in data

def test_place_order_endpoint(client, auth_token):
    order_data = {
        'symbol': 'RELIANCE',
        'quantity': 10,
        'order_type': 'MARKET',
        'transaction_type': 'BUY',
        'product': 'MIS'
    }
    
    response = client.post(
        '/api/order',
        headers={
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        },
        data=json.dumps(order_data)
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'order_id' in data
    assert data['status'] == 'success'

def test_portfolio_endpoint(client, auth_token):
    response = client.get(
        '/api/portfolio',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'positions' in data
    assert 'holdings' in data

def test_option_chain_endpoint(client, auth_token):
    response = client.get(
        '/api/option-chain?symbol=NIFTY&expiry=2025-02-27',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    if len(data) > 0:
        assert 'strikePrice' in data[0]
        assert 'CE' in data[0]
        assert 'PE' in data[0]

def test_historical_data_endpoint(client, auth_token):
    response = client.get(
        '/api/historical-data?symbol=RELIANCE&interval=1d&from=2025-01-01&to=2025-02-16',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    if len(data) > 0:
        assert 'timestamp' in data[0]
        assert 'open' in data[0]
        assert 'high' in data[0]
        assert 'low' in data[0]
        assert 'close' in data[0]
        assert 'volume' in data[0]

def test_ai_prediction_endpoint(client, auth_token):
    response = client.get(
        '/api/prediction?symbol=RELIANCE',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'prediction' in data
    assert 'confidence' in data
    assert 'factors' in data

def test_backtest_endpoint(client, auth_token):
    strategy_data = {
        'strategy': 'moving_average',
        'symbol': 'RELIANCE',
        'timeframe': '1d',
        'start_date': '2025-01-01',
        'end_date': '2025-02-16',
        'parameters': {
            'short_window': 20,
            'long_window': 50
        }
    }
    
    response = client.post(
        '/api/backtest',
        headers={
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        },
        data=json.dumps(strategy_data)
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'metrics' in data
    assert 'trades' in data

def test_unauthorized_access(client):
    response = client.get('/api/portfolio')
    assert response.status_code == 401

def test_invalid_token(client):
    response = client.get(
        '/api/portfolio',
        headers={'Authorization': 'Bearer invalid_token'}
    )
    assert response.status_code == 401

def test_missing_parameters(client, auth_token):
    order_data = {
        'symbol': 'RELIANCE',
        # Missing required parameters
    }
    
    response = client.post(
        '/api/order',
        headers={
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        },
        data=json.dumps(order_data)
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_invalid_symbol(client, auth_token):
    response = client.get(
        '/api/historical-data?symbol=INVALID&interval=1d&from=2025-01-01&to=2025-02-16',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 404

def test_rate_limiting(client, auth_token):
    # Make multiple requests quickly
    for _ in range(10):
        response = client.get(
            '/api/market-data',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
    
    # The last request should be rate limited
    assert response.status_code == 429
