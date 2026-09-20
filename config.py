import os


class Config:
    """
    Configuration class for the stock analysis application.
    Contains constants and settings used throughout the application.
    """

    # Watchlist of stock tickers categorized by industry or sector
    WATCHLIST = {
        "bat dong san": ["vic", "vhm", "agg", "cii", "ceo", "nlg", "pdr", "khg", "ntl", "tch", "dig", "dxg", "dxs"]
    }

    # Automatically flattens all tickers into a single list
    ALL_TICKERS = [t for tickers in WATCHLIST.values() for t in tickers]

    US_TICKERS = ["MU", "CRCL", "NVDA"]

    TOKENS = [
        "BTC/USDT", "ETH/USDT", "LINK/USDT"
    ]


    # Analysis Settings
    RSI_OVERSOLD_THRESHOLD = 33

    # Paths
    OUTPUT_DIR = "data/output"
    RAW_DIR = "data/raw"

    # API Configuration (Safe fallback method)
    # Corrected indentation, capitalization, and added environment variable support
    API_KEY = os.getenv("VNSTOCK_API_KEY", "vnstock_366108191e0a3190950b24d2a04fe157")
    API_KEY_twelvedata = os.getenv("twelvedata", "1652ed6172c64a948342413ca45a8ca3")