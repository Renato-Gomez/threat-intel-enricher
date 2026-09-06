from typing import Dict, Any
from src.formatters.base_formatter import BaseFormatter


class MarkdownFormatter(BaseFormatter):
    """
    Outputs data as a human-readable Markdown report.
    Ideal for SOC analysts reading the terminal or exporting to documentation.
    """

    def name(self) -> str:
        return "markdown"

    def format(self, data: Dict[str, Any]) -> str:
        lines = []
        alert_id = data.get("alert_id", "Unknown")
        severity = data.get("severity", "Unknown")

        lines.append(f"# Threat Intelligence Report: {alert_id}")
        lines.append(f"**Severity:** {severity}\n")

        enrichment = data.get("enrichment", {})

        # Format IPs
        ips = enrichment.get("ips", {})
        if ips:
            lines.append("## IP Addresses")
            for ip, providers in ips.items():
                lines.append(f"### `{ip}`")
                for provider_name, result in providers.items():
                    lines.append(f"- **{provider_name}:**")
                    for key, val in result.items():
                        lines.append(f"  - {key}: {val}")
                lines.append("")

        # Format Hashes
        hashes = enrichment.get("hashes", {})
        if hashes:
            lines.append("## File Hashes")
            for file_hash, providers in hashes.items():
                lines.append(f"### `{file_hash}`")
                for provider_name, result in providers.items():
                    lines.append(f"- **{provider_name}:**")
                    for key, val in result.items():
                        lines.append(f"  - {key}: {val}")
                lines.append("")

        return "\n".join(lines).strip()
