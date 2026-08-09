from vnstock import *
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from vnstock import register_user

register_user(api_key='vnstock_366108191e0a3190950b24d2a04fe157')

# Hoặc VCI - Dữ liệu đầy đủ hơn nhưng không chạy được trên Colab
quote = Quote(symbol='vnd', source='VCI')

# Hoặc lấy theo khoảng thời gian cụ thể
df = quote.history(start='2026-05-01', end='2026-08-08', interval="1d")


prices = df['close'].values
dates = df['time'].values

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

# 4. Trực quan hóa dữ liệu
plt.figure(figsize=(15, 8))
plt.plot(dates, prices, label='Giá Đóng Cửa', color='gray', alpha=0.5)

# Vẽ Đỉnh/Đáy cục bộ
plt.scatter(dates[peaks], prices[peaks], color='green', marker='^', label='Đỉnh (Highs)', alpha=0.6)
plt.scatter(dates[troughs], prices[troughs], color='red', marker='v', label='Đáy (Lows)', alpha=0.6)

# Đánh dấu điểm ĐẢO CHIỀU (Xác nhận cấu trúc LH + LL)
if reversal_signals:
    plt.scatter(dates[reversal_signals], prices[reversal_signals],
                color='darkred', marker='X', s=250, label='ĐIỂM ĐẢO CHIỀU GIẢM (LH + LL)')

    # Thêm chú thích tại các điểm đảo chiều
    for idx in reversal_signals:
        plt.annotate('Xác nhận Giảm', (dates[idx], prices[idx]),
                     textcoords="offset points", xytext=(0, -20), ha='center', color='darkred', fontweight='bold')

plt.title('Xác Định Điểm Đảo Chiều Xu Hướng: Đỉnh Thấp Hơn & Đáy Thấp Hơn', fontsize=14)
plt.xlabel('Thời gian')
plt.ylabel('Giá (VND)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.3)
plt.show()

# plt.title('Xác nhận Đảo chiều theo Cấu trúc Giá (HH/HL & LH/LL)')
# plt.legend()
# plt.show()