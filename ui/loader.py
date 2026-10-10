"""Đọc file tín hiệu per-strategy trong data/ và gom theo thị trường.

Mỗi strategy ghi 1 file data/<key>.json dạng [{"<key>": ["VIC", ...]}],
luôn ghi kể cả rỗng. Module này chỉ đọc và gom, không gọi mạng.
"""

import json
from datetime import datetime
from pathlib import Path

MARKETS = {
    "vn": ("🇻🇳 VN", "vn_stock_"),
    "us": ("🇺🇸 US", "us_stock_"),
    "crypto": ("🪙 Crypto", "binance_token_"),
}

SIGNAL_LABELS = {
    "sma": "SMA",
    "polarity": "Polarity",
    "094h": "Cool-off RSI",
    "rsi_oversold": "RSI quá bán",
    "rsi_overbought": "RSI quá mua",
    "rsi_oversold_1h": "RSI quá bán 1h",
    "rsi_overbought_1h": "RSI quá mua 1h",
    "wave_up": "Sóng tăng",
    "wave_down": "Sóng giảm",
    "hh_hl": "HH/HL uptrend",
    "ll_hh": "LL/LH downtrend",
}


def pretty_signal(key: str, prefix: str) -> str:
    """us_stock_rsi_oversold_1h -> 'RSI quá bán 1h'. Không khớp thì giữ nguyên key."""
    suffix = key[len(prefix):] if key.startswith(prefix) else key
    return SIGNAL_LABELS.get(suffix, key)


def discover_signals(data_dir) -> dict:
    """Đọc mọi *.json trong data_dir -> {signal_key: [mã]}. File lỗi thì bỏ qua."""
    try:
        files = sorted(Path(data_dir).glob("*.json"))
    except OSError:
        return {}
    signals = {}
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not payload or not isinstance(payload, list):
            continue
        first = payload[0]
        if not isinstance(first, dict):
            continue
        for key, tickers in first.items():
            if isinstance(tickers, list):
                signals[key] = [str(t) for t in tickers]
    return signals


def summarize_market(signals: dict, data_dir, prefix: str):
    """Gom tín hiệu của 1 market.

    Trả về (summary, detail, updated_at):
    - summary: [[mã, số tín hiệu, "tín hiệu 1, tín hiệu 2"]] xếp theo số tín hiệu giảm dần
    - detail: [[tên tín hiệu, số mã, "mã 1, mã 2"]]
    - updated_at: "YYYY-MM-DD HH:MM" của file mới nhất, None nếu chưa có file nào
    """
    by_ticker = {}
    detail = []
    for key in sorted(signals):
        if not key.startswith(prefix):
            continue
        label = pretty_signal(key, prefix)
        tickers = signals[key]
        detail.append([label, len(tickers), ", ".join(tickers)])
        for ticker in tickers:
            by_ticker.setdefault(ticker, []).append(label)
    summary = [
        [ticker, len(labels), ", ".join(labels)]
        for ticker, labels in sorted(by_ticker.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    ]
    try:
        mtimes = [p.stat().st_mtime for p in Path(data_dir).glob(f"{prefix}*.json") if p.is_file()]
    except OSError:
        mtimes = []
    updated_at = datetime.fromtimestamp(max(mtimes)).strftime("%Y-%m-%d %H:%M") if mtimes else None
    return summary, detail, updated_at
