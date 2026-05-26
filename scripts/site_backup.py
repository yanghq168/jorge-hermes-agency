#!/usr/bin/env python3
"""
全站备份脚本 - Hermes 兼容版
备份内容：
1. crontab配置
2. 环境变量/PATH
3. 关键配置文件
4. 推送到GitHub (jorge-hermes-agency)

注意：skills目录由 skill-backup.sh 单独备份到 jorge-hermes-skills
"""

import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/ubuntu/.hermes")
BACKUP_DIR = WORKSPACE / "backup"
GITHUB_REPO = "https://github.com/yanghq168/jorge-hermes-agency"

def run_cmd(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=60)
        return r.stdout.strip(), r.returncode
    except Exception as e:
        return str(e), 1

def backup_crontab():
    """备份crontab"""
    stdout, rc = run_cmd("crontab -l")
    if rc != 0:
        return False, "无法读取crontab"
    
    backup_file = BACKUP_DIR / "crontab.txt"
    with open(backup_file, 'w') as f:
        f.write(stdout + "\n")
    return True, backup_file

def backup_env():
    """备份环境变量"""
    env_file = BACKUP_DIR / "environment.txt"
    lines = [
        f"# 备份时间: {datetime.now().isoformat()}",
        f"PATH={os.environ.get('PATH', '')}",
        f"HOME={os.environ.get('HOME', '')}",
        f"USER={os.environ.get('USER', '')}",
    ]
    with open(env_file, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    return True, env_file

def backup_configs():
    """备份关键配置文件"""
    config_dir = BACKUP_DIR / "configs"
    config_dir.mkdir(exist_ok=True)
    
    files_to_backup = [
        (WORKSPACE / "cron" / "config" / "config.yaml", "cron-config.yaml"),
        (Path.home() / ".ssh" / "config", "ssh-config.txt"),
    ]
    
    backed_up = []
    for src, dst_name in files_to_backup:
        if src.exists():
            dst = config_dir / dst_name
            shutil.copy2(src, dst)
            backed_up.append(dst_name)
    
    return True, backed_up

def push_to_github():
    """推送到GitHub仓库"""
    git_dir = BACKUP_DIR / ".git"
    
    # 初始化git仓库（如果不存在）
    if not git_dir.exists():
        run_cmd("git init", cwd=BACKUP_DIR)
        run_cmd(f"git remote add origin {GITHUB_REPO}", cwd=BACKUP_DIR)
    
    # 配置git
    run_cmd('git config user.name "权权养的虾"', cwd=BACKUP_DIR)
    run_cmd('git config user.email "569545015@qq.com"', cwd=BACKUP_DIR)
    
    # 添加、提交、推送
    run_cmd("git add -A", cwd=BACKUP_DIR)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    stdout, rc = run_cmd(f'git commit -m "自动备份: {timestamp}"', cwd=BACKUP_DIR)
    
    if rc != 0 and "nothing to commit" in stdout:
        return True, "无变更，无需推送"
    
    stdout, rc = run_cmd("git push -u origin main --force", cwd=BACKUP_DIR)
    if rc != 0:
        # 尝试master分支
        stdout, rc = run_cmd("git push -u origin master --force", cwd=BACKUP_DIR)
    
    if rc == 0:
        return True, f"已推送到 {GITHUB_REPO}"
    else:
        return False, f"推送失败: {stdout[:200]}"

def main():
    print(f"💾 全站备份 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # 备份crontab
    ok, result = backup_crontab()
    if ok:
        print(f"✅ crontab已备份: {result}")
    else:
        print(f"⚠️ crontab备份失败: {result}")
    
    # 备份环境变量
    ok, result = backup_env()
    if ok:
        print(f"✅ 环境变量已备份: {result}")
    else:
        print(f"⚠️ 环境变量备份失败: {result}")
    
    # 备份配置文件
    ok, result = backup_configs()
    if ok:
        print(f"✅ 配置文件已备份: {', '.join(result)}")
    else:
        print(f"⚠️ 配置文件备份失败: {result}")
    
    # 推送到GitHub
    print("\n📤 推送到GitHub...")
    ok, result = push_to_github()
    if ok:
        print(f"✅ {result}")
    else:
        print(f"⚠️ {result}")
    
    print("\n" + "=" * 60)
    print(f"备份完成 - {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
