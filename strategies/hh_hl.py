from vnstock import *
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from vnstock import register_user
import time

register_user(api_key='vnstock_366108191e0a3190950b24d2a04fe157')

# Hoặc VCI - Dữ liệu đầy đủ hơn nhưng không chạy được trên Colab
quote = Quote(symbol='vds', source='VCI')
start_time = time.perf_counter()
# Hoặc lấy theo khoảng thời gian cụ thể
df = quote.history(start='2026-05-5', end='2026-06-19', interval="1d")

prices = df['close'].values
dates = df['time'].values

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

# 4. Vẽ biểu đồ
plt.figure(figsize=(14, 7))
plt.plot(dates, prices, label='Giá vci', color='lightgray')

# Vẽ tất cả đỉnh/đáy mờ
plt.scatter(dates[peaks], prices[peaks], color='blue', alpha=0.3, label='Đỉnh cục bộ')
plt.scatter(dates[troughs], prices[troughs], color='orange', alpha=0.3, label='Đáy cục bộ')

print (" prices preaks : " ,prices[peaks], " len : ", len(prices[peaks]))
print (" prices troughs : " ,prices[troughs], " len : ", len(prices[troughs]))

if len(prices[peaks])>=2 and len(prices[troughs]) >=2:
    print(f"cổ phếu {quote.symbol} vào sóng uptrend ")

# Đánh dấu điểm xác nhận xu hướng tăng (Đỉnh sau > Đỉnh trước & Đáy sau > Đáy trước)
if trend_signals:
    plt.scatter(dates[trend_signals], prices[trend_signals],
                color='red', marker='*', s=200, label='Xác nhận Xu hướng Tăng (HH+HL)')

plt.title('Xác định Điểm Đảo Chiều Xu Hướng (Higher Highs & Higher Lows)')
plt.legend()
plt.show()
end_time = time.perf_counter()
execution_time = end_time - start_time
print (f'"execution_time": {execution_time:.2f}')