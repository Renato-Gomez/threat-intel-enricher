import argparse
import sys
import json
import logging
import pkgutil
import importlib
import inspect
from pathlib import Path

from src.config import load_config
from src.core.ioc_extractor import IoCExtractor
from src.notifiers.output_formatter import OutputFormatter

# Importamos la clase base y el paquete de providers para escanearlo
from src.providers.base_provider import BaseProvider
import src.providers

# Setup basic logging for the orchestrator
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def discover_providers() -> list[type]:
    """
    Dynamically scans the src.providers package and returns a list of
    all classes that inherit from BaseProvider.
    """
    provider_classes = []

    # Iterate through all modules in the src.providers package
    for _, module_name, is_pkg in pkgutil.iter_modules(src.providers.__path__):
        if not is_pkg:
            # Import the module dynamically
            module = importlib.import_module(f"src.providers.{module_name}")

            # Find all classes in the module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if it inherits from BaseProvider and is not the BaseProvider itself
                if issubclass(obj, BaseProvider) and obj is not BaseProvider:
                    # Ignore the dummy provider used for testing
                    if obj.__name__ == "DummyProvider":
                        continue
                    provider_classes.append(obj)

    return provider_classes


def setup_argparse(
    available_provider_classes: list[type],
) -> tuple[argparse.ArgumentParser, dict]:
    """
    Creates and returns the ArgumentParser and a mapping of flag names to provider classes.
    Extracted as a pure function to allow easy unit testing of the dynamic CLI generation.
    """
    parser = argparse.ArgumentParser(
        description="Automated Threat Intel Enrichment Pipeline"
    )

    flags_map = {}
    for cls in available_provider_classes:
        # Infer the flag name from the class name (e.g., AbuseIPDBProvider -> abuseipdb)
        flag_name = cls.__name__.lower().replace("provider", "")
        parser.add_argument(
            f"--{flag_name}", action="store_true", help=f"Enable {flag_name} provider"
        )
        flags_map[flag_name] = cls

    return parser, flags_map


def main():
    # 1. Discover all available providers dynamically
    available_provider_classes = discover_providers()

    # 2. Setup CLI Arguments dynamically based on discovered providers
    parser, flags_map = setup_argparse(available_provider_classes)
    args = parser.parse_args()

    # 3. Determine which providers to run (If no flags, run all)
    any_flag_set = any(getattr(args, flag) for flag in flags_map.keys())
    run_all = not any_flag_set

    logger.info("Starting Threat Intel Enricher Pipeline...")

    # 4. Load configuration (Fail-fast if API keys are missing or invalid)
    settings = load_config()

    # 5. Initialize selected providers
    providers = []
    for flag_name, cls in flags_map.items():
        if run_all or getattr(args, flag_name):
            # Fetch the API key dynamically using the flag_name
            api_key = settings.get_api_key(flag_name)
            providers.append(cls(api_key=api_key))

    provider_names = [p.name() for p in providers]
    logger.info(f"Active providers: {', '.join(provider_names)}")

    # 6. Load the raw mock alert
    mock_file_path = Path("data/alert_mock.json")
    if not mock_file_path.exists():
        logger.error(f"Alert file not found: {mock_file_path}")
        sys.exit(1)

    with open(mock_file_path, "r", encoding="utf-8") as f:
        raw_alert = json.load(f)

    logger.info(f"Loaded alert: {raw_alert.get('alert_id', 'UNKNOWN')}")

    # 7. Extract IoCs (Functional Core - No side effects)
    extracted_iocs = IoCExtractor.extract(raw_alert)
    logger.info(
        f"Extracted {len(extracted_iocs.ips)} IPs, "
        f"{len(extracted_iocs.domains)} Domains, "
        f"{len(extracted_iocs.hashes)} Hashes."
    )

    # 8. Enrich IoCs (Imperative Shell - Calling external APIs)
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

    # 9. Format and Output
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
