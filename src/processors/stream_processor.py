#! /usr/bin/env python
# -*- coding: utf-8 -*-
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
import os
from dotenv import load_dotenv

load_dotenv()

class EmissionProcessor:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("CarbonEmissionsProcessor") \
            .config("spark.jars.packages",
                   "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
                   "com.microsoft.sqlserver:mssql-jdbc:12.4.2.jre8") \
            .getOrCreate()

        self.spark.sparkContext.setLogLevel("WARN")

    def create_schema(self):
        return StructType([
            StructField("timestamp", StringType(), True),
            StructField("facility_id", StringType(), True),
            StructField("sensor_id", StringType(), True),
            StructField("emission_type", StringType(), True),
            StructField("emission_value", DoubleType(), True),
            StructField("unit", StringType(), True),
            StructField("temperature", DoubleType(), True),
            StructField("humidity", DoubleType(), True),
            StructField("wind_speed", DoubleType(), True),
            StructField("latitude", DoubleType(), True),
            StructField("longitude", DoubleType(), True)
        ])

    def process_stream(self):
        schema = self.create_schema()

        df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", os.getenv('KAFKA_BOOTSTRAP_SERVERS')) \
            .option("subscribe", "emissions_topic") \
            .option("startingOffsets", "latest") \
            .load()

        parsed_df = df.select(
            from_json(col("value").cast("string"), schema).alias("data")
        ).select("data.*")

        enriched_df = parsed_df \
            .withColumn("processed_timestamp", current_timestamp()) \
            .withColumn("emission_severity",
                       when(col("emission_value") > 50, "HIGH")
                       .when(col("emission_value") > 20, "MEDIUM")
                       .otherwise("LOW")) \
            .withColumn("year", year(to_timestamp(col("timestamp")))) \
            .withColumn("month", month(to_timestamp(col("timestamp")))) \
            .withColumn("day", dayofmonth(to_timestamp(col("timestamp")))) \
            .withColumn("hour", hour(to_timestamp(col("timestamp"))))

        windowed_df = enriched_df \
            .withWatermark("processed_timestamp", "10 minutes") \
            .groupBy(
                window(col("processed_timestamp"), "5 minutes"),
                col("facility_id"),
                col("emission_type")
            ) \
            .agg(
                avg("emission_value").alias("avg_emission"),
                max("emission_value").alias("max_emission"),
                min("emission_value").alias("min_emission"),
                count("*").alias("reading_count"),
                avg("temperature").alias("avg_temperature"),
                avg("humidity").alias("avg_humidity")
            )

        query = enriched_df.writeStream \
            .outputMode("append") \
            .foreachBatch(self.write_to_azure_sql) \
            .option("checkpointLocation", "/tmp/checkpoint") \
            .start()

        aggregated_query = windowed_df.writeStream \
            .outputMode("update") \
            .foreachBatch(self.write_aggregated_to_azure_sql) \
            .option("checkpointLocation", "/tmp/checkpoint_agg") \
            .start()

        return query, aggregated_query

    def write_to_azure_sql(self, df, batch_id):
        df.write \
            .format("jdbc") \
            .option("url", f"jdbc:sqlserver://{os.getenv('AZURE_SQL_SERVER')};databaseName={os.getenv('AZURE_SQL_DATABASE')}") \
            .option("dbtable", "emissions_raw") \
            .option("user", os.getenv('AZURE_SQL_USERNAME')) \
            .option("password", os.getenv('AZURE_SQL_PASSWORD')) \
            .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
            .mode("append") \
            .save()

    def write_aggregated_to_azure_sql(self, df, batch_id):
        df.select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("facility_id"),
            col("emission_type"),
            col("avg_emission"),
            col("max_emission"),
            col("min_emission"),
            col("reading_count"),
            col("avg_temperature"),
            col("avg_humidity")
        ).write \
            .format("jdbc") \
            .option("url", f"jdbc:sqlserver://{os.getenv('AZURE_SQL_SERVER')};databaseName={os.getenv('AZURE_SQL_DATABASE')}") \
            .option("dbtable", "emissions_aggregated") \
            .option("user", os.getenv('AZURE_SQL_USERNAME')) \
            .option("password", os.getenv('AZURE_SQL_PASSWORD')) \
            .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
            .mode("append") \
            .save()

if __name__ == "__main__":
    processor = EmissionProcessor()
    query1, query2 = processor.process_stream()

    try:
        query1.awaitTermination()
        query2.awaitTermination()
    except KeyboardInterrupt:
        print("Stopping stream processing...")
        query1.stop()
        query2.stop()
