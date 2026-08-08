import requests
import logging
import time

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# --- CONFIGURATION ---
# Danh sách các mã cổ phiếu Công nghệ và AI của Mỹ (có thể mở rộng thêm)
TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "META", "TSLA",
    "AMZN", "ORCL", "SPXC", "AMD", "INTC", "CRM", "PLTR",
    "SMCI", "SNPS", "CDNS"
]
RSI_PERIOD = 14
RSI_OVERSOLD_THRESHOLD = 33
API_KEY = "1652ed6172c64a948342413ca45a8ca3"


def get_us_stock_rsi(symbol, interval):
    url = f"https://api.twelvedata.com/rsi?symbol={symbol}&interval={interval}&time_period=14&apikey={API_KEY}"
    response = requests.get(url).json()

    # Lấy giá trị RSI ngày gần nhất
    latest_rsi = response["values"][0]["rsi"]
    print(f"RSI hiện tại của {symbol} là: {latest_rsi}")
    time.sleep(8)

if __name__ == "__main__":
    # Danh sách các mã cổ phiếu Mỹ bạn muốn theo dõi trên Binance
    us_stocks = ["TSLA", "AAPL", "NVDA", "MSFT"]

    for symbol in us_stocks:
        # Lấy RSI theo khung ngày (1d) hoặc khung giờ (1h)
        df = get_us_stock_rsi(symbol=symbol, interval="1day")