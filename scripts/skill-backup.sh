#!/bin/bash
# 技能备份脚本 - Hermes 兼容版
# 备份 ~/.hermes/skills/ 到 jorge-hermes-skills 仓库

set -e

SKILLS_DIR="/home/ubuntu/.hermes/skills"
BACKUP_DIR="/home/ubuntu/.hermes/skills-backup"
GITHUB_REPO="https://github.com/yanghq168/jorge-hermes-skills"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "📦 技能备份 - ${TIMESTAMP}"
echo "============================================================"

# 创建备份目录
mkdir -p "${BACKUP_DIR}"

# 复制skills目录内容（排除.git）
rsync -av --delete --exclude='.git' "${SKILLS_DIR}/" "${BACKUP_DIR}/" 2>/dev/null || cp -r "${SKILLS_DIR}"/* "${BACKUP_DIR}/" 2>/dev/null

echo "✅ skills目录已同步到备份目录"

# 初始化git仓库（如果不存在）
cd "${BACKUP_DIR}"
if [ ! -d ".git" ]; then
    git init
    git remote add origin "${GITHUB_REPO}"
fi

# 配置git
git config user.name "权权养的虾"
git config user.email "569545015@qq.com"

# 添加、提交、推送
git add -A
git commit -m "自动备份: ${TIMESTAMP}" || echo "无变更或提交失败"
git push -u origin main --force 2>/dev/null || git push -u origin master --force 2>/dev/null || echo "⚠️ 推送失败，请检查GitHub仓库权限"

echo "============================================================"
echo "✅ 技能备份完成 - $(date '+%H:%M:%S')"
echo "📁 仓库: ${GITHUB_REPO}"
