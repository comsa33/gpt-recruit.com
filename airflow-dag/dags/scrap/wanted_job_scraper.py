import traceback
from datetime import timedelta, datetime

import requests
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.models import Variable

local_tz = pendulum.timezone("Asia/Seoul")
start_date = pendulum.now(tz=local_tz).subtract(days=1)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': start_date,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'scrap.wanted_job_scraper',
    default_args=default_args,
    description='Scrape job listings and details from Wanted',
    schedule_interval='0 0 * * *',  # 매일 00시 실행
    tags=['wanted', 'scrap', 'job'],
)

kakao_access_code = Variable.get("kakao_access_code")
kakao_token_gen_url = Variable.get("kakao_token_gen_url")
kakao_refresh_token_url = Variable.get("kakao_refresh_token_url")
kakao_message_url = Variable.get("kakao_message_url")


# 알림 함수 정의
def send_kakao_message(message):
    try:
        # 한국 시간으로 현재 시간을 가져옴
        now = datetime.now().astimezone(local_tz).strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{now}] {message}"
        headers = {
            'Content-Type': 'application/json',
        }
        data = {
            "object_type": "text",
            "text": message,
            "link": {}
        }
        response = requests.post(kakao_message_url, headers=headers, json=data)
        response.raise_for_status()
        
        if response.json().get('result_code') == 0:
            print("메시지를 성공적으로 보냈습니다.")
        else:
            print("메시지를 성공적으로 보내지 못했습니다. 오류메시지:", response.json())
    
    except Exception as e:
        print("Failed to send Kakao message")
        print(str(e))
        traceback.print_exc()


def scrape_job_ids():
    try:
        response = requests.post("http://ruoserver.iptime.org:32001/api/v1/wanted-joblist/scrape")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        traceback.print_exc()
        raise e


def scrape_job_details():
    try:
        response = requests.post("http://ruoserver.iptime.org:32001/api/v1/wanted-jobdetails/scrape")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        traceback.print_exc()
        raise e


start_task = DummyOperator(
    task_id='start',
    dag=dag,
)

end_task = DummyOperator(
    task_id='end',
    dag=dag,
)

notify_job_list_start = PythonOperator(
    task_id='notify_job_list_start',
    python_callable=send_kakao_message,
    op_args=['원티드 채용정보 job id 수집 시작'],
    dag=dag,
)

notify_job_list_end = PythonOperator(
    task_id='notify_job_list_end',
    python_callable=send_kakao_message,
    op_args=['원티드 채용정보 job id 수집 완료'],
    dag=dag,
)

scrape_job_ids_task = PythonOperator(
    task_id='scrape_job_ids',
    python_callable=scrape_job_ids,
    dag=dag,
)

scrape_job_details_task = PythonOperator(
    task_id='scrape_job_details',
    python_callable=scrape_job_details,
    dag=dag,
)

notify_job_details_start = PythonOperator(
    task_id='notify_job_details_start',
    python_callable=send_kakao_message,
    op_args=['원티드 채용정보 job details 수집 시작'],
    dag=dag,
)

notify_job_details_end = PythonOperator(
    task_id='notify_job_details_end',
    python_callable=send_kakao_message,
    op_args=['원티드 채용정보 job details 수집 완료'],
    dag=dag,
)

# DAG 설정
start_task >> notify_job_list_start >> scrape_job_ids_task >> notify_job_list_end >> notify_job_details_start >> scrape_job_details_task >> notify_job_details_end >> end_task
