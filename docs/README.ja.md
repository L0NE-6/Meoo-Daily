# 🍀 Meoo Daily

**Meoo 毎日ログイン特典 · 複数アカウント対応の単一ファイルスクリプト · JSONL レポート**

[简体中文](../README.md) · [English](README.en.md) · [繁體中文](README.zh-Hant.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (BR)](README.pt-BR.md)

> [!WARNING]
> `--status` は通常モードと同じ `GET /api/mc/entitlement/init` を送信します。このリクエスト自体が毎日ログイン特典を付与します。`--status` はレポート上のモードと文言だけを変えるため、読み取り専用の確認ではありません。

## 概要

スクリプトは次のエンドポイントを呼び出します。

```http
GET https://meoo.com/api/mc/entitlement/init
Cookie: <ブラウザの完全な Cookie>
```

HTTP 200 だけでは成功と判定せず、`dailyLoginGranted`、`dailyLoginSkipReason`、`dailyLoginGrantAmount`、`dailyLoginBalanceAfter` を確認します。

## クイックスタート

```powershell
python -m pip install -r requirements.txt
$env:MEOO_COOKIE = "sessionid=REPLACE_WITH_COOKIE; other_cookie=REPLACE_ME"
python .\meoo_daily.py
```

複数アカウントでは `MEOO_COOKIES` に 1 行 1 件の `メモ|Cookie` を設定します。

```text
メイン|sessionid=REPLACE_WITH_COOKIE
サブ|sessionid=REPLACE_WITH_ANOTHER_COOKIE
```

`MEOO_COOKIES` が空でない場合は `MEOO_COOKIE` より優先されます。通知は任意で `PUSHPLUS_TOKEN` と `QYWX_WEBHOOK` に対応します。

## Qinglong

1. `meoo_daily.py` をアップロードします。
2. 環境変数に `MEOO_COOKIES` または `MEOO_COOKIE` を追加します。
3. `requests` をインストールします。
4. 1 日 1 回のタスクを作り、コマンドを `task meoo_daily.py` にします。

## GitHub Actions

リポジトリを Fork / Import し、Cookie を Actions Secret に登録して一度手動実行します。同梱の [workflow](../.github/workflows/meoo.yml) は `push` でテスト、`schedule` で 1 日 1 回の実行を行い、コンソール JSONL を JSON 配列へ変換して両形式のレポートを artifact としてアップロードします。

## 成功条件

- `GRANTED`: 今回のリクエストで特典が付与されました。
- `ALREADY_GRANTED`: サーバーが `ALREADY_GRANTED_TODAY` を返しました。
- 認証、リダイレクト、ネットワーク、HTTP、JSON、レスポンス形式のエラーがある場合、`SUMMARY.ok` は false になります。

## 利用境界とプライバシー

公式リポジトリは無料です。転売、有料化、有料代行導入、作者のなりすまし、著作権表示の削除を禁止します。詳細は [NOTICE.md](../NOTICE.md) を参照してください。

Cookie はログイン資格情報です。環境変数または GitHub Secrets に保管し、実際の Cookie、電話番号、レポート、ログ、ローカル認証ファイルをコミットしないでください。

L0NE-6 がオリジナルで保守しています。
