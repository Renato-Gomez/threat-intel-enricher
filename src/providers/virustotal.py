from typing import Optional, Dict, Any
from src.providers.base_provider import BaseProvider


class VirusTotalProvider(BaseProvider):
    """
    Concrete implementation for the VirusTotal API (v3).
    Supports reputation checks for both IPs and File Hashes.
    """

    def name(self) -> str:
        return "VirusTotal"

    def enrich_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        """Queries VirusTotal v3 API for IP address reputation."""
        url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
        headers = {"accept": "application/json", "x-apikey": self.api_key}

        result = self._make_request("GET", url, headers=headers)

        if result and "data" in result:
            stats = result["data"].get("attributes", {}).get("last_analysis_stats", {})
            return {
                "malicious": stats.get("malicious", 0),
                "suspicious": stats.get("suspicious", 0),
                "harmless": stats.get("harmless", 0),
                "undetected": stats.get("undetected", 0),
            }

        return result

    def enrich_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Queries VirusTotal v3 API for file hash (MD5/SHA256) reputation."""
        url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
        headers = {"accept": "application/json", "x-apikey": self.api_key}

        result = self._make_request("GET", url, headers=headers)

        if result and "data" in result:
            stats = result["data"].get("attributes", {}).get("last_analysis_stats", {})
            return {
                "malicious": stats.get("malicious", 0),
                "suspicious": stats.get("suspicious", 0),
                "harmless": stats.get("harmless", 0),
                "undetected": stats.get("undetected", 0),
            }

        return result
