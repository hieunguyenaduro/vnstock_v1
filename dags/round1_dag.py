"""DAG vòng 1: quét 6 chiến lược, chạy 16h00 giờ Việt Nam mỗi ngày."""

from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.timetables.trigger import CronTriggerTimetable

from strategies import hh_hl, ll_lh, rsi_oversold, sma, wave_down, wave_up

# Việt Nam (UTC+7) không có giờ DST nên cron này ổn định quanh năm.
# Tasks tự lấy "hôm nay" theo giờ VN nên dùng Trigger timetable
# (logical_date = giờ chạy) thay vì DataInterval timetable.
VIETNAM_TZ = "Asia/Ho_Chi_Minh"
DAILY_4PM_ICT = CronTriggerTimetable("0 16 * * *", timezone=VIETNAM_TZ)

default_args = {
    "depends_on_past": False,
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="general_strategies",
    default_args=default_args,
    description="Quét 6 chiến lược tuần tự lúc 16h00 giờ Việt Nam mỗi ngày",
    schedule=DAILY_4PM_ICT,
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    # 6 task chiến lược chạy TUẦN TỰ theo thứ tự này (tránh dội rate-limit API
    # khi chạy song song), ghi kết quả ra data/*.json.
    # round2 (filter_strategies) chạy hourly độc lập nên không trigger kèm.
    t1 = PythonOperator(task_id="HH_HL", python_callable=hh_hl.python_operator_run)
    t2 = PythonOperator(task_id="LL_LH", python_callable=ll_lh.python_operator_run)
    t3 = PythonOperator(task_id="WAVE_UP", python_callable=wave_up.python_operator_run)
    t4 = PythonOperator(task_id="WAVE_DOWN", python_callable=wave_down.python_operator_run)
    t5 = PythonOperator(task_id="RSI_OVERSOLD", python_callable=rsi_oversold.python_operator_run)
    t6 = PythonOperator(task_id="SMA", python_callable=sma.python_operator_run)

    t1 >> t2 >> t3 >> t4 >> t5 >> t6

if __name__ == "__main__":
    dag.test(logical_date=datetime(2026, 5, 11, tzinfo=timezone.utc))
