"""Base class chung cho mọi chiến lược quét tín hiệu.

Mục tiêu:
- Gom logic lặp lại: khung ngày, đường dẫn ETL, đo thời gian, logging.
- Bọc try/except theo từng mã (per-ticker): 1 mã lỗi không kéo sập cả batch.
- Luôn ghi file JSON kể cả danh sách rỗng để consumer không đọc dữ liệu stale.
"""

import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Optional
from zoneinfo import ZoneInfo

from utils.common import Common

VN_TZ = "Asia/Ho_Chi_Minh"
LOOKBACK_DAYS = 60


def get_logger(name: str) -> logging.Logger:
    """Logger theo tên module. Không gắn handler để app quyết định output."""
    return logging.getLogger(name)


class BaseStrategy:
    """Lớp cha cho HhHl, LlLh, WaveUp, WaveDown, RSIOverSold, SMA, ..."""

    def __init__(self, name: str = "strategy", days: int = LOOKBACK_DAYS) -> None:
        self.name = name
        self.log = get_logger(f"vnstock.{name}")
        self.etl_path = str(Path(__file__).resolve().parents[1])
        now = datetime.now(ZoneInfo(VN_TZ))
        self.execution_date = now.strftime("%Y-%m-%d")
        self.execution_range_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")

    def safe_call(self, func: Callable, ticker: str, *args, default=None, **kwargs):
        """Gọi func(ticker, ...) an toàn: lỗi thì log ERROR và trả default (None)."""
        try:
            return func(ticker, *args, **kwargs)
        except Exception as exc:
            self.log.error("Loi xu ly %s: %s", ticker, exc)
            return default

    def scan_tickers(self, tickers, worker: Callable[[str, list], None]) -> list:
        """Quét từng mã, worker(ticker, found) tự append khi có tín hiệu.

        Mỗi mã được bọc try/except riêng nên 1 mã lỗi không dừng cả batch.
        """
        found: list = []
        for ticker in tickers or []:
            try:
                worker(ticker, found)
            except Exception as exc:
                self.log.error("Loi xu ly %s: %s", ticker, exc)
        return found

    def save_signal(self, key: str, tickers, filename: Optional[str] = None,
                    etl_path: Optional[str] = None) -> Path:
        """Ghi [{"key": [...] }] ra data/<filename>.json, luôn ghi kể cả rỗng."""
        root = etl_path or self.etl_path
        saved = Common.create_json_file([{key: list(tickers or [])}], root, filename or key)
        self.log.info("Ghi %s: %d ma -> %s", key, len(tickers or []), saved)
        return saved

    def run_timed(self, label: str, func: Callable, *args, **kwargs):
        """Chạy func và log thời gian thực thi."""
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            self.log.info("%s xong trong %.2fs", label, elapsed)

    # -- Logic zigzag dùng chung (WaveUp/WaveDown) -------------------------

    @staticmethod
    def identify_zigzag(df, threshold: float = 20) -> list:
        """Xác định pivot zigzag theo % biến động. Input xấu -> [] (không crash)."""
        if df is None or getattr(df, "empty", True):
            return []
        if "close" not in getattr(df, "columns", []) or len(df) < 2:
            return []
        try:
            prices = df["close"].to_numpy(dtype=float)
        except (TypeError, ValueError):
            return []
        if len(prices) < 2:
            return []

        pivots = [(0, prices[0], 0)]
        last_pivot_price = prices[0]
        last_pivot_idx = 0
        trend = 0

        for i in range(1, len(prices)):
            current_price = prices[i]
            if last_pivot_price == 0:
                # Tránh chia cho 0: giá đứng yên ở 0 coi như không biến động
                price_change = 0.0 if current_price == 0 else float("inf")
            else:
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

        pivots.append((len(prices) - 1, prices[-1], 0))
        return pivots

    @staticmethod
    def iter_wave_changes(pivots) -> "object":
        """Yield % biến động từng đoạn sóng, bỏ qua đoạn chia cho 0."""
        for i in range(len(pivots or []) - 1):
            price_start = pivots[i][1]
            price_end = pivots[i + 1][1]
            if price_start == 0:
                continue
            yield (price_end - price_start) / price_start * 100
