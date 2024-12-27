import pytest
import asyncio
from datetime import datetime, timedelta
from langflow.packages.gmgn import GmGnClient

@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def gmgn_client():
    """Create a GMGN client instance that will be reused for all tests"""
    client = GmGnClient()
    yield client

@pytest.fixture(scope="module")
def test_token_address():
    """Fixture to provide a test token address"""
    return "Cpzvdx6pppc9TNArsGsqgShCsKC9NCCjA2gtzHvUpump"

def test_get_trending(gmgn_client):
    """Test getting trending tokens"""
    response = gmgn_client.get_trending()
    assert response.code == 0
    assert response.data is not None
    assert "rank" in response.data

    # second try
    response = gmgn_client.get_trending(no_proxy=True)
    assert response.code == 0
    assert response.data is not None
    assert "rank" in response.data


def test_get_token_info(gmgn_client, test_token_address):
    """Test getting token information"""
    response = gmgn_client.get_token_info(test_token_address)
    assert response["code"] == 0
    assert response["data"] is not None
    assert response["data"]["address"] == test_token_address

def test_get_token_pool_info(gmgn_client, test_token_address):
    """Test getting token pool information"""
    response = gmgn_client.get_token_pool_info(test_token_address)
    assert response["code"] == 0
    assert response["data"] is not None

def test_get_token_stats(gmgn_client, test_token_address):
    """Test getting token statistics"""
    response = gmgn_client.get_token_stats(test_token_address)
    assert response.code == 0
    assert response.data is not None

def test_get_kline(gmgn_client, test_token_address):
    """Test getting token kline data"""
    from_time = datetime.now() - timedelta(days=1)
    to_time = datetime.now()
    
    response = gmgn_client.get_kline(
        test_token_address,
        resolution="5m",
        from_time=from_time,
        to_time=to_time
    )
    assert response["code"] == 0

def test_get_token_trade_history(gmgn_client, test_token_address):
    """Test getting token trade history"""
    response = gmgn_client.get_token_trade_history(test_token_address, limit=10)
    assert response["code"] == 0
    assert response["data"] is not None
    assert "history" in response["data"]
    assert len(response["data"]["history"]) > 0

def test_get_token_link(gmgn_client, test_token_address):
    """Test getting token links"""
    response = gmgn_client.get_token_link(test_token_address)
    assert response["code"] == 0
    assert response["data"] is not None

def test_get_top_buyers(gmgn_client, test_token_address):
    """Test getting top buyers information"""
    response = gmgn_client.get_top_buyers(test_token_address)
    assert response["code"] == 0
    assert "data" in response

def test_get_rug_history(gmgn_client, test_token_address):
    """Test getting rug pull history"""
    response = gmgn_client.get_rug_history(test_token_address)
    assert response["code"] == 0
    assert "data" in response

def test_get_tag_wallet_count(gmgn_client, test_token_address):
    """Test getting tag wallet count"""
    response = gmgn_client.get_tag_wallet_count(test_token_address)
    assert response.code == 0
    assert response.data is not None

@pytest.mark.asyncio
async def test_get_all_token_info_for_markdown(gmgn_client, test_token_address):
    """Test getting all token information in markdown format"""
    markdown = await gmgn_client.get_all_token_info_for_markdown(test_token_address)
    
    # Check if markdown contains all required sections
    required_sections = [
        "# Token Analysis Report for",
        "### Basic Token Information",
        "### Pool Information",
        "### Security Information",
        "### Developer Information",
        "### Trading Statistics",
        "### Wallet Analysis",
        "### Launchpad Information",
        "### Token Links",
        "## Short-term Analysis (5m)",
        "## Long-term Analysis (4h)",
        "### Recent Trades",
        "### Risk Assessment",
        "### Top Buyers Analysis"
    ]
    
    for section in required_sections:
        assert section in markdown, f"Missing section: {section}"
    
    # Check if token address is included
    assert test_token_address in markdown, "Token address not found in markdown"
    
    # Check if markdown contains actual data (not just N/A values)
    data_indicators = [
        "Symbol",
        "Name",
        "Holder Count",
        "Creation Time",
        "Liquidity",
        "Pool Address",
        "Creator Address"
    ]
    
    data_found = False
    for indicator in data_indicators:
        if f"**{indicator}**: N/A" not in markdown:
            data_found = True
            break
    
    assert data_found, "No actual data found in markdown output"
    
    # Check formatting
    assert markdown.count("#") >= len(required_sections), "Missing header formatting"
    assert markdown.count("**") >= 20, "Missing bold formatting for fields"
    assert markdown.count("-") >= 20, "Missing list item formatting"
    
    # Check for OHLC data
    assert "Time | Open | High | Low | Close | Volume | Type" in markdown, "Missing OHLC table header"
    assert "🟢" in markdown or "🔴" in markdown, "Missing candle type indicators"
    
    # Check for technical analysis
    technical_indicators = [
        "RSI (14)",
        "Trend Direction",
        "Support & Resistance",
        "Fibonacci Retracement Levels"
    ]
    
    for indicator in technical_indicators:
        assert indicator in markdown, f"Missing technical indicator: {indicator}" 