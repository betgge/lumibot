"""설명서 확인용: 자동 매매 알림 + 나만의 알림 예시를 백테스트로 돌려본다.
카톡은 실제로 보내지 않고, 보냈을 메시지를 화면에 출력한다.
실행: 저장소 폴더에서  python my_tests/verify_manual.py
"""
import os, json, sys, tempfile
from datetime import datetime
tok = os.path.join(tempfile.mkdtemp(), "kakao_token.json")
json.dump({"access_token": "fake", "refresh_token": "fake"}, open(tok, "w"))
os.environ.update(KAKAO_REST_API_KEY="fake", KAKAO_TOKEN_FILE=tok, KAKAO_TRADE_ALERTS="true",
                  KAKAO_ALERT_IN_BACKTEST="true", KAKAO_DAILY_SUMMARY="true", LUMIBOT_HIDE_BOTSPOT_TIP="1")
os.environ.pop("KAKAO_CLIENT_SECRET", None)
import pandas as pd
from lumibot.components.notifications import kakao as K
SENT = []
class R:
    status_code = 200
    def json(self): return {"result_code": 0}
def fake_post(self, text, access_token): SENT.append(text); return R()
K.KakaoNotificationProvider._post_message = fake_post
from lumibot.backtesting import PandasDataBacktesting
from lumibot.entities import Asset, Data
from lumibot.strategies import Strategy
NOTIFY = []
class Manual(Strategy):
    def initialize(self):
        self.sleeptime = "1M"; self.step = 0; self.sent = False
        self.notifications.configure_kakao()
    def on_trading_iteration(self):
        self.step += 1
        if self.step == 1: self.submit_order(self.create_order("DEMO", 10, "buy"))
        price = self.get_last_price("DEMO")
        if price > 101 and not self.sent:                       # 예시 1 형태
            NOTIFY.append(("예시1", self.notify("급락 감지", f"DEMO {price:,.0f}원")))
            self.sent = True
        if price >= 103 and self.get_position("DEMO"):         # 예시 2 형태
            self.sell_all()
            NOTIFY.append(("예시2", self.notify("목표가 도달", f"DEMO {price:,.0f}원")))
        NOTIFY.append(("cash", self.get_cash()))
asset = Asset("DEMO", Asset.AssetType.STOCK)
p = [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0]
f = pd.DataFrame({"open": p, "high": p, "low": p, "close": p, "volume": 1000},
                 index=pd.date_range("2025-01-06 09:30", periods=len(p), freq="min", tz="America/New_York"))
Manual.run_backtest(PandasDataBacktesting, datetime(2025,1,6,9,30), datetime(2025,1,6,9,37),
    pandas_data={asset: Data(asset, f, timestep="minute")}, budget=10_000, benchmark_asset=None,
    risk_free_rate=0.0, analyze_backtest=False, show_plot=False, show_tearsheet=False, save_tearsheet=False,
    show_indicators=False, save_logfile=False, show_progress_bar=False)
print("\n===== 자동 알림으로 보낸 카톡 =====")
for t in SENT: print("---\n" + t)
print("\n===== self.notify 결과 (백테스트) =====")
for name, r in NOTIFY:
    if name == "cash": continue
    print(name, [(x.provider, x.skipped, x.reason) for x in r])
SENT.clear()
r = K.KakaoNotificationProvider().notify(title="[악재] 삼성전자", message="리콜 관련 뉴스")
print("\n===== 예시 4 (전략 밖) =====\nok:", r.ok, "\n" + (SENT[0] if SENT else "(안 보냄)"))
