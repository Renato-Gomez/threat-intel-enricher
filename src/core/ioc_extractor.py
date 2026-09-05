import re
from typing import List
from pydantic import BaseModel, Field


class ExtractedIoCs(BaseModel):
    """
    Strict typing for extracted Indicators of Compromise.
    Guarantees that the extraction returns properly formatted lists.
    """

    ips: List[str] = Field(
        default_factory=list, description="List of extracted IPv4 addresses"
    )
    domains: List[str] = Field(
        default_factory=list, description="List of extracted domains"
    )
    hashes: List[str] = Field(
        default_factory=list, description="List of extracted MD5/SHA256 hashes"
    )


class IoCExtractor:
    """
    Pure functional core for extracting IoCs from a raw dictionary.
    Does not perform any IO or side effects. 100% testable.
    """

    # Regex for IPv4 format
    IPV4_PATTERN = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")

    # Regex for domains (e.g., malicious-site.com)
    DOMAIN_PATTERN = re.compile(r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b")

    # Regex for MD5 (32 hex) and SHA256 (64 hex)
    HASH_PATTERN = re.compile(r"\b([a-fA-F0-9]{32}|[a-fA-F0-9]{64})\b")

    @classmethod
    def extract(cls, raw_alert: dict) -> ExtractedIoCs:
        """
        Parses a raw alert dictionary and returns a validated ExtractedIoCs model.
        """
        # Using sets to automatically avoid duplicates
        extracted_ips = set()
        extracted_domains = set()
        extracted_hashes = set()

        # 1. Direct extraction from explicitly named fields
        if "destination_ip" in raw_alert:
            ip = str(raw_alert["destination_ip"])
            if cls.IPV4_PATTERN.fullmatch(ip):
                extracted_ips.add(ip)

        if "file_hash" in raw_alert:
            file_hash = str(raw_alert["file_hash"])
            if cls.HASH_PATTERN.fullmatch(file_hash):
                extracted_hashes.add(file_hash)

        # 2. Heuristic extraction from unstructured text blocks (like payload snippets)
        if "payload_snippet" in raw_alert:
            snippet = str(raw_alert["payload_snippet"])

            for ip in cls.IPV4_PATTERN.findall(snippet):
                extracted_ips.add(ip)

            for domain in cls.DOMAIN_PATTERN.findall(snippet):
                extracted_domains.add(domain)

        return ExtractedIoCs(
            ips=list(extracted_ips),
            domains=list(extracted_domains),
            hashes=list(extracted_hashes),
        )
