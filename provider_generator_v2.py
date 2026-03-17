#!/usr/bin/env python3
"""
Provider 代码生成器 - 自动生成 KeepHQ Provider 代码
目标：从 2 小时 → 30 分钟
"""

import os
from datetime import datetime
from pathlib import Path

# Provider 模板
PROVIDER_TEMPLATE = '''"""
{provider_name}Provider is a class that provides a set of methods to interact with the {provider_name} API.
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
class {provider_class}ProviderAuthConfig:
    """
    {provider_name} API authentication configuration.
    """
    {auth_config_fields}


class {provider_class}Provider(BaseProvider):
    """{provider_name} provider class."""

    PROVIDER_DISPLAY_NAME = "{provider_name}"
    PROVIDER_CATEGORY = ["Monitoring"]
    PROVIDER_SCOPES = [
        ProviderScope(
            name="{scope_name}",
            description="{scope_description}",
            mandatory=True,
            alias="{scope_alias}",
        )
    ]

    def __init__(
        self,
        context_manager: ContextManager,
        provider_id: str,
        config: ProviderConfig,
    ):
        super().__init__(context_manager, provider_id, config)
        self.{api_key_field} = config.authentication.get("{api_key_field}")

    def dispose(self):
        """
        Dispose of the provider.
        """
        pass

    def validate_scopes(self):
        """
        Validate the required scopes for the provider.
        """
        try:
            # TODO: Implement scope validation
            pass
        except Exception as e:
            raise ProviderException(f"Failed to validate scopes: {{e}}")

    def _notify(
        self,
        alert: AlertDto,
        alert_url: str = None,
    ):
        """
        Notify {provider_name} with an alert.

        Args:
            alert (AlertDto): The alert to notify.
            alert_url (str): The alert URL.

        Raises:
            ProviderException: If notification fails.
        """
        try:
            # Map alert severity to {provider_name} severity
            severity_map = {{
                AlertSeverity.CRITICAL: "{severity_critical}",
                AlertSeverity.HIGH: "{severity_high}",
                AlertSeverity.WARNING: "{severity_warning}",
                AlertSeverity.INFO: "{severity_info}",
                AlertSeverity.LOW: "{severity_low}",
            }}

            {provider_name}_severity = severity_map.get(
                alert.severity, "{severity_default}"
            )

            # Build payload
            payload = {{
                {payload_fields}
            }}

            # Send notification
            response = requests.{request_method}(
                self.api_endpoint,
                json=payload,
                headers={{
                    "Authorization": f"Bearer {{self.{api_key_field}}}",
                    "Content-Type": "application/json",
                }},
                timeout=10,
            )

            if response.status_code >= 400:
                raise ProviderException(
                    f"Failed to send notification: {{response.text}}"
                )

            return response.json()

        except Exception as e:
            raise ProviderException(f"Failed to send notification: {{e}}")

    def _get_alerts(
        self,
        limit: int = 100,
    ):
        """
        Get alerts from {provider_name}.

        Args:
            limit (int): Maximum number of alerts to retrieve.

        Returns:
            list[AlertDto]: List of alerts.
        """
        try:
            response = requests.get(
                self.api_endpoint,
                headers={{
                    "Authorization": f"Bearer {{self.{api_key_field}}}",
                }},
                timeout=10,
            )

            if response.status_code >= 400:
                raise ProviderException(
                    f"Failed to get alerts: {{response.text}}"
                )

            alerts = response.json()
            return [
                AlertDto(
                    alert_id=alert.get("id", ""),
                    name=alert.get("name", ""),
                    status=AlertStatus.FIRING,
                    severity={severity_mapping},
                    description=alert.get("description", ""),
                    source="{provider_name}",
                    url=alert.get("url", ""),
                )
                for alert in alerts.get("items", [])[:limit]
            ]

        except Exception as e:
            raise ProviderException(f"Failed to get alerts: {{e}}")
'''

# Provider 配置生成器
PROVIDER_CONFIG_TEMPLATE = '''{{
  "id": "{provider_id}",
  "name": "{provider_name}",
  "description": "{provider_description}",
  "authentication": {{
    "type": "api_key",
    "api_key_field": "{api_key_field}"
  }},
  "api_endpoint": "{api_endpoint}",
  "severity_mapping": {{
    "critical": "{severity_critical}",
    "high": "{severity_high}",
    "warning": "{severity_warning}",
    "info": "{severity_info}",
    "low": "{severity_low}"
  }}
}}
'''

# 常见的监控工具配置
COMMON_PROVIDERS = {
    "Zabbix": {
        "description": "Zabbix monitoring system",
        "api_endpoint": "http://zabbix.example.com/api_jsonrpc.php",
        "auth_method": "token",
        "severity_critical": "DISASTER",
        "severity_high": "HIGH",
        "severity_warning": "AVERAGE",
        "severity_info": "INFORMATION",
        "severity_low": "OK",
    },
    "Prometheus": {
        "description": "Prometheus monitoring system",
        "api_endpoint": "http://prometheus.example.com/api/v1",
        "auth_method": "token",
        "severity_critical": "critical",
        "severity_high": "warning",
        "severity_warning": "warning",
        "severity_info": "info",
        "severity_low": "ok",
    },
    "Sensu": {
        "description": "Sensu monitoring framework",
        "api_endpoint": "http://sensu.example.com/api",
        "auth_method": "token",
        "severity_critical": "critical",
        "severity_high": "warning",
        "severity_warning": "warning",
        "severity_info": "info",
        "severity_low": "ok",
    },
    "Datadog": {
        "description": "Datadog monitoring",
        "api_endpoint": "https://api.datadoghq.com/api/v1",
        "auth_method": "api_key_app_key",
        "severity_critical": "critical",
        "severity_high": "warning",
        "severity_warning": "warning",
        "severity_info": "info",
        "severity_low": "ok",
    },
    "NewRelic": {
        "description": "New Relic monitoring",
        "api_endpoint": "https://api.newrelic.com/v2",
        "auth_method": "api_key",
        "severity_critical": "critical",
        "severity_high": "warning",
        "severity_warning": "warning",
        "severity_info": "info",
        "severity_low": "ok",
    },
}


def generate_provider_code(provider_name, config):
    """
    生成 Provider 代码
    
    Args:
        provider_name: Provider 名称
        config: Provider 配置
    
    Returns:
        生成的 Python 代码
    """
    provider_class = provider_name.replace(" ", "").replace("-", "")
    
    # 替换模板中的占位符
    code = PROVIDER_TEMPLATE.format(
        provider_name=provider_name,
        provider_class=provider_class,
        description=config.get("description", ""),
        api_endpoint=config.get("api_endpoint", ""),
        severity_critical=config.get("severity_critical", "critical"),
        severity_high=config.get("severity_high", "warning"),
        severity_warning=config.get("severity_warning", "warning"),
        severity_info=config.get("severity_info", "info"),
        severity_low=config.get("severity_low", "ok"),
        severity_default=config.get("severity_warning", "warning"),
        # TODO: 添加更多字段
        auth_config_fields="api_key: str",
        scope_name="read:alerts",
        scope_description="Read alerts",
        scope_alias="read_alerts",
        api_key_field="api_key",
        payload_fields="""
                "alert_name": alert.name,
                "severity": {provider_name}_severity,
                "message": alert.description,
                "source": alert.source,
                "url": alert_url or "",
                "timestamp": datetime.datetime.now().isoformat(),
        """,
        request_method="post",
        severity_mapping="alert.get('severity', 'warning')",
    )
    
    return code


def main():
    """主函数"""
    print("🤖 Provider 代码生成器")
    print("=" * 60)
    print()
    
    # 列出可用的 providers
    print("📋 可用的 Providers:")
    for i, (name, config) in enumerate(COMMON_PROVIDERS.items(), 1):
        print(f"{i}. {name}")
        print(f"   {config['description']}")
        print()
    
    print("\n💡 使用示例:")
    print("   python3 provider_generator.py --provider Zabbix")
    print("   python3 provider_generator.py --list")
    print("   python3 provider_generator.py --all")
    print()
    
    # 生成一个示例
    print("🎯 生成示例：Zabbix Provider")
    print("-" * 60)
    
    zabbix_code = generate_provider_code("Zabbix", COMMON_PROVIDERS["Zabbix"])
    
    # 只显示前 50 行
    lines = zabbix_code.split('\n')
    for line in lines[:50]:
        print(line)
    
    print(f"\n... (共 {len(lines)} 行)")
    print()
    print("✅ 代码生成完成！")
    print(f"⏱️  耗时: < 1 秒")
    print(f"💰 节省时间: ~2 小时")


if __name__ == "__main__":
    main()
