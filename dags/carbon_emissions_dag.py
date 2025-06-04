#! /usr/bin/env python
# -*- coding: utf-8 -*-
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
from airflow.providers.microsoft.azure.operators.azure_sql import AzureSqlOperator
from datetime import datetime, timedelta
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'carbon_emissions_pipeline',
    default_args=default_args,
    description='Real-time carbon emissions monitoring and analytics',
    schedule_interval='@hourly',
    catchup=False,
    max_active_runs=1
)

def data_quality_check():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('AZURE_SQL_SERVER')};"
        f"DATABASE={os.getenv('AZURE_SQL_DATABASE')};"
        f"UID={os.getenv('AZURE_SQL_USERNAME')};"
        f"PWD={os.getenv('AZURE_SQL_PASSWORD')}"
    )
    
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT facility_id) as unique_facilities,
                AVG(emission_value) as avg_emission,
                MAX(processed_timestamp) as latest_record
            FROM emissions_raw 
            WHERE processed_timestamp >= DATEADD(hour, -1, GETDATE())
        """)
        
        result = cursor.fetchone()
        print(f"Quality Check - Records: {result[0]}, Facilities: {result[1]}, Avg Emission: {result[2]}")
        
        if result[0] == 0:
            raise ValueError("No new records found in the last hour")

def generate_compliance_report():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('AZURE_SQL_SERVER')};"
        f"DATABASE={os.getenv('AZURE_SQL_DATABASE')};"
        f"UID={os.getenv('AZURE_SQL_USERNAME')};"
        f"PWD={os.getenv('AZURE_SQL_PASSWORD')}"
    )
    
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO compliance_reports (
                report_date,
                facility_id,
                total_emissions,
                compliance_status,
                threshold_exceeded_count
            )
            SELECT 
                CAST(GETDATE() AS DATE),
                facility_id,
                SUM(emission_value) as total_emissions,
                CASE 
                    WHEN SUM(emission_value) > 1000 THEN 'NON_COMPLIANT'
                    WHEN SUM(emission_value) > 500 THEN 'WARNING'
                    ELSE 'COMPLIANT'
                END as compliance_status,
                SUM(CASE WHEN emission_value > 50 THEN 1 ELSE 0 END) as threshold_exceeded_count
            FROM emissions_raw
            WHERE CAST(processed_timestamp AS DATE) = CAST(GETDATE() AS DATE)
            GROUP BY facility_id
        """)
        
        conn.commit()
        print(f"Compliance report generated for {cursor.rowcount} facilities")

quality_check_task = PythonOperator(
    task_id='data_quality_check',
    python_callable=data_quality_check,
    dag=dag
)

databricks_analytics_task = DatabricksSubmitRunOperator(
    task_id='run_analytics',
    databricks_conn_id='databricks_default',
    existing_cluster_id='your-cluster-id',
    notebook_task={
        'notebook_path': '/Workspace/emissions_analytics',
        'base_parameters': {
            'date': '{{ ds }}',
            'environment': 'production'
        }
    },
    dag=dag
)

compliance_report_task = PythonOperator(
    task_id='generate_compliance_report',
    python_callable=generate_compliance_report,
    dag=dag
)

alerting_task = AzureSqlOperator(
    task_id='check_alerts',
    azure_sql_conn_id='azure_sql_default',
    sql="""
        INSERT INTO alerts (alert_timestamp, facility_id, alert_type, message, severity)
        SELECT 
            GETDATE(),
            facility_id,
            'HIGH_EMISSION',
            'Emission levels exceeded threshold: ' + CAST(emission_value AS VARCHAR),
            'CRITICAL'
        FROM emissions_raw
        WHERE emission_value > 75 
        AND processed_timestamp >= DATEADD(hour, -1, GETDATE())
        AND facility_id NOT IN (
            SELECT facility_id FROM alerts 
            WHERE alert_timestamp >= DATEADD(hour, -1, GETDATE())
            AND alert_type = 'HIGH_EMISSION'
        )
    """,
    dag=dag
)

quality_check_task >> databricks_analytics_task >> compliance_report_task >> alerting_task
