#!/usr/bin/env python3
"""
飞书日报推送脚本 (示例 - 去除Webhook URL)
使用前: cp send_feishu_report.example.py send_feishu_report.py
         将 WEBHOOK_URL 替换为你的实际地址
"""
import json, os, re, sys
from datetime import datetime, date

# ===== 配置区 =====
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_URL_HERE"
REPORT_PATH = os.path.expanduser("~/Desktop/竞品分析日报.html")

# ... 完整代码请参考本地 ~/Desktop/send_feishu_report.py
print("请复制 ~/Desktop/send_feishu_report.py 到本目录")
