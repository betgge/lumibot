"""카카오톡 '나에게 보내기' + 토큰 자동 갱신.

비밀값은 같은 폴더의 .env 와 kakao_token.json 에서 읽는다 (둘 다 GitHub에 올리지 않음).
"""
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY", "")
CLIENT_SECRET = os.environ.get("KAKAO_CLIENT_SECRET", "")
TOKEN_FILE = HERE / "kakao_token.json"

TOKEN_URL = "https://kauth.kakao.com/oauth/token"
SEND_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"


def load_token():
    with open(TOKEN_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_token(token):
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(token, f, ensure_ascii=False, indent=2)


def refresh_token():
    """refresh_token으로 새 access_token을 받아 파일에 저장한다."""
    token = load_token()
    data = {
        "grant_type": "refresh_token",
        "client_id": REST_API_KEY,
        "refresh_token": token["refresh_token"],
    }
    if CLIENT_SECRET:
        data["client_secret"] = CLIENT_SECRET
    result = requests.post(TOKEN_URL, data=data, timeout=10).json()
    if "access_token" not in result:
        # refresh_token까지 만료됐으면 다시 로그인해서 토큰을 새로 받아야 함
        raise RuntimeError(f"카카오 토큰 갱신 실패: {result}")

    token["access_token"] = result["access_token"]
    if "refresh_token" in result:  # 새 refresh_token을 줄 때만 교체
        token["refresh_token"] = result["refresh_token"]
    save_token(token)
    print("[kakao] 토큰 갱신 완료")


def send_kakao(text, retry=True):
    """내 카카오톡(나와의 채팅)으로 메시지를 보낸다. 만료되면 한 번 갱신 후 재시도."""
    token = load_token()
    template = {
        "object_type": "text",
        "text": text,
        "link": {"web_url": "https://github.com"},
    }
    r = requests.post(
        SEND_URL,
        headers={"Authorization": f"Bearer {token['access_token']}"},
        data={"template_object": json.dumps(template, ensure_ascii=False)},
        timeout=10,
    )
    if r.status_code == 401 and retry:  # access_token 만료
        refresh_token()
        return send_kakao(text, retry=False)
    return r.json()


if __name__ == "__main__":
    # 단독 실행 테스트: python kakao.py
    print(send_kakao("[테스트] Lumibot 알리미 연결 확인"))
