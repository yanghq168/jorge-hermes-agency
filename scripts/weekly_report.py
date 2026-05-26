#!/usr/bin/env python3
"""
周报生成脚本 - Hermes 兼容版
每周日自动生成周报
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/ubuntu/.hermes")
MEMORY_DIR = WORKSPACE / "memory"

def get_week_dates():
    """获取本周日期列表"""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return [monday + timedelta(days=i) for i in range(7)]

def get_weekly_work():
    """聚合本周工作记录"""
    all_work = []
    for date in get_week_dates():
        memory_file = MEMORY_DIR / f"{date.strftime('%Y-%m-%d')}.md"
        if memory_file.exists():
            content = memory_file.read_text(encoding='utf-8')
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('- [x]') or line.startswith('- [X]'):
                    item = line.replace('- [x]', '').replace('- [X]', '').strip()
                    if item:
                        all_work.append(item)
    return all_work

def generate_weekly_report():
    """生成周报"""
    week_dates = get_week_dates()
    work_items = get_weekly_work()
    
    report = f"""# 📊 周报

**周期**: {week_dates[0].strftime('%Y年%m月%d日')} - {week_dates[-1].strftime('%Y年%m月%d日')}
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 本周完成工作

"""
    
    if work_items:
        for i, item in enumerate(work_items, 1):
            report += f"{i}. {item}\n"
    else:
        report += "本周暂无工作记录\n"
    
    report += "\n---\n🦞 权权管家指挥中心自动生成\n"
    
    return report

def main():
    print(f"📊 周报生成器 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    report = generate_weekly_report()
    
    # 保存到文件
    report_file = WORKSPACE / "cron" / "logs" / f"weekly-report-{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 周报已保存: {report_file}")
    print(f"\n{report}")

if __name__ == "__main__":
    main()
