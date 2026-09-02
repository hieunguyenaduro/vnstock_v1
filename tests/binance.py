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



    list_ticket =[]
    for ticker in markets:

        if 'B/USDT' in ticker:
            list_ticket.append(ticker[:-6])
            # print("Các cặp TSLA có trên sàn:", ticker)

    list_remove = ['BNB/USDT', 'USDSB/USDT', 'DGB/USDT', 'TRB/USDT', 'CKB/USDT', 'SHIB/USDT', 'MOB/USDT',
                   'PHB/USDT', 'VIB/USDT', 'AMB/USDT', 'ARB/USDT', 'BB/USDT', 'YB/USDT', 'BNB/USD', 'TRB/USD',
                   'DGB/USD', '1000SHIB/USD', 'PHB/USD', 'CKB/USD', 'ARB/USD', 'AMB/USD', 'BB/USD', 'BROCCOLIF3B/USD',
                   'B/USD', '1000000BOB/USD', 'PTB/USD', 'UB/USD', 'YB/USD', 'LAB/USD', 'GAIB/USD', 'BOB/USD',
                   'BIRB/USD','BSB/USD', 'BRKB/USD', 'RKLB/USD', 'ALAB/USD' ,'BN', 'USDS', 'DG', 'TR', 'CK', 'SHI', 'MO', 'PH', 'VI', 'AM', 'AR', 'B', 'Y']

    for item in list_remove:
        if item in list_ticket:
            list_ticket.remove(item)

    print("ticket tech :", list_ticket)
    print("count ticket :",len( list_ticket))


def sma_50():
    import ccxt

    exchange = ccxt.binance({
        'enableRateLimit': True,
    })

    symbol = 'BTC/USDT'
    timeframe = '1d'

    # Fetch 200 candles
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=200)

    # Extract close prices
    close_prices = [candle[4] for candle in ohlcv]

    # Calculate SMAs from the most recent closing prices
    sma_50 = sum(close_prices[-50:]) / 50
    sma_200 = sum(close_prices[-200:]) / 200

    print(f"SMA 50:  ${sma_50:,.2f}")
    print(f"SMA 200: ${sma_200:,.2f}")

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


    sma_50()
