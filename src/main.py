import sys
import json
import logging
from pathlib import Path

from src.config import load_config
from src.core.ioc_extractor import IoCExtractor
from src.providers.abuseipdb import AbuseIPDBProvider
from src.providers.virustotal import VirusTotalProvider
from src.notifiers.output_formatter import OutputFormatter

# Setup basic logging for the orchestrator
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting Threat Intel Enricher Pipeline...")

    # 1. Load configuration (Fail-fast if API keys are missing or invalid)
    settings = load_config()

    # 2. Initialize providers using the dynamic keys
    abuse_api_key = settings.get_api_key("abuseipdb")
    vt_api_key = settings.get_api_key("virustotal")

    providers = [
        AbuseIPDBProvider(api_key=abuse_api_key),
        VirusTotalProvider(api_key=vt_api_key),
    ]

    # 3. Load the raw mock alert
    mock_file_path = Path("data/alert_mock.json")
    if not mock_file_path.exists():
        logger.error(f"Alert file not found: {mock_file_path}")
        sys.exit(1)

    with open(mock_file_path, "r", encoding="utf-8") as f:
        raw_alert = json.load(f)

    logger.info(f"Loaded alert: {raw_alert.get('alert_id', 'UNKNOWN')}")

    # 4. Extract IoCs (Functional Core - No side effects)
    extracted_iocs = IoCExtractor.extract(raw_alert)
    logger.info(
        f"Extracted {len(extracted_iocs.ips)} IPs, "
        f"{len(extracted_iocs.domains)} Domains, "
        f"{len(extracted_iocs.hashes)} Hashes."
    )

    # 5. Enrich IoCs (Imperative Shell - Calling external APIs)
    enrichment_results = {"ips": {}, "hashes": {}}

    # Enrich IPs across all providers
    for ip in extracted_iocs.ips:
        enrichment_results["ips"][ip] = {}
        for provider in providers:
            result = provider.enrich_ip(ip)
            if result:
                enrichment_results["ips"][ip][provider.name()] = result

    # Enrich Hashes across all providers
    for file_hash in extracted_iocs.hashes:
        enrichment_results["hashes"][file_hash] = {}
        for provider in providers:
            result = provider.enrich_hash(file_hash)
            if result:
                enrichment_results["hashes"][file_hash][provider.name()] = result

    # 6. Format and Output
    final_report = {
        "alert_id": raw_alert.get("alert_id"),
        "severity": raw_alert.get("severity"),
        "enrichment": enrichment_results,
    }

    print("\n" + "=" * 50)
    print("FINAL ENRICHED REPORT")
    print("=" * 50)
    print(OutputFormatter.format_json(final_report))
    print("=" * 50)


if __name__ == "__main__":
    main()
