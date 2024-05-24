from __future__ import annotations

import datetime
import logging
import traceback

import pendulum
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator

local_tz = pendulum.timezone("Asia/Seoul")

required_packages = [
    "apache-airflow-providers-mysql[common.sql]",
]

dag = DAG(
    dag_id="example.mysql_connect_test",
    description="A simple test for MySQL connection",
    schedule='@once',
    start_date=datetime.datetime(2024, 1, 1, tzinfo=local_tz),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
    tags=["example"],
)


def mysql_connect_test():
    import logging
    import traceback

    from airflow.providers.mysql.hooks.mysql import MySqlHook

    logging.info("mysql_connect_test")
    try:
        hook = MySqlHook.get_hook(conn_id="ruo_mysql")
        df = hook.get_pandas_df("SELECT * FROM news_scraper.daum_news LIMIT 10")
        logging.info(df.info())
        logging.info(df.head())
    except Exception as e:
        logging.error(f"Error: {e}")
        logging.error(traceback.format_exc())
        raise e


with dag:
    logging.info("mysql_connect_test_task")
    try:
        mysql_connect_test_task = PythonVirtualenvOperator(
            task_id="mysql_connect_test",
            python_callable=mysql_connect_test,
            requirements=required_packages,
        )

        mysql_connect_test_task
        logging.info("mysql_connect_test_task done")
    except Exception as e:
        logging.error(f"Error: {e}")
        logging.error(traceback.format_exc())
        raise e
