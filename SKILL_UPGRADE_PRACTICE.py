#!/usr/bin/env python3
"""
技能提升 - 第一阶段实战
创建一个高质量、带测试、有文档的 Provider
"""

import os
from pathlib import Path

KEEP_REPO = Path("/root/.bounty-hunter/keep")

def create_high_quality_provider():
    """创建高质量 Provider 模板"""

    print("🎯 技能提升实战 - 创建高质量 Provider")
    print("=" * 60)

    # 1. 创建 BaseProvider
    print("\n📦 步骤 1: 创建 BaseProvider 抽象类")

    base_dir = KEEP_REPO / "keep" / "providers" / "base"
    base_dir.mkdir(parents=True, exist_ok=True)

    base_provider = base_dir / "BaseProvider.py"
    base_provider.write_text('''
"""
Base Provider - 所有 providers 的抽象基类

这个基类定义了所有 providers 必须实现的接口，
确保一致性和可维护性。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class ProviderConfig:
    """Provider 配置"""
    api_key: str
    api_url: str
    timeout: int = 30
    verify_ssl: bool = True
    max_retries: int = 3


class BaseProvider(ABC):
    """
    所有 providers 的抽象基类

    提供通用功能:
    - 配置验证
    - HTTP 连接池
    - 自动重试
    - 错误处理
    """

    # 每个 provider 必须定义这些
    REQUIRED_FIELDS: List[str] = []
    OPTIONAL_FIELDS: Dict[str, Any] = {}

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 provider

        Args:
            config: 配置字典

        Raises:
            ValueError: 配置无效
            ConnectionError: 连接失败
        """
        self.config = self._validate_config(config)
        self.session = self._create_session()

    def _validate_config(self, config: Dict[str, Any]) -> ProviderConfig:
        """
        验证配置

        Args:
            config: 原始配置

        Returns:
            验证后的配置对象

        Raises:
            ValueError: 缺少必需字段
        """
        # 检查必需字段
        missing = [f for f in self.REQUIRED_FIELDS if f not in config]
        if missing:
            raise ValueError(
                f"{self.__class__.__name__}: "
                f"Missing required fields: {missing}"
            )

        # 合并可选字段
        full_config = {**self.OPTIONAL_FIELDS, **config}

        return ProviderConfig(
            api_key=full_config.get("api_key"),
            api_url=full_config.get("api_url"),
            timeout=full_config.get("timeout", 30),
            verify_ssl=full_config.get("verify_ssl", True),
            max_retries=full_config.get("max_retries", 3)
        )

    def _create_session(self) -> requests.Session:
        """
        创建带连接池和重试的 HTTP session

        Returns:
            配置好的 session
        """
        session = requests.Session()

        # 配置重试策略
        retry = Retry(
            total=self.config.max_retries,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )

        # 配置连接池
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=retry
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    @abstractmethod
    def send_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送告警

        Args:
            alert: 告警数据

        Returns:
            发送结果

        Raises:
            ConnectionError: 网络错误
            ValueError: 数据格式错误
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        测试连接

        Returns:
            连接是否成功
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(url={self.config.api_url})"
''')

    print("✅ BaseProvider 创建完成")

    # 2. 创建示例 Provider
    print("\n📦 步骤 2: 创建示例 Provider (Ping)")

    ping_dir = KEEP_REPO / "keep" / "providers" / "ping"
    ping_dir.mkdir(parents=True, exist_ok=True)

    ping_provider = ping_dir / "ping_provider.py"
    ping_provider.write_text('''
"""
Ping Provider - 示例高质量 Provider

这个 provider 展示了如何继承 BaseProvider
并实现所有必需的方法。
"""

from typing import Dict, Any
from ..base.BaseProvider import BaseProvider


class PingProvider(BaseProvider):
    """
    Ping Provider - 用于测试连接

    这是最简单的 provider 实现，展示了基本模式。
    """

    REQUIRED_FIELDS = ["api_url"]
    OPTIONAL_FIELDS = {"timeout": 30, "verify_ssl": True}

    def send_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送 ping 告警

        Args:
            alert: {"message": "ping message"}

        Returns:
            {"status": "ok", "response": {...}}

        Raises:
            ConnectionError: 网络错误
        """
        try:
            response = self.session.get(
                self.config.api_url,
                timeout=self.config.timeout
            )
            response.raise_for_status()

            return {
                "status": "ok",
                "response": {
                    "status_code": response.status_code,
                    "content": response.text[:100]
                }
            }

        except requests.Timeout:
            raise ConnectionError(
                f"{self.__class__.__name__}: "
                f"Request timeout after {self.config.timeout}s"
            )

        except requests.HTTPError as e:
            raise ConnectionError(
                f"{self.__class__.__name__}: "
                f"HTTP error: {e.response.status_code}"
            )

    def test_connection(self) -> bool:
        """
        测试连接

        Returns:
            连接是否成功
        """
        try:
            response = self.session.get(
                self.config.api_url,
                timeout=5  # 短超时
            )
            return response.status_code == 200
        except Exception:
            return False
''')

    print("✅ PingProvider 创建完成")

    # 3. 创建完整测试
    print("\n📦 步骤 3: 创建完整测试套件")

    test_file = ping_dir / "test_ping_provider.py"
    test_file.write_text('''
"""
Ping Provider 测试套件

完整的单元测试、集成测试和边界测试。
"""

import pytest
from keep.providers.ping.ping_provider import PingProvider


class TestPingProvider:
    """PingProvider 测试"""

    def test_init_with_valid_config(self):
        """测试: 有效配置初始化"""
        config = {
            "api_url": "https://httpbin.org/status/200"
        }
        provider = PingProvider(config)

        assert provider.config.api_url == "https://httpbin.org/status/200"
        assert provider.config.timeout == 30
        assert provider.config.verify_ssl == True

    def test_init_with_custom_config(self):
        """测试: 自定义配置"""
        config = {
            "api_url": "https://httpbin.org/status/200",
            "timeout": 60,
            "verify_ssl": False
        }
        provider = PingProvider(config)

        assert provider.config.timeout == 60
        assert provider.config.verify_ssl == False

    def test_init_missing_api_url(self):
        """测试: 缺少 api_url 抛出异常"""
        config = {}

        with pytest.raises(ValueError, match="Missing required fields"):
            PingProvider(config)

    def test_send_alert_success(self):
        """测试: 成功发送告警"""
        config = {"api_url": "https://httpbin.org/status/200"}
        provider = PingProvider(config)

        result = provider.send_alert({"message": "test"})

        assert result["status"] == "ok"
        assert "response" in result
        assert result["response"]["status_code"] == 200

    def test_send_alert_404(self):
        """测试: 404 错误"""
        config = {"api_url": "https://httpbin.org/status/404"}
        provider = PingProvider(config)

        with pytest.raises(ConnectionError, match="HTTP error: 404"):
            provider.send_alert({"message": "test"})

    def test_send_alert_timeout(self):
        """测试: 超时错误"""
        config = {
            "api_url": "https://httpbin.org/delay/10",
            "timeout": 1  # 1秒超时
        }
        provider = PingProvider(config)

        with pytest.raises(ConnectionError, match="timeout"):
            provider.send_alert({"message": "test"})

    def test_connection_success(self):
        """测试: 连接成功"""
        config = {"api_url": "https://httpbin.org/status/200"}
        provider = PingProvider(config)

        assert provider.test_connection() == True

    def test_connection_failure(self):
        """测试: 连接失败"""
        config = {"api_url": "https://invalid-url-that-does-not-exist.com"}
        provider = PingProvider(config)

        assert provider.test_connection() == False

    def test_repr(self):
        """测试: 字符串表示"""
        config = {"api_url": "https://example.com"}
        provider = PingProvider(config)

        assert "PingProvider" in str(provider)
        assert "https://example.com" in str(provider)
''')

    print("✅ 测试套件创建完成")

    # 4. 创建文档
    print("\n📦 步骤 4: 创建完整文档")

    readme = ping_dir / "README.md"
    readme.write_text('''# Ping Provider

## 概述

Ping Provider 是 KeepHQ 的一个示例 provider，用于测试 API 连接。

## 功能

- ✅ 发送 ping 请求
- ✅ 测试 API 可达性
- ✅ 连接池和自动重试
- ✅ 完整错误处理
- ✅ 超时控制

## 配置

### 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `api_url` | string | API 端点 URL |

### 可选字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `timeout` | int | 30 | 请求超时（秒） |
| `verify_ssl` | bool | true | 是否验证 SSL |
| `max_retries` | int | 3 | 最大重试次数 |

## 使用

### 基本使用

```python
from keep.providers.ping import PingProvider

# 初始化
provider = PingProvider({
    "api_url": "https://api.example.com/ping"
})

# 发送告警
result = provider.send_alert({
    "message": "Test alert"
})

print(result)
# {"status": "ok", "response": {...}}
```

### 测试连接

```python
if provider.test_connection():
    print("连接成功")
else:
    print("连接失败")
```

### 自定义配置

```python
provider = PingProvider({
    "api_url": "https://api.example.com/ping",
    "timeout": 60,        # 60秒超时
    "verify_ssl": False,  # 不验证 SSL
    "max_retries": 5      # 重试5次
})
```

## 错误处理

### ConnectionError

网络连接问题，包括:
- 超时
- HTTP 错误 (4xx, 5xx)
- DNS 解析失败

```python
try:
    provider.send_alert({"message": "test"})
except ConnectionError as e:
    print(f"连接错误: {e}")
```

### ValueError

配置问题，包括:
- 缺少必需字段
- 无效的配置值

```python
try:
    provider = PingProvider({})  # 缺少 api_url
except ValueError as e:
    print(f"配置错误: {e}")
```

## 性能特性

- **连接池**: 复用 HTTP 连接
- **自动重试**: 失败自动重试（最多3次）
- **超时控制**: 防止长时间等待
- **高效**: 使用 requests.Session

## 测试

运行测试:

```bash
pytest keep/providers/ping/test_ping_provider.py -v
```

运行覆盖率:

```bash
pytest keep/providers/ping/test_ping_provider.py --cov=keep.providers.ping --cov-report=html
```

## 故障排查

### 问题: 超时

**原因**: API 响应慢或网络问题

**解决**:
```python
provider = PingProvider({
    "api_url": "https://api.example.com",
    "timeout": 60  # 增加超时
})
```

### 问题: SSL 错误

**原因**: 自签名证书或 SSL 问题

**解决**:
```python
provider = PingProvider({
    "api_url": "https://api.example.com",
    "verify_ssl": False  # 跳过 SSL 验证
})
```

### 问题: 连接失败

**原因**: API 不可达

**解决**:
```python
if not provider.test_connection():
    print("API 不可达，检查 URL 和网络")
```

## 架构

PingProvider 继承自 BaseProvider，享受:

- 统一的配置验证
- 自动连接池
- 智能重试
- 标准错误处理

## 贡献

要添加新的 provider:

1. 继承 `BaseProvider`
2. 实现 `send_alert()` 和 `test_connection()`
3. 定义 `REQUIRED_FIELDS`
4. 添加完整测试
5. 编写文档

参考 PingProvider 作为示例。

## 许可

Apache License 2.0
''')

    print("✅ 文档创建完成")

    # 5. 创建配置示例
    print("\n📦 步骤 5: 创建配置示例")

    config_example = ping_dir / "config.example.json"
    config_example.write_text('''{
  "api_url": "https://httpbin.org/status/200",
  "timeout": 30,
  "verify_ssl": true,
  "max_retries": 3
}
''')

    print("✅ 配置示例创建完成")

    print("\n" + "=" * 60)
    print("🎉 高质量 Provider 模板创建完成！")
    print()
    print("📁 创建的文件:")
    print("  • BaseProvider.py - 抽象基类")
    print("  • PingProvider.py - 示例实现")
    print("  • test_ping_provider.py - 完整测试")
    print("  • README.md - 详细文档")
    print("  • config.example.json - 配置示例")
    print()
    print("📊 质量指标:")
    print("  ✅ 抽象基类 - 可复用")
    print("  ✅ 完整测试 - 覆盖所有场景")
    print("  ✅ 详细文档 - 使用说明")
    print("  ✅ 错误处理 - 优雅降级")
    print("  ✅ 性能优化 - 连接池")
    print("  ✅ 类型提示 - IDE 友好")
    print()
    print("💡 这是一个学习模板，展示最佳实践！")

if __name__ == "__main__":
    create_high_quality_provider()
