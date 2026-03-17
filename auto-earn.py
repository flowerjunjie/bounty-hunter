#!/usr/bin/env python3
"""
自动赚钱助手 - 监控新机会并快速响应
"""
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

STATE_FILE = Path("opportunities.json")

def load_opportunities():
    """加载已知机会"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"known_issues": [], "last_check": None}

def save_opportunities(opportunities):
    """保存机会状态"""
    with open(STATE_FILE, 'w') as f:
        json.dump(opportunities, f, indent=2)

def find_new_opportunities():
    """发现新的机会"""
    with open('state.json', 'r') as f:
        data = json.load(f)
    
    known = load_opportunities()
    known_issues = set(known.get('known_issues', []))
    
    # 找出所有可用的 bounties
    available = [b for b in data['known_bounties']
                 if 'Bounty claim' not in str(b.get('labels', []))
                 and 'Rewarded' not in str(b.get('labels', []))]
    
    # 找出新的机会
    new_opportunities = []
    for bounty in available:
        issue_id = f"{bounty['repo']}/{bounty['number']}"
        if issue_id not in known_issues:
            new_opportunities.append(bounty)
            known_issues.add(issue_id)
    
    # 更新已知机会
    known['known_issues'] = list(known_issues)
    known['last_check'] = datetime.now().isoformat()
    save_opportunities(known)
    
    return new_opportunities

def prioritize_opportunities(opportunities):
    """优先级排序"""
    def score(bounty):
        score = 0
        
        # 1. 优先选择 Provider 类型
        title = bounty['title'].lower()
        labels_str = str(bounty.get('labels', []))
        if 'provider' in title or 'provider' in labels_str.lower():
            score += 100
        
        # 2. 优先选择文档类任务
        if any(word in title for word in ['document', 'doc', 'example', 'guide']):
            score += 80
        
        # 3. 优先选择简单修复
        if any(word in title for word in ['fix', 'add', 'update']):
            score += 60
        
        # 4. 评论少的优先（竞争少）
        score -= bounty.get('comments', 0) * 2
        
        # 5. 最近更新的优先
        updated = bounty.get('updated_at', '')
        if updated:
            try:
                # 处理 ISO 格式时间
                if updated.endswith('Z'):
                    updated = updated.replace('Z', '+00:00')
                dt = datetime.fromisoformat(updated)
                days_old = (datetime.now() - dt.replace(tzinfo=None)).days
                score -= days_old * 0.5
            except:
                pass
        
        return score
    
    return sorted(opportunities, key=score, reverse=True)

def main():
    print(f"🤖 自动赚钱助手 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 查找新机会
    new_ops = find_new_opportunities()
    
    if not new_ops:
        print("✅ 没有发现新机会")
        print(f"💡 当前状态: {len(load_opportunities()['known_issues'])} 个已知 bounties")
        return
    
    print(f"🎉 发现 {len(new_ops)} 个新机会！")
    print()
    
    # 优先级排序
    prioritized = prioritize_opportunities(new_ops)
    
    print("📋 优先级列表:")
    for i, bounty in enumerate(prioritized[:5], 1):
        print(f"{i}. {bounty['repo']}/#{bounty['number']} - ${bounty.get('amount', 0)}")
        print(f"   {bounty['title'][:65]}...")
        print(f"   评论: {bounty.get('comments', 0)}")
        print()
    
    # 推荐最佳机会
    if prioritized:
        best = prioritized[0]
        print(f"🎯 推荐最佳机会:")
        print(f"   {best['repo']}/#{best['number']}")
        print(f"   标题: {best['title']}")
        print(f"   价值: ${best.get('amount', 0)}")
        print(f"   链接: {best['url']}")

if __name__ == '__main__':
    main()
