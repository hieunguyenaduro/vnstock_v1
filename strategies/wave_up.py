import pandas as pd
import numpy as np
import plotly.graph_objects as go

from vnstock import *
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from vnstock import register_user

register_user(api_key='vnstock_366108191e0a3190950b24d2a04fe157')

# Hoặc VCI - Dữ liệu đầy đủ hơn nhưng không chạy được trên Colab
quote = Quote(symbol='vjc', source='VCI')

# Hoặc lấy theo khoảng thời gian cụ thể
df = quote.history(start='2025-01-01', end='2026-04-24', interval="1W")


def identify_zigzag_waves(df, threshold=20):
    """
    Xác định các đỉnh và đáy dựa trên phần trăm biến động.
    """
    # prices = df['Close'].values
    prices = df['close'].values
    n = len(prices)

    # Khởi tạo danh sách các điểm xoay (Pivot Points)
    # Cấu trúc: (index, price, type) | type: 1 cho Đỉnh, -1 cho Đáy
    pivots = [(0, prices[0], 0)]

    last_pivot_price = prices[0]
    last_pivot_idx = 0
    trend = 0  # 1 là đang tăng, -1 là đang giảm

    for i in range(1, n):
        current_price = prices[i]
        price_change = (current_price - last_pivot_price) / last_pivot_price * 100

        if trend == 0:
            if price_change >= threshold:
                trend = 1
            elif price_change <= -threshold:
                trend = -1

        if trend == 1:  # Đang trong xu hướng tăng
            if current_price > last_pivot_price:
                last_pivot_price = current_price
                last_pivot_idx = i
            elif price_change <= -threshold:
                pivots.append((last_pivot_idx, last_pivot_price, 1))
                last_pivot_price = current_price
                last_pivot_idx = i
                trend = -1

        elif trend == -1:  # Đang trong xu hướng giảm
            if current_price < last_pivot_price:
                last_pivot_price = current_price
                last_pivot_idx = i
            elif price_change >= threshold:
                pivots.append((last_pivot_idx, last_pivot_price, -1))
                last_pivot_price = current_price
                last_pivot_idx = i
                trend = 1

    # Thêm điểm cuối cùng vào pivots
    pivots.append((n - 1, prices[-1], 0))
    return pivots


def plot_growth_waves(df, threshold=20):
    pivots = identify_zigzag_waves(df, threshold)

    pivot_indices = [p[0] for p in pivots]
    pivot_prices = [p[1] for p in pivots]

    fig = go.Figure()

    # 1. Vẽ đường giá chính (Candlestick hoặc Line)
    # fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Giá Đóng Cửa', line=dict(color='lightgrey', width=1)))
    fig.add_trace(go.Scatter(x=df.index, y=df['close'], name='Giá Đóng Cửa', line=dict(color='lightgrey', width=1)))

    # 2. Vẽ đường ZigZag nối các Đỉnh/Đáy
    fig.add_trace(go.Scatter(x=df.index[pivot_indices], y=pivot_prices,
                             mode='lines+markers', name=f'Sóng ZigZag >{threshold}%',
                             line=dict(color='blue', width=2)))

    # 3. Tính toán và đánh dấu các đoạn sóng tăng
    for i in range(len(pivots) - 1):
        idx_start, price_start, type_start = pivots[i]
        idx_end, price_end, type_end = pivots[i + 1]

        change_pct = (price_end - price_start) / price_start * 100

        # Chỉ đánh dấu sóng tăng từ 20% trở lên
        if change_pct >= threshold:
            # Tô màu xanh cho đoạn sóng tăng
            fig.add_trace(go.Scatter(
                x=df.index[idx_start:idx_end + 1],
                # y=df['Close'].iloc[idx_start:idx_end + 1],
                y=df['close'].iloc[idx_start:idx_end + 1],
                mode='lines',
                line=dict(color='limegreen', width=4),
                showlegend=False
            ))

            # Hiển thị text % tăng trưởng tại đỉnh
            fig.add_annotation(
                x=df.index[idx_end], y=price_end,
                text=f"+{change_pct:.1f}%",
                showarrow=True, arrowhead=1, ax=0, ay=-30,
                font=dict(color="green", size=12)
            )

    fig.update_layout(title=f'Phân Tích Sóng Tăng Trưởng (Ngưỡng: {threshold}%)',
                      xaxis_title='Thời gian', yaxis_title='Giá',
                      template='plotly_white')
    fig.show()


# --- VÍ DỤ SỬ DỤNG ---
# Giả lập dữ liệu mẫu
# np.random.seed(42)
# dates = pd.date_range('2024-01-01', periods=200)
# prices = 100 + np.cumsum(np.random.normal(0, 5, 200))  # Giá ngẫu nhiên
# df_sample = pd.DataFrame({'Close': prices}, index=dates)

df_sample = df

# Chạy hàm vẽ
plot_growth_waves(df_sample, threshold=10)