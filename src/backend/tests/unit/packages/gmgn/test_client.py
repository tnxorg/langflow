import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from langflow.packages.gmgn import GmGnClient

@pytest.fixture
def gmgn_client():
    return GmGnClient()

@pytest.fixture
def mock_response():
    mock = Mock()
    mock.json.return_value = {"code": 0, "msg": "success", "data": {}}
    mock.raise_for_status.return_value = None
    return mock

def test_init_client(gmgn_client):
    assert isinstance(gmgn_client, GmGnClient)
    assert gmgn_client.BASE_URL == "https://gmgn.ai"

@patch('cloudscraper.create_scraper')
def test_make_request(mock_scraper, gmgn_client, mock_response):
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    mock_scraper.return_value = mock_session
    
    endpoint = "/test/endpoint"
    params = {"test": "param"}
    
    response = gmgn_client._make_request(endpoint, params)
    
    mock_session.get.assert_called_once_with(
        f"{GmGnClient.BASE_URL}{endpoint}",
        params=params
    )
    assert response == {"code": 0, "msg": "success", "data": {}}

@patch('cloudscraper.create_scraper')
def test_get_trending(mock_scraper, gmgn_client, mock_response):
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    mock_scraper.return_value = mock_session
    
    response = gmgn_client.get_trending()
    
    mock_session.get.assert_called_once()
    assert "swaps/1h" in mock_session.get.call_args[0][0]

@patch('cloudscraper.create_scraper')
def test_get_token_info(mock_scraper, gmgn_client, mock_response):
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    mock_scraper.return_value = mock_session
    
    token_address = "test_address"
    response = gmgn_client.get_token_info(token_address)
    
    mock_session.get.assert_called_once()
    assert token_address in mock_session.get.call_args[0][0]

@patch('cloudscraper.create_scraper')
def test_get_kline_with_datetime(mock_scraper, gmgn_client, mock_response):
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    mock_scraper.return_value = mock_session
    
    token_address = "test_address"
    from_time = datetime(2024, 1, 1)
    to_time = datetime(2024, 1, 2)
    
    response = gmgn_client.get_kline(
        token_address,
        from_time=from_time,
        to_time=to_time
    )
    
    mock_session.get.assert_called_once()
    call_args = mock_session.get.call_args[1]['params']
    assert isinstance(call_args['from'], int)
    assert isinstance(call_args['to'], int)

@patch('cloudscraper.create_scraper')
def test_get_token_trade_history(mock_scraper, gmgn_client, mock_response):
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    mock_scraper.return_value = mock_session
    
    token_address = "test_address"
    limit = 50
    maker = "test_maker"
    
    response = gmgn_client.get_token_trade_history(
        token_address,
        limit=limit,
        maker=maker
    )
    
    mock_session.get.assert_called_once()
    call_args = mock_session.get.call_args[1]['params']
    assert call_args['limit'] == limit
    assert call_args['maker'] == maker 