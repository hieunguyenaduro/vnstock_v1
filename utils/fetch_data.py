import logging
import time
from vnstock import Quote, register_user
import config
import pandas as pd

logger = logging.getLogger(__name__)

INTERVAL_MAP = {"1H": "1h", "4H": "4h", "1D": "1D", "1W": "1w", "1M": "1M"}


class FetchData():
    def __init__(self):
        register_user(api_key=config.Config.API_KEY)

    @staticmethod
    def fetch_data_for_ticker(ticker: str, timeframe: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        timeframe: '1H', '4H', '1D', '1W', '1M'
        vnstock3 interval map: '1H'->'1h', '4H'->'4h', '1D'->'1D'
        """
        if timeframe not in INTERVAL_MAP:
            raise ValueError(f"timeframe không hỗ trợ: {timeframe!r}. Chọn trong {sorted(INTERVAL_MAP)}")
        time.sleep(5)
        logger.debug("Lay du lieu %s khung %s (%s -> %s)", ticker, timeframe, start_date, end_date)

        quote = Quote(symbol=ticker, source='VCI')
        df = quote.history(start=start_date, end=end_date, interval=INTERVAL_MAP[timeframe])

        return df


if __name__ == '__main__':
    FetchData().fetch_data_for_ticker("vds", "1D", "2026-05-05", "2026-06-19")
