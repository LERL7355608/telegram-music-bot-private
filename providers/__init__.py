import os
import inspect

from providers.base import DownloadProvider


def build_provider(name: str) -> DownloadProvider:
    if name == "mock":
        from providers.mock import MockProvider

        return MockProvider()
    if name == "custom":
        from providers.custom import CustomProvider

        if "token" in inspect.signature(CustomProvider).parameters:
            return CustomProvider(token=os.getenv("CUSTOM_PROVIDER_TOKEN"))
        return CustomProvider()
    raise RuntimeError(f"Unknown provider: {name}")
