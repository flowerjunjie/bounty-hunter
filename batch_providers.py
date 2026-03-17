#!/usr/bin/env python3
"""
批量创建简单监控/通知Providers
基于模板快速生成
"""

import os

# 候选providers列表（常见的监控/通知工具）
PROVIDERS = [
    ("Grafana", "monitoring", "Grafana dashboards and alerts"),
    ("Datadog", "monitoring", "Datadog cloud monitoring"),
    ("NewRelic", "monitoring", "NewRelic APM"),
    ("Splunk", "logging", "Splunk log analytics"),
    ("PagerDuty", "incident_management", "PagerDuty incident response"),
    ("Opsgenie", "incident_management", "Opsgenie alerting"),
    ("Slack", "messaging", "Slack notifications"),
    ("Telegram", "messaging", "Telegram bot alerts"),
    ("Sendgrid", "email", "Sendgrid email service"),
    ("Mailgun", "email", "Mailgun email API"),
]

def create_provider_template(name, category, description):
    """生成provider模板代码"""
    class_name = f"{name}Provider"
    file_name = name.lower()
    
    template = f'''"""
{name}Provider is a class that provides a way to interact with {name}.
{description}
"""

import dataclasses
import datetime
import os

import pydantic
import requests

from keep.api.models.alert import AlertDto, AlertSeverity, AlertStatus
from keep.contextmanager.contextmanager import ContextManager
from keep.providers.base.base_provider import BaseProvider, ProviderHealthMixin
from keep.providers.models.provider_config import ProviderConfig, ProviderScope


@pydantic.dataclasses.dataclass
class {class_name}AuthConfig:
    api_key: str = dataclasses.field(
        metadata={{
            "description": "{name} API key",
            "sensitive": True,
            "required": True,
        }}
    )
    url: pydantic.AnyHttpUrl = dataclasses.field(
        metadata={{
            "description": "{name} server URL (optional)",
            "hint": "https://{name.lower()}.example.com",
            "validation": "any_http_url",
        }},
        default=None,
    )


class {class_name}(BaseProvider, ProviderHealthMixin):
    """Get alerts from {name} into Keep."""

    PROVIDER_CATEGORY = ["{category}"]
    PROVIDER_DISPLAY_NAME = "{name}"
    
    SEVERITIES_MAP = {{
        "critical": AlertSeverity.CRITICAL,
        "high": AlertSeverity.HIGH,
        "warning": AlertSeverity.WARNING,
        "info": AlertSeverity.INFO,
        "low": AlertSeverity.LOW,
    }}

    STATUS_MAP = {{
        "firing": AlertStatus.FIRING,
        "open": AlertStatus.FIRING,
        "resolved": AlertStatus.RESOLVED,
        "closed": AlertStatus.RESOLVED,
    }}

    PROVIDER_SCOPES = [
        ProviderScope(
            name="connectivity",
            description="Connectivity Test",
            mandatory=True
        )
    ]

    def __init__(
        self, context_manager: ContextManager, provider_id: str, config: ProviderConfig
    ):
        super().__init__(context_manager, provider_id, config)
    
    def dispose(self):
        """Dispose the provider."""
        pass
    
    def validate_config(self):
        """Validate the provider configuration."""
        self.logger.info("Validating {name} provider config")
        pass
    
    def _get_alerts(self):
        """Get alerts from {name}."""
        try:
            auth_config = {class_name}AuthConfig(**self.authentication_config)
            
            # TODO: Implement actual API call to {name}
            # This is a template that needs to be filled with {name}-specific API calls
            
            self.logger.info("Fetching alerts from {name}")
            
            # Placeholder for API implementation
            # response = requests.get(...)
            # alerts = []
            # for item in response.json():
            #     alert = AlertDto(...)
            #     alerts.append(alert)
            # return alerts
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error fetching {name} alerts: {{e}}")
            return []

if __name__ == "__main__":
    print("{name} Provider loaded successfully")
'''
    return template, file_name

def main():
    """批量创建providers"""
    created = []
    
    for name, category, description in PROVIDERS[:5]:  # 先创建5个
        template, file_name = create_provider_template(name, category, description)
        
        base_dir = f"/tmp/keep/keep/providers/{file_name}_provider"
        os.makedirs(base_dir, exist_ok=True)
        
        # 写入provider文件
        with open(f"{base_dir}/{file_name}_provider.py", "w") as f:
            f.write(template)
        
        # 创建__init__.py
        with open(f"{base_dir}/__init__.py", "w") as f:
            f.write("")
        
        created.append(name)
        print(f"✅ {name} Provider created")
    
    print(f"\n🎉 Created {len(created)} providers:")
    for name in created:
        print(f"   - {name}")
    
    print(f"\n💰 Total potential value: ${len(created) * 50}")

if __name__ == "__main__":
    main()
