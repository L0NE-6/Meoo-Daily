# 🍀 Meoo Daily

**Meoo 일일 로그인 포인트 · 다중 계정 단일 파일 스크립트 · JSONL 결과**

[简体中文](../README.md) · [English](README.en.md) · [繁體中文](README.zh-Hant.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (BR)](README.pt-BR.md)

> [!WARNING]
> `--status`는 일반 모드와 동일한 `GET /api/mc/entitlement/init` 요청을 보냅니다. 이 요청 자체가 일일 로그인 포인트를 지급합니다. `--status`는 보고서의 모드와 문구만 바꾸며 읽기 전용 조회가 아닙니다.

## 기능

스크립트는 다음 요청을 사용합니다.

```http
GET https://meoo.com/api/mc/entitlement/init
Cookie: <전체 브라우저 Cookie>
```

HTTP 200만으로 성공을 판단하지 않고 `dailyLoginGranted`, `dailyLoginSkipReason`, `dailyLoginGrantAmount`, `dailyLoginBalanceAfter`를 확인합니다.

## 빠른 시작

```powershell
python -m pip install -r requirements.txt
$env:MEOO_COOKIE = "sessionid=REPLACE_WITH_COOKIE; other_cookie=REPLACE_ME"
python .\meoo_daily.py
```

여러 계정은 `MEOO_COOKIES`에 한 줄씩 `메모|Cookie` 형식으로 입력합니다.

```text
본계정|sessionid=REPLACE_WITH_COOKIE
부계정|sessionid=REPLACE_WITH_ANOTHER_COOKIE
```

`MEOO_COOKIES`가 비어 있지 않으면 `MEOO_COOKIE`보다 우선합니다. 선택 알림 변수는 `PUSHPLUS_TOKEN`과 `QYWX_WEBHOOK`입니다.

## Qinglong

1. `meoo_daily.py`를 업로드합니다.
2. 환경 변수에 `MEOO_COOKIES` 또는 `MEOO_COOKIE`를 추가합니다.
3. `requests`를 설치합니다.
4. 하루 한 번 실행되는 작업을 만들고 명령을 `task meoo_daily.py`로 설정합니다.

## GitHub Actions

저장소를 Fork / Import하고 Cookie를 Actions Secret에 등록한 뒤 한 번 수동 실행합니다. 포함된 [workflow](../.github/workflows/meoo.yml)는 `push`에서 테스트를 실행하고, `schedule`에서 하루 한 번 포인트를 받으며 콘솔 JSONL을 JSON 배열로 변환해 두 형식의 보고서를 artifact로 업로드합니다.
Cookie Secret이 없으면 예약 실행은 명시적인 SKIPPED notice를 남기고 정상 종료합니다. 인증 정보가 설정된 뒤에는 스크립트 오류를 계속 실패로 처리합니다.

## 성공 기준

- `GRANTED`: 이번 요청에서 포인트가 지급되었습니다.
- `ALREADY_GRANTED`: 서버가 `ALREADY_GRANTED_TODAY`를 반환했습니다.
- 인증, 리디렉션, 네트워크, HTTP, JSON 또는 응답 구조 오류가 있으면 `SUMMARY.ok`는 false입니다.

## 사용 경계 및 개인정보

공식 저장소는 무료입니다. 재판매, 유료화, 유료 대행 배포, 작성자 사칭, 저작권 표시 제거를 금지합니다. 자세한 내용은 [NOTICE.md](../NOTICE.md)를 참조하세요.

Cookie는 로그인 자격 증명입니다. 환경 변수 또는 GitHub Secrets에 보관하고 실제 Cookie, 전화번호, 보고서, 로그, 로컬 인증 파일을 커밋하지 마세요.

L0NE-6이 직접 유지보수합니다.
