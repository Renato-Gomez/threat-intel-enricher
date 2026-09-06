import json
from typing import Dict, Any
from src.formatters.base_formatter import BaseFormatter


class JsonFormatter(BaseFormatter):
    """
    Outputs data as an indented JSON string.
    Ideal for piping to other tools or ingesting into a SIEM.
    """

    def name(self) -> str:
        return "json"

    def format(self, data: Dict[str, Any]) -> str:
        return json.dumps(data, indent=4, ensure_ascii=False)
