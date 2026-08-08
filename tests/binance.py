import ccxt
import pandas as pd
import pandas_ta as ta


def get_binance_rsi(symbol="BTC/USDT", timeframe="1d", period=14, limit=100):
    # 1. Khởi tạo sàn Binance
    exchange = ccxt.binance()

    # 2. Lấy dữ liệu nến (OHLCV) từ Binance
    # timeframe có thể chọn: '1m', '5m', '15m', '1h', '4h', '1d', ...
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    # 3. Chuyển đổi dữ liệu thành DataFrame
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # 4. Tính toán chỉ báo RSI bằng pandas_ta
    df['RSI'] = ta.rsi(df['close'], length=period)

    return df


def get_us_stock_tickers_on_crypto_exchange():
    import ccxt

    # Ví dụ kết nối sàn MEXC hoặc Gate.io
    # exchange = ccxt.mexc()
    # exchange = ccxt.gateio()
    exchange = ccxt.binance()

    # Tải danh sách các cặp giao dịch hiện có trên sàn đó
    markets = exchange.load_markets()

    # Kiểm tra xem sàn có mã TSLA hay không
    # tsla_symbols = [symbol for symbol in markets if 'TSLA' in symbol]
    for ticker in markets:
        if 'B/USDT' in ticker:
            print("Các cặp TSLA có trên sàn:", ticker)


# Run
if __name__ == "__main__":
    symbol = "BTC/USDT"
    timeframe = "1d"

    data = get_binance_rsi(symbol=symbol, timeframe=timeframe, period=14)

    # Hiển thị 5 cây nến mới nhất
    print(f"--- Dữ liệu RSI mới nhất của {symbol} (Khung {timeframe}) ---")
    print(data[['timestamp', 'close', 'RSI']].tail())

    # Giá trị RSI hiện tại (cây nến gần nhất)
    current_rsi = data['RSI'].iloc[-1]
    print(f"\nGiá RSI hiện tại: {current_rsi:.2f}")

    get_us_stock_tickers_on_crypto_exchange()
