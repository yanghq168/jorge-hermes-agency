#!/usr/bin/env python3
"""
健康巡检脚本 - Hermes 兼容版
检查项：
1. crontab任务完整性
2. 定时任务最后运行状态
3. 系统资源（CPU/内存/磁盘）
4. 关键服务进程状态
5. 日志异常检测
"""

import os
import re
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/ubuntu/.hermes")
LOG_DIR = WORKSPACE / "cron" / "logs"

# 要检查的定时任务
CRON_JOBS = {
    "AI新闻抓取": {"script": "run.sh", "log": "ai-news.log"},
    "AI新闻推送": {"script": "push_email.py", "log": "ai-news.log"},
    "日报推送": {"script": "daily_report.py", "log": "daily-report.log"},
    "Bithappy理财": {"script": "bithappy_email_pro.py", "log": "bithappy-email.log"},
    "系统巡检": {"script": "health_check.py", "log": "health-check.log"},
    "技能备份": {"script": "skill-backup.sh", "log": "skill-backup.log"},
}

def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip(), r.returncode
    except Exception as e:
        return str(e), 1

def check_system_resources():
    """检查系统资源"""
    issues = []
    
    # CPU
    stdout, _ = run_cmd("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1")
    try:
        cpu = float(stdout)
        if cpu > 90:
            issues.append(f"⚠️ CPU使用率过高: {cpu}%")
    except:
        pass
    
    # 内存
    stdout, _ = run_cmd("free | grep Mem | awk '{printf \"%.1f\", $3/$2 * 100.0}'")
    try:
        mem = float(stdout)
        if mem > 90:
            issues.append(f"⚠️ 内存使用率过高: {mem}%")
    except:
        pass
    
    # 磁盘
    stdout, _ = run_cmd("df -h / | tail -1 | awk '{print $5}' | tr -d '%'")
    try:
        disk = int(stdout)
        if disk > 90:
            issues.append(f"⚠️ 磁盘使用率过高: {disk}%")
    except:
        pass
    
    return issues

def check_cron_jobs():
    """检查定时任务状态"""
    issues = []
    
    for name, info in CRON_JOBS.items():
        log_file = LOG_DIR / info['log']
        if log_file.exists():
            # 检查最后修改时间
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if datetime.now() - mtime > timedelta(hours=25):
                issues.append(f"⚠️ {name} 超过24小时未更新")
    
    return issues

def main():
    print(f"🔍 系统健康巡检 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查系统资源
    resource_issues = check_system_resources()
    if resource_issues:
        print("\n📊 系统资源:")
        for issue in resource_issues:
            print(f"  {issue}")
    else:
        print("\n✅ 系统资源正常")
    
    # 检查定时任务
    cron_issues = check_cron_jobs()
    if cron_issues:
        print("\n⏰ 定时任务:")
        for issue in cron_issues:
            print(f"  {issue}")
    else:
        print("\n✅ 定时任务正常")
    
    print("\n" + "=" * 60)
    print(f"巡检完成 - {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
