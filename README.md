# 📊 競品分析日報系統

> 自動爬取競品社媒數據 → 生成可視化報告 → 部署到 GitHub Pages

## 系統架構

```
SNS爬蟲 (Puppeteer/Playwright)
        ↓
  每日更新腳本 (auto_update.sh)
        ↓
  競品分析日報.html (本地桌面)
        ↓
  GitHub Pages (公開訪問)
        ↓
  團隊成員瀏覽
```

## 文件說明

| 文件 | 說明 |
|------|------|
| `index.html` | 競品分析日報主頁（每日更新） |
| `.nojekyll` | 禁用 Jekyll 處理 |
| `auto_update.sh` | 每日自動更新腳本（爬蟲→推送） |
| `push_update.sh` | 快速同步腳本（僅推送最新 HTML） |
| `one_click_push.sh` | 一鍵部署腳本（含 SSH 檢查） |
| `setup_cron.sh` | 設置每日定時任務 |

## 部署步驟

### 第一步：創建 GitHub 倉庫
1. 打開 https://github.com/new
2. 倉庫名填 `competitive-report`（或其他名稱）
3. 選擇 **Public**
4. 創建後複製倉庫地址

### 第二步：克隆倉庫到本地
```bash
git clone https://github.com/你的賬號/competitive-report.git ~/competitive-report-repo
```

### 第三步：複製系統文件
```bash
# 先備份本倉庫的所有文件
cp ~/competitive-report-repo/* ~/competitive-report-repo/

# 複製日報 HTML
cp ~/Desktop/競品分析日報.html ~/competitive-report-repo/index.html
```

### 第四步：推送並啟用 GitHub Pages
```bash
cd ~/competitive-report-repo
git add -A
git commit -m "Initial commit"
git push origin main
```

然後在 GitHub 倉庫 Settings → Pages 中：
- Source: **Deploy from a branch**
- Branch: **main** / **/(root)**
- 點 **Save**

### 第五步：設置每日自動更新
```bash
bash ~/competitive-report-repo/setup_cron.sh
```

## 🔄 每日更新流程

每天 10:00 自動執行：
1. SNS 爬蟲抓取競品最新貼文數據
2. 更新 `競品分析日報.html`
3. 同步到 GitHub Pages
4. 團隊可通過網址查看最新數據

## 🛠️ 手動操作

```bash
# 快速同步最新日報到網頁
bash ~/competitive-report-repo/push_update.sh

# 完整更新（爬蟲 + 推送）
bash auto_update.sh

# 查看更新日誌
cat /tmp/competitive_report_deploy.log
```

## 🧩 定制化指南

### 修改競品列表
編輯 `index.html` 中的 `DATA` 對象：
- `DATA.jp` — 日本競品
- `DATA.us` — 歐美競品
- `DATA.hktw` — 港台競品

### 修改營銷日曆
直接在 HTML 的 `calendar` 數組中添加或刪除事件。

### 更換 SNS 爬蟲
SNS 爬蟲位於 `~/Desktop/我的/skill-codex/SNS爬蟲/`，可根據需要替換或修改。

## 📁 本地重要文件

| 路徑 | 說明 |
|------|------|
| `~/Desktop/競品分析日報.html` | 主報告文件（編輯此文件） |
| `~/competitive-report-repo/` | GitHub Pages 本地倉庫 |
| `~/Desktop/我的/skill-codex/SNS爬蟲/` | SNS 社媒爬蟲工具 |
| `~/Desktop/send_feishu_report.py` | 飛書推送腳本（可選） |
| `/tmp/competitive_report_deploy.log` | 部署日誌 |
| `~/.ssh/competitive_report` | SSH 部署密鑰 |

## 📝 依賴

- macOS（launchd/cron 定時任務）
- Python 3（數據提取）
- Node.js（SNS 爬蟲）
- Git（版本控制）
- GitHub 賬號（Pages 託管）

---

> 如有問題或需要定制，請參考上述步驟重新部署。
