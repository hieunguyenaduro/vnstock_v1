# from datetime import datetime, timedelta, timezone
#
# from airflow import DAG
# from airflow.providers.standard.operators.python import PythonOperator
# from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
# from airflow.models import DagModel
#
# from strategies import hh_hl, ll_lh, rsi_oversold, wave_down, wave_up, sma
#
# default_args = {
#     "depends_on_past": False,
#     "email": ["airflow@example.com"],
#     "email_on_failure": False,
#     "email_on_retry": False,
#     "retries": 0,
#     "retry_delay": timedelta(minutes=5),
# }
#
# with DAG(
#         dag_id="general_strategies",
#         default_args=default_args,
#         description="the general strategies DAG running parallel strategy tasks",
#         schedule=None,
#         start_date=datetime(2026, 1, 1),
#         catchup=False,
# ) as dag:
#     t1 = PythonOperator(
#         task_id="HH_HL",
#         python_callable=hh_hl.python_operator_run,
#     )
#
#     t2 = PythonOperator(
#         task_id="LL_LH",
#         python_callable=ll_lh.python_operator_run,
#     )
#
#     t3 = PythonOperator(
#         task_id="WAVE_UP",
#         python_callable=wave_up.python_operator_run,
#     )
#
#     t4 = PythonOperator(
#         task_id="WAVE_DOWN",
#         python_callable=wave_down.python_operator_run,
#     )
#
#     t5 = PythonOperator(
#         task_id="RSI_OVERSOLD",
#         python_callable=rsi_oversold.python_operator_run,
#     )
#
#     t6 = PythonOperator(
#         task_id="SMA",
#         python_callable=sma.python_operator_run,
#     )
#     dag_trigger_id = "filter_strategies"
#     dag_id_trigger_after_complete = dag_trigger_id.upper()
#
#     dag_model = DagModel()
#     target_dag_model = dag_model.get_dagmodel(dag_id=dag_id_trigger_after_complete)
#
#     is_disabled_dag = target_dag_model.is_paused
#     if not is_disabled_dag:
#         trigger_task_id = f'TRIGGER_DAG_{dag_id_trigger_after_complete}'
#
#         trigger_next_dag = TriggerDagRunOperator(
#             task_id=trigger_task_id,
#             trigger_dag_id=dag_trigger_id,  # Thay tên dag_id bạn muốn kích hoạt vào đây
#             conf={"message": "Gửi tham số nếu cần"},  # (Tùy chọn) Truyền tham số/data sang DAG tiếp theo
#             wait_for_completion=False,  # True: chờ DAG tiếp theo chạy xong mới đánh giá task này thành công
#         )
#
#         # 5 task chiến lược chạy SONG SONG, sau khi TẤT CẢ xong mới gọi trigger_next_dag
#         [t1, t2, t3, t4, t5] >> trigger_next_dag
#     else:
#         # 5 task chiến lược chạy SONG SONG, sau khi TẤT CẢ xong mới gọi trigger_next_dag
#         [t1, t2, t3, t4, t5]
#
# if __name__ == "__main__":
#     dag.test(logical_date=datetime(2026, 5, 11, tzinfo=timezone.utc))



from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

from strategies import hh_hl, ll_lh, rsi_oversold, sma, wave_down, wave_up

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
    description="The general strategies DAG running parallel strategy tasks",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    # 1. Instantiate Strategy Tasks
    t1 = PythonOperator(task_id="HH_HL", python_callable=hh_hl.python_operator_run)
    t2 = PythonOperator(task_id="LL_LH", python_callable=ll_lh.python_operator_run)
    t3 = PythonOperator(task_id="WAVE_UP", python_callable=wave_up.python_operator_run)
    t4 = PythonOperator(task_id="WAVE_DOWN", python_callable=wave_down.python_operator_run)
    t5 = PythonOperator(task_id="RSI_OVERSOLD", python_callable=rsi_oversold.python_operator_run)
    t6 = PythonOperator(task_id="SMA", python_callable=sma.python_operator_run)

    # 2. Trigger Operator (No top-level DB queries)
    trigger_next_dag = TriggerDagRunOperator(
        task_id="TRIGGER_DAG_FILTER_STRATEGIES",
        trigger_dag_id="filter_strategies",
        conf={"message": "send params if needed"},
        wait_for_completion=False,
    )

    # 3. Parallel Execution -> Trigger (Including t6/SMA)
    [t1, t2, t3, t4, t5, t6] >> trigger_next_dag

if __name__ == "__main__":
    dag.test(logical_date=datetime(2026, 5, 11, tzinfo=timezone.utc))