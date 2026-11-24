# 🍀 Meoo Daily

**Meoo daily login credits · multi-account single-file runner · JSONL results**

[简体中文](../README.md) · [English](README.en.md) · [繁體中文](README.zh-Hant.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (BR)](README.pt-BR.md)

> [!WARNING]
> `--status` sends the same `GET /api/mc/entitlement/init` request as the normal mode. That request grants the daily login credits. `--status` changes only the report mode and wording; it is not a read-only query.

## What it does

The script calls:

```http
GET https://meoo.com/api/mc/entitlement/init
Cookie: <full browser Cookie>
```

It checks `dailyLoginGranted`, `dailyLoginSkipReason`, `dailyLoginGrantAmount`, and `dailyLoginBalanceAfter` instead of treating HTTP 200 as success.

## Quick start

```powershell
python -m pip install -r requirements.txt
$env:MEOO_COOKIE = "sessionid=REPLACE_WITH_COOKIE; other_cookie=REPLACE_ME"
python .\meoo_daily.py
```

For multiple accounts, set `MEOO_COOKIES` with one `note|Cookie` pair per line:

```text
main|sessionid=REPLACE_WITH_COOKIE
second|sessionid=REPLACE_WITH_ANOTHER_COOKIE
```

`MEOO_COOKIES` takes precedence over `MEOO_COOKIE`. Optional notification variables are `PUSHPLUS_TOKEN` and `QYWX_WEBHOOK`.

## Qinglong

1. Upload `meoo_daily.py`.
2. Add `MEOO_COOKIES` or `MEOO_COOKIE` in the environment variables panel.
3. Install `requests`.
4. Create one daily task with `task meoo_daily.py`.

## GitHub Actions

Fork or import the repository, add the Cookie as an Actions Secret, then run the workflow manually once. The included [workflow](../.github/workflows/meoo.yml) runs tests on `push`, runs the check-in once per day on `schedule`, converts the console JSONL into a JSON array, and uploads both report formats.
If no Cookie Secret is configured, the scheduled check-in is skipped with an explicit notice; once credentials are present, script failures remain failures.

## Success criteria

- `GRANTED`: credits were granted in this request.
- `ALREADY_GRANTED`: the server returned `ALREADY_GRANTED_TODAY`.
- Any auth, redirect, network, HTTP, JSON, or response-shape error makes `SUMMARY.ok` false.

## Usage and privacy

The official repository is free. Resale, paywalling, paid redeployment, impersonation, and removal of copyright notices are prohibited. See [NOTICE.md](../NOTICE.md).

Cookie values are login credentials. Keep them in environment variables or GitHub Secrets. Do not commit real Cookies, phone numbers, reports, logs, or local authentication files.

Maintained by L0NE-6.
