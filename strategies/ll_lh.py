import time
import json
from pathlib import Path

from scipy.signal import find_peaks
from utiils.fetch_data import FetchData
from config import Config

etl_path = str(Path(__file__).resolve().parents[1])


class HhHl:

    def __init__(self):
        self.fetcher = FetchData()

    @staticmethod
    def create_json_file(data, filename):
        if not filename.endswith('.json'):
            filename = Path(f"{etl_path}/data/{filename}.json")

        filename.parent.mkdir(parents=True, exist_ok=True)

        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

    def main(self):

        start_time = time.perf_counter()

        list_ticker_uptrend = []
        list_ticker_2_bottom = []
        data = []
        for ticket in Config.ALL_TICKERS:
            df = self.fetcher.fetch_data_for_ticker(ticker=ticket, timeframe='1D', start_date='2026-03-5',
                                                    end_date='2026-06-26')
            prices = df['close'].values

            # 2. Tìm Đỉnh (Peaks) và Đáy (Troughs)
            # distance=5: Khoảng cách tối thiểu giữa 2 đỉnh/đáy là 5 phiên
            # prominence=1: Độ cao chênh lệch tối thiểu để coi là 1 đỉnh/đáy rõ nét
            peaks, _ = find_peaks(prices, distance=5, prominence=1)
            troughs, _ = find_peaks(-prices, distance=5, prominence=1)

            # 3. Thuật toán xác định Điểm Đảo Chiều Giảm (LH + LL)
            reversal_signals = []

            # Chúng ta duyệt qua các đáy để tìm Lower Low (LL)
            for i in range(1, len(troughs)):
                current_trough_idx = troughs[i]
                prev_trough_idx = troughs[i - 1]

                # ĐIỀU KIỆN 1: Đáy sau thấp hơn đáy trước (Lower Low)
                if prices[current_trough_idx] < prices[prev_trough_idx]:

                    # ĐIỀU KIỆN 2: Tìm các đỉnh nằm trước đáy hiện tại để kiểm tra Lower High (LH)
                    recent_peaks = [p for p in peaks if p < current_trough_idx]

                    if len(recent_peaks) >= 2:
                        # Nếu đỉnh gần nhất thấp hơn đỉnh trước đó
                        if prices[recent_peaks[-1]] < prices[recent_peaks[-2]]:
                            # Đây là điểm xác nhận đảo chiều xu hướng sang giảm
                            reversal_signals.append(current_trough_idx)

            print(" prices peaks : ", prices[peaks], " len : ", len(prices[peaks]))
            print(" prices troughs : ", prices[troughs], " len : ", len(prices[troughs]))

            # Flag confirmed uptrend points (next peak > previous peak & next trough > previous trough)
            # Đánh dấu điểm ĐẢO CHIỀU (Xác nhận cấu trúc LH + LL)
            if reversal_signals:
                plt.scatter(dates[reversal_signals], prices[reversal_signals],
                            color='darkred', marker='X', s=250, label='ĐIỂM ĐẢO CHIỀU GIẢM (LH + LL)')

            # Flag stocks where the next trough is higher than the previous one; peaks don't matter here
            elif len(prices[troughs]) >= 2:
                count = 0
                for i in range(1, len(troughs)):
                    if prices[troughs[i]] >= prices[troughs[i - 1]]:
                        count += 1
                if count > 0:
                    print(f"stock {ticket} entering an uptrend wave ")
                    list_ticker_2_bottom.append(ticket)

        if len(list_ticker_uptrend)>1:
            data.append({"hh_hl": list_ticker_uptrend})
        if len(list_ticker_2_bottom)>1:
            data.append({"2_bottom": list_ticker_2_bottom})

        if len(data)>1:
            self.create_json_file(data, "hh_hl")

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f'"execution_time": {execution_time:.2f}')


if __name__ == '__main__':
    HhHl().main()


def python_operator_run(**kwargs):
    HhHl().main()