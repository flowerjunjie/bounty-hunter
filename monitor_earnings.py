#!/usr/bin/env python3
"""
赚钱监控脚本 - 跟踪 PR 状态和收益
"""
import json
import subprocess
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("earnings.json")

def load_state():
    """加载收益状态"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "submitted_prs": [],
        "pending_bounties": 0,
        "total_value": 0,
        "last_check": None
    }

def save_state(state):
    """保存收益状态"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def check_pr_status(pr_url):
    """检查 PR 状态"""
    try:
        # 解析 URL
        if 'keephq/keep' in pr_url:
            result = subprocess.run(
                ['gh', 'pr', 'view', pr_url.split('/')[-1], '--repo', 'keephq/keep', '--json', 'state,mergeable,title'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    'state': data.get('state'),
                    'mergeable': data.get('mergeable'),
                    'title': data.get('title')
                }
    except Exception as e:
        print(f"检查 PR 失败: {e}")
    return None

def update_earnings():
    """更新收益状态"""
    state = load_state()
    
    print(f"💰 赚钱监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 检查已提交的 PR
    if state['submitted_prs']:
        print(f"\n📋 已提交的 PR ({len(state['submitted_prs'])}):")
        for pr in state['submitted_prs']:
            status = check_pr_status(pr['url'])
            if status:
                status_icon = "✅" if status['state'] == "MERGED" else "⏳"
                print(f"  {status_icon} {pr['url']}")
                print(f"     状态: {status['state']} | 可合并: {status.get('mergeable', 'N/A')}")
                pr['status'] = status['state']
                pr['last_check'] = datetime.now().isoformat()
    
    # 读取最新的 bounty 数据
    with open('state.json', 'r') as f:
        bounty_data = json.load(f)
    
    print(f"\n🎯 当前 Bounties:")
    print(f"  总数: {bounty_data['total_count']}")
    print(f"  总价值: ${bounty_data['total_value']}")
    
    # 保存更新
    state['last_check'] = datetime.now().isoformat()
    save_state(state)
    
    print(f"\n✅ 状态已保存到 {STATE_FILE}")
    
    # 计算潜在收益
    merged = [p for p in state.get('submitted_prs', []) if p.get('status') == 'MERGED']
    pending = [p for p in state.get('submitted_prs', []) if p.get('status') not in ['MERGED', 'CLOSED']]
    
    print(f"\n💵 收益统计:")
    print(f"  已合并: {len(merged)} 个 PR")
    print(f"  待审核: {len(pending)} 个 PR")
    print(f"  潜在收益: ${len(pending) * 50}")  # 假设每个 $50

if __name__ == '__main__':
    update_earnings()
