#!/usr/bin/env python3
"""
任务 1: zio-http#3133 - Flag ZClient.request as deprecated
预计: 30分钟
价值: $50
"""

import subprocess
from pathlib import Path

WORKSPACE = Path("/root/.bounty-hunter")
ZIO_HTTP = WORKSPACE / "zio-http"

def step1_clone():
    """克隆仓库"""
    print("📥 步骤 1: 克隆 zio-http...")
    if ZIO_HTTP.exists():
        print("✅ 仓库已存在")
        return True

    result = subprocess.run(
        ["gh", "repo", "clone", "zio/zio-http", str(ZIO_HTTP)],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ 克隆成功")
        return True
    else:
        print(f"❌ 克隆失败: {result.stderr}")
        return False

def step2_find_file():
    """找到 ZClient 文件"""
    print("\n🔍 步骤 2: 找到 ZClient.request...")

    # 搜索 ZClient
    result = subprocess.run(
        ["find", str(ZIO_HTTP), "-name", "*.scala", "-type", "f"],
        capture_output=True,
        text=True
    )

    files = result.stdout.strip().split('\n')

    # 查找包含 ZClient 的文件
    for file in files:
        try:
            content = Path(file).read_text()
            if "object ZClient" in content or "class ZClient" in content:
                print(f"✅ 找到: {file}")
                return file
        except:
            continue

    print("❌ 未找到 ZClient")
    return None

def step3_add_deprecated(zclient_file):
    """添加 deprecated 标记"""
    print(f"\n✍️  步骤 3: 添加 deprecated 标记...")
    print(f"   文件: {zclient_file}")

    content = Path(zclient_file).read_text()

    # 检查是否已经有 deprecated
    if "@deprecated" in content:
        print("⚠️  已经有 deprecated 标记")
        return False

    # 找到 def request 的位置
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'def request(' in line:
            # 在前面添加 deprecated
            indent = len(line) - len(line.lstrip())
            deprecated_line = ' ' * indent + '@deprecated("Use ZClient.service.request instead")'
            lines.insert(i, deprecated_line)
            print("✅ 已添加 deprecated 标记")
            break

    # 写回文件
    new_content = '\n'.join(lines)
    Path(zclient_file).write_text(new_content)

    print("✅ 文件已更新")
    return True

def step4_commit():
    """提交 PR"""
    print("\n📤 步骤 4: 提交 PR...")

    # 创建分支
    subprocess.run(
        ["git", "checkout", "-b", "deprecate-zclient-request"],
        cwd=ZIO_HTTP,
        capture_output=True
    )

    # 添加修改
    subprocess.run(
        ["git", "add", "."],
        cwd=ZIO_HTTP,
        capture_output=True
    )

    # 提交
    subprocess.run(
        ["git", "commit", "-m", "feat: Deprecate ZClient.request (#3133)"],
        cwd=ZIO_HTTP,
        capture_output=True
    )

    # 推送
    result = subprocess.run(
        ["git", "push", "-u", "fork", "deprecate-zclient-request"],
        cwd=ZIO_HTTP,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ 推送成功")
        print("🔗 PR 链接: https://github.com/zio/zio-http/compare/main...flowerjunjie:zio-http:deprecate-zclient-request")
        return True
    else:
        print(f"❌ 推送失败: {result.stderr}")
        return False

def main():
    print("🚀 任务 1: zio-http#3133")
    print("=" * 60)

    if not step1_clone():
        return False

    zclient_file = step2_find_file()
    if not zclient_file:
        return False

    if not step3_add_deprecated(zclient_file):
        return False

    if not step4_commit():
        return False

    print("\n" + "=" * 60)
    print("✅ 任务 1 完成！")
    print("💰 价值: $50")
    print("⏱️  用时: ~30分钟")
    print()

    return True

if __name__ == "__main__":
    main()
