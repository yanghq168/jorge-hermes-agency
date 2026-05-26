#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号【围炉家常】每日文章生成器 - Hermes 兼容版
每晚22:00运行，生成家庭人情关系主题文章
发送邮件至 569545015@qq.com
发件人：权权管家（公众号）
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

# ==================== 文章模板 ====================
ARTICLE_TEMPLATE = """# {title}

> 作者：权权管家
> 日期：{date}
> 阅读时间：5分钟

## 引言

{opening}

## 正文

{body}

## 名人语录

> {quote}

## 结语

{conclusion}

---

📌 **今日话题**：{topic}

💬 你在生活中遇到过类似的情况吗？欢迎在评论区分享你的故事。

👍 觉得有共鸣，请点个「在看」，转发给需要的人。

---

🎨 封面图提示词：
{cover_prompt}

🖼️ 文中配图提示词：
{image_prompts}

---
*权权管家 | 围炉家常*
*每晚22:00，陪你聊聊家里那些事*
"""

def get_today_topic():
    """根据日期选择今日主题"""
    day_of_year = datetime.now().timetuple().tm_yday
    topic_index = day_of_year % len(TOPICS)
    return TOPICS[topic_index]

def generate_article(topic):
    """生成文章"""
    date_str = datetime.now().strftime("%Y年%m月%d日")
    
    # 生成标题
    titles = [
        f"{topic}，我才发现真相",
        f"关于{topic}，我想说说心里话",
        f"{topic}？看完这篇文章你就懂了",
        f"{topic}，这是我听过最扎心的回答",
    ]
    title = random.choice(titles)
    
    # 生成引言
    openings = [
        f"前几天，一位读者给我留言，说起了{topic}的事。听完她的故事，我沉默了很久。",
        f"说起{topic}，相信很多人都有一肚子话想说。今天，我们就来聊聊这个话题。",
        f"{topic}，这是一个老生常谈却又永远谈不完的话题。",
    ]
    opening = random.choice(openings)
    
    # 生成正文（简化版）
    body = f"""
在这个快节奏的社会里，{topic}似乎成了很多人心中的痛。

我们总以为亲情是最牢固的纽带，却忘了人心是最难测的深渊。

{topic}，说到底，考验的不仅是感情，更是人性。

有人说，血缘关系是斩不断的。可现实告诉我们，有些亲情，比纸还薄。

{topic}，你经历过吗？
"""
    
    # 生成名人语录
    quotes = [
        "杨绛说：'世间好物不坚牢，彩云易散琉璃脆。'亲情也是如此，需要用心呵护。",
        "莫言说：'人这一辈子，最难看透的是人心，最难维系的是感情。'",
        "老舍说：'人若是看透了自己，便不会再小看别人。'",
    ]
    quote = random.choice(quotes)
    
    # 生成结语
    conclusions = [
        f"{topic}，或许我们无法改变别人，但我们可以选择做好自己。",
        f"关于{topic}，你有什么想说的？欢迎在评论区留言。",
        f"{topic}，愿我们都能在复杂的人际关系中，保持一颗善良的心。",
    ]
    conclusion = random.choice(conclusions)
    
    # 生成配图提示词
    cover_prompt = f"A warm and emotional illustration about family relationships, Chinese style, soft lighting, watercolor painting, people sitting around a table, nostalgic atmosphere --ar 16:9 --v 6"
    
    image_prompts = f"""1. 老人独自坐在窗边的背影，暖色调，油画风格
2. 一家人围坐吃饭的场景，温馨氛围，水彩画
3. 空荡荡的客厅，夕阳斜照，写实风格"""
    
    return ARTICLE_TEMPLATE.format(
        title=title,
        date=date_str,
        topic=topic,
        opening=opening,
        body=body,
        quote=quote,
        conclusion=conclusion,
        cover_prompt=cover_prompt,
        image_prompts=image_prompts
    )

def send_email(subject, body):
    """发送邮件"""
    if not SMTP_PASS:
        print("⚠️ 邮件密码未配置，跳过发送")
        return False
    
    msg = MIMEMultipart()
    msg['From'] = f"权权管家（公众号） <{SMTP_USER}>"
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
    print(f"📰 公众号文章生成器 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    topic = get_today_topic()
    print(f"\n📌 今日主题: {topic}")
    
    article = generate_article(topic)
    
    print(f"\n{'='*60}")
    print(article)
    print(f"{'='*60}")
    
    # 发送邮件
    send_email(f"【公众号】{topic}", article)

if __name__ == "__main__":
    main()
