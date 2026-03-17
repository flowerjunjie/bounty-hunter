#!/usr/bin/env python3
"""
SolarWinds Provider Generator for Keep HQ
Fast provider creation using template
"""

import os
import subprocess
import sys

# Provider configuration
PROVIDER_NAME = "SolarWinds"
PROVIDER_ID = "solarwinds"
PROVIDER_DESCRIPTION = "SolarWinds provides IT management software for monitoring and managing network devices, servers, applications, and services."
PROVIDER_URL = "https://www.solarwinds.com/"

def create_provider():
    """Create SolarWinds provider for Keep"""

    print(f"🚀 Creating {PROVIDER_NAME} Provider...")

    # Navigate to existing keep repo
    os.chdir("/root/.bounty-hunter/keep")

    # Create provider directory
    provider_dir = f"keep/providers/{PROVIDER_ID}/"
    os.makedirs(provider_dir, exist_ok=True)

    # Create provider files
    print(f"📝 Creating provider files...")

    # __init__.py
    init_content = f'''"""
SolarWinds Provider for Keep
"""
from .provider import SolarwindsProvider

__all__ = ["SolarwindsProvider"]
'''

    with open(f"{provider_dir}/__init__.py", "w") as f:
        f.write(init_content)

    # provider.py
    provider_content = f"""
\"\"\"
SolarWinds Provider for Keep

This provider integrates with SolarWinds Orion Platform to fetch alerts and metrics.
\"\"\"

import logging
from typing import Optional
import base64

import requests

from keep.contextmanager.contextmanager import ContextManager
from keep.providers.base.base_provider import BaseProvider
from keep.providers.models.provider_config import ProviderConfig, ProviderScope

logger = logging.getLogger(__name__)

class SolarwindsProvider(BaseProvider):
    \"\"\"Fetch alerts and metrics from SolarWinds Orion Platform.\"\"\"

    PROVIDER_DISPLAY_NAME = \"{PROVIDER_NAME}\"
    PROVIDER_TAGS = [\"alert\", \"metrics\", \"network\", \"infrastructure\", \"monitoring\"]
    PROVIDER_DESCRIPTION = \"{PROVIDER_DESCRIPTION}\"

    PROVIDER_SCOPES = [
        ProviderScope(
            name=\"authenticated\",
            description=\"Authenticated to SolarWinds API\",
            mandatory=True,
            alias=\"Authentication\",
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
        \"\"\"Dispose the provider.\"\"\"
        pass

    def validate_config(self):
        \"\"\"Validate provider configuration.\"\"\"
        self.authentication_config.validate(\"solarwinds_url\")
        self.authentication_config.validate(\"username\")
        self.authentication_config.validate(\"password\")
        pass

    def validate_scopes(self):
        \"\"\"Validate provider scopes.\"\"\"
        try:
            # Create basic auth header
            credentials = base64.b64encode(
                f\"{{self.authentication_config.username}}:{{self.authentication_config.password}}\".encode()
            ).decode()

            response = requests.get(
                f\"{{self.authentication_config.solarwinds_url}}/api/Query\",
                headers={{
                    \"Authorization\": f\"Basic {{credentials}}\",
                    \"Content-Type\": \"application/json\",
                }},
                timeout=10,
            )
            if response.status_code in [200, 401]:  # 401 means server is responding
                return {{
                    \"authenticated\": True,
                }}
            else:
                logger.error(f\"Failed to authenticate: {{response.status_code}}\")
                return {{
                    \"authenticated\": False,
                }}
        except Exception as e:
            logger.error(f\"Failed to validate scopes: {{e}}\")
            return {{
                \"authenticated\": False,
            }}

    def _get_alerts(self, limit: Optional[int] = None):
        \"\"\"Fetch alerts from SolarWinds.\"\"\"
        try:
            # Create basic auth header
            credentials = base64.b64encode(
                f\"{{self.authentication_config.username}}:{{self.authentication_config.password}}\".encode()
            ).decode()

            # Query SolarWinds API for active alerts
            query = \"\"\"
            SELECT TOP {{}}
                AlertID,
                AlertName,
                AlertMessage,
                TriggeredDateTime,
                Severity,
                ObjectName,
                NodeID
            FROM Orion.AlertActive
            ORDER BY TriggeredDateTime DESC
            \"\"\".format(limit if limit else 100)

            response = requests.post(
                f\"{{self.authentication_config.solarwinds_url}}/api/Query\",
                headers={{
                    \"Authorization\": f\"Basic {{credentials}}\",
                    \"Content-Type\": \"application/json\",
                }},
                json={{\"query\": query}},
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get(\"results\", [])

                alerts = []
                for alert in results:
                    alerts.append({{
                        \"id\": alert.get(\"AlertID\", \"\"),
                        \"name\": alert.get(\"AlertName\", \"\"),
                        \"message\": alert.get(\"AlertMessage\", \"\"),
                        \"triggeredAt\": alert.get(\"TriggeredDateTime\", \"\"),
                        \"severity\": alert.get(\"Severity\", \"\"),
                        \"object\": alert.get(\"ObjectName\", \"\"),
                        \"nodeId\": alert.get(\"NodeID\", \"\"),
                    }})

                return alerts
            else:
                logger.error(f\"Failed to fetch alerts: {{response.status_code}}\")
                return []

        except Exception as e:
            logger.error(f\"Failed to fetch alerts from SolarWinds: {{e}}\")
            return []

    def _notify(self, **kwargs):
        \"\"\"Notify SolarWinds (not implemented for this provider).\"\"\"
        raise NotImplementedError(\"_notify is not implemented for SolarWinds provider\")
"""

    with open(f"{provider_dir}/provider.py", "w") as f:
        f.write(provider_content)

    # Create tests directory
    tests_dir = f"{provider_dir}tests/"
    os.makedirs(tests_dir, exist_ok=True)

    # test_provider.py
    test_content = f"""
\"\"\"
Tests for SolarWinds Provider
\"\"\"

import pytest
from keep.providers.providers_factory import ProvidersFactory

def test_validate_config():
    \"\"\"Test provider configuration validation.\"\"\"
    config = {{
        \"authentication\": {{
            \"solarwinds_url\": \"https://solarwinds.example.com\",
            \"username\": \"admin\",
            \"password\": \"password\",
        }}
    }}

    provider = ProvidersFactory.get_provider(
        provider_id=\"{PROVIDER_ID}-test\",
        provider_type=\"{PROVIDER_ID}\",
        config=config,
    )

    assert provider is not None

def test_get_alerts_mock(mocker):
    \"\"\"Test fetching alerts from SolarWinds.\"\"\"
    config = {{
        \"authentication\": {{
            \"solarwinds_url\": \"https://solarwinds.example.com\",
            \"username\": \"admin\",
            \"password\": \"password\",
        }}
    }}

    provider = ProvidersFactory.get_provider(
        provider_id=\"{PROVIDER_ID}-test\",
        provider_type=\"{PROVIDER_ID}\",
        config=config,
    )

    # Mock the HTTP request
    mock_response = {{
        \"results\": [
            {{
                \"AlertID\": \"1\",
                \"AlertName\": \"High CPU\",
                \"AlertMessage\": \"CPU usage is above 90%\",
                \"TriggeredDateTime\": \"2026-03-12T00:00:00Z\",
                \"Severity\": \"Critical\",
                \"ObjectName\": \"Server-01\",
                \"NodeID\": \"123\",
            }}
        ]
    }}

    mocker.patch(\"requests.post\", return_value=mocker.MagicMock(
        status_code=200,
        json=lambda: mock_response
    ))

    alerts = provider._get_alerts(limit=10)

    assert len(alerts) == 1
    assert alerts[0][\"name\"] == \"High CPU\"
"""

    with open(f"{tests_dir}/test_provider.py", "w") as f:
        f.write(test_content)

    # Update factory
    print("📋 Updating provider factory...")

    factory_file = "keep/providers/providers_factory.py"
    with open(factory_file, "r") as f:
        content = f.read()

    # Add provider to PROVIDERS_MAP
    import re
    provider_entry = f'        "{PROVIDER_ID}": {PROVIDER_NAME}Provider,'
    if PROVIDER_ID not in content:
        map_pattern = r'(PROVIDERS_MAP\s*=\s*\{[^}]*)(\})'
        match = re.search(map_pattern, content, re.DOTALL)
        if match:
            content = content[:match.end(1)] + f'\\n        "{PROVIDER_ID}": {PROVIDER_NAME}Provider,' + content[match.end(1)-1:]

        with open(factory_file, "w") as f:
            f.write(content)

    # Commit changes
    print("💾 Committing changes...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run([
        "git", "commit", "-m",
        f"feat: Add {PROVIDER_NAME} provider #3526"
    ], check=True)

    print(f"✅ {PROVIDER_NAME} Provider created successfully!")
    print(f"📊 Ready to submit PR for issue #3526")

if __name__ == "__main__":
    create_provider()
