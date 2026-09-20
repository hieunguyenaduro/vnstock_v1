import plotly.graph_objects as go
from vnstock import *
from vnstock import register_user

register_user(api_key='vnstock_366108191e0a3190950b24d2a04fe157')

# Sử dụng nguồn TCBS thay vì VCI để tránh lỗi 503
try:
    quote = Quote(symbol='VJC', source='TCBS')
    df = quote.history(start='2026-07-22', end='2026-09-18', interval="1d")
except Exception as e:
    print("Nguồn TCBS gặp sự cố, đang chuyển sang nguồn DNSE...")
    quote = Quote(symbol='VJC', source='DNSE')
    df = quote.history(start='2026-07-22', end='2026-09-18', interval="1d")

# Kiểm tra dữ liệu trước khi chạy thuật toán
if df is None or df.empty:
    print("Không lấy được dữ liệu trong khoảng thời gian đã chọn.")
else:
    # Các hàm identify_zigzag_waves và plot_growth_waves giữ nguyên
    def identify_zigzag_waves(df, threshold=20):
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

    def plot_growth_waves(df, threshold=20):
        pivots = identify_zigzag_waves(df, threshold)

        pivot_indices = [p[0] for p in pivots]
        pivot_prices = [p[1] for p in pivots]

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df.index, y=df['close'], name='Giá Đóng Cửa', line=dict(color='lightgrey', width=1)))

        fig.add_trace(go.Scatter(x=df.index[pivot_indices], y=pivot_prices,
                                 mode='lines+markers', name=f'Sóng ZigZag >{threshold}%',
                                 line=dict(color='blue', width=2)))

        for i in range(len(pivots) - 1):
            idx_start, price_start, type_start = pivots[i]
            idx_end, price_end, type_end = pivots[i + 1]

            change_pct = (price_end - price_start) / price_start * 100

            if change_pct >= threshold:
                fig.add_trace(go.Scatter(
                    x=df.index[idx_start:idx_end + 1],
                    y=df['close'].iloc[idx_start:idx_end + 1],
                    mode='lines',
                    line=dict(color='limegreen', width=4),
                    showlegend=False
                ))

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

    # Chạy vẽ đồ thị
    plot_growth_waves(df, threshold=10)