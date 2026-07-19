import time
from pathlib import Path
import plotly.graph_objects as go

from utiils.fetch_data import FetchData
from utiils.common import Common
from config import Config

etl_path = str(Path(__file__).resolve().parents[1])


class WaveDown:

    def __init__(self):
        self.fetcher = FetchData()

    @staticmethod
    def identify_zigzag_waves(df, threshold=10):
        """
        Xác định các đỉnh và đáy dựa trên phần trăm biến động.
        """
        prices = df['close'].values
        n = len(prices)
        pivots = [(0, prices[0], 0)]
        last_pivot_price = prices[0]
        last_pivot_idx = 0
        trend = 0

        for i in range(1, n):
            current_price = prices[i]
            price_change = (current_price - last_pivot_price) / last_pivot_price * 100

            if trend == 0:
                if price_change >= threshold:
                    trend = 1
                elif price_change <= -threshold:
                    trend = -1

            if trend == 1:
                if current_price > last_pivot_price:
                    last_pivot_price = current_price
                    last_pivot_idx = i
                elif price_change <= -threshold:
                    pivots.append((last_pivot_idx, last_pivot_price, 1))
                    last_pivot_price = current_price
                    last_pivot_idx = i
                    trend = -1
            elif trend == -1:
                if current_price < last_pivot_price:
                    last_pivot_price = current_price
                    last_pivot_idx = i
                elif price_change >= threshold:
                    pivots.append((last_pivot_idx, last_pivot_price, -1))
                    last_pivot_price = current_price
                    last_pivot_idx = i
                    trend = 1

        pivots.append((n - 1, prices[-1], 0))
        return pivots

    def plot_growth_waves(self, df, threshold=20):
        pivots = self.identify_zigzag_waves(df, threshold)
        pivot_indices = [p[0] for p in pivots]
        pivot_prices = [p[1] for p in pivots]

        fig = go.Figure()

        # 1. Vẽ đường giá chính
        fig.add_trace(go.Scatter(x=df.index, y=df['close'], name='Giá Đóng Cửa',
                                 line=dict(color='lightgrey', width=1)))

        # 2. Vẽ đường ZigZag tổng quát
        fig.add_trace(go.Scatter(x=df.index[pivot_indices], y=pivot_prices,
                                 mode='lines+markers', name=f'ZigZag {threshold}%',
                                 line=dict(color='rgba(100, 100, 100, 0.5)', width=1, dash='dot')))

        # 3. LỌC VÀ VẼ SÓNG GIẢM >= 10%
        percentage_wave = None
        for i in range(len(pivots) - 1):
            idx_start, price_start, _ = pivots[i]
            idx_end, price_end, _ = pivots[i + 1]

            change_pct = (price_end - price_start) / price_start * 100

            # Chỉ đánh dấu sóng giảm từ 20% trở lên
            if change_pct <= -threshold:
                percentage_wave = change_pct

        return percentage_wave

    def main(self):

        start_time = time.perf_counter()
        data = []
        list_ticker_20_percent = []
        for ticket in Config.ALL_TICKERS:
            df = self.fetcher.fetch_data_for_ticker(ticker=ticket, timeframe='1D', start_date='2026-03-5',
                                                    end_date='2026-05-10')

            percentage_wave = self.plot_growth_waves(df, threshold=10)
            if percentage_wave:
                list_ticker_20_percent.append(ticket)

        data.append({"percentage_wave": list_ticker_20_percent})
        if len(data) > 0:
            Common.create_json_file(data, etl_path, "wave_down")

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f'"execution_time": {execution_time:.2f}')


if __name__ == '__main__':
    WaveDown().main()


def python_operator_run(**kwargs):
    WaveDown().main()
