import pytest
import json
from src.formatters.json_formatter import JsonFormatter
from src.formatters.markdown_formatter import MarkdownFormatter


@pytest.fixture
def mock_data():
    return {
        "alert_id": "ALT-123",
        "severity": "High",
        "enrichment": {
            "ips": {"8.8.8.8": {"VirusTotal": {"malicious": 2, "suspicious": 1}}},
            "hashes": {},
        },
    }


def test_json_formatter(mock_data):
    """Test that the JsonFormatter returns a valid JSON string."""
    formatter = JsonFormatter()
    assert formatter.name() == "json"

    result = formatter.format(mock_data)

    # Verify it's a valid JSON string
    parsed = json.loads(result)
    assert parsed["alert_id"] == "ALT-123"
    assert parsed["enrichment"]["ips"]["8.8.8.8"]["VirusTotal"]["malicious"] == 2


def test_markdown_formatter(mock_data):
    """Test that the MarkdownFormatter returns a structured Markdown string."""
    formatter = MarkdownFormatter()
    assert formatter.name() == "markdown"

    result = formatter.format(mock_data)

    # Verify key markdown elements are present
    assert "# Threat Intelligence Report: ALT-123" in result
    assert "**Severity:** High" in result
    assert "## IP Addresses" in result
    assert "### `8.8.8.8`" in result
    assert "- **VirusTotal:**" in result
    assert "malicious: 2" in result
