#!/bin/bash
# Agency备份脚本
# 备份 ~/.hermes/agency-backup/ 到 jorge-hermes-agency 仓库

set -e

AGENCY_DIR="/home/ubuntu/.hermes/agency-backup"
TOKEN=$(grep -o 'x-access-token:[^@]*' "$HOME/.git-credentials" | sed 's/x-access-token://')
GITHUB_REPO="https://x-access-token:${TOKEN}@github.com/yanghq168/jorge-hermes-agency.git"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "📦 Agency备份 - ${TIMESTAMP}"
echo "============================================================"

cd "$AGENCY_DIR"

# 配置git
git config user.name "权权养的虾"
git config user.email "569545015@qq.com"

# 添加、提交、推送
git add -A
git commit -m "Agency备份: ${TIMESTAMP}" || echo "无变更或提交失败"
git push -u origin main --force 2>/dev/null || git push -u origin master --force 2>/dev/null || echo "⚠️ 推送失败，请检查GitHub仓库权限"

echo "============================================================"
echo "✅ Agency备份完成 - $(date '+%H:%M:%S')"
echo "📁 仓库: $GITHUB_REPO"