#!/usr/bin/env python3
"""
月报生成脚本 - Hermes 兼容版
每月最后一天自动生成月报
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/ubuntu/.hermes")
MEMORY_DIR = WORKSPACE / "memory"

def get_month_dates():
    """获取本月日期列表"""
    today = datetime.now()
    first_day = today.replace(day=1)
    if today.month == 12:
        last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    dates = []
    d = first_day
    while d <= last_day and d <= today:
        dates.append(d)
        d += timedelta(days=1)
    return dates

def get_monthly_work():
    """聚合本月工作记录"""
    all_work = []
    for date in get_month_dates():
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

def generate_monthly_report():
    """生成月报"""
    month_dates = get_month_dates()
    work_items = get_monthly_work()
    
    report = f"""# 📈 月报

**周期**: {month_dates[0].strftime('%Y年%m月%d日')} - {month_dates[-1].strftime('%Y年%m月%d日')}
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 本月完成工作

"""
    
    if work_items:
        for i, item in enumerate(work_items, 1):
            report += f"{i}. {item}\n"
    else:
        report += "本月暂无工作记录\n"
    
    report += "\n---\n🦞 权权管家指挥中心自动生成\n"
    
    return report

def main():
    print(f"📈 月报生成器 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    report = generate_monthly_report()
    
    # 保存到文件
    report_file = WORKSPACE / "cron" / "logs" / f"monthly-report-{datetime.now().strftime('%Y%m')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 月报已保存: {report_file}")
    print(f"\n{report}")

if __name__ == "__main__":
    main()
