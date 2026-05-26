#!/usr/bin/env python3
"""
飞书推送脚本 - Hermes 兼容版
"""

import json
import urllib.request
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/ubuntu/.hermes")

def push_to_feishu(message):
    """推送消息到飞书"""
    # 这里需要配置飞书 webhook
    webhook_url = ""
    
    if not webhook_url:
        print("⚠️ 飞书 webhook 未配置")
        return False
    
    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0:
                print("✅ 飞书推送成功")
                return True
            else:
                print(f"⚠️ 飞书推送失败: {result}")
                return False
    except Exception as e:
        print(f"❌ 飞书推送错误: {e}")
        return False

def main():
    print(f"📱 飞书推送 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    message = f"🦞 权权管家日报 - {datetime.now().strftime('%Y年%m月%d日')}\n\n今日任务已完成，请查收邮件。"
    
    push_to_feishu(message)

if __name__ == "__main__":
    main()
