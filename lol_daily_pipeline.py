# ====================================================
# АВТОМАТИЗАЦИЯ ЕЖЕДНЕВНОГО ПАЙПЛАЙНА ДЛЯ LOL И ОБНОВЛЕНИЯ ДАШБОРДА
# ====================================================

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from scripts.riot_pipeline import run_pipeline
from scripts.EDA import run_exploratory_data_analysis
from scripts.dashboard_etl import run_dashboard_etl

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

    collect_riot_data = PythonOperator(
        task_id="collect_riot_data",
        python_callable=run_pipeline
    )

    run_analytics = PythonOperator(
        task_id="run_eda_analysis",
        python_callable=run_exploratory_data_analysis
    )

    refresh_dashboard = PythonOperator(
        task_id="refresh_dashboard_tables",
        python_callable=run_dashboard_etl
    )

    collect_riot_data >> run_analytics >> refresh_dashboard