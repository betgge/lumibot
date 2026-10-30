"""체결·취소되면 카카오톡으로 알림을 보내는 연습용 전략.

인터넷 가격 데이터 없이 가짜 가격으로 돌린다 (공식 예제 first_backtest.py 방식).
실행: my_tests 폴더에서  python alert_test.py
"""
from datetime import datetime

import pandas as pd

from lumibot.backtesting import PandasDataBacktesting
from lumibot.entities import Asset, Data
from lumibot.strategies import Strategy

from kakao import send_kakao


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

    # 주문이 체결되면 Lumibot이 자동으로 불러 주는 함수
    def on_filled_order(self, position, order, price, quantity, multiplier):
        side = "매수" if order.side == "buy" else "매도"
        holding = position.quantity if position else 0
        text = (
            f"[체결 알림] {order.asset.symbol} {quantity:g}주 {side}\n"
            f"가격: {price:,.0f}\n"
            f"보유: {holding:g}주\n"
            f"시각: {self.get_datetime():%Y-%m-%d %H:%M}"
        )
        print(text)
        print(send_kakao(text))

    # 주문이 취소되면 불리는 함수
    def on_canceled_order(self, order):
        text = f"[취소 알림] {order.asset.symbol} {order.quantity}주 주문 취소"
        print(text)
        print(send_kakao(text))


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
