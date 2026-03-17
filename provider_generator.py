#!/usr/bin/env python3
"""
Quick Provider Generator for Keep
Generate multiple monitoring providers rapidly
"""

import os
import sys
from pathlib import Path

# Simple monitoring tools that need providers
PROVIDERS_TO_CREATE = [
    {
        "name": "Zabbix",
        "description": "Zabbix monitoring system",
        "api_path": "api_jsonrpc.php",
        "auth_method": "token",
        "states": {
            "OK": "resolved",
            "PROBLEM": "firing",
            "DISASTER": "critical",
            "HIGH": "critical",
            "AVERAGE": "warning",
            "WARNING": "warning",
            "INFORMATION": "info",
            "NOT_CLASSIFIED": "pending"
        }
    },
    {
        "name": "Prometheus",
        "description": "Prometheus monitoring system",
        "api_path": "api/v1",
        "auth_method": "token",
        "states": {
            "up": "resolved",
            "down": "firing",
            "critical": "critical",
            "warning": "warning"
        }
    },
    {
        "name": "Sensu",
        "description": "Sensu monitoring framework",
        "api_path": "api",
        "auth_method": "token",
        "states": {
            "ok": "resolved",
            "warning": "warning",
            "critical": "critical",
            "unknown": "info"
        }
    },
    {
        "name": "Icinga",
        "description": "Icinga monitoring system",
        "api_path": "api/v1",
        "auth_method": "token",
        "states": {
            "0": "resolved",  # OK
            "1": "warning",  # Warning
            "2": "critical", # Critical
            "3": "info"      # Unknown
        }
    },
    {
        "name": "UptimeRobot",
        "description": "UptimeRobot monitoring service",
        "api_path": "api/v2",
        "auth_method": "api_key",
        "states": {
            "up": "resolved",
            "down": "critical",
            "paused": "pending"
        }
    },
    {
        "name": "Pingdom",
        "description": "Pingdom monitoring service",
        "api_path": "api/v3",
        "auth_method": "bearer_token",
        "states": {
            "up": "resolved",
            "down": "critical",
            "paused": "pending",
            "unknown": "info"
        }
    },
    {
        "name": "StatusCake",
        "description": "StatusCake monitoring",
        "api_path": "api/v1",
        "auth_method": "api_key",
        "states": {
            "Up": "resolved",
            "Down": "critical",
            "Unknown": "info"
        }
    },
    {
        "name": "BetterUptime",
        "description": "BetterUptime monitoring",
        "api_path": "api/v2",
        "auth_method": "bearer_token",
        "states": {
            "operational": "resolved",
            "degraded_performance": "warning",
            "partial_outage": "warning",
            "major_outage": "critical",
            "under_maintenance": "pending"
        }
    }
]

def create_provider_template(provider_info):
    """Generate provider code from template"""
    name = provider_info["name"]
    name_lower = name.lower()
    
    # This is a simplified template - would need customization per provider
    template = f'''"""
{name}Provider is a class that provides a set of methods to interact with the {name} API.
"""

import dataclasses
import datetime
import requests

import pydantic

from keep.api.models.alert import AlertDto, AlertSeverity, AlertStatus
from keep.contextmanager.contextmanager import ContextManager
from keep.exceptions.provider_exception import ProviderException
from keep.providers.base.base_provider import BaseProvider
from keep.providers.models.provider_config import ProviderConfig, ProviderScope


@pydantic.dataclasses.dataclass
class {name}ProviderAuthConfig:
    """
    {name}ProviderAuthConfig is a class that holds the authentication information for the {name}Provider.
    """

    host_url: pydantic.AnyHttpUrl = dataclasses.field(
        metadata={
            "required": True,
            "description": "{name} Host URL (e.g., https://{name_lower}.example.com)",
            "sensitive": False,
            "validation": "any_http_url",
        },
    )

    api_token: str = dataclasses.field(
        metadata={
            "required": True,
            "description": "{name} API Token",
            "sensitive": True,
        },
        default=None,
    )

    verify_ssl: bool = dataclasses.field(
        metadata={
            "required": False,
            "description": "Verify SSL certificate",
            "sensitive": False,
        },
        default=True,
    )


class {name}Provider(BaseProvider):
    PROVIDER_DISPLAY_NAME = "{name}"
    PROVIDER_TAGS = ["alert", "monitoring"]
    PROVIDER_CATEGORY = ["Monitoring"]
    PROVIDER_SCOPES = [
        ProviderScope(name="authenticated", description="User is authenticated"),
    ]

    """
    {name} monitoring states mapping
    """

    STATUS_MAP = {
        # Map {name} states to Keep AlertStatus
        "firing": AlertStatus.FIRING,
        "resolved": AlertStatus.RESOLVED,
        "pending": AlertStatus.PENDING,
    }

    SEVERITY_MAP = {
        # Map {name} severities to Keep AlertSeverity
        "critical": AlertSeverity.CRITICAL,
        "warning": AlertSeverity.WARNING,
        "info": AlertSeverity.INFO,
        "low": AlertSeverity.LOW,
    }

    def __init__(
        self, context_manager: ContextManager, provider_id: str, config: ProviderConfig
    ):
        super().__init__(context_manager, provider_id, config)

    def dispose(self):
        pass

    def validate_config(self):
        """
        Validates the configuration of the {name} provider.
        """
        self.logger.info("Validating {name} provider configuration")
        
        try:
            # Test authentication
            response = self._query_{name_lower}("test")
            
            if response.status_code == 200:
                self.logger.info("{name} provider configuration is valid")
                return {"authenticated": True}
            else:
                raise ProviderException(
                    f"Failed to authenticate with {name}: {response.status_code}"
                )
        except Exception as e:
            self.logger.error(f"Failed to validate {name} configuration: {e}")
            raise ProviderException(f"Failed to validate {name} configuration: {e}")

    def _query_{name_lower}(self, endpoint: str, method: str = "GET", data: dict = None):
        """
        Query the {name} API.
        """
        config = self.config.authentication
        
        url = f"{config.host_url.rstrip('/')}/{provider_info.get('api_path', 'api/v1')}/{endpoint}"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_token}",
        }
        
        params = {
            "verify_ssl": config.verify_ssl if hasattr(config, 'verify_ssl') else True
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, params=params)
            else:
                raise ProviderException(f"Unsupported HTTP method: {{method}}")
            
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise ProviderException(f"Failed to query {name} API: {{e}}")

    def _get_alerts(self) -> list[AlertDto]:
        """
        Get alerts from {name}.
        """
        self.logger.info("Getting alerts from {name}")
        
        try:
            # Query alerts
            response = self._query_{name_lower}("alerts")
            
            alerts = []
            
            if response.status_code == 200:
                data = response.json()
                for alert_data in data.get("alerts", []):
                    alert = self._parse_alert(alert_data)
                    if alert:
                        alerts.append(alert)
            
            self.logger.info(f"Retrieved {len(alerts)} alerts from {name}")
            return alerts
            
        except Exception as e:
            self.logger.error(f"Failed to get alerts from {name}: {e}")
            raise ProviderException(f"Failed to get alerts from {name}: {e}")

    def _parse_alert(self, alert_data: dict) -> AlertDto:
        """
        Parse an alert from {name}.
        """
        # Generic parsing - customize per provider
        status = AlertStatus.FIRING  # Default
        severity = AlertSeverity.INFO  # Default
        
        return AlertDto(
            id=f"{name_lower}-{alert_data.get('id', 'unknown')}",
            name=alert_data.get('name', 'Unknown Alert'),
            status=status,
            severity=severity,
            lastReceived=datetime.datetime.now().isoformat(),
            description=alert_data.get('description', 'No description'),
            source=["{name_lower}"],
            labels={
                "provider": "{name_lower}",
                "id": alert_data.get('id', 'unknown'),
            },
        )

    def get_alerts(self) -> list[AlertDto]:
        """
        Get alerts from {name}.
        """
        return self._get_alerts()

    def notify(self, alert: AlertDto | dict = None):
        """
        Notify {name} about an alert (not implemented).
        """
        raise ProviderException("{name} provider does not support sending alerts")

    def setup_webhook(
        self, tenant_id: str, keep_api_url: str, api_key: str, setup_alerts: bool = True
    ):
        """
        Setup webhook for {name} (not applicable).
        """
        raise ProviderException("Webhooks are not supported for {name} provider")
'''
    
    return template

def main():
    """Generate all providers"""
    
    print("🚀 Generating Keep Providers...")
    print("=" * 60)
    
    for provider in PROVIDERS_TO_CREATE:
        name = provider["name"]
        name_lower = name.lower()
        
        print(f"\n✨ Creating {name} Provider...")
        
        # Create provider directory
        provider_dir = Path(f"/tmp/keep/keep/providers/{name_lower}_provider")
        provider_dir.mkdir(exist_ok=True)
        
        # Generate provider code
        code = create_provider_template(provider)
        
        # Write provider file
        provider_file = provider_dir / f"{name_lower}_provider.py"
        provider_file.write_text(code)
        
        # Write __init__.py
        init_file = provider_dir / "__init__.py"
        init_file.write_text(f"from .{name_lower}_provider import {name}Provider\n\n__all__ = ['{name}Provider']\n")
        
        print(f"   ✅ Created {provider_dir}")
        print(f"   💰 Potential bounty: $50")
    
    print("\n" + "=" * 60)
    print(f"✨ Generated {len(PROVIDERS_TO_CREATE)} providers!")
    print(f"💰 Total potential value: ${len(PROVIDERS_TO_CREATE) * 50}")
    print("\n📝 Next steps:")
    print("1. Review and customize each provider")
    print("2. Test authentication")
    print("3. Create pull requests")

if __name__ == "__main__":
    main()
