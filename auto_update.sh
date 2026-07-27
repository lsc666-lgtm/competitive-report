#!/bin/bash
# 竞品分析日报 · 每日自动更新 & 部署
# 1. 更新SNS数据 → 2. 复制HTML → 3. 推送到GitHub Pages

REPO_DIR="$HOME/competitive-report-repo"
REPORT_FILE="$HOME/Desktop/竞品分析日报.html"
LOG="/tmp/competitive_report_deploy.log"

echo "===== $(date) =====" >> "$LOG"

echo "[1/3] 更新SNS数据..." | tee -a "$LOG"
cd "$HOME/Desktop/我的/skill-codex/SNS爬虫/技术开发" && bash update.sh >> "$LOG" 2>&1

echo "[2/3] 复制到Git仓库..." | tee -a "$LOG"
cp "$REPORT_FILE" "$REPO_DIR/index.html"

echo "[3/3] 提交并推送到GitHub..." | tee -a "$LOG"
cd "$REPO_DIR"
git add index.html
git commit -m "每日更新 $(date '+%Y/%m/%d')" >> "$LOG" 2>&1
git push origin main >> "$LOG" 2>&1

echo "✅ 完成！" | tee -a "$LOG"
echo "🌐 https://lsc666-lgtm.github.io/competitive-report/" | tee -a "$LOG"
