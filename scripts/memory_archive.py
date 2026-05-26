#!/usr/bin/env python3
"""
记忆归档脚本 - Hermes 兼容版
每周日凌晨归档旧记忆文件
"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/ubuntu/.hermes")
MEMORY_DIR = WORKSPACE / "memory"
ARCHIVE_DIR = WORKSPACE / "archive"

def archive_old_memories():
    """归档7天前的记忆文件"""
    ARCHIVE_DIR.mkdir(exist_ok=True)
    
    cutoff = datetime.now() - timedelta(days=7)
    archived = []
    
    for mem_file in MEMORY_DIR.glob("*.md"):
        try:
            mtime = datetime.fromtimestamp(mem_file.stat().st_mtime)
            if mtime < cutoff:
                # 压缩归档
                archive_name = ARCHIVE_DIR / f"{mem_file.stem}.md.gz"
                with open(mem_file, 'rb') as f_in:
                    with gzip.open(archive_name, 'wb') as f_out:
                        f_out.write(f_in.read())
                
                # 删除原文件
                mem_file.unlink()
                archived.append(archive_name.name)
        except Exception as e:
            print(f"⚠️ 归档失败 {mem_file}: {e}")
    
    return archived

def main():
    print(f"📦 记忆归档 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    archived = archive_old_memories()
    
    if archived:
        print(f"✅ 已归档 {len(archived)} 个文件:")
        for name in archived:
            print(f"  - {name}")
    else:
        print("ℹ️ 没有需要归档的文件")
    
    print("\n" + "=" * 60)
    print(f"归档完成 - {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
