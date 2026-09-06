import pytest
import requests
from unittest.mock import patch, MagicMock
from typing import Optional, Dict, Any

from src.providers.base_provider import BaseProvider


class DummyProvider(BaseProvider):
    """
    Dummy implementation of the abstract BaseProvider class.
    Created strictly to test the inherited _make_request method in isolation.
    """

    def name(self) -> str:
        return "DummyProvider"

    def enrich_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        pass

    def enrich_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        pass


@pytest.fixture
def provider():
    """Fixture providing a fresh DummyProvider instance for each test."""
    return DummyProvider(api_key="test_key", timeout=5)


@patch("src.providers.base_provider.requests.request")
def test_make_request_success(mock_request, provider):
    """Test that a successful HTTP 200 response correctly parses and returns JSON."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok", "data": "dummy_data"}
    mock_request.return_value = mock_response

    result = provider._make_request("GET", "http://test.local")

    assert result == {"status": "ok", "data": "dummy_data"}
    mock_request.assert_called_once_with(
        method="GET", url="http://test.local", headers=None, params=None, timeout=5
    )


@patch("src.providers.base_provider.requests.request")
def test_make_request_rate_limit(mock_request, provider):
    """Test that an HTTP 429 explicitly returns a rate limit error dictionary."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_request.return_value = mock_response

    result = provider._make_request("GET", "http://test.local")

    assert result == {"error": "Rate limit exceeded"}


@patch("src.providers.base_provider.requests.request")
def test_make_request_timeout(mock_request, provider):
    """Test that a requests.exceptions.Timeout is caught and handled gracefully."""
    mock_request.side_effect = requests.exceptions.Timeout("Connection timed out")

    result = provider._make_request("GET", "http://test.local")

    assert result == {"error": "Connection timeout"}


@patch("src.providers.base_provider.requests.request")
def test_make_request_http_error(mock_request, provider):
    """Test that a general HTTPError (like 404 or 500) is caught and returns the status code."""
    mock_response = MagicMock()
    mock_response.status_code = 503
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Service Unavailable"
    )
    mock_request.return_value = mock_response

    result = provider._make_request("GET", "http://test.local")

    assert result == {"error": "HTTP error: 503"}


@patch("src.providers.base_provider.requests.request")
def test_make_request_network_failure(mock_request, provider):
    """Test that any generic RequestException (e.g. DNS failure) is handled."""
    mock_request.side_effect = requests.exceptions.RequestException("DNS lookup failed")

    result = provider._make_request("GET", "http://test.local")

    assert result == {"error": "Network failure"}
