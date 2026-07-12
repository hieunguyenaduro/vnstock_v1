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

            # 2. Tìm tất cả các Đỉnh và Đáy cục bộ
            # Điều chỉnh distance và prominence tùy theo độ nhiễu của mã chứng khoán
            peaks, _ = find_peaks(prices, distance=5, prominence=1)
            troughs, _ = find_peaks(-prices, distance=5, prominence=1)

            # 3. Thuật toán xác định Điểm Đảo Chiều (HH và HL)
            trend_signals = []

            for i in range(1, len(peaks)):
                # Kiểm tra Đỉnh sau cao hơn Đỉnh trước (Higher High)
                if prices[peaks[i]] > prices[peaks[i - 1]]:
                    # Kiểm tra Đáy gần nhất cũng phải cao hơn Đáy trước đó (Higher Low)
                    # Tìm các đáy nằm giữa hoặc ngay trước 2 đỉnh này
                    recent_troughs = [t for t in troughs if t < peaks[i]]
                    if len(recent_troughs) >= 2:
                        if prices[recent_troughs[-1]] > prices[recent_troughs[-2]]:
                            trend_signals.append(peaks[i])

            print(" prices peaks : ", prices[peaks], " len : ", len(prices[peaks]))
            print(" prices troughs : ", prices[troughs], " len : ", len(prices[troughs]))

            # Đánh dấu điểm xác nhận xu hướng tăng (Đỉnh sau > Đỉnh trước & Đáy sau > Đáy trước)
            if trend_signals:
                print(f"cổ phiếu {ticket} vào sóng uptrend ")
                list_ticker_uptrend.append(ticket)

            # đánh dấu những cổ phiếu nào co đáy sau cao hơn đáy trước, đỉnh không quan trọng
            elif len(prices[troughs]) >= 2:
                count = 0
                for i in range(1, len(troughs)):
                    if prices[troughs[i]] >= prices[troughs[i - 1]]:
                        count += 1
                if count > 0:
                    print(f"cổ phiếu {ticket} vào sóng uptrend ")
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
