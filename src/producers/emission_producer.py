#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
import os
from dotenv import load_dotenv

load_dotenv()

class EmissionDataProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )

    def generate_emission_data(self):
        facilities = ['Factory_A', 'Factory_B', 'Warehouse_C', 'Office_D', 'Plant_E']
        emission_types = ['CO2', 'CH4', 'N2O', 'HFCs']

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'facility_id': random.choice(facilities),
            'sensor_id': f"SENSOR_{random.randint(1000, 9999)}",
            'emission_type': random.choice(emission_types),
            'emission_value': round(random.uniform(0.1, 100.0), 2),
            'unit': 'tons_co2_eq',
            'temperature': round(random.uniform(-10, 45), 1),
            'humidity': round(random.uniform(30, 90), 1),
            'wind_speed': round(random.uniform(0, 25), 1),
            'latitude': round(random.uniform(40.0, 41.0), 6),
            'longitude': round(random.uniform(-74.0, -73.0), 6)
        }

    def start_streaming(self):
        try:
            while True:
                data = self.generate_emission_data()
                key = f"{data['facility_id']}_{data['sensor_id']}"

                self.producer.send('emissions_topic', key=key, value=data)
                self.producer.flush()

                print(f"Sent: {data}")
                time.sleep(2)

        except KeyboardInterrupt:
            print("Stopping producer...")
        finally:
            self.producer.close()

if __name__ == "__main__":
    producer = EmissionDataProducer()
    producer.start_streaming()
