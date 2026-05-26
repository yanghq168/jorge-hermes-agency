#!/usr/bin/env python3
"""
性能数据采集脚本 - Hermes 兼容版
每4小时采集一次系统性能数据
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/ubuntu/.hermes")
METRICS_DIR = WORKSPACE / "memory" / "metrics"

def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except Exception as e:
        return str(e)

def collect_metrics():
    """采集系统性能数据"""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "cpu": {},
        "memory": {},
        "disk": {},
    }
    
    # CPU
    stdout = run_cmd("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1")
    try:
        metrics["cpu"]["usage"] = float(stdout)
    except:
        metrics["cpu"]["usage"] = -1
    
    # 内存
    stdout = run_cmd("free | grep Mem | awk '{printf \"%.1f\", $3/$2 * 100.0}'")
    try:
        metrics["memory"]["usage"] = float(stdout)
    except:
        metrics["memory"]["usage"] = -1
    
    # 磁盘
    stdout = run_cmd("df -h / | tail -1 | awk '{print $5}' | tr -d '%'")
    try:
        metrics["disk"]["usage"] = int(stdout)
    except:
        metrics["disk"]["usage"] = -1
    
    return metrics

def main():
    print(f"📊 性能数据采集 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    
    metrics = collect_metrics()
    
    # 保存到文件
    metrics_file = METRICS_DIR / f"{datetime.now().strftime('%Y%m%d')}.json"
    
    existing = []
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            existing = json.load(f)
    
    existing.append(metrics)
    
    with open(metrics_file, 'w') as f:
        json.dump(existing, f, indent=2)
    
    print(f"✅ 性能数据已保存: {metrics_file}")
    print(f"   CPU: {metrics['cpu']['usage']}%")
    print(f"   内存: {metrics['memory']['usage']}%")
    print(f"   磁盘: {metrics['disk']['usage']}%")

if __name__ == "__main__":
    main()
