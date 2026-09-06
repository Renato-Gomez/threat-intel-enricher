from src.main import setup_argparse
from src.providers.base_provider import BaseProvider


class DummyTestProvider(BaseProvider):
    """
    A dummy provider strictly used to test the dynamic CLI logic.
    """

    def name(self) -> str:
        return "DummyTest"

    def enrich_ip(self, ip: str):
        pass

    def enrich_hash(self, file_hash: str):
        pass


def test_setup_argparse_creates_dynamic_flags():
    """
    Test that setup_argparse correctly infers flag names from Provider classes
    and registers them as valid CLI arguments.
    """
    # 1. Provide a dummy class to the setup function
    available_providers = [DummyTestProvider]
    available_formatters = {"json": None}  # Dummy formatter for testing

    parser, flags_map = setup_argparse(available_providers, available_formatters)

    # 2. Verify that the flags_map correctly inferred the name:
    # "DummyTestProvider" -> remove "Provider" -> lowercase -> "dummytest"
    assert "dummytest" in flags_map
    assert flags_map["dummytest"] == DummyTestProvider

    # 3. Simulate the user executing the script with the flag: python main.py --dummytest
    args = parser.parse_args(["--dummytest"])

    # 4. Verify the argument was successfully recognized and set to True by argparse
    assert hasattr(args, "dummytest")
    assert args.dummytest is True
