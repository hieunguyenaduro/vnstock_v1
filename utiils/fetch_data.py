from vnstock import *
from scipy.signal import find_peaks
from vnstock import register_user
import config
import pandas as pd
from vnstock_data import Market
from vnstock_ta import Indicator


class FetchData():
    def __init__(self):
        register_user(api_key=config.api_key)

    def fetch_data_for_ticker(self, ticker: str, timeframe: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        timeframe: '1H', '4H', '1D'
        vnstock3 interval map: '1H'->'1h', '4H'->'4h', '1D'->'1D'
        """
        interval_map = {"1H": "1h", "4H": "4h", "1D": "1D", "1W": "1w", "1M": "1M"}

        quote = Quote(symbol=ticker, source='VCI')
        df = quote.history(start=start_date, end=end_date, interval=interval_map[timeframe])

        return df
    
    def fetch_indicators_for_ticker(self, ticker: str) -> pd.DataFrame:
        m = Market()

        df = m.equity(ticker).ohlcv(length=365, interval="1D")
        df = df.set_index('time')

        ta = Indicator(data=df)

        sma_200 = ta.trend.sma(length=200)
        sma_50 = ta.trend.sma(length=50)
        rsi_14 = ta.momentum.rsi(length=14)

        return sma_200, sma_50, rsi_14
    
    def fetch_09_for_ticker(self, ticker: str, timeframe: str) -> pd.DataFrame:
        m = Market()

        df = m.equity(ticker).ohlcv(length=365, interval=timeframe)
        df = df.set_index('time')

        ta = Indicator(data=df)
        rsi_14 = ta.momentum.rsi(length=14)

        return rsi_14
    

if __name__ == '__main__':
    FetchData().fetch_data_for_ticker("vds", "1D", "2026-05-05", "2026-06-19")
