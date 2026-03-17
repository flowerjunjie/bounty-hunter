#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import subprocess
import requests
from datetime import datetime

BOUNTY_DIR = "/root/.bounty-hunter"
WORK_DIR = "/tmp/bounty_work"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    s = f"[{ts}] {msg}"
    print(s)
    with open(os.path.join(BOUNTY_DIR, "manual_claim.log"), "a") as f:
        f.write(s + "\n")

def main():
    log("=== Manual Bounty Claim Helper ===")
    log("\nSince GitHub API has rate limits, here are the bounties to claim manually:\n")
    
    # Load state
    try:
        state_path = os.path.join(BOUNTY_DIR, "state.json")
        with open(state_path, "r") as f:
            state = json.load(f)
    except Exception as e:
        log(f"No state file found: {e}")
        return
    
    all_bounties = state.get("known_bounties", [])
    
    # Filter for high-value, easy bounties
    priority_bounties = []
    for b in all_bounties:
        if "Bounty claim" in "".join(b.get("labels", [])):
            continue
        
        title_lower = b["title"].lower()
        hard_keywords = ["performance", "memory leak", "race condition", "concurrent", "optimize"]
        if any(k in title_lower for k in hard_keywords):
            continue
        
        easy_keywords = ["test", "doc", "enable", "add", "create", "document"]
        if any(k in title_lower for k in easy_keywords):
            priority_bounties.append(b)
    
    priority_bounties.sort(key=lambda x: x.get("amount", 50), reverse=True)
    
    log(f"Found {len(priority_bounties)} priority bounties")
    log(f"\n{'='*60}")
    log("TOP 10 HIGH-VALUE EASY BOUNTIES TO CLAIM:")
    log(f"{'='*60}\n")
    
    total_value = 0
    for i, bounty in enumerate(priority_bounties[:10], 1):
        num = bounty["number"]
        title = bounty["title"]
        repo = bounty["repo"]
        amount = bounty.get("amount", 50)
        url = bounty["url"]
        total_value += amount
        
        print(f"{i}. [{repo}] #{num}")
        print(f"   Title: {title}")
        print(f"   Value: ${amount}")
        print(f"   URL: {url}")
        print()
    
    log(f"{'='*60}")
    log(f"Total potential value: ${total_value}")
    log(f"{'='*60}")
    log("\nNext steps:")
    log("1. Visit each issue URL")
    log("2. Comment: 'I'm working on this and will submit a PR shortly.'")
    log("3. Fork the repo")
    log("4. Create a branch and implement the fix")
    log("5. Open a PR with clear description")
    log(f"{'='*60}")

if __name__ == "__main__":
    main()
