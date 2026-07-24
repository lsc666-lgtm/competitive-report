#!/bin/bash
# 快速同步：将桌面最新报告推送到GitHub Pages
REPO_DIR="$HOME/competitive-report-repo"
cp "$HOME/Desktop/竞品分析日报.html" "$REPO_DIR/index.html"
cd "$REPO_DIR"
git add index.html
git commit -m "更新 $(date '+%m/%d %H:%M')"
git push origin main
echo "🌐 https://lsc666-lgtm.github.io/competitive-report/"
