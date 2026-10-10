"""Test tín hiệu kỹ thuật bằng DataFrame giả lập — không gọi mạng, không đọc file thật."""

import warnings

import numpy as np
import pandas as pd
import pytest

from strategies.base import BaseStrategy
from strategies.hh_hl import HhHl
from strategies.ll_lh import LlLh
from strategies.wave_down import WaveDown
from strategies.wave_up import WaveUp
from utils.fetch_binance_data import compute_rsi
from utils.fetch_data import FetchData
from utils.fetch_us_stock_data import FetchUsStockData

# Chuỗi tăng cầu thang: đỉnh/đáy đều cao dần, find_peaks(distance=5) bắt được
UPTREND = [10, 11, 12, 13, 14, 15, 14, 13, 14, 15, 16, 17, 16, 15, 16, 17, 18,
           19, 18, 17, 18, 19, 20, 21, 20, 19, 20, 21, 22, 23, 22, 21, 22, 23,
           24, 25, 24, 25, 26, 27]


def make_df(prices):
    return pd.DataFrame({"close": pd.Series(prices, dtype=float)})


def test_hh_hl_detects_uptrend():
    tickers = []
    HhHl.hh_hl(make_df(UPTREND), tickers, "TEST")
    assert tickers == ["TEST"]


def test_hh_hl_flat_market_no_signal():
    tickers = []
    HhHl.hh_hl(make_df([10.0] * 40), tickers, "FLAT")
    assert tickers == []


def test_hh_hl_downtrend_no_uptrend_signal():
    tickers = []
    HhHl.hh_hl(make_df(UPTREND[::-1]), tickers, "DOWN")
    assert tickers == []


def test_ll_lh_detects_downtrend():
    tickers = []
    LlLh.ll_lh(make_df(UPTREND[::-1]), tickers, "D")
    assert tickers == ["D"]


def test_ll_lh_uptrend_no_downtrend_signal():
    tickers = []
    LlLh.ll_lh(make_df(UPTREND), tickers, "U")
    assert tickers == []


def test_signal_guards_invalid_input():
    for bad in (None, pd.DataFrame(), pd.DataFrame({"open": [1.0, 2.0]})):
        assert HhHl.hh_hl(bad, [], "X") is None
        assert LlLh.ll_lh(bad, [], "X") is None
        assert WaveUp.identify_zigzag_waves(bad) == []
        assert WaveDown.identify_zigzag_waves(bad) == []


def test_wave_up_finds_growth_wave():
    df = make_df(np.linspace(100, 140, 50))
    assert WaveUp().plot_growth_waves(df, threshold=10) == 40.0


def test_wave_down_ignores_rising_market():
    df = make_df(np.linspace(100, 140, 50))
    assert WaveDown().plot_growth_waves(df, threshold=10) is None


def test_wave_down_finds_drop_wave():
    df = make_df(np.linspace(140, 100, 50))
    pct = WaveDown().plot_growth_waves(df, threshold=10)
    assert pct is not None and pct <= -10


def test_wave_flat_market_no_signal():
    df = make_df([100.0] * 50)
    assert WaveUp().plot_growth_waves(df, threshold=10) is None
    assert WaveDown().plot_growth_waves(df, threshold=10) is None


def test_wave_zero_price_no_crash_no_warning():
    df = make_df([0.0] * 50)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert WaveUp().plot_growth_waves(df, threshold=10) is None
        assert WaveDown().plot_growth_waves(df, threshold=10) is None


def test_zigzag_guards_divide_by_zero():
    # Giá pivot = 0 không được gây ZeroDivision/Warning, vẫn trả pivots hợp lệ
    pivots = WaveUp.identify_zigzag_waves(make_df([0.0, 0.0, 10.0, 12.0]))
    assert isinstance(pivots, list) and len(pivots) >= 2


def test_rsi_wilder_direction():
    rising = pd.Series(np.linspace(100, 140, 50))
    falling = pd.Series(np.linspace(140, 100, 50))
    assert compute_rsi(rising, period=14).dropna().iloc[-1] > 70
    assert compute_rsi(falling, period=14).dropna().iloc[-1] < 30


def test_rsi_wilder_flat_is_undefined():
    flat = pd.Series([100.0] * 50)
    assert compute_rsi(flat, period=14).isna().all()


def test_rsi_matches_pandas_ta_reference():
    # Chuẩn Wilder có nhiều cách seed warmup; quan trọng là giá trị ổn định
    # sau warmup phải khớp reference trong sai số float.
    pandas_ta = pytest.importorskip("pandas_ta")
    rng = np.random.default_rng(42)
    close = pd.Series(100 + np.cumsum(rng.normal(0, 1, 200)))
    got = compute_rsi(close, period=14)
    want = pandas_ta.rsi(close, length=14)
    assert got.iloc[:14].isna().all()  # warmup chưa đủ 14 nến
    pd.testing.assert_series_equal(got.iloc[14:], want.iloc[14:], check_names=False)


def test_fetch_data_rejects_unknown_timeframe():
    with pytest.raises(ValueError):
        FetchData.fetch_data_for_ticker(
            ticker="VIC", timeframe="9Z", start_date="2024-01-01", end_date="2024-02-01"
        )


def test_normalize_twelvedata_interval():
    # TwelveData chỉ nhận 1day/1week/1month/5min..., không nhận kiểu yfinance 1d/1w/15m
    norm = FetchUsStockData.normalize_interval
    assert norm("1d") == "1day"
    assert norm("1D") == "1day"
    assert norm("1day") == "1day"
    assert norm("1h") == "1h"
    assert norm("4h") == "4h"
    assert norm("15m") == "15min"
    assert norm("5m") == "5min"
    assert norm("1w") == "1week"
    assert norm("1M") == "1month"


def test_base_strategy_saves_empty_list(tmp_path):
    s = BaseStrategy(name="test")
    f = s.save_signal("my_key", [], filename="my_key", etl_path=str(tmp_path))
    assert f.exists()
    import json

    assert json.loads(f.read_text(encoding="utf-8")) == [{"my_key": []}]


def test_base_strategy_safe_call_survives_error(caplog):
    s = BaseStrategy(name="test")

    def boom(ticker):
        raise RuntimeError("mang loi")

    with caplog.at_level("ERROR"):
        assert s.safe_call(boom, "VIC") is None
    assert any("VIC" in r.message for r in caplog.records)
