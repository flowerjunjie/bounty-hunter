#!/usr/bin/env python3
"""
快速赚钱脚本 - 立即执行！
选择最简单的 bounty 快速完成
"""

import subprocess
import json

def analyze_simple_bounty():
    """分析并选择最简单的 bounty"""
    print("\n" + "="*70)
    print("⚡ 分析最简单的 Bounty...".center(70))
    print("="*70 + "\n")

    # 最简单的候选
    candidates = [
        {
            "issue": "zio/zio#9084",
            "title": "Add ZStream.fromInputStreamInterruptible",
            "reason": "添加新功能，不需要修改现有代码",
            "complexity": "低",
            "time": "2-3小时",
        },
        {
            "issue": "zio/zio#8664",
            "title": "zio-test: classic assertion `equalTo` using `Diff`",
            "reason": "文档改进，使用现有 Diff 功能",
            "complexity": "低",
            "time": "1-2小时",
        },
    ]

    print("🎯 推荐完成顺序:\n")

    for i, candidate in enumerate(candidates, 1):
        print(f"{i}. {candidate['issue']}")
        print(f"   标题: {candidate['title']}")
        print(f"   原因: {candidate['reason']}")
        print(f"   复杂度: {candidate['complexity']}")
        print(f"   预计时间: {candidate['time']}")
        print()

    # 选择第一个
    selected = candidates[1]  # zio/zio#8664 - 最简单
    print(f"{'='*70}")
    print(f"✅ 选择: {selected['issue']}".center(70))
    print(f"{'='*70}\n")

    return selected

def fetch_issue_details(issue_number):
    """获取 issue 详情"""
    print(f"📋 获取 Issue #{issue_number} 详情...\n")

    cmd = f"gh issue view {issue_number} --repo zio/zio --json title,body,comments --jq '{{title, body}}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(result.stdout)
        return json.loads(result.stdout)
    else:
        print(f"❌ 获取失败: {result.stderr}")
        return None

def create_implementation_plan():
    """创建实现计划"""
    print("\n" + "="*70)
    print("📝 实现计划".center(70))
    print("="*70 + "\n")

    plan = """
目标: zio/zio#8664 - zio-test: classic assertion `equalTo` using `Diff`

分析:
1. 这是一个文档改进任务
2. 需要让 equalTo 使用 Diff 渲染
3. 应该已经有 Diff 实现，只需要集成

步骤:
1. 克隆 zio/zio 仓库
2. 查找 Diff 相关代码
3. 修改 equalTo 断言
4. 编写测试
5. 提交 PR

预计时间: 1-2小时
预期收益: $50
成功率: 80%
"""

    print(plan)
    return plan

def execute_quick_cash():
    """执行快速赚钱"""
    print("\n" + "="*70)
    print("🚀 开始执行快速赚钱！".center(70))
    print("="*70 + "\n")

    # 1. 分析最简单的 bounty
    selected = analyze_simple_bounty()

    # 2. 创建实现计划
    plan = create_implementation_plan()

    # 3. 下一步指令
    print("="*70)
    print("📋 下一步操作:".center(70))
    print("="*70 + "\n")

    steps = [
        "1. gh issue view 8664 --repo zio/zio (查看详情)",
        "2. gh repo clone zio/zio (克隆仓库)",
        "3. 研究代码库，找到 Diff 相关实现",
        "4. 修改 equalTo 断言",
        "5. 测试并提交 PR",
    ]

    for step in steps:
        print(f"  {step}")

    print(f"\n💰 预期收益: $50")
    print(f"⏰ 预计时间: 1-2小时")
    print(f"✅ 成功率: 80%")

    print("\n" + "="*70)
    print("🎯 准备好了吗？让我们开始赚钱！".center(70))
    print("="*70 + "\n")

if __name__ == "__main__":
    execute_quick_cash()
