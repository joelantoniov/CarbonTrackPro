#! /usr/bin/env python
# -*- coding: utf-8 -*-
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import json
import os
from dotenv import load_dotenv

load_dotenv()

class KafkaManager:
    def __init__(self):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

    def create_topic(self, topic_name, num_partitions=3, replication_factor=1):
        admin_client = KafkaAdminClient(
            bootstrap_servers=self.bootstrap_servers,
            client_id='carbon_track_admin'
        )

        topic = NewTopic(
            name=topic_name,
            num_partitions=num_partitions,
            replication_factor=replication_factor
        )

        try:
            admin_client.create_topics([topic])
            print(f"Topic '{topic_name}' created successfully")
        except Exception as e:
            print(f"Topic creation failed: {e}")

    def get_producer(self):
        return KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )

    def get_consumer(self, topic, group_id):
        return KafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
