# 🍀 Meoo Daily

**Meoo（秒悟）每日登入積分 · 多帳號單檔腳本 · JSONL 結果**

[简体中文](../README.md) · [English](README.en.md) · [繁體中文](README.zh-Hant.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (BR)](README.pt-BR.md)

> [!WARNING]
> `--status` 與正常模式都會送出相同的 `GET /api/mc/entitlement/init` 請求，而該請求本身會發放每日登入積分。`--status` 只改變報告模式與文案，不是唯讀查詢。

## 功能

腳本呼叫：

```http
GET https://meoo.com/api/mc/entitlement/init
Cookie: <完整網頁 Cookie>
```

腳本會檢查 `dailyLoginGranted`、`dailyLoginSkipReason`、`dailyLoginGrantAmount` 與 `dailyLoginBalanceAfter`，不會把 HTTP 200 直接當成成功。

## 快速開始

```powershell
python -m pip install -r requirements.txt
$env:MEOO_COOKIE = "sessionid=REPLACE_WITH_COOKIE; other_cookie=REPLACE_ME"
python .\meoo_daily.py
```

多帳號請設定 `MEOO_COOKIES`，每行格式為 `備註|Cookie`：

```text
主號|sessionid=REPLACE_WITH_COOKIE
小號|sessionid=REPLACE_WITH_ANOTHER_COOKIE
```

`MEOO_COOKIES` 非空時優先於 `MEOO_COOKIE`。可選推送變數為 `PUSHPLUS_TOKEN` 與 `QYWX_WEBHOOK`。

## 青龍面板

1. 上傳 `meoo_daily.py`。
2. 在環境變數中新增 `MEOO_COOKIES` 或 `MEOO_COOKIE`。
3. 安裝 `requests`。
4. 建立每日一次的任務，命令使用 `task meoo_daily.py`。

## GitHub Actions

Fork / Import 倉庫後，把 Cookie 加入 Actions Secrets，並手動執行一次。內建的 [workflow](../.github/workflows/meoo.yml) 會在 `push` 時跑測試、在 `schedule` 時每天執行一次領取，將主控台 JSONL 轉成 JSON 陣列，並上傳兩種報告格式。

## 成功判據

- `GRANTED`：本次請求實際發放積分。
- `ALREADY_GRANTED`：伺服器回傳 `ALREADY_GRANTED_TODAY`。
- 驗證、重定向、網路、HTTP、JSON 或回應結構錯誤都會使 `SUMMARY.ok=false`。

## 使用邊界與隱私

官方倉庫永久免費。禁止倒賣、付費牆、收費代部署、冒充作者或刪除版權資訊。完整規則見 [NOTICE.md](../NOTICE.md)。

Cookie 等同登入憑證，只應放在環境變數或 GitHub Secrets。請勿提交真實 Cookie、手機號、報告、日誌或本機認證檔案。

由 L0NE-6 原創維護。
