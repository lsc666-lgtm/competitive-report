#!/bin/bash
# 竞品分析日报 · 一键设置每日自动更新

CRON_LINE="0 10 * * * bash \$HOME/competitive-report-repo/auto_update.sh > /tmp/competitive_cron.log 2>&1"

# Add to crontab
(crontab -l 2>/dev/null | grep -v "auto_update.sh"; echo "$CRON_LINE") | crontab -

echo "✅ 每日自动更新已设置！"
echo "⏰ 每天 10:00 自动执行："
echo "   1. 更新SNS社媒数据"
echo "   2. 同步到 GitHub Pages"
echo ""
echo "📋 查看日志：cat /tmp/competitive_cron.log"
echo "🌐 访问地址：https://lsc666-lgtm.github.io/competitive-report/"
