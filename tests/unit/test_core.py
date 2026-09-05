from src.core.ioc_extractor import IoCExtractor, ExtractedIoCs


def test_extractor_initialization():
    """Test that the ExtractedIoCs model initializes empty properly."""
    iocs = ExtractedIoCs()
    assert iocs.ips == []
    assert iocs.domains == []
    assert iocs.hashes == []


def test_extract_direct_fields():
    """Test extraction from explicitly known dictionary keys."""
    alert = {
        "destination_ip": "192.168.1.1",
        "file_hash": "44d88612fea8a8f36de82e1278abb02f",
    }
    result = IoCExtractor.extract(alert)
    assert "192.168.1.1" in result.ips
    assert "44d88612fea8a8f36de82e1278abb02f" in result.hashes
    assert len(result.domains) == 0


def test_extract_payload_snippet():
    """Test heuristic extraction from unstructured text using regex."""
    alert = {
        "payload_snippet": "GET / HTTP/1.1\r\nHost: evil-malware.com\r\nIP: 8.8.8.8"
    }
    result = IoCExtractor.extract(alert)
    assert "evil-malware.com" in result.domains
    assert "8.8.8.8" in result.ips
    assert len(result.hashes) == 0


def test_extract_invalid_formats_ignored():
    """Test that completely malformed strings are safely ignored by the regex."""
    alert = {
        "destination_ip": "not_an_ip_address",
        "file_hash": "too_short_to_be_a_hash",
    }
    result = IoCExtractor.extract(alert)
    assert len(result.ips) == 0
    assert len(result.hashes) == 0


def test_extract_empty_alert():
    """Test robustness when processing a completely empty dictionary."""
    result = IoCExtractor.extract({})
    assert result.ips == []
    assert result.domains == []
    assert result.hashes == []


def test_extract_removes_duplicates():
    """Test that the extractor returns unique IoCs even if they appear multiple times."""
    alert = {"destination_ip": "1.1.1.1", "payload_snippet": "Connecting to 1.1.1.1"}
    result = IoCExtractor.extract(alert)
    assert len(result.ips) == 1
    assert result.ips[0] == "1.1.1.1"
