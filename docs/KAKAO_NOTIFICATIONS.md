# KakaoTalk 매매 알림 (Kakao Notifications)

주문이 체결·부분 체결·취소될 때와 장 마감 후에 **내 카카오톡(나와의 채팅)**으로 알림을 보낸다.
전략 코드는 고칠 필요 없이 `.env` 설정만 켜면 동작한다.

## 구성

| 파일 | 역할 |
|---|---|
| `lumibot/components/notifications/kakao.py` | `KakaoNotificationProvider`(메시지 전송, 토큰 자동 갱신), `KakaoTradeAlerts`(자동 매매 알림) |
| `lumibot/components/notifications/base.py` | `NotificationManager.configure_kakao()` 추가 |
| `lumibot/strategies/strategy_executor.py` | 체결·부분 체결·취소·장 마감 이벤트에서 `KakaoTradeAlerts` 호출 (기존 Discord 자동 알림과 같은 위치) |
| `tests/test_kakao_notification.py` | 가짜 응답(Mock) 단위 테스트 |

## 준비

1. [Kakao Developers](https://developers.kakao.com)에서 앱을 만들고 다음을 설정한다.
   - [카카오 로그인] → [사용 설정] ON
   - [앱] → [플랫폼 키] → [REST API 키] → 카카오 로그인 리다이렉트 URI 등록
   - [카카오 로그인] → [동의항목] → "카카오톡 메시지 전송(talk_message)" 이용 중 동의
2. `scope=talk_message`로 로그인해 인가 코드를 받고, 토큰을 발급한다.
3. 받은 토큰을 실행 폴더의 `kakao_token.json`에 저장한다. (GitHub에 올리지 않는다)

```json
{"access_token": "...", "refresh_token": "..."}
```

## 설정 (`.env`)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `KAKAO_REST_API_KEY` | (필수) | 앱의 REST API 키 |
| `KAKAO_CLIENT_SECRET` | | 클라이언트 시크릿을 켠 경우 |
| `KAKAO_TOKEN_FILE` | `kakao_token.json` | 토큰 저장 파일 |
| `KAKAO_TRADE_ALERTS` | `false` | `true`면 자동 매매 알림 사용 |
| `KAKAO_DAILY_SUMMARY` | `true` | 장 마감 후 하루 요약 |
| `KAKAO_ALERT_IN_BACKTEST` | `false` | 백테스트 중에도 보낼지 |
| `KAKAO_BACKTEST_MAX_ALERTS` | `20` | 백테스트 1회당 최대 메시지 수 |

## 동작 규칙

- 액세스 토큰이 만료돼 401이 오면 `refresh_token`으로 새 토큰을 받아 파일에 저장하고 한 번 다시 보낸다.
- 카카오 텍스트 메시지 길이 제한(200자)에 맞춰 자른다.
- 알림이 실패해도 예외를 밖으로 던지지 않는다. 경고 로그만 남기고 매매는 계속된다.
- 백테스트에서는 기본으로 보내지 않는다. 켜더라도 최대 개수를 넘으면 더 보내지 않는다(일일 쿼터 보호).
- `hide_trades` 설정이 켜져 있으면 종목·수량·가격을 숨긴다.

## 메시지 예시

```
[체결] 005930 10주 매수
가격: 70,000원
금액: 700,000원
보유: 10주
시각: 2026-11-02 09:30
```

## 테스트

```bash
pytest tests/test_kakao_notification.py -q
```

## 알려진 제한

- "나에게 보내기"는 나와의 채팅에 쌓이며 휴대폰 푸시 알림이 울리지 않을 수 있다.
- `refresh_token`도 만료되면(약 2개월) 다시 로그인해 토큰을 받아야 한다.
