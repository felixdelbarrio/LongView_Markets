from __future__ import annotations

from app.providers.mock_provider import MockProvider


class Provider(MockProvider):
    provider_name = "external-placeholder"
