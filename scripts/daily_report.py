#!/usr/bin/env python3
"""
日报生成与发送系统 - Hermes 兼容版
使用统一邮件模板，专业样式
"""

import os
import sys
import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# 配置路径
WORKSPACE = Path("/home/ubuntu/.hermes")
MEMORY_DIR = WORKSPACE / "memory"
SKILL_DIR = WORKSPACE / "skills" / "daily-report"
CONFIG_FILE = SKILL_DIR / "config.json"

def load_config():
    """加载邮件配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_quanquan_work(date):
    """获取工作记录"""
    memory_file = MEMORY_DIR / f"{date.strftime('%Y-%m-%d')}.md"
    
    if not memory_file.exists():
        return ['今日暂无工作记录']
    
    content = memory_file.read_text(encoding='utf-8')
    work_items = []
    
    # 匹配完成事项
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('- [x]') or line.startswith('- [X]'):
            item = line.replace('- [x]', '').replace('- [X]', '').strip()
            if item:
                work_items.append(item)
    
    return work_items if work_items else ['今日暂无工作记录']

def generate_daily_report():
    """生成日报内容"""
    today = datetime.now()
    date_str = today.strftime("%Y年%m月%d日")
    
    work_items = get_quanquan_work(today)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>每日工作日报 - {date_str}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; margin-bottom: 10px; }}
        .date {{ color: #999; margin-bottom: 30px; }}
        .section {{ margin-bottom: 25px; }}
        .section-title {{ font-size: 18px; font-weight: 600; color: #667eea; margin-bottom: 15px; }}
        .work-list {{ list-style: none; padding: 0; }}
        .work-list li {{ padding: 10px 15px; background: #f8f9fa; border-radius: 8px; margin-bottom: 8px; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 每日工作日报</h1>
        <div class="date">{date_str} · 权权管家指挥中心</div>
        
        <div class="section">
            <div class="section-title">🦞 今日工作</div>
            <ul class="work-list">
                {''.join([f'<li>{item}</li>' for item in work_items])}
            </ul>
        </div>
        
        <div class="footer">
            🦞 权权管家指挥中心自动生成<br>
            发送时间: {today.strftime("%H:%M:%S")}
        </div>
    </div>
</body>
</html>"""
    
    return html

def send_email(subject, html_content):
    """发送邮件"""
    config = load_config()
    email_config = config.get('email', {})
    
    smtp_server = email_config.get('smtp_server', 'smtp.qq.com')
    smtp_port = email_config.get('smtp_port', 465)
    smtp_user = email_config.get('username', '')
    smtp_pass = email_config.get('password', '')
    to_email = email_config.get('to', ['569545015@qq.com'])
    
    if not smtp_pass:
        print("⚠️ 邮件密码未配置，跳过发送")
        return False
    
    msg = MIMEMultipart('alternative')
    msg['From'] = f"权权管家 <{smtp_user}>"
    msg['To'] = ', '.join(to_email) if isinstance(to_email, list) else to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email if isinstance(to_email, list) else [to_email], msg.as_string())
        server.quit()
        print(f"✅ 日报已发送: {subject}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def main():
    print(f"📋 日报生成器 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    report = generate_daily_report()
    
    # 保存到文件
    report_file = WORKSPACE / "cron" / "logs" / f"daily-report-{datetime.now().strftime('%Y%m%d')}.html"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ 日报已保存: {report_file}")
    
    # 发送邮件
    if '--send' in sys.argv:
        send_email(f"📋 每日工作日报 - {datetime.now().strftime('%Y年%m月%d日')}", report)

if __name__ == "__main__":
    main()
