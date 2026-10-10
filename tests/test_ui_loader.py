"""Test loader tín hiệu cho UI — chỉ dùng JSON giả trong tmp_path, không mạng."""

import json

from ui.loader import MARKETS, discover_signals, summarize_market


def write(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_discover_reads_all_signal_files(tmp_path):
    write(tmp_path / "us_stock_sma.json", [{"us_stock_sma": ["AAPL", "MSFT"]}])
    write(tmp_path / "us_stock_polarity.json", [{"us_stock_polarity": ["AAPL"]}])
    signals = discover_signals(str(tmp_path))
    assert signals == {"us_stock_sma": ["AAPL", "MSFT"], "us_stock_polarity": ["AAPL"]}


def test_discover_tolerates_bad_files(tmp_path):
    write(tmp_path / "us_stock_sma.json", [{"us_stock_sma": ["AAPL"]}])
    (tmp_path / "us_stock_rsi_oversold.json").write_text("{vo-van", encoding="utf-8")
    (tmp_path / "ghi-chu.txt").write_text("khong phai json", encoding="utf-8")
    signals = discover_signals(str(tmp_path))
    assert signals == {"us_stock_sma": ["AAPL"]}


def test_discover_missing_dir_returns_empty(tmp_path):
    assert discover_signals(str(tmp_path / "khong-ton-tai")) == {}


def test_summarize_groups_by_ticker(tmp_path):
    write(tmp_path / "us_stock_sma.json", [{"us_stock_sma": ["AAPL", "MSFT"]}])
    write(tmp_path / "us_stock_polarity.json", [{"us_stock_polarity": ["AAPL"]}])
    write(tmp_path / "vn_stock_sma.json", [{"vn_stock_sma": ["VIC"]}])
    signals = discover_signals(str(tmp_path))
    summary, detail, updated = summarize_market(signals, str(tmp_path), "us_stock_")
    # AAPL có 2 tín hiệu đứng đầu, MSFT 1 tín hiệu, không lẫn VIC
    assert summary[0][0] == "AAPL" and summary[0][1] == 2
    assert {row[0] for row in summary} == {"AAPL", "MSFT"}
    assert any(row[0] == "SMA" and row[1] == 2 for row in detail)
    assert updated


def test_summarize_empty_market(tmp_path):
    write(tmp_path / "us_stock_sma.json", [{"us_stock_sma": []}])
    signals = discover_signals(str(tmp_path))
    summary, detail, updated = summarize_market(signals, str(tmp_path), "vn_stock_")
    assert summary == [] and detail == []
    assert updated is None


def test_markets_cover_all_prefixes():
    prefixes = {prefix for _, prefix in MARKETS.values()}
    assert prefixes == {"vn_stock_", "us_stock_", "binance_token_"}
