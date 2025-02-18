import json
import os
import time

from confluent_kafka import Producer
from connect import CommentDB


class ReplyProducer:
    def __init__(self):
        self.bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS", "localhost:9095")
        self.topic = os.getenv("TOPIC", "new_reply")
        self.conf = {"bootstrap.servers": self.bootstrap_servers}
        self.producer = Producer(self.conf)
        self.comment_db = CommentDB("data/comments.db")

    def produce_reply_data(self):
        while True:
            reply_data = self.comment_db.get_random_comment_id()
            if reply_data:
                self.producer.produce(self.topic, key="1", value=json.dumps(reply_data))
                self.producer.flush()
                print("Produced:", reply_data)
            else:
                print("No data to produce")

            time.sleep(1)


if __name__ == "__main__":
    print("ReplyService started!")
    reply_producer = ReplyProducer()
    reply_producer.produce_reply_data()
