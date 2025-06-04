#! /usr/bin/env python
# -*- coding: utf-8 -*-
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window
import os
from dotenv import load_dotenv

load_dotenv()

class DatabricksAnalytics:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("EmissionsAnalytics") \
            .getOrCreate()

    def load_data_from_azure_sql(self):
        return self.spark.read \
            .format("jdbc") \
            .option("url", f"jdbc:sqlserver://{os.getenv('AZURE_SQL_SERVER')};databaseName={os.getenv('AZURE_SQL_DATABASE')}") \
            .option("dbtable", "emissions_raw") \
            .option("user", os.getenv('AZURE_SQL_USERNAME')) \
            .option("password", os.getenv('AZURE_SQL_PASSWORD')) \
            .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
            .load()

    def perform_advanced_analytics(self):
        df = self.load_data_from_azure_sql()

        monthly_trends = df.groupBy("facility_id", "year", "month", "emission_type") \
            .agg(
                sum("emission_value").alias("total_emissions"),
                avg("emission_value").alias("avg_emissions"),
                count("*").alias("measurement_count")
            ) \
            .orderBy("facility_id", "year", "month")

        facility_rankings = df.groupBy("facility_id") \
            .agg(
                sum("emission_value").alias("total_facility_emissions"),
                avg("emission_value").alias("avg_facility_emissions")
            ) \
            .orderBy(desc("total_facility_emissions"))

        emission_correlations = df.select(
            "emission_value",
            "temperature",
            "humidity",
            "wind_speed"
        ).stat.corr("emission_value", "temperature")

        anomaly_detection = df.withColumn(
            "z_score",
            (col("emission_value") - avg("emission_value").over(Window.partitionBy("facility_id"))) /
            stddev("emission_value").over(Window.partitionBy("facility_id"))
        ).filter(abs(col("z_score")) > 2)

        return {
            'monthly_trends': monthly_trends,
            'facility_rankings': facility_rankings,
            'anomalies': anomaly_detection
        }

if __name__ == "__main__":
    analytics = DatabricksAnalytics()
    results = analytics.perform_advanced_analytics()

    print("Analytics completed:")
    print(f"Monthly trends: {results['monthly_trends'].count()} records")
    print(f"Facility rankings: {results['facility_rankings'].count()} facilities")
    print(f"Anomalies detected: {results['anomalies'].count()} incidents")
