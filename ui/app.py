"""VN Stock Screener — hiển thị tín hiệu kỹ thuật từ data/*.json theo 3 thị trường."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gradio as gr
import requests

from ui.loader import MARKETS, discover_signals, summarize_market

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = os.getenv("VNSTOCK_DATA_DIR", str(REPO_ROOT / "data"))
AIRFLOW_URL = os.getenv("AIRFLOW_URL", "http://localhost:8080/api/v1")
AIRFLOW_AUTH = (os.getenv("AIRFLOW_USER", "airflow"), os.getenv("AIRFLOW_PASS", "airflow"))

SUMMARY_HEADERS = ["Ticker", "Số tín hiệu", "Các tín hiệu"]
DETAIL_HEADERS = ["Tín hiệu", "Số mã", "Các mã"]


def load_market(market_key):
    """Đọc tín hiệu 1 thị trường -> (summary, detail, trạng thái). Không bao giờ raise."""
    try:
        _title, prefix = MARKETS[market_key]
        signals = discover_signals(DATA_DIR)
        summary, detail, updated = summarize_market(signals, DATA_DIR, prefix)
        status = f"Cập nhật lúc: {updated}" if updated else "Chưa có dữ liệu — hãy chạy pipeline."
        return summary, detail, status
    except Exception as exc:
        return [], [], f"Lỗi: {exc}"


def load_all():
    """Gom dữ liệu cả 3 thị trường cho nút Refresh và lần load đầu."""
    outputs = []
    for market_key in MARKETS:
        summary, detail, status = load_market(market_key)
        outputs.extend([summary, detail, status])
    return outputs


def trigger_pipeline():
    try:
        r = requests.post(
            f"{AIRFLOW_URL}/dags/general_strategies/dagRuns",
            json={"conf": {}},
            auth=AIRFLOW_AUTH,
            timeout=10,
        )
        r.raise_for_status()
        try:
            run_id = r.json().get('dag_run_id', '')
        except ValueError:
            run_id = ''
        return f"✅ Đã trigger pipeline — Run ID: {run_id}"
    except Exception as e:
        return f"❌ Lỗi trigger: {e}"


with gr.Blocks(title="VN Stock Screener") as app:
    gr.Markdown("## 🇻🇳 VN Stock Screener — Tín hiệu kỹ thuật tự động")

    with gr.Row():
        refresh_btn = gr.Button("🔄 Refresh dữ liệu", variant="secondary")
        run_btn = gr.Button("▶ Chạy Pipeline ngay", variant="primary")

    status_box = gr.Textbox(label="Trạng thái", interactive=False)

    tab_outputs = []
    with gr.Tabs():
        for market_key, (title, _prefix) in MARKETS.items():
            with gr.Tab(title):
                summary_table = gr.Dataframe(
                    headers=SUMMARY_HEADERS,
                    datatype=["str", "number", "str"],
                    interactive=False,
                    label="Tổng hợp theo mã",
                )
                detail_table = gr.Dataframe(
                    headers=DETAIL_HEADERS,
                    datatype=["str", "number", "str"],
                    interactive=False,
                    label="Chi tiết từng tín hiệu",
                )
                update_box = gr.Textbox(label="", interactive=False)
                tab_outputs.extend([summary_table, detail_table, update_box])

    def on_refresh():
        tables = load_all()
        return tables + ["✅ Đã load dữ liệu mới nhất"]

    refresh_btn.click(on_refresh, outputs=tab_outputs + [status_box])
    run_btn.click(trigger_pipeline, outputs=[status_box])
    app.load(load_all, outputs=tab_outputs)


if __name__ == "__main__":
    app.launch(server_port=int(os.getenv("GRADIO_PORT", "7860")))
