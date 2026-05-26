#!/usr/bin/env python3
"""
心跳检查脚本 - Hermes 兼容版
每30分钟检查系统状态
"""

import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/ubuntu/.hermes")
LOG_FILE = WORKSPACE / "cron" / "logs" / "heartbeat.log"

def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return r.stdout.strip(), r.returncode
    except Exception as e:
        return str(e), 1

def check_services():
    """检查关键服务"""
    services = {
        "hermes-agent": "pgrep -f hermes-agent",
    }
    
    results = {}
    for name, cmd in services.items():
        stdout, rc = run_cmd(cmd)
        results[name] = rc == 0
    
    return results

def main():
    print(f"💓 心跳检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    services = check_services()
    
    status = "✅ 正常" if all(services.values()) else "⚠️ 异常"
    
    log_line = f"{datetime.now().isoformat()} - {status}"
    
    with open(LOG_FILE, 'a') as f:
        f.write(log_line + "\n")
    
    print(f"状态: {status}")
    for name, ok in services.items():
        print(f"  {name}: {'✅' if ok else '❌'}")

if __name__ == "__main__":
    main()
