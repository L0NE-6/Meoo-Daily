<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# 🍀 Meoo Daily

**Meoo（秒悟）每日登录积分 · 多账号单文件脚本 · JSONL 结果回读**

> 当前版本：**v1.0.1**（2026-11-24） · 认证方式：网页 Cookie

**[简体中文](README.md)** · [English](docs/README.en.md) · [繁體中文](docs/README.zh-Hant.md) · [日本語](docs/README.ja.md) · [한국어](docs/README.ko.md) · [Português (BR)](docs/README.pt-BR.md)

Cookie 登录 · 每日积分 · 多账号隔离 · JSONL 报告 · 可选推送 · 青龙 · Actions

<img src="https://img.shields.io/badge/Version-v1.0.1-2ea44f?style=for-the-badge&logo=github" alt="Version v1.0.1" />
<img src="https://img.shields.io/github/stars/L0NE-6/Meoo-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" alt="Stars" />
<img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+" />
<img src="https://img.shields.io/badge/Qinglong-ready-4EAA25?style=for-the-badge" alt="Qinglong" />
<img src="https://img.shields.io/badge/GitHub%20Actions-supported-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="GitHub Actions" />

[边界](#policy) · [速览](#overview) · [协议](#protocol) · [凭据](#credentials) · [快速开始](#quickstart) · [青龙](#qinglong) · [Actions](#actions) · [CLI](#cli) · [结果码](#result-codes) · [成功判据](#success) · [测试](#tests) · [目录](#layout) · [版本](#release) · [赞赏](#donate) · [反馈](#feedback)

</div>

---

<a id="policy"></a>
## 🚫 使用边界

### 🚫 使用边界与转载声明

> [!IMPORTANT]
> **官方版本永久免费。** 未经作者书面许可，禁止付费包装、搬运引流、冒充作者，或使用作者身份与二维码制造官方授权假象。

禁止把本仓库、脚本、部署说明或 Release 包装成付费资源、内部版、独家版、会员权益、收费课程、代部署服务或包更新服务；禁止搬运到其他账号、群组、频道、网盘、电商和付费平台进行涨粉、截流、倒卖或引流；禁止删除作者与版权信息后冒充原创。

官方仓库和 Release 始终免费。第三方以“下载费、激活费、内部版、代部署、会员门槛”等名义收费，均与作者无关。完整规则见 **[NOTICE.md](NOTICE.md)**。

---

---

<a id="overview"></a>
## ✨ 30 秒速览

### ✨ 30 秒速览

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

---

<a id="what"></a>
## 🧭 这是什么

---

<a id="protocol"></a>
## 🔁 协议与回读

### 核心请求

```http
GET https://meoo.com/api/mc/entitlement/init
Cookie: <完整网页 Cookie>
```

该 GET 请求本身就会触发每日登录积分发放。`--status` 只改变报告文案，不是只读请求。

### 回读字段

| 字段 | 验收用途 |
| :--- | :--- |
| `dailyLoginGranted` | 本次是否实际发放积分 |
| `dailyLoginGrantAmount` | 本次发放数量 |
| `dailyLoginSkipReason` | 未发放原因，`ALREADY_GRANTED_TODAY` 表示今日已领 |
| `dailyLoginBalanceAfter` | 请求后的积分余额 |

HTTP 200 不等于成功，脚本会继续校验 `data` 与上述业务字段。

### 🧠 每日登录领取原理

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

---

<a id="credentials"></a>
## 🔑 凭据与账号

| 变量 | 必需 | 说明 |
| :--- | :---: | :--- |
| `MEOO_COOKIES` | 二选一 | 多账号，每行 `备注|Cookie`，优先于单账号变量 |
| `MEOO_COOKIE` | 二选一 | 单账号完整网页 Cookie |

Cookie 属于账号级凭据。脚本输出会对 Cookie 做脱敏，README、日志与 Issue 中也不应出现完整值。

---

<a id="quickstart"></a>
## 🚀 快速开始

---

<a id="qinglong"></a>
## 🐧 青龙面板

### 🚀 部署方式一：青龙面板

| 步骤 | 操作 |
| :---: | :--- |
| **1. 上传脚本** | 把 `meoo_daily.py` 上传到青龙脚本目录。 |
| **2. 设置变量** | 在青龙环境变量中新增 `MEOO_COOKIES` 或 `MEOO_COOKIE`。 |
| **3. 新建任务** | 命令填 `task meoo_daily.py`，建议每天执行一次，例如 `17 7 * * *`。 |
| **4. 安装依赖** | 在青龙依赖管理中安装 `requests`，或执行 `pip3 install requests`。 |

> 使用 `task meoo_daily.py` 让青龙注入面板环境变量。直接调用裸 `python meoo_daily.py` 可能读不到你在面板里配置的变量。

---

---

<a id="actions"></a>
## ☁️ GitHub Actions

### ☁️ 部署方式二：GitHub Actions

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

---

<a id="cli"></a>
## ⌨️ CLI 与环境变量

### 🔧 环境变量

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

#### 本地运行

```powershell
python -m pip install -r requirements.txt
$env:MEOO_COOKIE = "sessionid=REPLACE_WITH_COOKIE; other_cookie=REPLACE_ME"
python .\meoo_daily.py
python .\meoo_daily.py --status
```

---

---

<a id="result-codes"></a>
## 🚦 结果码

| 结果 | 含义 | 退出码影响 |
| :--- | :--- | :--- |
| `GRANTED` | 本次实际发放每日积分 | 成功 |
| `ALREADY_GRANTED` | 今日已领取，属于中性成功 | 成功 |
| `FAILED` | 登录失效、风控、响应契约异常或网络失败 | 失败 |
| 配置错误 | Cookie 格式不合法或账号为空 | 退出码 2 |

---

<a id="success"></a>
## ✅ 成功判据

只有 `dailyLoginGranted=true` 或 `dailyLoginSkipReason=ALREADY_GRANTED_TODAY` 且业务信封完整时才算当日成功。

### ✅ 成功判据

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

---

<a id="tests"></a>
## 🧪 测试

```powershell
$env:PYTHONUTF8 = "1"
python -m unittest discover -s tests -v
python -m py_compile meoo_daily.py
python -m ruff check .
```

单测验证账号解析、响应分类、脱敏与推送分支，不替代真实 Cookie 的服务端积分回读。

### 🧪 测试与质量检查

```powershell
python -m unittest discover -s tests -v
python -m compileall -q .
python -m ruff check .
```

测试全部使用 fake session，不访问真实 Meoo 接口，也不需要真实 Cookie。

---

---

<a id="design"></a>
## 🧱 设计原则

- 单文件自包含，运行期仅依赖 `requests`。
- 账号逐条隔离，单账号失败不阻断其他账号。
- 以业务字段判定成功，不以 HTTP 200 冒充到账。
- 输出固定为 JSONL，便于青龙、Actions 与本地日志处理。
- Cookie 不进入报告、异常文本或推送正文。

---

<a id="privacy"></a>
## 🔒 隐私与安全

凭据、状态文件、日志与运行缓存都属于账号级数据。仓库和 Issue 中只保留脱敏片段。

### 🔒 隐私说明

本仓库不包含账号、手机号、Token、Cookie、JWT 或本机认证文件。Cookie 只通过环境变量、青龙变量或 GitHub Secrets 注入。

请勿提交：

- 真实 Cookie、Token 或认证文件；
- 运行日志、报告和包含真实账号信息的截图；
- `.env`、`auth.json`、`login_result.json` 等本地凭据文件。

`.gitignore` 已覆盖常见运行文件，但提交前仍应人工检查。

---

---

<a id="layout"></a>
## 📁 目录结构

### 📁 目录结构

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

---

<a id="release"></a>
## 📦 版本与发布

当前标签为 `v1.0.1`。发布包应只包含脚本、README、文档、许可证与依赖清单，不带 Cookie、缓存或日志。

### 📦 版本

- 当前版本：`v1.0.1`
- 首次独立发布：2026-11-23
- 后续实质更新遵循语义化版本，并保留独立变更记录。

---

---

<a id="disclaimer"></a>
## ⚠️ 免责声明

仓库内容用于账号持有人维护自身权益。使用前应确认账号、服务条款与所在地规则；作者不对账号限制、接口变化、网络失败或第三方部署造成的损失作出保证。

完整展示与转载规则见 [NOTICE.md](NOTICE.md)。

---

<a id="donate"></a>
## ☕ 赞赏码

### 支持与投喂

如果这个项目节省了你的时间，可以扫码支持维护。赞赏完全自愿，不影响代码、文档与 Issue 处理。

<div align="center">
<table>
<tr>
<td align="center"><strong>微信赞赏码</strong><br /><img src="assets/donate-wechat.png" width="260" alt="微信赞赏码" /></td>
<td align="center"><strong>支付宝赞赏码</strong><br /><img src="assets/donate-alipay.jpg" width="260" alt="支付宝赞赏码" /></td>
</tr>
</table>
</div>

---

<a id="feedback"></a>
## 💬 反馈与 Star History

### 反馈与贡献

- [提交 Issue](https://github.com/L0NE-6/Meoo-Daily/issues)
- [提交 Pull Request](https://github.com/L0NE-6/Meoo-Daily/pulls)
- [查看更新日志](CHANGELOG.md)

反馈请附脱敏日志、复现步骤、运行环境与实际结果。不要贴 Token、Cookie、JWT、手机号或运行状态文件。

<a href="https://star-history.com/#L0NE-6/Meoo-Daily&Date">
  <img src="https://api.star-history.com/svg?repos=L0NE-6/Meoo-Daily&type=Date" alt="Meoo-Daily Star History" />
</a>
