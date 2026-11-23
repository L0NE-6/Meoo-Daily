#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Meoo（秒悟）每日登录积分领取脚本。

每日登录接口：

    GET https://meoo.com/api/mc/entitlement/init
    Cookie: <完整网页 Cookie>

响应字段：
    dailyLoginGranted
    dailyLoginGrantAmount
    dailyLoginSkipReason       # ALREADY_GRANTED_TODAY 表示今天已领
    dailyLoginBalanceAfter

重要：该 GET 请求本身就会触发每日登录积分发放，不是只读查询。
因此 --status 也会发送完全相同的 GET；它只改变报告中的 mode 字段和文案，
不能避免领取动作。

环境变量：
    MEOO_COOKIES       多账号，每行“备注|Cookie”
    MEOO_COOKIE        单账号 Cookie；MEOO_COOKIES 非空时优先使用多账号
    PUSHPLUS_TOKEN     可选，PushPlus token
    QYWX_WEBHOOK       可选，企业微信机器人完整 URL 或仅 key

PowerShell 示例：
    $env:MEOO_COOKIES = "主号|sessionid=...; other=...`n小号|sessionid=...; other=..."
    python .\meoo_daily.py
    python .\meoo_daily.py --status

输出：
    每个账号一行 JSON，最后一行 SUMMARY JSON。任何输出都不包含 Cookie。

退出码：
    0  所有账号为 GRANTED 或 ALREADY_GRANTED
    1  至少一个账号失败
    2  配置错误
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Any, Callable, Mapping, Optional, Sequence

import requests


API_URL = "https://meoo.com/api/mc/entitlement/init"
ORIGIN = "https://meoo.com"
REFERER = ORIGIN + "/"
REQUEST_TIMEOUT = 20
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/147.0.0.0 Safari/537.36"
)
ALREADY_GRANTED = "ALREADY_GRANTED_TODAY"
BASE_HEADERS = {
    "Accept": "application/json",
    "Referer": REFERER,
    "User-Agent": USER_AGENT,
}


class ConfigError(ValueError):
    """账号环境变量格式错误。"""


def emit(payload: Mapping[str, Any]) -> None:
    """输出单行 JSON。"""
    print(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str),
        flush=True,
    )


def _redact(value: Any, secrets: Sequence[str]) -> str:
    text = str(value)
    for secret in secrets:
        if secret:
            text = text.replace(secret, "[REDACTED]")
    return text


def _optional_number(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    if number.is_integer():
        return int(number)
    return number


def _result(
    account: Mapping[str, str],
    mode: str,
    result: str,
    ok: bool,
    message: str,
    *,
    http_status: Optional[int] = None,
    granted: bool = False,
    amount: Optional[float] = None,
    balance_after: Optional[float] = None,
    skip_reason: str = "",
) -> dict[str, Any]:
    return {
        "account": account.get("note", ""),
        "mode": mode,
        "result": result,
        "ok": ok,
        "message": message,
        "http_status": http_status,
        "granted": granted,
        "amount": amount,
        "balance_after": balance_after,
        "skip_reason": skip_reason,
    }


def load_accounts(env: Optional[Mapping[str, str]] = None) -> list[dict[str, str]]:
    """从 MEOO_COOKIES 或 MEOO_COOKIE 读取账号，绝不输出 Cookie。"""
    values = os.environ if env is None else env
    multi = str(values.get("MEOO_COOKIES", "") or "").strip()
    if multi:
        accounts = []
        for line_number, raw_line in enumerate(multi.splitlines(), 1):
            line = raw_line.strip()
            if not line:
                continue
            if "|" not in line:
                raise ConfigError(
                    "MEOO_COOKIES 第 %d 行格式错误，应为“备注|Cookie”"
                    % line_number
                )
            note, cookie = line.split("|", 1)
            note = note.strip()
            cookie = cookie.strip()
            if not note or not cookie:
                raise ConfigError(
                    "MEOO_COOKIES 第 %d 行的备注或 Cookie 为空" % line_number
                )
            accounts.append({"note": note, "cookie": cookie})
        if not accounts:
            raise ConfigError("MEOO_COOKIES 没有有效账号")
        return accounts

    single = str(values.get("MEOO_COOKIE", "") or "").strip()
    if single:
        return [{"note": "默认账号", "cookie": single}]
    raise ConfigError("未配置 MEOO_COOKIES 或 MEOO_COOKIE")


def make_session() -> requests.Session:
    """创建隔离的 requests.Session。"""
    session = requests.Session()
    session.trust_env = False
    session.headers.update(BASE_HEADERS)
    return session


def _request_result(
    session: requests.Session,
    cookie: str,
    account: Mapping[str, str],
    mode: str,
) -> dict[str, Any]:
    headers = {"Cookie": cookie}
    try:
        response = session.get(
            API_URL,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        return _result(
            account,
            mode,
            "NETWORK_ERROR",
            False,
            "网络请求失败：%s" % _redact(exc, [cookie]),
        )

    status = int(getattr(response, "status_code", 0) or 0)
    if status in (401, 403):
        return _result(
            account,
            mode,
            "AUTH_EXPIRED",
            False,
            "Cookie 已失效（HTTP %d）" % status,
            http_status=status,
        )
    if 300 <= status < 400:
        return _result(
            account,
            mode,
            "REDIRECT",
            False,
            "请求被重定向，Cookie 可能失效（HTTP %d）" % status,
            http_status=status,
        )
    if not 200 <= status < 300:
        return _result(
            account,
            mode,
            "HTTP_ERROR",
            False,
            "接口请求失败（HTTP %d）" % status,
            http_status=status,
        )

    try:
        payload = response.json()
    except ValueError as exc:
        return _result(
            account,
            mode,
            "INVALID_JSON",
            False,
            "接口返回不是 JSON：%s" % _redact(exc, [cookie]),
            http_status=status,
        )

    if not isinstance(payload, dict):
        return _result(
            account,
            mode,
            "INVALID_RESPONSE",
            False,
            "接口 JSON 顶层不是对象",
            http_status=status,
        )
    if payload.get("success") is False:
        error = payload.get("error")
        if isinstance(error, dict):
            detail = error.get("message") or error.get("code") or ""
        else:
            detail = payload.get("message") or ""
        return _result(
            account,
            mode,
            "BUSINESS_ERROR",
            False,
            "接口返回业务失败：%s" % (_redact(detail, [cookie]) or "未提供原因"),
            http_status=status,
        )

    data = payload.get("data")
    if not isinstance(data, dict):
        return _result(
            account,
            mode,
            "INVALID_RESPONSE",
            False,
            "接口响应缺少 data 对象",
            http_status=status,
        )

    granted = data.get("dailyLoginGranted") is True
    skip_reason = str(data.get("dailyLoginSkipReason") or "").strip()
    amount = _optional_number(data.get("dailyLoginGrantAmount"))
    balance_after = _optional_number(data.get("dailyLoginBalanceAfter"))
    prefix = "状态查询触发领取" if mode == "status" else "每日登录"

    if granted:
        parts = ["%s成功" % prefix]
        if amount is not None:
            parts.append("+%s" % amount)
        if balance_after is not None:
            parts.append("余额 %s" % balance_after)
        return _result(
            account,
            mode,
            "GRANTED",
            True,
            "，".join(parts),
            http_status=status,
            granted=True,
            amount=amount,
            balance_after=balance_after,
            skip_reason=skip_reason,
        )

    if skip_reason == ALREADY_GRANTED:
        message = "%s：今日已领取" % prefix
        if balance_after is not None:
            message += "，余额 %s" % balance_after
        return _result(
            account,
            mode,
            "ALREADY_GRANTED",
            True,
            message,
            http_status=status,
            balance_after=balance_after,
            skip_reason=skip_reason,
        )

    return _result(
        account,
        mode,
        "NOT_GRANTED",
        False,
        "%s未发放积分，且未返回 %s" % (prefix, ALREADY_GRANTED),
        http_status=status,
        amount=amount,
        balance_after=balance_after,
        skip_reason=skip_reason,
    )


def check_account(
    account: Mapping[str, str],
    *,
    mode: str = "checkin",
    session_factory: Callable[[], requests.Session] = make_session,
) -> dict[str, Any]:
    """处理单个账号；Session 创建失败也只影响当前账号。"""
    cookie = str(account.get("cookie", "") or "")
    session = None
    try:
        session = session_factory()
    except Exception as exc:
        return _result(
            account,
            mode,
            "SESSION_ERROR",
            False,
            "会话或请求处理异常：%s" % _redact(exc, [cookie]),
        )

    try:
        if hasattr(session, "trust_env"):
            session.trust_env = False
        if hasattr(session, "headers"):
            session.headers.update(BASE_HEADERS)
        return _request_result(session, cookie, account, mode)
    finally:
        close = getattr(session, "close", None)
        if callable(close):
            close()


def run_accounts(
    accounts: Sequence[Mapping[str, str]],
    *,
    mode: str = "checkin",
    session_factory: Callable[[], requests.Session] = make_session,
    output: Callable[[Mapping[str, Any]], None] = emit,
) -> list[dict[str, Any]]:
    """逐账号执行，单个账号失败不会阻断后续账号。"""
    results = []
    for account in accounts:
        result = check_account(
            account,
            mode=mode,
            session_factory=session_factory,
        )
        results.append(result)
        output(result)
    return results


def build_summary(results: Sequence[Mapping[str, Any]], mode: str) -> dict[str, Any]:
    granted = sum(1 for item in results if item.get("result") == "GRANTED")
    already = sum(
        1 for item in results if item.get("result") == "ALREADY_GRANTED"
    )
    failed = sum(1 for item in results if not item.get("ok"))
    return {
        "mode": mode,
        "result": "SUMMARY",
        "ok": failed == 0 and bool(results),
        "total": len(results),
        "granted": granted,
        "already_granted": already,
        "failed": failed,
    }


def _truncate_utf8(text: str, limit: int) -> str:
    raw = text.encode("utf-8")
    if len(raw) <= limit:
        return text
    suffix = "\n...(内容过长已截断)"
    body = raw[: max(0, limit - len(suffix.encode("utf-8")))]
    return body.decode("utf-8", "ignore") + suffix


def build_notification_text(
    results: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
) -> str:
    lines = ["Meoo 每日登录积分报告", "模式: %s" % summary.get("mode", "")]
    for index, item in enumerate(results, 1):
        state = "成功" if item.get("ok") else "失败"
        lines.append(
            "%d. %s [%s] %s - %s"
            % (
                index,
                item.get("account", "账号%d" % index),
                state,
                item.get("result", ""),
                item.get("message", ""),
            )
        )
    lines.append(
        "汇总: 共%d，成功%d，已领%d，失败%d"
        % (
            summary.get("total", 0),
            summary.get("granted", 0),
            summary.get("already_granted", 0),
            summary.get("failed", 0),
        )
    )
    return "\n".join(lines)


def send_pushplus(
    title: str,
    content: str,
    *,
    env: Optional[Mapping[str, str]] = None,
    session_factory: Callable[[], requests.Session] = make_session,
) -> Optional[dict[str, Any]]:
    values = os.environ if env is None else env
    token = str(values.get("PUSHPLUS_TOKEN", "") or "").strip()
    if not token:
        return None
    session = None
    try:
        session = session_factory()
        if hasattr(session, "trust_env"):
            session.trust_env = False
        response = session.post(
            "https://www.pushplus.plus/send",
            json={
                "token": token,
                "title": title,
                "content": content[:18000],
                "template": "txt",
            },
            timeout=REQUEST_TIMEOUT,
        )
        payload = response.json()
        ok = 200 <= int(response.status_code) < 300 and str(
            payload.get("code")
        ) == "200"
        return {
            "channel": "pushplus",
            "ok": ok,
            "message": "成功" if ok else str(payload.get("msg") or "发送失败"),
        }
    except Exception as exc:
        return {
            "channel": "pushplus",
            "ok": False,
            "message": "异常：%s" % _redact(exc, [token]),
        }
    finally:
        close = getattr(session, "close", None)
        if callable(close):
            close()


def send_qywx(
    title: str,
    content: str,
    *,
    env: Optional[Mapping[str, str]] = None,
    session_factory: Callable[[], requests.Session] = make_session,
) -> Optional[dict[str, Any]]:
    values = os.environ if env is None else env
    raw_url = str(values.get("QYWX_WEBHOOK", "") or "").strip()
    if not raw_url:
        return None
    url = raw_url
    if not raw_url.startswith(("http://", "https://")):
        url = (
            "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + raw_url
        )
    message = _truncate_utf8("%s\n%s" % (title, content), 2000)
    session = None
    try:
        session = session_factory()
        if hasattr(session, "trust_env"):
            session.trust_env = False
        response = session.post(
            url,
            json={"msgtype": "text", "text": {"content": message}},
            timeout=REQUEST_TIMEOUT,
        )
        payload = response.json()
        ok = (
            200 <= int(response.status_code) < 300
            and payload.get("errcode") == 0
        )
        return {
            "channel": "qywx",
            "ok": ok,
            "message": "成功"
            if ok
            else str(payload.get("errmsg") or "发送失败"),
        }
    except Exception as exc:
        return {
            "channel": "qywx",
            "ok": False,
            "message": "异常：%s" % _redact(exc, [raw_url]),
        }
    finally:
        close = getattr(session, "close", None)
        if callable(close):
            close()


def notify_all(
    results: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    *,
    env: Optional[Mapping[str, str]] = None,
    session_factory: Callable[[], requests.Session] = make_session,
) -> list[dict[str, Any]]:
    """推送已配置的渠道；未配置的渠道不产生结果。"""
    title = "Meoo 每日登录积分报告"
    content = build_notification_text(results, summary)
    notifications = [
        send_pushplus(
            title,
            content,
            env=env,
            session_factory=session_factory,
        ),
        send_qywx(
            title,
            content,
            env=env,
            session_factory=session_factory,
        ),
    ]
    return [item for item in notifications if item is not None]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Meoo 每日登录积分。注意：默认模式和 --status 都会发送同一个 "
            "GET /api/mc/entitlement/init，该请求本身会触发领取。"
        )
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help=(
            "只改变输出模式标识；仍发送与正常签到相同的 GET 请求，"
            "因此同样会触发每日登录积分发放"
        ),
    )
    parser.add_argument(
        "action",
        nargs="?",
        choices=("status",),
        help=argparse.SUPPRESS,
    )
    return parser


def main(
    argv: Optional[Sequence[str]] = None,
    *,
    env: Optional[Mapping[str, str]] = None,
    session_factory: Callable[[], requests.Session] = make_session,
    notify_session_factory: Callable[
        [], requests.Session
    ] = make_session,
    output: Callable[[Mapping[str, Any]], None] = emit,
) -> int:
    args = build_parser().parse_args(argv)
    mode = "status" if args.status or args.action == "status" else "checkin"
    try:
        accounts = load_accounts(env)
    except ConfigError as exc:
        output(
            {
                "result": "CONFIG_ERROR",
                "ok": False,
                "mode": mode,
                "message": str(exc),
            }
        )
        return 2

    results = run_accounts(
        accounts,
        mode=mode,
        session_factory=session_factory,
        output=output,
    )
    summary = build_summary(results, mode)
    notifications = notify_all(
        results,
        summary,
        env=env,
        session_factory=notify_session_factory,
    )
    if notifications:
        summary["notifications"] = notifications
    output(summary)
    return 0 if summary["ok"] else 1


def _configure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


if __name__ == "__main__":
    _configure_utf8_stdio()
    sys.exit(main())
