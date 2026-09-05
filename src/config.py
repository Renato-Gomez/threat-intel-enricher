import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError


class Settings(BaseModel):
    """
    Pydantic model to validate and store system configurations.
    """

    # Dynamically store any key that follows the pattern in a dictionary.
    api_keys: dict[str, str] = Field(
        default_factory=dict, description="Dynamic dictionary of API Keys"
    )

    def get_api_key(self, provider_name: str) -> str:
        """
        Returns the API Key for a specific provider.
        Raises ValueError if it does not exist, maintaining the 'fail-fast' principle.
        """
        key = f"{provider_name.upper()}_API_KEY"
        if key not in self.api_keys or not self.api_keys[key]:
            raise ValueError(f"Required configuration missing in .env: {key}")
        return self.api_keys[key]


def load_config() -> Settings:
    """
    Dynamically loads environment variables for extensibility.
    Any variable ending in '_API_KEY' will be loaded automatically.
    """
    load_dotenv()

    try:
        # Extract any environment variable that ends in '_API_KEY'
        # This allows adding new APIs in the future without modifying this file (Open/Closed Principle).
        dynamic_keys = {
            key: value
            for key, value in os.environ.items()
            if key.endswith("_API_KEY") and value.strip()
        }

        return Settings(api_keys=dynamic_keys)

    except ValidationError as e:
        print("CRITICAL ERROR: Configuration validation failed.")
        print(f"Details:\n{e}")
        raise SystemExit(1)
