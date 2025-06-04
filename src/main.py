#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from dotenv import load_dotenv

from producers.emission_producer import EmissionDataProducer
from processors.stream_processor import EmissionProcessor
from analytics.databricks_analytics import DatabricksAnalytics

load_dotenv()

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.main [producer|processor|analytics]")
        print("Commands:")
        print("  producer  - Start data ingestion")
        print("  processor - Start stream processing")
        print("  analytics - Run advanced analytics")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "producer":
        print("Starting Carbon Emissions Data Producer...")
        producer = EmissionDataProducer()
        producer.start_streaming()

    elif mode == "processor":
        print("Starting Stream Processor...")
        processor = EmissionProcessor()
        query1, query2 = processor.process_stream()

        try:
            print("Stream processing started. Press Ctrl+C to stop.")
            query1.awaitTermination()
            query2.awaitTermination()
        except KeyboardInterrupt:
            print("Stopping stream processing...")
            query1.stop()
            query2.stop()

    elif mode == "analytics":
        print("Running Advanced Analytics...")
        analytics = DatabricksAnalytics()
        results = analytics.perform_advanced_analytics()

        print("Analytics completed:")
        print(f"Monthly trends: {results['monthly_trends'].count()} records")
        print(f"Facility rankings: {results['facility_rankings'].count()} facilities")
        print(f"Anomalies detected: {results['anomalies'].count()} incidents")

    else:
        print(f"Invalid mode '{mode}'. Use: producer, processor, or analytics")
        sys.exit(1)

if __name__ == "__main__":
    main()
