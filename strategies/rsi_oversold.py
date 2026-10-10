"""Chiến lược RSI quá mua/quá bán cho US stocks và Binance tokens."""

from config import Config
from strategies.base import BaseStrategy
from utils.fetch_binance_data import FetchBinanceData
from utils.fetch_us_stock_data import FetchUsStockData

RSI_OVERSOLD = 33
RSI_OVERBOUGHT = 67


def latest_rsi_from_df(df):
    """Trích RSI mới nhất từ DataFrame Binance, None nếu thiếu dữ liệu."""
    if df is None or getattr(df, "empty", True) or "RSI" not in df.columns:
        return None
    series = df["RSI"].dropna()
    return float(series.iloc[-1]) if not series.empty else None


class RSIOverSold(BaseStrategy):

    def __init__(self, interval):
        super().__init__(name="rsi_oversold")
        self.fetcher_us_data = FetchUsStockData()
        self.fetcher_binance_data = FetchBinanceData()
        self.interval = interval

    def us_stock(self):
        # Fetcher tự chuẩn hóa interval về chuẩn TwelveData (1d -> 1day, ...)
        interval = self.interval

        oversold, overbought = [], []
        for ticket in Config.US_TICKERS:
            rsi = self.safe_call(self.fetcher_us_data.get_us_stock_rsi, ticket, interval=interval)
            if rsi is not None and rsi <= RSI_OVERSOLD:
                oversold.append(ticket)
            if rsi is not None and rsi >= RSI_OVERBOUGHT:
                overbought.append(ticket)

        self.save_signal("us_stock_rsi_oversold", oversold)
        self.save_signal("us_stock_rsi_overbought", overbought)

    def binance_token(self):
        oversold, overbought = [], []
        for token in Config.TOKENS:
            df = self.safe_call(self.fetcher_binance_data.get_binance_data, token,
                                timeframe=self.interval)
            rsi = latest_rsi_from_df(df)
            if rsi is not None and rsi <= RSI_OVERSOLD:
                oversold.append(token)
            if rsi is not None and rsi >= RSI_OVERBOUGHT:
                overbought.append(token)

        self.save_signal("binance_token_rsi_oversold", oversold)
        self.save_signal("binance_token_rsi_overbought", overbought)

    def main(self):
        self.run_timed("rsi_oversold", lambda: (self.us_stock(), self.binance_token()))


if __name__ == '__main__':
    RSIOverSold(interval='1d').main()
"""
    - interval: ('5m', '15m', '1h', '1d'...)
"""
def python_operator_run(**kwargs):
    interval = kwargs.get("interval") or kwargs.get("op_kwargs", {}).get("interval")
    RSIOverSold(interval=interval if interval else "1d").main()
