import time
from pathlib import Path

from utiils.common import Common
from config import Config
from utiils.fetch_us_stock_data import FetchUsStockData
from utiils.fetch_binance_data import FetchBinanceData

etl_path = str(Path(__file__).resolve().parents[1])


class RSIOverSold:

    def __init__(self, interval):
        self.fetcher_us_data = FetchUsStockData()
        self.fetcher_binance_data = FetchBinanceData()
        self.interval = interval

    def us_stock(self):
        list_ticker_rsi_oversold = []
        list_us_stock_rsi_overbought = []
        data = []

        us_ticket_on_binance = self.fetcher_binance_data.get_us_stock_tickers_on_crypto_exchange()

        us_tickets = []
        for item in us_ticket_on_binance:
            us_tickets.append(item.replace('B/USDT',''))

        if self.interval == "1d":
            interval = "1day"
        else:
            interval = self.interval

        for ticket in Config.US_TICKERS:
            latest_rsi = self.fetcher_us_data.get_us_stock_rsi(ticker=ticket, interval=interval)
            if latest_rsi is not None and latest_rsi <= 33:
                list_ticker_rsi_oversold.append(latest_rsi)
            if latest_rsi is not None and latest_rsi <= 67:
                list_us_stock_rsi_overbought.append(latest_rsi)


        if len(list_ticker_rsi_oversold) > 0:
            data.append({"rsi_oversold_us_stock": list_ticker_rsi_oversold})
        if len(list_us_stock_rsi_overbought) > 0:
            data.append({"rsi_overbought_us_stock": list_us_stock_rsi_overbought})

        if len(data) > 0:
            Common.create_json_file(data, etl_path, "rsi_us_stock")

    def binance_token(self):
        list_token_rsi_oversold = []
        list_token_rsi_overbought = []

        data = []
        for token in Config.TOKENS:
            df = self.fetcher_binance_data.get_binance_data(token=token, timeframe=self.interval)
            latest_rsi = df[['timestamp', 'close', 'RSI']].tail()
            latest_rsi = latest_rsi.iloc[4]["RSI"]
            if latest_rsi is not None and latest_rsi <= 33:
                list_token_rsi_oversold.append(latest_rsi)
            if latest_rsi is not None and latest_rsi <= 67:
                list_token_rsi_overbought.append(latest_rsi)

        if len(list_token_rsi_oversold) > 0:
            data.append({"rsi_oversold_binance_token": list_token_rsi_oversold})
        if len(list_token_rsi_overbought) > 0:
            data.append({"rsi_overbought_binance_token": list_token_rsi_oversold})

        if len(data) > 0:
            Common.create_json_file(data, etl_path, "rsi_{}_binance_token".format(self.interval))

    def main(self):
        start_time = time.perf_counter()

        self.us_stock()
        self.binance_token()

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f'"execution_time": {execution_time:.2f}')


if __name__ == '__main__':
    RSIOverSold(interval='1d').main()
"""
    - interval: ('5m', '15m', '1h', '1d'...)
"""
def python_operator_run(**kwargs):
    global airflow_context
    airflow_context = kwargs
    RSIOverSold(interval=airflow_context).main()
