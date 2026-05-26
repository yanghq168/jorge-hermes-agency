#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音图文【围炉家常】每日内容生成器 - Hermes 兼容版
每晚22:30运行，生成抖音图文
发送邮件至 569545015@qq.com
发件人：权权管家（抖音）
"""

import random
import smtplib
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

# ==================== 主题轮换库 ====================
TOPICS = [
    "亲戚借钱不还的人情冷暖",
    "兄弟姐妹长大后为何疏远",
    "父母偏心造成的家庭裂痕",
    "婆媳关系的相处智慧",
    "过年走亲戚的虚伪与真心",
    "远亲不如近邻的现实感悟",
    "老人赡养推诿的子女百态",
    "家族群里那些让人心寒的事",
    "穷在闹市无人问，富在深山有远亲",
    "人走茶凉，亲戚关系的凉薄时刻",
]

# ==================== 内容模板 ====================
DOUYIN_TEMPLATE = """📱 抖音图文 #{topic}

🎵 BGM建议：《岁月神偷》《父亲写的散文诗》《时间都去哪儿了》

📸 配图提示词：
{image_prompt}

✍️ 文案：

{content}

🏷️ 话题标签：
#家庭 #亲戚 #人情冷暖 #围炉家常 #权权管家

---
🦞 权权管家 | 抖音
"""

def get_today_topic():
    """根据日期选择今日主题"""
    day_of_year = datetime.now().timetuple().tm_yday
    topic_index = day_of_year % len(TOPICS)
    return TOPICS[topic_index]

def generate_content(topic):
    """生成抖音文案"""
    # 生成尖锐、简短、扎心的文案
    contents = [
        f"""{topic}

你以为的血浓于水
不过是利益面前的遮羞布

别不信
穷一次你就知道了""",
        f"""{topic}

小时候以为亲戚是最亲的人
长大后才发现
有些亲戚连陌生人都不如

你同意吗？""",
        f"""{topic}

不是人心变了
是利益让亲情现了原形

评论区说说你的故事""",
    ]
    
    content = random.choice(contents)
    
    # 配图提示词
    image_prompt = "A vertical 9:16 image about family relationships, emotional, Chinese style, warm lighting, realistic photography, people silhouette, nostalgic atmosphere --ar 9:16 --v 6"
    
    return DOUYIN_TEMPLATE.format(
        topic=topic,
        image_prompt=image_prompt,
        content=content
    )

def send_email(subject, body):
    """发送邮件"""
    if not SMTP_PASS:
        print("⚠️ 邮件密码未配置，跳过发送")
        return False
    
    msg = MIMEMultipart()
    msg['From'] = f"权权管家（抖音） <{SMTP_USER}>"
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
    print(f"🎵 抖音图文生成器 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    topic = get_today_topic()
    print(f"\n📌 今日主题: {topic}")
    
    content = generate_content(topic)
    
    print(f"\n{'='*60}")
    print(content)
    print(f"{'='*60}")
    
    # 发送邮件
    send_email(f"【抖音】{topic}", content)

if __name__ == "__main__":
    main()
