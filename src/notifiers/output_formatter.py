import json
from typing import Dict, Any


class OutputFormatter:
    """
    Handles the formatting of the final enriched data for the SOC analyst.
    Separating this logic allows us to easily add Markdown or HTML formatters in the future.
    """

    @staticmethod
    def format_json(data: Dict[str, Any]) -> str:
        """
        Returns the data as a beautifully indented JSON string,
        making it easy to read on the terminal or ingest into a SIEM.
        """
        return json.dumps(data, indent=4, ensure_ascii=False)
