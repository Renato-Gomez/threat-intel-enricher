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

# Import plugins
from src.providers.base_provider import BaseProvider
import src.providers

from src.formatters.base_formatter import BaseFormatter
import src.formatters

# Setup basic logging for the orchestrator
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def discover_providers() -> list[type]:
    provider_classes = []
    for _, module_name, is_pkg in pkgutil.iter_modules(src.providers.__path__):
        if not is_pkg:
            module = importlib.import_module(f"src.providers.{module_name}")
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseProvider) and obj is not BaseProvider:
                    if obj.__name__ in ("DummyProvider", "DummyTestProvider"):
                        continue
                    provider_classes.append(obj)
    return provider_classes


def discover_formatters() -> dict[str, type]:
    """Dynamically scans src.formatters and returns a dict mapping format name to the class."""
    formatters_map = {}
    for _, module_name, is_pkg in pkgutil.iter_modules(src.formatters.__path__):
        if not is_pkg:
            module = importlib.import_module(f"src.formatters.{module_name}")
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseFormatter) and obj is not BaseFormatter:
                    try:
                        instance = obj()
                        formatters_map[instance.name()] = obj
                    except Exception:
                        pass
    return formatters_map


def setup_argparse(
    available_provider_classes: list[type], available_formatters: dict[str, type]
) -> tuple[argparse.ArgumentParser, dict]:
    parser = argparse.ArgumentParser(
        description="Automated Threat Intel Enrichment Pipeline"
    )

    # Provider Flags
    flags_map = {}
    for cls in available_provider_classes:
        flag_name = cls.__name__.lower().replace("provider", "")
        parser.add_argument(
            f"--{flag_name}", action="store_true", help=f"Enable {flag_name} provider"
        )
        flags_map[flag_name] = cls

    # Formatter Flag
    formatter_choices = list(available_formatters.keys())
    default_format = "json" if "json" in formatter_choices else formatter_choices[0]

    parser.add_argument(
        "--format",
        type=str,
        choices=formatter_choices,
        default=default_format,
        help="Output format for the report",
    )

    return parser, flags_map


def main():
    # 1. Discover plugins
    available_provider_classes = discover_providers()
    available_formatters = discover_formatters()

    # 2. Setup CLI Arguments
    parser, flags_map = setup_argparse(available_provider_classes, available_formatters)
    args = parser.parse_args()

    # 3. Determine which providers to run (If no flags, run all)
    any_flag_set = any(getattr(args, flag) for flag in flags_map.keys())
    run_all = not any_flag_set

    logger.info("Starting Threat Intel Enricher Pipeline...")

    # 4. Load configuration
    settings = load_config()

    # 5. Initialize selected providers
    providers = []
    for flag_name, cls in flags_map.items():
        if run_all or getattr(args, flag_name):
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

    # 7. Extract IoCs
    extracted_iocs = IoCExtractor.extract(raw_alert)
    logger.info(
        f"Extracted {len(extracted_iocs.ips)} IPs, "
        f"{len(extracted_iocs.domains)} Domains, "
        f"{len(extracted_iocs.hashes)} Hashes."
    )

    # 8. Enrich IoCs
    enrichment_results = {"ips": {}, "hashes": {}}

    for ip in extracted_iocs.ips:
        enrichment_results["ips"][ip] = {}
        for provider in providers:
            result = provider.enrich_ip(ip)
            if result:
                enrichment_results["ips"][ip][provider.name()] = result

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

    formatter_cls = available_formatters[args.format]
    formatter = formatter_cls()

    print("\n" + "=" * 50)
    print("FINAL ENRICHED REPORT")
    print("=" * 50)
    print(formatter.format(final_report))
    print("=" * 50)


if __name__ == "__main__":
    main()
