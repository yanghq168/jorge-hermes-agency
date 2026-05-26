#!/usr/bin/env python3
"""
Bithappy 理财监控 Pro 版
- SQLite 数据库存储历史数据
- APY 趋势分析
- 异常告警（暴跌、下架）
- 专业 HTML 邮件模板
"""

import subprocess
import time
import re
import json
import os
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional, Tuple
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# 邮件配置
# ==================== 邮件配置 ====================
# 优先从 config.yaml 读取，否则使用默认值
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
TO_EMAIL = "569545015@qq.com"

# 数据库路径
DB_PATH = os.path.expanduser("~/.openclaw/workspace/data/bithappy.db")
DATA_DIR = os.path.dirname(DB_PATH)


@dataclass
class Product:
    """理财产品数据类"""
    coin: str
    platform: str
    apy: float
    time_left: str
    fetched_at: datetime = None
    
    def __post_init__(self):
        if self.fetched_at is None:
            self.fetched_at = datetime.now()
    
    @property
    def unique_key(self) -> str:
        """唯一标识：币种+平台"""
        return f"{self.coin}@{self.platform}"


class Database:
    """SQLite 数据库管理"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin TEXT NOT NULL,
                platform TEXT NOT NULL,
                apy REAL NOT NULL,
                time_left TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(coin, platform, fetched_at)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_key ON products(coin, platform)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fetched_at ON products(fetched_at)')
        
        conn.commit()
        conn.close()
        print(f"✅ 数据库初始化完成: {self.db_path}")
    
    def save_products(self, products: List[Product]):
        """保存产品数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for p in products:
            try:
                cursor.execute('''
                    INSERT INTO products (coin, platform, apy, time_left, fetched_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (p.coin, p.platform, p.apy, p.time_left, p.fetched_at))
                saved_count += 1
            except sqlite3.IntegrityError:
                pass
        
        conn.commit()
        conn.close()
        print(f"✅ 保存 {saved_count} 条产品数据")
        return saved_count
    
    def get_previous_products(self, hours: int = 24) -> List[Product]:
        """获取N小时前的产品数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        target_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT coin, platform, apy, time_left, fetched_at
            FROM products
            WHERE fetched_at <= ?
            ORDER BY fetched_at DESC
            LIMIT 100
        ''', (target_time,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [Product(r[0], r[1], r[2], r[3], datetime.fromisoformat(r[4])) for r in rows]
    
    def get_stats(self) -> dict:
        """获取数据库统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*), COUNT(DISTINCT DATE(fetched_at)), MIN(fetched_at), MAX(fetched_at) FROM products')
        row = cursor.fetchone()
        conn.close()
        
        return {
            'total_records': row[0] or 0,
            'total_snapshots': row[1] or 0,
            'first_record': row[2] or 'N/A',
            'last_record': row[3] or 'N/A'
        }


def send_email(subject, text_content, html_content=None):
    """发送邮件（同时支持纯文本和HTML）"""
    msg = MIMEMultipart('alternative')
    from_header = Header('权权养的虾（投资）', 'utf-8')
    from_header.append(f'<{SMTP_USER}>', 'ascii')
    msg['From'] = from_header
    msg['To'] = TO_EMAIL
    msg['Subject'] = Header(subject, 'utf-8')
    
    # 纯文本版本
    msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
    
    # HTML版本
    if html_content:
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [TO_EMAIL], msg.as_string())
        server.quit()
        print(f"✅ 邮件已发送至 {TO_EMAIL}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False


def run_browser():
    """运行浏览器抓取数据（支持多tab）"""
    AGENT_BROWSER = '/root/.local/share/pnpm/agent-browser'
    CDP_ARGS = ['--cdp', '9222']
    
    # 设置完整 PATH，确保能找到 node
    env = os.environ.copy()
    env['PATH'] = '/root/.nvm/versions/node/v22.22.0/bin:' + env.get('PATH', '')
    
    result = subprocess.run(
        [AGENT_BROWSER] + CDP_ARGS + ['open', 'https://bithappy.xyz/products'],
        capture_output=True, text=True, env=env
    )
    if result.returncode != 0:
        print(f"❌ 打开页面失败: {result.stderr}")
        return None
    
    time.sleep(3)
    
    # 抓取"理财们" tab 数据（默认显示）
    result = subprocess.run(
        [AGENT_BROWSER] + CDP_ARGS + ['snapshot'],
        capture_output=True, text=True, env=env
    )
    snapshot_licai = result.stdout
    print(f"📊 理财们 tab 抓取完成")
    
    # 点击"猪脚饭们" tab
    result = subprocess.run(
        [AGENT_BROWSER] + CDP_ARGS + ['find', 'text', '猪脚饭们', 'click'],
        capture_output=True, text=True, env=env
    )
    if result.returncode == 0:
        time.sleep(3)
        result = subprocess.run(
            [AGENT_BROWSER] + CDP_ARGS + ['snapshot'],
            capture_output=True, text=True, env=env
        )
        snapshot_zhujiao = result.stdout
        print(f"📊 猪脚饭们 tab 抓取完成")
        # 合并两个 tab 的快照
        snapshot = snapshot_licai + "\n" + snapshot_zhujiao
    else:
        print(f"⚠️ 点击猪脚饭们失败，仅使用理财们数据: {result.stderr}")
        snapshot = snapshot_licai
    
    subprocess.run([AGENT_BROWSER] + CDP_ARGS + ['close'], capture_output=True, env=env)
    return snapshot


def extract_products(text) -> List[Product]:
    """从快照文本提取产品信息（适配新版表格结构）"""
    products = []
    static_texts = re.findall(r'- StaticText "([^"]+)"', text)
    
    # 已知的稳定币列表（用于验证）
    known_coins = {'USDE', 'USDC', 'USDT', 'USDG', 'GHO', 'RLUSD', 'USDGO', 'USD1', 'USDD', 'BYUSDT', 'WBTC', 'WETH'}
    
    i = 0
    while i < len(static_texts):
        text_item = static_texts[i]
        
        # 匹配 APY 格式: 16.54%, 10.00% 等
        if re.match(r'^\d+\.\d+%$', text_item):
            apy_str = text_item
            apy = float(apy_str.replace('%', ''))
            
            # 往前找 platform 和 coin
            if i >= 2:
                platform = static_texts[i-1]
                coin = static_texts[i-2]
                
                # 验证：coin 应该是大写字母/单词，platform 不应该是表头关键词
                if coin in ['预期年化收益', '币种', '平台', '操作']:
                    i += 1
                    continue
                if platform in ['预期年化收益', '币种', '平台', '操作']:
                    i += 1
                    continue
                
                # 找 time_left（结束时间/期限）
                time_left = None
                for j in range(i+1, min(i+10, len(static_texts))):
                    next_text = static_texts[j]
                    # 跳过收益数字（如 $10k 收益, 1.65k）
                    if next_text.startswith('$') or re.match(r'^\d+\.?\d*k$', next_text):
                        continue
                    if '无固定' in next_text or '剩余' in next_text:
                        time_left = next_text
                        break
                    elif next_text in ['长期', '短期']:
                        time_left = next_text
                        break
                
                if time_left is None:
                    time_left = '长期'
                
                products.append(Product(coin, platform, apy, time_left))
        
        i += 1
    
    # 去重
    seen = set()
    unique_products = []
    for p in products:
        key = p.unique_key
        if key not in seen:
            seen.add(key)
            unique_products.append(p)
    
    return unique_products


def analyze_trends(db: Database, current_products: List[Product]) -> Tuple[List[dict], List[Product], List[Product]]:
    """分析趋势：APY变化、新产品、下架产品"""
    prev_products = db.get_previous_products(hours=24)
    
    # 去重：同一个产品只保留最新的记录
    prev_dict = {}
    for p in sorted(prev_products, key=lambda x: x.fetched_at):
        prev_dict[p.unique_key] = p
    
    current_dict = {p.unique_key: p for p in current_products}
    
    apy_changes = []
    new_products = []
    removed_products = []
    
    for curr in current_products:
        key = curr.unique_key
        if key in prev_dict:
            prev = prev_dict[key]
            change = curr.apy - prev.apy
            if abs(change) >= 1.0:
                apy_changes.append({
                    'product': curr,
                    'old_apy': prev.apy,
                    'new_apy': curr.apy,
                    'change': change,
                })
    
    for curr in current_products:
        if curr.unique_key not in prev_dict:
            new_products.append(curr)
    
    for prev in prev_dict.values():
        if prev.unique_key not in current_dict:
            removed_products.append(prev)
    
    return apy_changes, new_products, removed_products


def generate_html_report(db: Database, products: List[Product]) -> str:
    """生成专业的 HTML 邮件报告"""
    if not products:
        return "<p>⚠️ 未能获取到理财数据</p>"
    
    sorted_products = sorted(products, key=lambda x: x.apy, reverse=True)
    apy_changes, new_products, removed_products = analyze_trends(db, products)
    stats = db.get_stats()
    
    has_alerts = bool(apy_changes or new_products or removed_products)
    
    high_yield = [p for p in sorted_products if p.apy >= 15]
    medium_yield = [p for p in sorted_products if 8 <= p.apy < 15]
    low_yield = [p for p in sorted_products if p.apy < 8]
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -0.5px; }}
        .header .meta {{ margin-top: 12px; opacity: 0.9; font-size: 15px; }}
        .content {{ padding: 30px; }}
        .alert-box {{ background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); border-left: 5px solid #f39c12; padding: 24px; border-radius: 12px; margin-bottom: 28px; }}
        .alert-box.critical {{ background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); border-left-color: #e74c3c; }}
        .section {{ background: #f8f9fa; padding: 24px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #e9ecef; }}
        .section-title {{ font-size: 18px; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; color: #2c3e50; }}
        table {{ width: 100%; border-collapse: separate; border-spacing: 0; font-size: 14px; background: white; border-radius: 8px; overflow: hidden; }}
        th {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 12px; text-align: left; font-weight: 600; }}
        td {{ padding: 14px 12px; border-bottom: 1px solid #e9ecef; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover {{ background: #f8f9fa; }}
        .apy-high {{ color: #e74c3c; font-weight: 700; font-size: 16px; }}
        .apy-medium {{ color: #e67e22; font-weight: 700; font-size: 16px; }}
        .apy-low {{ color: #27ae60; font-weight: 700; font-size: 16px; }}
        .change-up {{ color: #27ae60; font-weight: 700; }}
        .change-down {{ color: #e74c3c; font-weight: 700; }}
        .badge {{ display: inline-block; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; margin: 4px; }}
        .badge-new {{ background: #d4edda; color: #155724; }}
        .badge-removed {{ background: #f8d7da; color: #721c24; }}
        .badge-change-up {{ background: #d4edda; color: #155724; }}
        .badge-change-down {{ background: #f8d7da; color: #721c24; }}
        .stats-bar {{ display: flex; justify-content: center; gap: 30px; margin-top: 30px; padding-top: 24px; border-top: 2px solid #e9ecef; font-size: 13px; color: #6c757d; }}
        .risk-notice {{ background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); padding: 20px; border-radius: 12px; margin-top: 24px; font-size: 13px; color: #856404; text-align: center; border: 1px solid #f39c12; }}
        .footer {{ text-align: center; padding: 24px; color: #adb5bd; font-size: 12px; background: #f8f9fa; }}
        @media (max-width: 600px) {{ body {{ padding: 10px; }} .header {{ padding: 30px 20px; }} .content {{ padding: 20px; }} .section {{ padding: 16px; }} th, td {{ padding: 10px 8px; font-size: 13px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 理财看板 Pro</h1>
            <div class="meta">⏰ {datetime.now().strftime('%Y年%m月%d日 %H:%M')} · 📈 {len(products)} 个产品 · 🔥 实时追踪</div>
        </div>
        <div class="content">"""
    
    # 变动提醒
    if has_alerts:
        alert_class = "alert-box critical" if apy_changes else "alert-box"
        html += f'<div class="{alert_class}">\n'
        html += '<div class="section-title">🚨 重要变动提醒</div>\n'
        
        if apy_changes:
            html += '<p style="margin-bottom:16px;font-weight:600;">📉 APY 显著变化</p>\n'
            html += '<table>\n<tr><th>产品</th><th>变动</th><th>当前 APY</th></tr>\n'
            for change in sorted(apy_changes, key=lambda x: abs(x['change']), reverse=True)[:5]:
                direction_class = "change-up" if change['change'] > 0 else "change-down"
                direction_icon = "📈 +" if change['change'] > 0 else "📉 "
                html += f'<tr><td><strong>{change["product"].coin}</strong><br><small>{change["product"].platform}</small></td>'
                html += f'<td class="{direction_class}">{direction_icon}{change["change"]:.2f}%</td>'
                html += f'<td class="apy-high">{change["new_apy"]:.2f}%</td></tr>\n'
            html += '</table>\n'
        
        if new_products:
            html += '<p style="margin:20px 0 12px;font-weight:600;">✨ 新上线产品</p>\n'
            for p in new_products[:5]:
                html += f'<span class="badge badge-new">{p.coin} @ {p.platform} - {p.apy:.1f}%</span>\n'
        
        if removed_products:
            html += '<p style="margin:20px 0 12px;font-weight:600;">❌ 已下架产品</p>\n'
            for p in removed_products[:5]:
                html += f'<span class="badge badge-removed">{p.coin} @ {p.platform}</span>\n'
        
        html += '</div>\n'
    
    # 产品列表
    def render_section(title, icon, products, apy_class):
        if not products:
            return ""
        html = '<div class="section">\n'
        html += f'<div class="section-title">{icon} {title}</div>\n'
        html += '<table>\n<tr><th>币种</th><th>平台</th><th>APY</th><th>期限</th></tr>\n'
        for p in products[:8]:
            html += f'<tr><td><strong>{p.coin}</strong></td><td>{p.platform}</td>'
            html += f'<td class="{apy_class}">{p.apy:.2f}%</td><td>{p.time_left}</td></tr>\n'
        html += '</table>\n</div>\n'
        return html
    
    html += render_section("高收益推荐 (≥15%)", "🔥", high_yield, "apy-high")
    html += render_section("稳健收益 (8-15%)", "💎", medium_yield, "apy-medium")
    html += render_section("保守收益 (<8%)", "🛡️", low_yield, "apy-low")
    
    # 页脚
    html += f'''
            <div class="stats-bar">
                <div>📊 已追踪 <strong>{stats['total_snapshots']}</strong> 天</div>
                <div>📝 共 <strong>{stats['total_records']}</strong> 条记录</div>
                <div>🤖 {datetime.now().strftime('%H:%M')} 自动生成</div>
            </div>
            <div class="risk-notice">
                ⚠️ <strong>风险提示：</strong>以上仅为信息整理，不构成投资建议。DeFi 理财有风险，投资需谨慎！
            </div>
        </div>
        <div class="footer">
            🦞 理财监控 Pro · 数据驱动投资决策
        </div>
    </div>
</body>
</html>'''
    
    return html


def generate_text_report(db: Database, products: List[Product]) -> str:
    """生成纯文本报告（邮件备用）"""
    if not products:
        return "⚠️ 未能获取到理财数据"
    
    sorted_products = sorted(products, key=lambda x: x.apy, reverse=True)
    apy_changes, new_products, removed_products = analyze_trends(db, products)
    stats = db.get_stats()
    
    lines = []
    lines.append("📊 理财看板 Pro 报告")
    lines.append(f"⏰ 数据时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"📈 共发现 {len(products)} 个理财产品\n")
    
    has_alerts = apy_changes or new_products or removed_products
    if has_alerts:
        lines.append("🚨 【重要变动提醒】")
        lines.append("-" * 40)
        
        if apy_changes:
            lines.append("\n📉 APY 显著变化:")
            for change in sorted(apy_changes, key=lambda x: abs(x['change']), reverse=True):
                direction = "📈 上涨" if change['change'] > 0 else "📉 下跌"
                lines.append(f"  {direction} {change['product'].coin} @ {change['product'].platform}")
                lines.append(f"     {change['old_apy']:.2f}% → {change['new_apy']:.2f}% ({change['change']:+.2f}%)")
        
        if new_products:
            lines.append("\n✨ 新上线产品:")
            for p in new_products:
                lines.append(f"  • {p.coin} @ {p.platform} - {p.apy}%")
        
        if removed_products:
            lines.append("\n❌ 已下架产品:")
            for p in removed_products:
                lines.append(f"  • {p.coin} @ {p.platform} (上次 APY: {p.apy}%)")
        
        lines.append("\n" + "-" * 40 + "\n")
    
    high_yield = [p for p in sorted_products if p.apy >= 15]
    if high_yield:
        lines.append("🔥 高收益推荐 (≥15%)")
        for p in high_yield[:5]:
            lines.append(f"  • {p.coin} @ {p.platform} - {p.apy}% ({p.time_left})")
        lines.append("")
    
    medium_yield = [p for p in sorted_products if 8 <= p.apy < 15]
    if medium_yield:
        lines.append("💎 稳健收益 (8-15%)")
        for p in medium_yield[:5]:
            lines.append(f"  • {p.coin} @ {p.platform} - {p.apy}% ({p.time_left})")
        lines.append("")
    
    low_yield = [p for p in sorted_products if p.apy < 8]
    if low_yield:
        lines.append("🛡️ 保守收益 (<8%)")
        for p in low_yield[:5]:
            lines.append(f"  • {p.coin} @ {p.platform} - {p.apy}% ({p.time_left})")
        lines.append("")
    
    lines.append("-" * 40)
    lines.append(f"📊 已追踪 {stats['total_snapshots']} 天，共 {stats['total_records']} 条记录")
    lines.append("\n⚠️ 风险提示: 以上仅为信息整理，不构成投资建议。DeFi理财有风险！")
    
    return '\n'.join(lines)


def export_to_json(products: List[Product]):
    """导出 JSON 备份"""
    json_path = os.path.join(DATA_DIR, f"bithappy_data_{datetime.now().strftime('%Y-%m-%d')}.json")
    data = {
        'fetch_time': datetime.now().isoformat(),
        'products': [{'coin': p.coin, 'platform': p.platform, 'apy': p.apy, 'time_left': p.time_left} for p in products]
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON 备份: {json_path}")


def main():
    print("🦞 理财监控 Pro 启动...")
    
    db = Database()
    
    snapshot = run_browser()
    if not snapshot:
        print("❌ 数据抓取失败")
        send_email("🦞 理财报告获取失败", "无法抓取理财数据，请检查数据源是否可用。", None)
        return
    
    products = extract_products(snapshot)
    if not products:
        print("❌ 未解析到产品数据")
        return
    
    print(f"✅ 抓取到 {len(products)} 个产品")
    
    db.save_products(products)
    export_to_json(products)
    
    text_report = generate_text_report(db, products)
    html_report = generate_html_report(db, products)
    
    print("\n" + text_report[:500] + "...")
    
    has_alerts = "【重要变动提醒】" in text_report
    alert_emoji = "🚨" if has_alerts else "📊"
    subject = f"{alert_emoji} 理财报告 {datetime.now().strftime('%m-%d %H:%M')}"
    
    send_email(subject, text_report, html_report)
    print("\n✅ 完成")


if __name__ == '__main__':
    main()
