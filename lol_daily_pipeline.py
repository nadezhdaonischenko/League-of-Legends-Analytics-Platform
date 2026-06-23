# ====================================================
# АВТОМАТИЗАЦИЯ ЕЖЕДНЕВНОГО ПАЙПЛАЙНА LOL
# ====================================================

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from main import main as extract_main
from run_transform_load import main as transform_load_main
from EDA import run_exploratory_data_analysis
from dashboard_etl import run_dashboard_etl


default_args = {
    "owner": "NadezhdaO",
    "depends_on_past": False,
    "retries": 2
}


with DAG(
    dag_id="lol_daily_pipeline",
    default_args=default_args,
    description="Daily Riot ETL, analytics and dashboard refresh",
    start_date=datetime(2026, 6, 1),
    schedule="0 2 * * *",
    catchup=False,
    max_active_runs=1,
    tags=["riot", "lol", "analytics", "dash"]
) as dag:
    

    # ---------------- EXTRACT ----------------
    extract_data_task = PythonOperator(
        task_id="extract_riot_data",
        python_callable=extract_main
    )

    # ---------------- TRANSFORM + LOAD ----------------
    transform_load_task = PythonOperator(
        task_id="transform_and_load",
        python_callable=transform_load_main
    )

    # ---------------- EDA ----------------
    run_analytics_task = PythonOperator(
        task_id="run_eda_analysis",
        python_callable=run_exploratory_data_analysis
    )

    # ---------------- DASHBOARD ----------------
    refresh_dashboard_task = PythonOperator(
        task_id="refresh_dashboard_tables",
        python_callable=run_dashboard_etl
    )

    (
        extract_data_task
        >> transform_load_task
        >> run_analytics_task
        >> refresh_dashboard_task
    )