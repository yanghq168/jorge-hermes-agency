#!/usr/bin/env python3
"""
统一配置加载器 - Hermes 兼容版
"""
import os
import yaml
from pathlib import Path

CONFIG_PATH = Path("/home/ubuntu/.hermes/cron/config/config.yaml")

def get_config():
    """加载完整配置"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}

def get_mail_config():
    """加载邮件配置"""
    config = get_config()
    return config.get('mail', {})

def get_hermes_config():
    """加载 Hermes 配置"""
    config = get_config()
    return config.get('hermes', {})

def get_paths_config():
    """加载路径配置"""
    config = get_config()
    return config.get('paths', {})
