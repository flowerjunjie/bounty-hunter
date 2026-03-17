#!/usr/bin/env python3
import json
import os
from datetime import datetime
import requests
import time

BOUNTY_DIR = '/root/.bounty-hunter'
STATE_FILE = BOUNTY_DIR + '/state.json'
LOG_FILE = BOUNTY_DIR + '/cron.log'
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# Search for bounty emoji in labels
BOUNTY_LABELS = ['Bounty', '💎 Bounty', 'bounty', 'BOUNTY']

TARGET_REPOS = [
    ('zio', 'zio'),
    ('zio', 'zio-http'), 
    ('zio', 'zio-json'),
    ('zio', 'zio-quill'),
    ('keephq', 'keep'),
    ('golemcloud', 'golem'),
    ('maybe-finance', 'maybe'),
    ('unsiloed-ai', 'unsiloed'),
]

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    s = f'[{ts}] {msg}'
    print(s)
    with open(LOG_FILE, 'a') as f:
        f.write(s + '\n')

def has_bounty_label(labels):
    for label in labels:
        label_name = label.get('name', '')
        for bounty_label in BOUNTY_LABELS:
            if bounty_label.lower() in label_name.lower():
                return True
    return False

def extract_amount(labels, title):
    # Try to extract amount from labels
    for label in labels:
        label_name = label.get('name', '')
        if '$' in label_name or label_name.startswith('$'):
            try:
                # Extract number from strings like 00, Bounty 00
                import re
                match = re.search(r'$(\d+)', label_name)
                if match:
                    return int(match.group(1))
            except:
                pass
    
    # Try to extract from title
    import re
    match = re.search(r'$(\d+)', title)
    if match:
        return int(match.group(1))
    
    return 50  # Default bounty amount

def scan_repo(owner, repo):
    bounties = []
    try:
        url = 'https://api.github.com/search/issues'
        # Search for issues with bounty-related keywords
        params = {
            'q': f'repo:{owner}/{repo} {BOUNTY_LABELS[0]}',
            'state': 'open',
            'per_page': 100,
            'sort': 'updated',
            'order': 'desc'
        }
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {GITHUB_TOKEN}',
            'User-Agent': 'BountyHunter/1.0'
        }
        
        r = requests.get(url, params=params, headers=headers, timeout=30)
        
        if r.status_code == 200:
            data = r.json()
            items = data.get('items', [])
            
            for item in items:
                labels = item.get('labels', [])
                
                # Filter by bounty label
                if has_bounty_label(labels):
                    amount = extract_amount(labels, item.get('title', ''))
                    
                    bounties.append({
                        'number': item['number'],
                        'title': item['title'],
                        'url': item['html_url'],
                        'amount': amount,
                        'labels': [l.get('name') for l in labels],
                        'created_at': item.get('created_at'),
                        'updated_at': item.get('updated_at'),
                        'comments': item.get('comments', 0),
                        'repo': f'{owner}/{repo}'
                    })
            
            if bounties:
                log(f'Found {len(bounties)} bounties in {owner}/{repo}')
        
        time.sleep(1)
        
    except Exception as e:
        log(f'Error scanning {owner}/{repo}: {str(e)}')
    
    return bounties

def main():
    log('=== Bounty Hunter Scan Started ===')
    all_b = []
    
    for owner, repo in TARGET_REPOS:
        all_b.extend(scan_repo(owner, repo))
    
    total = sum(b['amount'] for b in all_b)
    
    state = {
        'known_bounties': all_b,
        'last_scan': datetime.now().isoformat(),
        'total_value': total,
        'total_count': len(all_b)
    }
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
    
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f'{BOUNTY_DIR}/bounties_{ts}.json', 'w') as f:
        json.dump({
            'scan_time': datetime.now().isoformat(),
            'total_bounties': len(all_b),
            'total_value': total,
            'avg_bounty': total / len(all_b) if all_b else 0,
            'bounties': all_b
        }, f, indent=2)
    
    log(f'=== Scan Complete: {len(all_b)} bounties, ${total} total ===')
    return len(all_b), total

if __name__ == '__main__':
    main()
