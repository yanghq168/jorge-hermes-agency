#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日小红书旅游攻略生成器 - Hermes 兼容版
每晚23:00运行，随机选国内景点，生成小红书文案
发送邮件至 569545015@qq.com
发件人：权权养的虾（小红书）
"""

import random
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ==================== 邮件配置 ====================
try:
    from config_loader import get_mail_config
    _mail = get_mail_config()
    SMTP_SERVER = _mail.get('smtp_server', 'smtp.qq.com')
    SMTP_PORT = _mail.get('smtp_port', 465)
    SMTP_USER = _mail.get('smtp_user', '569545015@qq.com')
    SMTP_PASS = _mail.get('smtp_pass', '')
    TO_EMAIL = _mail.get('to_email', '569545015@qq.com')
except Exception:
    SMTP_SERVER = "smtp.qq.com"
    SMTP_PORT = 465
    SMTP_USER = "569545015@qq.com"
    SMTP_PASS = ""
    TO_EMAIL = "569545015@qq.com"

# ==================== 景点库 ====================
DESTINATIONS = [
    # === 小众秘境 ===
    {"name": "沙溪古镇", "province": "云南", "days": 2, "type": "小众",
     "tags": ["茶马古道", "白族民居", "慢生活", "先锋书局"],
     "foods": ["土八碗", "地参子", "乳饼", "三道茶"],
     "highlight": "千年茶马古道上的幸存古镇，没有过度商业化"},
    {"name": "诺邓古村", "province": "云南", "days": 2, "type": "小众",
     "tags": ["千年白族村", "诺邓火腿", "盐井古道", "玉皇阁"],
     "foods": ["诺邓火腿", "井盐炒饭", "白族八大碗", "苦荞粑粑"],
     "highlight": "因《舌尖上的中国》诺邓火腿而出名的千年白族古村"},
    # ... (更多景点)
]

# ==================== 标题模板 ====================
TITLE_TEMPLATES = [
    "刚从{name}回来，后劲太大了😭",
    "{name}｜被低估的宝藏小城",
    "在{name}待了3天，不想走了",
    "{name}攻略｜本地人带路不踩雷",
    "救命！{name}也太美了吧",
    "{name}｜适合一个人发呆的地方",
    "去了{name}才知道，什么叫人间值得",
    "{name}｜小众但绝美，趁还没火快去",
]

# ==================== 内容模板 ====================
CONTENT_TEMPLATE = """📍 {name} · {province}

{title}

✨ 为什么去：
{highlight}

🗓 建议天数：{days}天

📸 必打卡：
{tags_str}

🍜 必吃美食：
{foods_str}

💡 实用Tips：
• 最佳季节：春秋两季
• 交通建议：高铁+当地包车
• 住宿推荐：古镇内民宿
• 预算参考：人均800-1500元

#{tags_hash}

🎨 海报提示词：
A beautiful travel poster of {name}, {province}, China. {highlight_en}. Warm sunset lighting, cinematic composition, watercolor illustration style, vintage travel poster aesthetic, rich colors, detailed architecture, dreamy atmosphere. --ar 3:4 --v 6

---
🦞 权权养的虾 | 每日一景
"""

def generate_post():
    """生成小红书文案"""
    dest = random.choice(DESTINATIONS)
    
    title = random.choice(TITLE_TEMPLATES).format(name=dest['name'])
    
    tags_str = '\n'.join([f"• {tag}" for tag in dest['tags']])
    foods_str = '\n'.join([f"• {food}" for food in dest['foods']])
    tags_hash = ' '.join([f"#{tag}" for tag in dest['tags'][:3]])
    
    content = CONTENT_TEMPLATE.format(
        name=dest['name'],
        province=dest['province'],
        title=title,
        highlight=dest['highlight'],
        days=dest['days'],
        tags_str=tags_str,
        foods_str=foods_str,
        tags_hash=tags_hash,
        highlight_en=dest['highlight'][:50]
    )
    
    return title, content

def send_email(subject, body):
    """发送邮件"""
    if not SMTP_PASS:
        print("⚠️ 邮件密码未配置，跳过发送")
        return False
    
    msg = MIMEMultipart()
    msg['From'] = f"权权养的虾（小红书） <{SMTP_USER}>"
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, TO_EMAIL, msg.as_string())
        server.quit()
        print(f"✅ 邮件已发送: {subject}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def main():
    print(f"🦞 小红书旅游攻略生成器 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    title, content = generate_post()
    
    print(f"\n📱 今日主题: {title}")
    print(f"\n{'='*60}")
    print(content)
    print(f"{'='*60}")
    
    # 发送邮件
    send_email(f"【小红书】{title}", content)

if __name__ == "__main__":
    main()
