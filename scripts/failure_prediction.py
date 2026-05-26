#!/usr/bin/env python3
"""
故障预测脚本 - Hermes 兼容版
每天14:00检查系统趋势
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/ubuntu/.hermes")
METRICS_DIR = WORKSPACE / "memory" / "metrics"

def analyze_trends():
    """分析性能趋势"""
    today = datetime.now()
    
    # 读取最近7天的数据
    metrics = []
    for i in range(7):
        date = today - timedelta(days=i)
        metrics_file = METRICS_DIR / f"{date.strftime('%Y%m%d')}.json"
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                data = json.load(f)
                metrics.extend(data)
    
    if not metrics:
        return "无数据"
    
    # 计算平均值
    cpu_avg = sum(m['cpu']['usage'] for m in metrics if m['cpu']['usage'] >= 0) / len(metrics)
    mem_avg = sum(m['memory']['usage'] for m in metrics if m['memory']['usage'] >= 0) / len(metrics)
    disk_avg = sum(m['disk']['usage'] for m in metrics if m['disk']['usage'] >= 0) / len(metrics)
    
    # 预测
    predictions = []
    if cpu_avg > 80:
        predictions.append("CPU使用率持续偏高，建议优化")
    if mem_avg > 80:
        predictions.append("内存使用率持续偏高，建议扩容")
    if disk_avg > 80:
        predictions.append("磁盘使用率持续偏高，建议清理")
    
    return predictions if predictions else ["系统状态良好"]

def main():
    print(f"🔮 故障预测 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    predictions = analyze_trends()
    
    for pred in predictions:
        print(f"  • {pred}")
    
    print("\n" + "=" * 60)
    print(f"预测完成 - {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
