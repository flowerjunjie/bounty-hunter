import json
import requests
from pathlib import Path
from datetime import datetime

def scan_and_save():
    """扫描并保存"""
    # 扫描 bounty hunter 状态
    state_file = Path("/root/.bounty-hunter/state.json")
    if state_file.exists():
        data = json.loads(state_file.read_text())
        total = data.get("total_count", 0)
        value = data.get("total_value", 0)
        
        # 创建报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "bounties": total,
            "value": value,
            "status": "scanned"
        }
        
        Path("/root/.bounty-hunter/auto_report.json").write_text(json.dumps(report, indent=2))
        print(f"✅ 扫描完成: {total} bounties, ${value}")
    
    return True

if __name__ == "__main__":
    scan_and_save()
