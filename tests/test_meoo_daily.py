import contextlib
import io
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import meoo_daily


class FakeResponse:
    def __init__(self, status_code=200, payload=None, json_error=None):
        self.status_code = status_code
        self.payload = payload
        self.json_error = json_error

    def json(self):
        if self.json_error is not None:
            raise self.json_error
        return self.payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.headers = {}
        self.trust_env = True
        self.closed = False

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if not self.responses:
            raise AssertionError("unexpected GET")
        return self.responses.pop(0)

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if not self.responses:
            raise AssertionError("unexpected POST")
        return self.responses.pop(0)

    def close(self):
        self.closed = True


class SessionFactory:
    def __init__(self, responses):
        self.responses = [list(item) for item in responses]
        self.sessions = []

    def __call__(self):
        session = FakeSession(self.responses.pop(0))
        self.sessions.append(session)
        return session


class MeooDailyTests(unittest.TestCase):
    def test_success_is_reported_and_cookie_is_never_emitted(self):
        factory = SessionFactory(
            [
                [
                    FakeResponse(
                        payload={
                            "success": True,
                            "data": {
                                "dailyLoginGranted": True,
                                "dailyLoginGrantAmount": 100,
                                "dailyLoginBalanceAfter": 1300,
                            },
                        }
                    )
                ]
            ]
        )

        result = meoo_daily.check_account(
            {"note": "主号", "cookie": "sessionid=secret-one"},
            session_factory=factory,
        )

        self.assertEqual("GRANTED", result["result"])
        self.assertTrue(result["ok"])
        self.assertEqual(100, result["amount"])
        self.assertEqual(1300, result["balance_after"])
        self.assertNotIn("secret-one", json.dumps(result, ensure_ascii=False))
        self.assertTrue(factory.sessions[0].closed)
        url, kwargs = factory.sessions[0].calls[0]
        self.assertEqual(meoo_daily.API_URL, url)
        self.assertEqual(
            "sessionid=secret-one",
            kwargs["headers"]["Cookie"],
        )
        self.assertFalse(kwargs["allow_redirects"])

    def test_already_granted_is_distinct_success(self):
        factory = SessionFactory(
            [
                [
                    FakeResponse(
                        payload={
                            "success": True,
                            "data": {
                                "dailyLoginGranted": False,
                                "dailyLoginSkipReason": (
                                    "ALREADY_GRANTED_TODAY"
                                ),
                                "dailyLoginBalanceAfter": 1300,
                            },
                        }
                    )
                ]
            ]
        )

        result = meoo_daily.check_account(
            {"note": "主号", "cookie": "sessionid=already"},
            session_factory=factory,
        )

        self.assertEqual("ALREADY_GRANTED", result["result"])
        self.assertTrue(result["ok"])
        self.assertFalse(result["granted"])
        self.assertEqual(
            "ALREADY_GRANTED_TODAY",
            result["skip_reason"],
        )

    def test_auth_and_redirect_failures_are_classified(self):
        cases = [
            (401, "AUTH_EXPIRED"),
            (403, "AUTH_EXPIRED"),
            (302, "REDIRECT"),
        ]
        for status, expected in cases:
            with self.subTest(status=status):
                factory = SessionFactory(
                    [[FakeResponse(status_code=status, payload={})]]
                )
                result = meoo_daily.check_account(
                    {"note": "失效号", "cookie": "sessionid=bad"},
                    session_factory=factory,
                )
                self.assertEqual(expected, result["result"])
                self.assertFalse(result["ok"])
                self.assertEqual(status, result["http_status"])

    def test_multi_accounts_use_isolated_sessions_and_continue_after_failure(self):
        accounts = meoo_daily.load_accounts(
            {
                "MEOO_COOKIES": (
                    "主号|sessionid=secret-one\n"
                    "小号|sessionid=secret-two"
                )
            }
        )
        factory = SessionFactory(
            [
                [FakeResponse(status_code=401, payload={})],
                [
                    FakeResponse(
                        payload={
                            "success": True,
                            "data": {
                                "dailyLoginGranted": True,
                                "dailyLoginGrantAmount": 50,
                                "dailyLoginBalanceAfter": 550,
                            },
                        }
                    )
                ],
            ]
        )
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            results = meoo_daily.run_accounts(
                accounts,
                session_factory=factory,
            )

        self.assertEqual(2, len(results))
        self.assertEqual("AUTH_EXPIRED", results[0]["result"])
        self.assertEqual("GRANTED", results[1]["result"])
        self.assertIsNot(factory.sessions[0], factory.sessions[1])
        self.assertEqual(
            "sessionid=secret-one",
            factory.sessions[0].calls[0][1]["headers"]["Cookie"],
        )
        self.assertEqual(
            "sessionid=secret-two",
            factory.sessions[1].calls[0][1]["headers"]["Cookie"],
        )
        self.assertTrue(all(session.closed for session in factory.sessions))

        lines = [
            json.loads(line)
            for line in output.getvalue().splitlines()
            if line.strip()
        ]
        self.assertEqual(2, len(lines))
        self.assertNotIn("secret-one", output.getvalue())
        self.assertNotIn("secret-two", output.getvalue())

    def test_status_mode_still_calls_the_same_mutating_endpoint(self):
        for argv in (["--status"], ["status"]):
            with self.subTest(argv=argv):
                factory = SessionFactory(
                    [
                        [
                            FakeResponse(
                                payload={
                                    "success": True,
                                    "data": {
                                        "dailyLoginGranted": True,
                                        "dailyLoginGrantAmount": 20,
                                        "dailyLoginBalanceAfter": 220,
                                    },
                                }
                            )
                        ]
                    ]
                )
                output = []

                code = meoo_daily.main(
                    argv,
                    env={"MEOO_COOKIE": "sessionid=status"},
                    session_factory=factory,
                    output=output.append,
                )

                self.assertEqual(0, code)
                self.assertEqual("status", output[0]["mode"])
                self.assertEqual("GRANTED", output[0]["result"])
                self.assertEqual(
                    meoo_daily.API_URL,
                    factory.sessions[0].calls[0][0],
                )

    def test_invalid_json_is_not_treated_as_success(self):
        factory = SessionFactory(
            [[FakeResponse(payload=None, json_error=ValueError("bad json"))]]
        )

        result = meoo_daily.check_account(
            {"note": "主号", "cookie": "sessionid=invalid-json"},
            session_factory=factory,
        )

        self.assertEqual("INVALID_JSON", result["result"])
        self.assertFalse(result["ok"])

    def test_main_emits_account_json_then_summary_without_network(self):
        factory = SessionFactory(
            [
                [
                    FakeResponse(
                        payload={
                            "success": True,
                            "data": {
                                "dailyLoginGranted": True,
                                "dailyLoginGrantAmount": 10,
                                "dailyLoginBalanceAfter": 110,
                            },
                        }
                    )
                ]
            ]
        )
        output = []

        code = meoo_daily.main(
            [],
            env={"MEOO_COOKIE": "sessionid=main-secret"},
            session_factory=factory,
            output=output.append,
        )

        self.assertEqual(0, code)
        self.assertEqual("GRANTED", output[0]["result"])
        self.assertEqual("SUMMARY", output[-1]["result"])
        self.assertTrue(output[-1]["ok"])
        self.assertNotIn(
            "main-secret",
            json.dumps(output, ensure_ascii=False),
        )


if __name__ == "__main__":
    unittest.main()
