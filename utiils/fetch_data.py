from vnstock3 import Vnstock
import pandas as pd, json, os
from config import RAW_DIR

def fetch_ohlcv(ticker: str, timeframe: str, n_bars: int = 200) -> pd.DataFrame:
    """
    timeframe: '1H', '4H', '1D'
    vnstock3 interval map: '1H'->'1h', '4H'->'4h', '1D'->'1D'
    """
    interval_map = {"1H": "1h", "4H": "4h", "1D": "1D"}
    stock = Vnstock().stock(symbol=ticker, source="TCBS")
    df = stock.quote.history(
        start="2024-01-01",
        end=pd.Timestamp.now().strftime("%Y-%m-%d"),
        interval=interval_map[timeframe]
    )
    df = df.rename(columns={"open":"Open","high":"High","low":"Low","close":"Close","volume":"Volume"})
    return df.tail(n_bars)

def save_raw(ticker: str, timeframe: str, df: pd.DataFrame):
    path = f"{RAW_DIR}/{ticker}_{timeframe}.json"
    df.to_json(path, orient="records", date_format="iso")

def load_raw(ticker: str, timeframe: str) -> pd.DataFrame:
    path = f"{RAW_DIR}/{ticker}_{timeframe}.json"
    return pd.read_json(path)