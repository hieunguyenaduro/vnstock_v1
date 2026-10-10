"""Test cho utils.common — chỉ dùng dữ liệu giả, không gọi mạng."""

import json

import pytest

from utils.common import Common


def test_create_and_read_roundtrip(tmp_path):
    Common.create_json_file([{"us_stock_sma": ["AAPL", "MSFT"]}], str(tmp_path), "us_stock_sma")
    out_file = tmp_path / "data" / "us_stock_sma.json"
    assert out_file.exists()
    assert Common.get_data_from_file(str(out_file), "us_stock_sma") == ["AAPL", "MSFT"]


def test_create_accepts_filename_with_json_suffix(tmp_path):
    # Bao phủ bug cũ: filename là str đã có .json thì .parent crash
    target = tmp_path / "data" / "with.json"
    Common.create_json_file([{"k": [1]}], str(tmp_path), str(target))
    assert target.exists()
    assert Common.get_data_from_file(str(target), "k") == [1]


def test_get_missing_file_returns_empty(tmp_path):
    assert Common.get_data_from_file(str(tmp_path / "khong-ton-tai.json"), "k") == []


def test_get_missing_key_returns_empty(tmp_path):
    f = tmp_path / "a.json"
    f.write_text(json.dumps([{"k": ["X"]}]), encoding="utf-8")
    assert Common.get_data_from_file(str(f), "key-khac") == []


def test_get_malformed_json_returns_empty(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text("{khong-phai-json", encoding="utf-8")
    assert Common.get_data_from_file(str(f), "k") == []


def test_always_write_empty_list(tmp_path):
    # Producer phải luôn ghi file kể cả rỗng để consumer không đọc dữ liệu stale
    Common.create_json_file([{"us_stock_sma": []}], str(tmp_path), "us_stock_sma")
    out_file = tmp_path / "data" / "us_stock_sma.json"
    assert out_file.exists()
    assert Common.get_data_from_file(str(out_file), "us_stock_sma") == []
