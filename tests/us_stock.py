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

def get_sma():
    import requests
    # url = "https://api.twelvedata.com/complex_data?apikey={}".format(API_KEY)
    url = f"https://api.twelvedata.com/sma?symbol=TSLA&interval=1day&time_period=50&apikey={API_KEY}"

    response = requests.get(url).json()
    latest_sma = response["values"][0]["sma"]

    # payload = {
    #     "symbols": "TSLA",
    #     "intervals": '1day',
    #     "methods": [
    #         {"name": "sma", "time_period": 50, "outputsize": 1},
    #         {"name": "sma", "time_period": 200, "outputsize": 1}
    #     ]
    # }
    #
    # response = requests.post(url, json=payload)
    # data = response.json()


import yfinance as yf


def get_stock_price(symbol):
    ticker = yf.Ticker(symbol)

    # Fast lookup for fast real-time/latest price
    fast_info = ticker.fast_info
    current_price = fast_info['lastPrice']
    previous_close = fast_info['previousClose']

    print(f"Ticker: {symbol.upper()}")
    print(f"Current Price: ${current_price:.2f}")
    print(f"Previous Close: ${previous_close:.2f}")


def get_stock_data_from_timeseries():
    ticker='AMD'
    """Chỉ gọi 1 API /time_series với outputsize=200 để lấy giá hiện tại + tự tính SMA50 và SMA200"""
    url = f"https://api.twelvedata.com/time_series?symbol={ticker}&interval=1day&outputsize=200&apikey={API_KEY}"

    try:
        res = requests.get(url).json()
        values = res.get("values", [])

        # Cần tối thiểu 200 phiên giao dịch để tính SMA200
        if len(values) < 200:
            return None, None, None

        # Nến mới nhất là values[0]
        current_price = float(values[0]["close"])

        # Lấy giá đóng cửa của 50 và 200 phiên gần nhất
        closes_50 = [float(item["close"]) for item in values[:50]]
        closes_200 = [float(item["close"]) for item in values[:200]]

        sma50 = sum(closes_50) / 50
        sma200 = sum(closes_200) / 200

        print(f"Current Price: ${current_price:.2f}")
        print(f"Current sma50: ${sma50:.2f}")
        print(f"Current sma200: ${sma200:.2f}")

        return current_price, sma50, sma200

    except Exception as e:
        print(f"Lỗi lấy time_series cho mã {ticker}: {e}")
        return None, None, None

if __name__ == "__main__":

    # Example: Get Apple (AAPL) price
    # get_stock_price("AMD")

    get_stock_data_from_timeseries()

    # get_sma()

    # Danh sách các mã cổ phiếu Mỹ bạn muốn theo dõi trên Binance
    us_stocks = ["TSLA", "AAPL", "NVDA", "MSFT"]

    for symbol in us_stocks:
        # Lấy RSI theo khung ngày (1d) hoặc khung giờ (1h)
        df = get_us_stock_rsi(symbol=symbol, interval="1day")