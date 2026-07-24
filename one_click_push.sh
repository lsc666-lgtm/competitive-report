#!/bin/bash
# ================================================
# 竞品分析日报 · 一键部署到GitHub Pages
# 运行前请先添加SSH密钥到GitHub
# ================================================

set -e

REPO_DIR="$HOME/competitive-report-repo"
REPORT_FILE="$HOME/Desktop/竞品分析日报.html"

echo "📦 竞品分析日报 · 部署工具"
echo "========================"

# Step 1: Check SSH
echo ""
echo "[1/4] 检查SSH连接..."
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "  ✅ SSH连接成功"
else
    echo "  ⚠️ SSH需要配置"
    echo "  请添加密钥: cat ~/.ssh/competitive_report.pub"
    echo "  然后到: https://github.com/settings/ssh/new"
    exit 1
fi

# Step 2: Copy report
echo "[2/4] 复制日报文件..."
cp "$REPORT_FILE" "$REPO_DIR/index.html"
echo "  ✅ index.html 已更新"

# Step 3: Commit
echo "[3/4] 提交到Git..."
cd "$REPO_DIR"
git add index.html
git commit -m "每日更新: $(date '+%Y/%m/%d %H:%M')" 2>/dev/null || echo "  ⏭️ 无新变更"

# Step 4: Push
echo "[4/4] 推送到GitHub..."
git push origin main
echo "  ✅ 推送成功！"
echo ""
echo "🌐 访问地址: https://lsc666-lgtm.github.io/competitive-report/"
