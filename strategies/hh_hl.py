import time
from pathlib import Path

from scipy.signal import find_peaks
from utiils.fetch_data import FetchData
from utiils.common import Common
from config import Config

etl_path = str(Path(__file__).resolve().parents[1])


class HhHl:

    def __init__(self):
        self.fetcher = FetchData()

    def main(self):

        start_time = time.perf_counter()

        list_ticker_uptrend = []
        list_ticker_2_bottom = []
        data = []
        for ticket in Config.ALL_TICKERS:
            df = self.fetcher.fetch_data_for_ticker(ticker=ticket, timeframe='1D', start_date='2026-03-5',
                                                    end_date='2026-06-26')
            prices = df['close'].values

            # 2. Find all local peaks and troughs
            # Adjust distance and prominence depending on how noisy the stock is
            peaks, _ = find_peaks(prices, distance=5, prominence=1)
            troughs, _ = find_peaks(-prices, distance=5, prominence=1)

            # 3. Algorithm to detect reversal points (HH and HL)
            trend_signals = []

            for i in range(1, len(peaks)):
                # Check that the next peak is higher than the previous one (Higher High)
                if prices[peaks[i]] > prices[peaks[i - 1]]:
                    # Check that the most recent trough is also higher than the one before it (Higher Low)
                    # Find the troughs that fall between or right before these two peaks
                    recent_troughs = [t for t in troughs if t < peaks[i]]
                    if len(recent_troughs) >= 2:
                        if prices[recent_troughs[-1]] > prices[recent_troughs[-2]]:
                            trend_signals.append(peaks[i])

            print(" prices peaks : ", prices[peaks], " len : ", len(prices[peaks]))
            print(" prices troughs : ", prices[troughs], " len : ", len(prices[troughs]))

            # Flag confirmed uptrend points (next peak > previous peak & next trough > previous trough)
            if trend_signals:
                print(f"stock {ticket} entering an uptrend wave ")
                list_ticker_uptrend.append(ticket)

            # Flag stocks where the next trough is higher than the previous one; peaks don't matter here
            elif len(prices[troughs]) >= 2:
                count = 0
                for i in range(1, len(troughs)):
                    if prices[troughs[i]] >= prices[troughs[i - 1]]:
                        count += 1
                if count > 0:
                    print(f"stock {ticket} entering an uptrend wave ")
                    list_ticker_2_bottom.append(ticket)

        if len(list_ticker_uptrend) > 1:
            data.append({"hh_hl": list_ticker_uptrend})
        if len(list_ticker_2_bottom) > 1:
            data.append({"2_bottom": list_ticker_2_bottom})

        if len(data) > 1:
            Common.create_json_file(data, etl_path, "hh_hl")

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f'"execution_time": {execution_time:.2f}')


if __name__ == '__main__':
    HhHl().main()


def python_operator_run(**kwargs):
    HhHl().main()
