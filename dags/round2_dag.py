from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from strategies import binance_token_1h, us_stock_1h

default_args = {
    "depends_on_past": False,
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
        dag_id="filter_strategies",
        default_args=default_args,
        description="the filter strategies DAG running parallel strategy tasks",
        schedule=None,
        start_date=datetime(2026, 1, 1),
        catchup=False,
) as dag:

    t1 = PythonOperator(
        task_id="BINANCE_RSI_1H",
        python_callable=binance_token_1h.python_operator_run,
        op_kwargs={
            "interval": "1h"
        },
    )

    t2 = PythonOperator(
        task_id="US_STOCK_RSI_1H",
        python_callable=us_stock_1h.python_operator_run,
        op_kwargs={
            "interval": "1h"
        },
    )
    t1 >> t2

if __name__ == "__main__":
    dag.test(logical_date=datetime(2026, 5, 11, tzinfo=timezone.utc))