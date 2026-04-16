"""Example: Auto-detecting available providers and using fallback chain."""

from autogen_api_agent.config import AppConfig
from autogen_api_agent.providers.factory import ModelClientFactory


def main() -> None:
    config = AppConfig()
    factory = ModelClientFactory(config)

    available = factory.list_available()
    print("Available providers:")
    for provider, model in available.items():
        print(f"  {provider}: {model}")

    if not available:
        print("No providers configured. Set at least one API key in .env")
        return

    try:
        client = factory.create_best_available()
        print(f"\nBest available client: {type(client).__name__}")
    except RuntimeError as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
