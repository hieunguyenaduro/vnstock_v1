import os


class Config:
    """
    Configuration class for the stock analysis application.
    Contains constants and settings used throughout the application.
    """

    # Watchlist of stock tickers categorized by industry or sector
    WATCHLIST = {
        "bat dong san": ["vic", "vhm", "agg", "cii", "ceo", "nlg", "pdr", "khg", "ntl", "tch", "dig", "dxg", "dxs"],
        "chung khoan": ["ssi", "apg", "dsc", "dse", "vck", "vix", "mbs", "vci", "bms", "cts", "fts", "vds", "shs",
                        "vnd", "bsi", "tcx", "vpx", "hcm", "bvs"],
        "ngan hang": ["bvb", "tpb", "msb", "nab", "tcb", "vib", "shb", "vab", "bab", "nvb", "eib", "hdb", "mbb", "ctg",
                      "acb", "vcb", "vpb", "stb", "evf", "ocb", "bid", "lpb"],
        "thep": ["vgs", "nkg", "hsg", "hpg"],  # Removed 'bvh' (Insurance) from here
        "bao hiem": ["bvh"],  # Created a proper home for Bao Viet
        "det may": ["msh", "tng"],
        "ban le": ["frt", "mwg", "pnj", "pet", "dgw", "msn", "vjc", "hvn", "acv"],
        "bds kcn": ["idc", "sip", "ntc", "szc", "szl", "vgc", "kbc", "gvr", "bcm", "tip", "phr"],
        "cong nghe - viettel": ["fpt", "vtp", "ctr"],
        "dien - nangluong": ["geg", "ree", "pow", "gee", "gex"],
        "cang bien - vantai": ["sgp", "gmd", "vsc", "vos"],
        "hoa chat - phancbon - nhua": ["dgc", "dcm", "dpm", "bfc", "las", "csv", "ntp", "bmp", "aaa"],
        "thuc pham - thuy hai san - cao su": ["baf", "pan", "qns", "gdt", "vhc", "anv", "cmx", "dri", "trc"]
    }

    # Automatically flattens all tickers into a single list
    ALL_TICKERS = [t for tickers in WATCHLIST.values() for t in tickers]

    US_TICKERS = [
        "AAPL", "MSFT", "NVDA", "GOOGL", "META", "TSLA",
        "AMZN", "ORCL", "SPXC", "AMD", "INTC", "CRM", "PLTR",
        "SMCI", "SNPS", "CDNS"
    ]

    TOKENS = [
        # "BTC", "ETH", "LINK"
        "OP/USDT"
    ]


    # Analysis Settings
    RSI_OVERSOLD_THRESHOLD = 33

    # Paths
    OUTPUT_DIR = "data/output"
    RAW_DIR = "data/raw"

    # API Configuration (Safe fallback method)
    # Corrected indentation, capitalization, and added environment variable support
    API_KEY = os.getenv('VNSTOCK_API_KEY', 'vnstock_366108191e0a3190950b24d2a04fe157')
    API_KEY_twelvedata = os.getenv('twelvedata', '1652ed6172c64a948342413ca45a8ca3')