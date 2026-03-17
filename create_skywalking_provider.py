#!/usr/bin/env python3
"""
SkyWalking Provider Generator for Keep HQ
Fast provider creation using template
"""

import os
import subprocess
import sys

# Provider configuration
PROVIDER_NAME = "SkyWalking"
PROVIDER_ID = "skywalking"
PROVIDER_DESCRIPTION = "Apache SkyWalking is an APM (Application Performance Monitoring) platform for distributed systems."
PROVIDER_URL = "https://skywalking.apache.org/"
DOCS_URL = "https://skywalking.apache.org/docs/main/next/en/api/backend/"

def create_provider():
    """Create SkyWalking provider for Keep"""

    print(f"🚀 Creating {PROVIDER_NAME} Provider...")

    # Fork and clone the repository
    repo_url = "https://github.com/keephq/keep.git"
    fork_url = "https://github.com/flowerjunjie/keep.git"  # Your fork

    print(f"📦 Cloning repository...")
    if not os.path.exists("keep"):
        subprocess.run(["git", "clone", repo_url], check=True)
        os.chdir("keep")
        subprocess.run(["git", "remote", "add", "fork", fork_url], check=True)
    else:
        os.chdir("keep")
        subprocess.run(["git", "checkout", "main"], check=True)
        subprocess.run(["git", "pull", "origin", "main"], check=True)

    # Create provider directory
    provider_dir = f"keep/providers/{PROVIDER_ID}/"
    os.makedirs(provider_dir, exist_ok=True)

    # Create provider files
    print(f"📝 Creating provider files...")

    # __init__.py
    init_content = f'''"""
SkyWalking Provider for Keep
"""
from .provider import SkywalkingProvider

__all__ = ["SkywalkingProvider"]
'''

    with open(f"{provider_dir}/__init__.py", "w") as f:
        f.write(init_content)

    # provider.py
    provider_content = f'''"""
SkyWalking Provider for Keep

This provider integrates with Apache SkyWalking APM to fetch metrics and alerts.
"""

import logging
from typing import Optional

import requests

from keep.contextmanager.contextmanager import ContextManager
from keep.providers.base.base_provider import BaseProvider
from keep.providers.models.provider_config import ProviderConfig, ProviderScope

logger = logging.getLogger(__name__)

class SkywalkingProvider(BaseProvider):
    """Fetch alerts and metrics from Apache SkyWalking."""

    PROVIDER_DISPLAY_NAME = "{PROVIDER_NAME}"
    PROVIDER_TAGS = ["alert", "metrics", "apm", "observability"]
    PROVIDER_DESCRIPTION = "{PROVIDER_DESCRIPTION}"

    PROVIDER_SCOPES = [
        ProviderScope(
            name="authenticated",
            description="Authenticated to SkyWalking API",
            mandatory=True,
            alias="Authentication",
        ),
    ]

    def __init__(
        self,
        context_manager: ContextManager,
        provider_id: str,
        config: ProviderConfig,
    ):
        super().__init__(context_manager, provider_id, config)

    def dispose(self):
        """Dispose the provider."""
        pass

    def validate_config(self):
        """Validate provider configuration."""
        self.authentication_config.validate("skywalking_url")
        self.authentication_config.validate("authentication_token")
        pass

    def validate_scopes(self):
        """Validate provider scopes."""
        try:
            response = requests.get(
                f"{{self.authentication_config.skywalking_url}}/graphql",
                headers={{"Authorization": f"Bearer {{self.authentication_config.authentication_token}}"}},
                timeout=10,
            )
            if response.status_code == 200:
                return {{
                    "authenticated": True,
                }}
            else:
                logger.error(f"Failed to authenticate: {{response.status_code}}")
                return {{
                    "authenticated": False,
                }}
        except Exception as e:
            logger.error(f"Failed to validate scopes: {{e}}")
            return {{
                "authenticated": False,
            }}

    def _get_alerts(self, limit: Optional[int] = None):
        """Fetch alerts from SkyWalking."""
        try:
            # Query SkyWalking API for alarms
            query = """
            query {{
                alarm: queryAlarm {{
                    message
                    startTime
                    scope
                    tags {{
                        key
                        value
                    }}
                }}
            }}
            """

            response = requests.post(
                f"{{self.authentication_config.skywalking_url}}/graphql",
                headers={{
                    "Authorization": f"Bearer {{self.authentication_config.authentication_token}}",
                    "Content-Type": "application/json",
                }},
                json={{"query": query}},
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                alarms = data.get("data", {{}}).get("alarm", [])

                alerts = []
                for alarm in alarms[:limit] if limit else alarms:
                    alerts.append({{
                        "id": alarm.get("id", ""),
                        "message": alarm.get("message", ""),
                        "startedAt": alarm.get("startTime", ""),
                        "scope": alarm.get("scope", ""),
                        "tags": alarm.get("tags", []),
                    }})

                return alerts
            else:
                logger.error(f"Failed to fetch alarms: {{response.status_code}}")
                return []

        except Exception as e:
            logger.error(f"Failed to fetch alerts from SkyWalking: {{e}}")
            return []

    def _notify(self, **kwargs):
        """Notify SkyWalking (not implemented for this provider)."""
        raise NotImplementedError("_notify is not implemented for SkyWalking provider")
'''

    with open(f"{provider_dir}/provider.py", "w") as f:
        f.write(provider_content)

    # Create tests directory
    tests_dir = f"{provider_dir}tests/"
    os.makedirs(tests_dir, exist_ok=True)

    # test_provider.py
    test_content = f'''"""
Tests for SkyWalking Provider
"""

import pytest
from keep.providers.providers_factory import ProvidersFactory

def test_validate_config():
    """Test provider configuration validation."""
    config = {{
        "authentication": {{
            "skywalking_url": "http://localhost:8080",
            "authentication_token": "test_token",
        }}
    }}

    provider = ProvidersFactory.get_provider(
        provider_id="{PROVIDER_ID}-test",
        provider_type="{PROVIDER_ID}",
        config=config,
    )

    assert provider is not None

def test_get_alerts_mock(mocker):
    """Test fetching alerts from SkyWalking."""
    config = {{
        "authentication": {{
            "skywalking_url": "http://localhost:8080",
            "authentication_token": "test_token",
        }}
    }}

    provider = ProvidersFactory.get_provider(
        provider_id="{PROVIDER_ID}-test",
        provider_type="{PROVIDER_ID}",
        config=config,
    )

    # Mock the HTTP request
    mock_response = {{
        "data": {{
            "alarm": [
                {{
                    "id": "1",
                    "message": "High CPU usage",
                    "startTime": "2026-03-12T00:00:00Z",
                    "scope": "SERVICE",
                    "tags": [{{"key": "service", "value": "my-service"}}],
                }}
            ]
        }}
    }}

    mocker.patch("requests.post", return_value=mocker.MagicMock(
        status_code=200,
        json=lambda: mock_response
    ))

    alerts = provider._get_alerts(limit=10)

    assert len(alerts) == 1
    assert alerts[0]["message"] == "High CPU usage"
'''

    with open(f"{tests_dir}/test_provider.py", "w") as f:
        f.write(test_content)

    # Update registry
    print("📋 Updating provider registry...")

    registry_file = "keep/providers/providers_factory.py"
    with open(registry_file, "r") as f:
        content = f.read()

    # Find and update PROVIDERS_MAP in the factory file
    import re

    # Add provider to PROVIDERS_MAP
    provider_entry = f'        "{PROVIDER_ID}": {PROVIDER_NAME}Provider,'
    if PROVIDER_ID not in content:
        # Find the PROVIDERS_MAP dictionary
        map_pattern = r'(PROVIDERS_MAP\s*=\s*\{[^}]*)(\})'
        match = re.search(map_pattern, content, re.DOTALL)
        if match:
            # Insert before the closing brace
            content = content[:match.end(1)] + f'\\n        "{PROVIDER_ID}": {PROVIDER_NAME}Provider,' + content[match.end(1)-1:]

    with open(registry_file, "w") as f:
        f.write(content)

    # Commit and push
    print("💾 Committing changes...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run([
        "git", "commit", "-m",
        f"feat: Add {PROVIDER_NAME} provider #5487"
    ], check=True)

    print("🚀 Pushing to fork...")
    subprocess.run(["git", "push", "fork", "main"], check=True)

    print(f"✅ {PROVIDER_NAME} Provider created successfully!")
    print(f"📊 Ready to submit PR for issue #5487")

if __name__ == "__main__":
    create_provider()
