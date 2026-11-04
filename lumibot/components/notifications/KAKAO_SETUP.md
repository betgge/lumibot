# 카카오톡 매매 알림 설정 안내

주문이 체결·부분 체결·취소될 때와 장 마감 후에 내 카카오톡 "나와의 채팅"으로 알림을 받는다.
처음 한 번만 아래 순서대로 설정하면 된다.

이 안내는 터미널에서 언제든 다시 볼 수 있다.

    lumibot kakao guide


## 1단계. 카카오 앱 만들기 (직접, 처음 한 번)

카카오 개발자 콘솔은 프로그램이 대신 설정할 수 없어서 직접 해야 한다.

1. https://developers.kakao.com/console/app 에 로그인하고 [앱 추가]로 앱을 만든다.
2. [카카오 로그인] → [사용 설정] → 상태를 ON 으로 바꾼다.
3. [앱] → [플랫폼 키] → [REST API 키] 로 들어가서
   "카카오 로그인 리다이렉트 URI" 에 아래 주소를 추가하고 저장한다.

       http://localhost:5000/kakao/callback

4. [카카오 로그인] → [동의항목] 에서 "카카오톡 메시지 전송(talk_message)" 의
   [설정] 을 눌러 "이용 중 동의" 로 바꾸고 저장한다.
5. 같은 [REST API 키] 화면에서 REST API 키를 복사한다.
   클라이언트 시크릿이 "활성화 ON" 이면 그 코드도 복사한다.


## 2단계. .env 에 키 넣기 (직접, 처음 한 번)

전략을 실행하는 폴더의 .env 파일에 넣는다. .env 는 GitHub 에 올리지 않는다.

    KAKAO_REST_API_KEY=복사한_REST_API_키
    KAKAO_CLIENT_SECRET=복사한_클라이언트_시크릿   (시크릿이 꺼져 있으면 생략)


## 3단계. 로그인 (명령 한 번, 동의 클릭 한 번)

전략을 실행하는 폴더에서 실행한다.

    lumibot kakao login

브라우저가 열리면 카카오 로그인 후 "동의하고 계속하기" 만 누르면 된다.
나머지(토큰 발급, kakao_token.json 저장, 권한 확인, 테스트 메시지)는 자동으로 한다.
kakao_token.json 도 GitHub 에 올리지 않는다.

토큰은 자동으로 갱신된다. 약 2개월 동안 쓰지 않아 갱신이 끊기면 이 명령을 다시 실행한다.


## 4단계. 알림 켜기

.env 에 한 줄을 추가하고 평소처럼 전략을 실행한다. 전략 코드는 고칠 필요가 없다.

    KAKAO_TRADE_ALERTS=true

선택 설정

    KAKAO_DAILY_SUMMARY=true        장 마감 후 하루 요약 (기본 true)
    KAKAO_ALERT_IN_BACKTEST=false   백테스트 중에도 보낼지 (기본 false)
    KAKAO_BACKTEST_MAX_ALERTS=20    백테스트 1회당 최대 메시지 수
    KAKAO_TOKEN_FILE=kakao_token.json
    KAKAO_REDIRECT_URI=http://localhost:5000/kakao/callback


## 자주 나오는 문제

| 화면/메시지 | 원인 | 해결 |
|---|---|---|
| 로그인 화면에 KOE004 | 카카오 로그인이 꺼져 있음 | 1단계 2번 |
| 로그인 화면에 KOE006 | 리다이렉트 URI 미등록 또는 불일치 | 1단계 3번, 주소를 글자 하나까지 똑같이 |
| KOE010 | REST API 키 또는 클라이언트 시크릿이 틀림 | 2단계 다시 확인 |
| 권한(talk_message) 없음 | 동의항목 미설정 | 1단계 4번 후 3단계 다시 |
| 메시지는 성공인데 알림이 안 울림 | "나에게 보내기" 는 나와의 채팅에 조용히 쌓임 | 카카오톡 "나와의 채팅" 확인 |

테스트 메시지만 다시 보내 보려면

    lumibot kakao test
