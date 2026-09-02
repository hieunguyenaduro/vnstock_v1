"""
            đây đươc gọi là chiến lược chuan bị kiếm đảo chiều xh, bằng cách kiếm cổ phiếu dưới ma200 nhưng trên ma50

            và có đỉnh đáy đảo chiều thì gần như tỷ lệ thành công khá cao

            chiến lươc này dành cho đánh đảo chiều xh trên khung lớn


            thêm 1 chiến lược là : vượt ma50 và ma200 không qu 15% . mục tiêu là kiếm chiến lược polarity ( vượt kháng cự và backtest)
            """

import time
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

    def us_stock(self):
        list_ticker_sma = []
        list_ticker_polarity = []

        for ticker in Config.US_TICKERS:
            current_stock_price, sma50, sma200 = self.fetcher_us_data.get_stock_data_from_timeseries(ticker=ticker)

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

        if list_ticker_sma:
            data = [{"list_ticker_sma": list_ticker_sma}]
            Common.create_json_file(data, etl_path, "us_stock_sma")
        if list_ticker_polarity:
            data = [{"list_ticker_polarity": list_ticker_sma}]
            Common.create_json_file(data, etl_path, "us_stock_polarity")

    def binance_token(self):
        list_token_sma = []
        list_token_polarity = []

        for token in Config.TOKENS:
            current_price, sma50, sma200 = self.fetcher_binance_data.get_binance_from_timeseries(token=token)

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

        if list_token_sma:
            data = [{"list_token_sma": list_token_sma}]
            Common.create_json_file(data, etl_path, "token_sma")
        if list_token_polarity:
            data = [{"list_token_polarity": list_token_polarity}]
            Common.create_json_file(data, etl_path, "token_polarity")

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
    global airflow_context
    airflow_context = kwargs
    SMA(interval=airflow_context).main()
