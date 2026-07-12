import pandas as pd
import numpy as np
import plotly.graph_objects as go
from vnstock import *

# Đăng ký API (Giữ nguyên của bạn)
register_user(api_key='vnstock_366108191e0a3190950b24d2a04fe157')

# Lấy dữ liệu
quote = Quote(symbol='hhs', source='VCI')
df = quote.history(start='2025-06-01', end='2026-03-14', interval="1D")

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

def plot_decline_waves(df, threshold=10):
    pivots = identify_zigzag_waves(df, threshold)
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
    for i in range(len(pivots) - 1):
        idx_start, price_start, _ = pivots[i]
        idx_end, price_end, _ = pivots[i + 1]

        change_pct = (price_end - price_start) / price_start * 100

        # ĐIỀU KIỆN: Chỉ lấy sóng giảm sâu hơn hoặc bằng ngưỡng threshold (âm)
        if change_pct <= -threshold:
            # Tô màu đỏ cho đoạn sóng giảm
            fig.add_trace(go.Scatter(
                x=df.index[idx_start:idx_end + 1],
                y=df['close'].iloc[idx_start:idx_end + 1],
                mode='lines',
                line=dict(color='crimson', width=4),
                name='Sóng Giảm'
            ))

            # Hiển thị % giảm tại đáy sóng
            fig.add_annotation(
                x=df.index[idx_end], y=price_end,
                text=f"{change_pct:.1f}%",
                showarrow=True, arrowhead=2, ax=0, ay=30,
                font=dict(color="red", size=12),
                bgcolor="white"
            )

    fig.update_layout(title=f'Phân Tích Sóng Giảm (Ngưỡng: -{threshold}%) - {quote.symbol.upper()}',
                      xaxis_title='Thời gian', yaxis_title='Giá',
                      template='plotly_white', showlegend=False)
    fig.show()

# Thực thi
plot_decline_waves(df, threshold=10)