"""
            đây đươc gọi là chiến lược chuan bị kiếm đảo chiều xh, bằng cách kiếm cổ phiếu dưới ma200 nhưng trên ma50

            và có đỉnh đáy đảo chiều thì gần như tỷ lệ thành công khá cao

            chiến lươc này dành cho đánh đảo chiều xh trên khung lớn


            thêm 1 chiến lược là : vượt ma50 và ma200 không quá 15% .
            mục tiêu là kiếm chiến lược polarity ( vượt kháng cự và backtest)
            """


"""
           giá nằm trên ma200

           rsi quá ban 4h ~~ 32

            kiểu : cool off rsi kết hợp với shakeout trước khi bay lên trời. ck vn có PET 2026-09-20
            """

import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pathlib import Path

from utiils.common import Common
from config import Config
from utiils.fetch_us_stock_data import FetchUsStockData
from utiils.fetch_binance_data import FetchBinanceData

etl_path = str(Path(__file__).resolve().parents[1])


class SMA:

    def __init__(self, interval):
        self.fetcher_us_data = FetchUsStockData()
        self.fetcher_binance_data = FetchBinanceData()
        self.interval = interval
        self.execution_date = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime('%Y-%m-%d')
        range_date = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")) - timedelta(days=60)
        self.execution_range_date = range_date.strftime('%Y-%m-%d')
        # utc
        # self.execution_date = datetime.now(ZoneInfo("UTC")).strftime('%Y-%m-%d')

    def us_stock(self):
        list_ticker_sma = []
        list_ticker_polarity = []
        list_ticker_094h = []

        for ticker in Config.US_TICKERS:
            unpacked = self.fetcher_us_data.get_stock_data_from_timeseries(ticker=ticker)
            if unpacked is None:
                continue
            current_stock_price, sma50, sma200 = unpacked

            rsi_4h = self.fetcher_us_data.get_us_stock_rsi(ticker=ticker, interval=self.interval)

            if None not in (current_stock_price, sma50, sma200):
                if sma200 >= current_stock_price >= sma50:
                    list_ticker_sma.append(ticker)

                # 2. Kiểm tra điều kiện:
                # - Lớn hơn SMA50 và SMA200
                # - Không vượt quá 15% (tức là <= 1.15 lần SMA)
                is_above_sma50 = sma50 < current_stock_price <= (sma50 * 1.15)
                is_above_sma200 = sma200 < current_stock_price <= (sma200 * 1.15)

                if is_above_sma50 and is_above_sma200:
                    list_ticker_polarity.append(ticker)

            if None not in (current_stock_price, rsi_4h, sma200):
                if current_stock_price >= sma200 and rsi_4h <= 32:
                    list_ticker_094h.append(ticker)

        Common.create_json_file([{"us_stock_sma": list_ticker_sma}], etl_path, "us_stock_sma")
        Common.create_json_file([{"us_stock_polarity": list_ticker_polarity}], etl_path, "us_stock_polarity")
        Common.create_json_file([{"us_stock_094h": list_ticker_094h}], etl_path, "us_stock_094h")

    def binance_token(self):
        list_token_sma = []
        list_token_polarity = []
        list_token_094h=[]

        for token in Config.TOKENS:
            unpacked = self.fetcher_binance_data.get_binance_from_timeseries(token=token)
            if unpacked is None:
                continue
            current_price, sma50, sma200 = unpacked

            rsi_df = self.fetcher_binance_data.get_binance_data(token=token, timeframe=self.interval)
            rsi_4h = None
            if rsi_df is not None and not rsi_df.empty and "RSI" in rsi_df.columns:
                rsi_series = rsi_df["RSI"].dropna()
                if not rsi_series.empty:
                    rsi_4h = float(rsi_series.iloc[-1])

            if None not in (current_price, sma50, sma200):
                if sma200 >= current_price >= sma50:
                    list_token_sma.append(token)
                # 2. Kiểm tra điều kiện:
                # - Lớn hơn SMA50 và SMA200
                # - Không vượt quá 15% (tức là <= 1.15 lần SMA)
                is_above_sma50 = sma50 < current_price <= (sma50 * 1.15)
                is_above_sma200 = sma200 < current_price <= (sma200 * 1.15)

                if is_above_sma50 and is_above_sma200:
                    list_token_polarity.append(token)

            if None not in (current_price, rsi_4h, sma200):
                if current_price >= sma200 and rsi_4h <= 32:
                    list_token_094h.append(token)

        Common.create_json_file([{"binance_token_sma": list_token_sma}], etl_path, "binance_token_sma")
        Common.create_json_file([{"binance_token_polarity": list_token_polarity}], etl_path, "binance_token_polarity")
        Common.create_json_file([{"binance_token_094h": list_token_094h}], etl_path, "binance_token_094h")

    def main(self):
        start_time = time.perf_counter()

        self.us_stock()
        self.binance_token()

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f'"execution_time": {execution_time:.2f}')


if __name__ == '__main__':
    SMA(interval='1d').main()


def python_operator_run(**kwargs):
    interval = kwargs.get("interval") or kwargs.get("op_kwargs", {}).get("interval")
    SMA(interval=interval if interval else "1d").main()
