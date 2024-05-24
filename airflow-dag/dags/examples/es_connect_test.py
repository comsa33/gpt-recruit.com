from __future__ import annotations

import datetime
import logging
import traceback

import pendulum
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator

local_tz = pendulum.timezone("Asia/Seoul")

required_packages = [
    "apache-airflow-providers-elasticsearch[common.sql]",
]

dag = DAG(
    dag_id="example.es_connect_test",
    description="A simple test for Elasticsearch connection",
    schedule='@once',
    start_date=datetime.datetime(2024, 1, 1, tzinfo=local_tz),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
    tags=["example"],
)


def es_connect_test():
    import logging
    import traceback

    from airflow.providers.elasticsearch.hooks.elasticsearch import ElasticsearchHook

    logging.info("es_connect_test")
    try:
        hook = ElasticsearchHook.get_hook(conn_id="ruo_es")
        es = hook.get_conn().es
        info = es.info()
        logging.info(info)
    except Exception as e:
        logging.error(f"Error: {e}")
        logging.error(traceback.format_exc())
        raise e


with dag:
    logging.info("es_connect_test_task")
    try:
        es_connect_test_task = PythonVirtualenvOperator(
            task_id="es_connect_test",
            python_callable=es_connect_test,
            requirements=required_packages,
        )

        es_connect_test_task
        logging.info("es_connect_test_task done")
    except Exception as e:
        logging.error(f"Error: {e}")
        logging.error(traceback.format_exc())
        raise e
