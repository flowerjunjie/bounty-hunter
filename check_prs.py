#!/usr/bin/env python3
"""
检查我的 PR 状态并寻找新机会
"""
import json
import subprocess
from datetime import datetime

def check_my_prs():
    """检查 keephq/keep 的 PR 状态"""
    try:
        result = subprocess.run(
            ['gh', 'pr', 'list', '--repo', 'keephq/keep', '--search', 'author:app/kai-agent-free'],
            capture_output=True,
            text=True,
            timeout=30
        )
        print("📋 我的 PR 状态:")
        print(result.stdout)
    except Exception as e:
        print(f"检查 PR 失败: {e}")

def find_easy_wins():
    """寻找容易完成的 bounties"""
    with open('state.json', 'r') as f:
        data = json.load(f)
    
    # 寻找 "Provider" 标签的 bounties（通常比较容易）
    provider_bounties = [b for b in data['known_bounties'] 
                        if any('Provider' in label for label in b.get('labels', []))]
    
    print(f"\n🎯 发现 {len(provider_bounties)} 个 Provider bounties:")
    for bounty in provider_bounties[:5]:
        print(f"  - {bounty['repo']}/{bounty['number']}: ${bounty.get('amount', 0)}")
        print(f"    {bounty['title'][:60]}...")

if __name__ == '__main__':
    print(f"=== 赚钱状态检查 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    check_my_prs()
    find_easy_wins()
