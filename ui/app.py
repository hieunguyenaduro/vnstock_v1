import gradio as gr
import json, requests

AIRFLOW_URL = "http://localhost:8080/api/v1"
AIRFLOW_AUTH = ("airflow", "airflow")

def load_signals():
    try:
        with open("data/output/final_signals.json") as f:
            data = json.load(f)
        signals = data["signals"]
        rows = []
        for s in signals:
            conf = s.get("confirmations", {})
            row = [
                s["ticker"],
                "🟢 Long" if s.get("signal_type","long") == "long" else "🔴 Short",
                s["total_score"],
                "✅" if conf.get("HH_HL_1D") else "—",
                "✅" if conf.get("RSI_1D_4H") else "—",
                "✅" if conf.get("RSI_1H_confirm") else "—",
            ]
            rows.append(row)
        gen_at = data.get("generated_at","")
        return rows, f"Cập nhật lúc: {gen_at}"
    except Exception as e:
        return [], f"Lỗi: {e}"

def trigger_pipeline():
    try:
        r = requests.post(
            f"{AIRFLOW_URL}/dags/round1_screener/dagRuns",
            json={"conf": {}},
            auth=AIRFLOW_AUTH,
        )
        return f"✅ Đã trigger pipeline — Run ID: {r.json().get('dag_run_id','')}"
    except Exception as e:
        return f"❌ Lỗi trigger: {e}"

with gr.Blocks(title="VN Stock Screener") as app:
    gr.Markdown("## 🇻🇳 VN Stock Screener — Tín hiệu kỹ thuật tự động")

    with gr.Row():
        refresh_btn = gr.Button("🔄 Refresh dữ liệu", variant="secondary")
        run_btn     = gr.Button("▶ Chạy Pipeline ngay", variant="primary")

    status_box = gr.Textbox(label="Trạng thái", interactive=False)

    with gr.Tabs():
        with gr.Tab("📊 Tất cả tín hiệu"):
            table = gr.Dataframe(
                headers=["Ticker","Signal","Score","HH/HL 1D","RSI 4H/1D","RSI 1H"],
                datatype=["str","str","number","str","str","str"],
                interactive=False,
            )
            update_time = gr.Textbox(label="", interactive=False)

    def on_refresh():
        rows, ts = load_signals()
        return rows, ts, "✅ Đã load dữ liệu mới nhất"

    refresh_btn.click(on_refresh, outputs=[table, update_time, status_box])
    run_btn.click(trigger_pipeline, outputs=[status_box])
    app.load(on_refresh, outputs=[table, update_time, status_box])

app.launch(server_port=7860)