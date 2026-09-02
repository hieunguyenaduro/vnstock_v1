from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

from strategies import hh_hl, ll_lh, rsi_oversold, wave_down, wave_up, sma

default_args = {
    "depends_on_past": False,
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="tutorial",
    default_args=default_args,
    description="A simple tutorial DAG running parallel strategy tasks",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    t1 = PythonOperator(
        task_id="HH_HL",
        python_callable=hh_hl.python_operator_run,
    )

    t2 = PythonOperator(
        task_id="LL_LH",
        python_callable=ll_lh.python_operator_run,
    )

    t3 = PythonOperator(
        task_id="WAVE_UP",
        python_callable=wave_up.python_operator_run,
    )

    t4 = PythonOperator(
        task_id="WAVE_DOWN",
        python_callable=wave_down.python_operator_run,
    )

    t5 = PythonOperator(
        task_id="RSI_OVERSOLD",
        python_callable=rsi_oversold.python_operator_run,
    )

    t6 = PythonOperator(
        task_id="SMA",
        python_callable=sma.python_operator_run,
    )


    trigger_next_dag = TriggerDagRunOperator(
        task_id="trigger_target_dag",
        trigger_dag_id="id_cua_dag_tiep_theo",  # Thay tên dag_id bạn muốn kích hoạt vào đây
        conf={"message": "Gửi tham số nếu cần"},  # (Tùy chọn) Truyền tham số/data sang DAG tiếp theo
        wait_for_completion=False,  # True: chờ DAG tiếp theo chạy xong mới đánh giá task này thành công
    )

    # 5 task chiến lược chạy SONG SONG, sau khi TẤT CẢ xong mới gọi trigger_next_dag
    [t1, t2, t3, t4, t5] >> trigger_next_dag

if __name__ == "__main__":
    dag.test(logical_date=datetime(2026, 5, 11, tzinfo=timezone.utc))