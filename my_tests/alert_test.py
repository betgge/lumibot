"""카카오톡 자동 체결 알림 확인용 전략.

이 파일에는 카톡 관련 코드가 하나도 없다.
my_tests/.env 에 KAKAO_TRADE_ALERTS=true 만 켜 두면 Lumibot이 알아서
체결·취소될 때와 장 마감 후에 카톡을 보낸다.

백테스트에서도 보려면 .env 에 KAKAO_ALERT_IN_BACKTEST=true 를 함께 켠다.
실행: my_tests 폴더에서  python alert_test.py
"""
from datetime import datetime

import pandas as pd

from lumibot.backtesting import PandasDataBacktesting
from lumibot.entities import Asset, Data
from lumibot.strategies import Strategy


class AlertTest(Strategy):
    def initialize(self):
        self.sleeptime = "1M"  # 1분마다 실행
        self.step = 0

    def on_trading_iteration(self):
        self.step += 1
        if self.step == 1:
            self.submit_order(self.create_order("DEMO", 10, "buy"))   # 1번째: 10주 매수
        elif self.step == 4:
            self.submit_order(self.create_order("DEMO", 10, "sell"))  # 4번째: 10주 매도


if __name__ == "__main__":
    asset = Asset("DEMO", Asset.AssetType.STOCK)
    prices = [100.0, 101.0, 102.0, 103.0, 104.0, 105.0]
    frame = pd.DataFrame(
        {"open": prices, "high": prices, "low": prices, "close": prices, "volume": 1000},
        index=pd.date_range("2025-01-06 09:30", periods=6, freq="min", tz="America/New_York"),
    )
    AlertTest.run_backtest(
        PandasDataBacktesting,
        datetime(2025, 1, 6, 9, 30),
        datetime(2025, 1, 6, 9, 35),
        pandas_data={asset: Data(asset, frame, timestep="minute")},
        budget=10_000,
        benchmark_asset=None,
        risk_free_rate=0.0,
        analyze_backtest=False,
        show_plot=False,
        show_tearsheet=False,
        save_tearsheet=False,
        show_indicators=False,
        save_logfile=False,
        show_progress_bar=False,
    )
