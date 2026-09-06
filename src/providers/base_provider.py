import abc
import logging
import requests
from typing import Optional, Dict, Any

# Configure a basic logger for the providers
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseProvider(abc.ABC):
    """
    Abstract Base Class for all Threat Intelligence providers.
    Enforces the Open/Closed Principle and centralizes error handling.
    """

    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout

    @abc.abstractmethod
    def name(self) -> str:
        """Returns the human-readable name of the provider."""
        pass

    @abc.abstractmethod
    def enrich_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        """
        Enriches an IP address.
        Returns a structured dictionary with the findings, or None if the provider doesn't support IPs.
        """
        pass

    @abc.abstractmethod
    def enrich_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Enriches a file hash (MD5/SHA256).
        Returns a structured dictionary, or None if the provider doesn't support hashes.
        """
        pass

    def _make_request(
        self, method: str, url: str, headers: dict = None, params: dict = None
    ) -> Optional[Dict[str, Any]]:
        """
        Centralized request handler with strict error and timeout management.
        Guarantees that the automation will not crash or hang indefinitely on network issues.
        """
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )

            # Explicit handling for Rate Limiting (HTTP 429)
            if response.status_code == 429:
                logger.warning(f"[{self.name()}] Rate limit exceeded (HTTP 429).")
                return {"error": "Rate limit exceeded"}

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"[{self.name()}] Connection timeout after {self.timeout}s.")
            return {"error": "Connection timeout"}
        except requests.exceptions.HTTPError as e:
            logger.error(f"[{self.name()}] HTTP error occurred: {e}")
            return {"error": f"HTTP error: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"[{self.name()}] Network failure: {e}")
            return {"error": "Network failure"}
