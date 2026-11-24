<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# 🍀 Meoo Daily

**Meoo（秒悟）每日登录积分 · 多账号单文件脚本 · JSONL 结果回读**

> 当前版本：**v1.0.1**（2026-11-24） · 由 L0NE-6 原创维护的 Meoo 每日登录积分领取仓库

[简体中文](README.md) · [English](docs/README.en.md) · [繁體中文](docs/README.zh-Hant.md) · [日本語](docs/README.ja.md) · [한국어](docs/README.ko.md) · [Português (BR)](docs/README.pt-BR.md)

🪪 Cookie 登录 · 🎁 每日积分 · 👥 多账号隔离 · 🧾 JSONL 报告 · 📢 可选推送 · 🐧 青龙友好 · ☁️ GitHub Actions

<img src="https://img.shields.io/badge/Version-v1.0.1-2ea44f?style=for-the-badge&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/Meoo-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20%E9%9D%92%E9%BE%99-4EAA25?style=for-the-badge&logo=linux&logoColor=white" />
<img src="https://img.shields.io/badge/Deploy-%E9%9D%92%E9%BE%99%20%7C%20GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" />

[✨ 速览](#-30-秒速览) · [🧠 领取原理](#-每日登录领取原理) · [🚀 青龙部署](#-部署方式一青龙面板) · [☁️ Actions](#-部署方式二github-actions) · [🔧 环境变量](#-环境变量) · [🚫 使用边界](#usage-policy) · [✦ 星轨](#-星轨-star-trail)

</div>

---

<a id="usage-policy"></a>
## 🚫 使用边界与转载声明

> [!IMPORTANT]
> **官方版本永久免费。** 未经作者书面许可，禁止付费包装、搬运引流、冒充作者，或使用作者身份与二维码制造官方授权假象。

禁止把本仓库、脚本、部署说明或 Release 包装成付费资源、内部版、独家版、会员权益、收费课程、代部署服务或包更新服务；禁止搬运到其他账号、群组、频道、网盘、电商和付费平台进行涨粉、截流、倒卖或引流；禁止删除作者与版权信息后冒充原创。

官方仓库和 Release 始终免费。第三方以“下载费、激活费、内部版、代部署、会员门槛”等名义收费，均与作者无关。完整规则见 **[NOTICE.md](NOTICE.md)**。

---

## ✨ 30 秒速览

| 维度 | 说明 |
| :--- | :--- |
| **做什么** | 调用 Meoo 每日登录权益接口，领取当日登录积分并报告余额。 |
| **输入** | 一个或多个 Meoo 网页登录 Cookie；可选 PushPlus、企业微信通知配置。 |
| **输出** | 每账号一行 JSON，最后一行 `SUMMARY` JSON；任何结果都不输出 Cookie。 |
| **部署** | Windows / Linux / 青龙面板 / GitHub Actions。 |
| **依赖** | Python 3.9+；运行时仅依赖 `requests`。 |
| **成功判据** | `dailyLoginGranted=true` 为 `GRANTED`；`dailyLoginSkipReason=ALREADY_GRANTED_TODAY` 为 `ALREADY_GRANTED`；两者都算当日成功。 |

> [!WARNING]
> **`--status` 会触发领取。** 正常模式与 `--status` 都会发送同一个 `GET /api/mc/entitlement/init`；该 GET 本身就是发放每日登录积分的动作。`--status` 只改变报告中的 `mode` 和文案，不是只读查询。

---

## 🧠 每日登录领取原理

L0NE-6 原创维护的脚本使用 Meoo 每日登录接口：

```http
GET https://meoo.com/api/mc/entitlement/init
Cookie: <完整网页 Cookie>
```

响应中的关键字段：

| 字段 | 含义 |
| :--- | :--- |
| `dailyLoginGranted` | 本次请求是否实际发放了每日登录积分。 |
| `dailyLoginGrantAmount` | 本次发放数量。 |
| `dailyLoginSkipReason` | 未发放时的原因；`ALREADY_GRANTED_TODAY` 表示今天已经领取。 |
| `dailyLoginBalanceAfter` | 请求后的积分余额。 |

脚本不会把 HTTP 200 直接当作成功，而是继续检查 `data` 对象和上述业务字段。重复运行由服务端返回的 `ALREADY_GRANTED_TODAY` 处理，脚本将它识别为中性成功。

---

## 🚀 部署方式一：青龙面板

| 步骤 | 操作 |
| :---: | :--- |
| **1. 上传脚本** | 把 `meoo_daily.py` 上传到青龙脚本目录。 |
| **2. 设置变量** | 在青龙环境变量中新增 `MEOO_COOKIES` 或 `MEOO_COOKIE`。 |
| **3. 新建任务** | 命令填 `task meoo_daily.py`，建议每天执行一次，例如 `17 7 * * *`。 |
| **4. 安装依赖** | 在青龙依赖管理中安装 `requests`，或执行 `pip3 install requests`。 |

> 使用 `task meoo_daily.py` 让青龙注入面板环境变量。直接调用裸 `python meoo_daily.py` 可能读不到你在面板里配置的变量。

---

## ☁️ 部署方式二：GitHub Actions

仓库已内置 [`.github/workflows/meoo.yml`](.github/workflows/meoo.yml)：

- `push` 到 `main`：安装依赖并运行单元测试、`compileall` 与 Ruff；
- `schedule`：每天执行一次 `python meoo_daily.py`；
- `workflow_dispatch`：支持手动运行测试和领取；
- 控制台 JSONL 会转换为合法 JSON 数组 `meoo-report.json`，并保留原始 `meoo-report.jsonl`；即使脚本失败也会尝试上传 artifact。
- 未配置 `MEOO_COOKIES` / `MEOO_COOKIE` 时，定时领取会输出明确 SKIPPED notice 并成功结束；配置凭据后，脚本异常仍会保持失败状态。

使用步骤：

1. Fork / Import 本仓库到你自己的账号；
2. 打开 **Settings → Secrets and variables → Actions**；
3. 按需添加 `MEOO_COOKIES` 或 `MEOO_COOKIE`；
4. 在 Actions 页面手动运行一次，确认 Secrets 和报告；
5. 在 `meoo-report` artifact 中查看每账号 JSON 与 `SUMMARY`。

GitHub 的 `schedule` 使用 UTC，并且可能延迟。当前工作流设置为 `17 23 * * *`，对应北京时间每天约 `07:17`，只安排一次。

---

## 🔧 环境变量

| 变量 | 必填 | 说明 |
| :--- | :---: | :--- |
| `MEOO_COOKIES` | ⬜ | 多账号。每行一个 `备注\|Cookie`；非空时优先于 `MEOO_COOKIE`。 |
| `MEOO_COOKIE` | ⬜ | 单账号完整网页 Cookie。 |
| `PUSHPLUS_TOKEN` | ⬜ | 可选，PushPlus 推送令牌。 |
| `QYWX_WEBHOOK` | ⬜ | 可选，企业微信机器人完整 URL 或仅 webhook key。 |

`MEOO_COOKIES` 示例：

```text
主号|sessionid=REPLACE_WITH_COOKIE; other_cookie=REPLACE_ME
小号|sessionid=REPLACE_WITH_ANOTHER_COOKIE; other_cookie=REPLACE_ME
```

`MEOO_COOKIE` 示例：

```text
sessionid=REPLACE_WITH_COOKIE; other_cookie=REPLACE_ME
```

> Cookie 等同于登录凭据。示例只含占位符，请勿把真实 Cookie 写入仓库、Issue、日志或截图。

### 本地运行

```powershell
python -m pip install -r requirements.txt
$env:MEOO_COOKIE = "sessionid=REPLACE_WITH_COOKIE; other_cookie=REPLACE_ME"
python .\meoo_daily.py
python .\meoo_daily.py --status
```

---

## ✅ 成功判据

| 结果 | 是否成功 | 含义 |
| :--- | :---: | :--- |
| `GRANTED` | ✅ | 本次实际发放积分，报告数量与余额。 |
| `ALREADY_GRANTED` | ✅ | 今天已领取，服务端返回 `ALREADY_GRANTED_TODAY`。 |
| `AUTH_EXPIRED` | ❌ | HTTP 401/403，Cookie 已失效。 |
| `REDIRECT` | ❌ | 请求被重定向，通常表示登录态无效。 |
| `NOT_GRANTED` | ❌ | 未发放，且未返回“今日已领”原因。 |
| `NETWORK_ERROR` / `HTTP_ERROR` / `INVALID_JSON` / `INVALID_RESPONSE` | ❌ | 网络、HTTP 或响应结构异常。 |
| `CONFIG_ERROR` | ❌ | 没有配置 Cookie，或账号格式错误。 |

最终 `SUMMARY.ok=true` 的条件是：至少有一个账号，且没有账号失败。单测通过只证明代码路径和错误分类，不代表某个真实账号当天已经领取成功。

---

## 🧪 测试与质量检查

```powershell
python -m unittest discover -s tests -v
python -m compileall -q .
python -m ruff check .
```

测试全部使用 fake session，不访问真实 Meoo 接口，也不需要真实 Cookie。

---

## 🔒 隐私说明

本仓库不包含账号、手机号、Token、Cookie、JWT 或本机认证文件。Cookie 只通过环境变量、青龙变量或 GitHub Secrets 注入。

请勿提交：

- 真实 Cookie、Token 或认证文件；
- 运行日志、报告和包含真实账号信息的截图；
- `.env`、`auth.json`、`login_result.json` 等本地凭据文件。

`.gitignore` 已覆盖常见运行文件，但提交前仍应人工检查。

---

## 📁 目录结构

```text
Meoo-Daily/
├── .github/workflows/meoo.yml
├── assets/
│   ├── donate-alipay.jpg
│   └── donate-wechat.png
├── docs/
│   ├── README.en.md
│   ├── README.zh-Hant.md
│   ├── README.ja.md
│   ├── README.ko.md
│   └── README.pt-BR.md
├── tests/test_meoo_daily.py
├── CHANGELOG.md
├── LICENSE
├── NOTICE.md
├── THIRD_PARTY_NOTICES.md
├── meoo_daily.py
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

## 📦 版本

- 当前版本：`v1.0.1`
- 首次独立发布：2026-11-23
- 后续实质更新遵循语义化版本，并保留独立变更记录。

---

## ⚠️ 免责声明

本项目用于个人学习和合法的个人自动化。Meoo 的活动规则、接口、积分数量和账号资格由平台决定；使用前请确认对应服务条款，并自行承担账号、网络和活动变化带来的风险。

---

## ☕ 支持与投喂

脚本完全免费，无广告、无功能限制。如果它确实帮你省了时间，欢迎自愿赞赏；不影响任何功能，也不影响 Issue 响应。

<p align="center">
  <img src="assets/donate-wechat.png" width="260" alt="微信赞赏码" />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/donate-alipay.jpg" width="260" alt="支付宝收款码" />
</p>
<p align="center"><sub>💚 微信支付（左） &nbsp;|&nbsp; 💙 支付宝（右）</sub></p>

> 收款码仅用于向作者自愿赞赏。任何第三方以代下载、代部署、内部资源或会员群为由收费，均与作者无关。

---

## 💬 反馈与贡献

- [提交 Issue](https://github.com/L0NE-6/Meoo-Daily/issues)
- [发起 Pull Request](https://github.com/L0NE-6/Meoo-Daily/pulls)

反馈问题时，请附上脱敏后的结果 JSON、运行环境和复现步骤。不要上传真实 Cookie、手机号或完整账号日志。

---

## ✦ 星轨 Star Trail

<a href="https://star-history.com/#L0NE-6/Meoo-Daily&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=L0NE-6/Meoo-Daily&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=L0NE-6/Meoo-Daily&type=Date" />
    <img alt="Meoo Daily Star Trail" src="https://api.star-history.com/svg?repos=L0NE-6/Meoo-Daily&type=Date" />
  </picture>
</a>

---

<div align="center">
  <sub>L0NE-6 · DAILY SIGNAL &nbsp;|&nbsp; 点个 <b>Star</b>，让下一轮自动化有迹可循 ✨</sub>
</div>
