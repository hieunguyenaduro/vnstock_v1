from datetime import datetime, timedelta

from airflow import DAG

# Operators; we need this to operate!
from airflow.providers.standard.operators.python import PythonOperator
from strategies import hh_hl

with DAG(
        "tutorial",
        # These args will get passed on to each operator
        # You can override them on a per-task basis during operator initialization
        default_args={
            "depends_on_past": False,
            "email": ["airflow@example.com"],
            "email_on_failure": False,
            "email_on_retry": False,
            "retries": 1,
            "retry_delay": timedelta(minutes=5),
        },
        description="A simple tutorial DAG",
        schedule=None,
        start_date=datetime(2026, 1, 1),
        catchup=False,
) as dag:
    # t1, t2 are examples of tasks created by instantiating operators
    t1 = PythonOperator(
        task_id='HH_HL',
        python_callable=hh_hl.python_operator_run,
        dag=dag)
    t1

if __name__ == "__main__":
    from datetime import datetime, timezone

    dag.test(logical_date=datetime(2026, 5, 11, tzinfo=timezone.utc))
