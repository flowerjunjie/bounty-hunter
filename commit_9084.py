#!/usr/bin/env python3
"""
提交 zio#9084 的 PR
"""

import subprocess
from pathlib import Path

ZIO_REPO = Path("/root/.bounty-hunter/zio-zio-new")

def run_cmd(cmd, cwd=None):
    """运行命令"""
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd or ZIO_REPO,
        capture_output=True,
        text=True
    )
    return result

def main():
    print("🚀 提交 zio#9084 PR")
    print("=" * 60)

    # 1. 检查当前分支
    print("\n📂 检查仓库状态...")
    result = run_cmd("git status")
    print(result.stdout)

    # 2. 创建新分支
    branch_name = "add-fromInputStreamInterruptible"
    print(f"\n🌿 创建分支: {branch_name}")
    result = run_cmd(f"git checkout -b {branch_name}")
    if result.returncode != 0:
        print(f"⚠️  分支可能已存在，切换到该分支")
        result = run_cmd(f"git checkout {branch_name}")
    print("✅ 分支创建/切换完成")

    # 3. 添加修改
    print("\n➕ 添加修改...")
    result = run_cmd("git add streams/shared/src/main/scala/zio/stream/ZStream.scala")
    print("✅ 文件已添加")

    # 4. 提交
    print("\n💾 提交修改...")
    commit_msg = '''Add ZStream.fromInputStreamInterruptible (#9084)

Implements a new `fromInputStreamInterruptible` method that properly
handles fiber interruption by closing the InputStream when interrupted.

Unlike `fromInputStream`, this ensures resources are properly cleaned
up when the stream is interrupted.

Changes:
- Added `fromInputStreamInterruptible` method to ZStream companion
- Method uses `ZStream.scope` and `addFinalizer` for proper cleanup
- Maintains API compatibility with existing `fromInputStream`'''

    result = run_cmd(f'git commit -m "{commit_msg}"')
    if result.returncode == 0:
        print("✅ 提交成功")
        print(result.stdout)
    else:
        print("❌ 提交失败")
        print(result.stderr)
        return False

    # 5. 推送到远程
    print("\n📤 推送到远程...")
    result = run_cmd(f"git push -u origin {branch_name}")
    if result.returncode == 0:
        print("✅ 推送成功")
        print(result.stdout)
    else:
        print("❌ 推送失败")
        print(result.stderr)
        return False

    print("\n" + "=" * 60)
    print("✅ PR 准备完成！")
    print(f"\n🔗 分支: {branch_name}")
    print("💰 Bounty: $50")
    print("🎯 Issue: zio/zio#9084")
    print("\n下一步:")
    print("  访问 GitHub 创建 PR: https://github.com/zio/zio/compare")

    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 完成！")
        else:
            print("\n❌ 失败")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
