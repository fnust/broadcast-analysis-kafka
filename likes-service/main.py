import json
import os
import time

from confluent_kafka import Producer
from connect import CommentDB


class LikeProducer:
    def __init__(self):
        self.bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS", "localhost:9095")
        self.topic = os.getenv("TOPIC", "new_like")
        self.conf = {"bootstrap.servers": self.bootstrap_servers}
        self.producer = Producer(self.conf)
        self.comment_db = CommentDB("data/comments.db")

    def produce_like_data(self):
        while True:
            like_data = self.comment_db.get_random_comment_id()
            if like_data:
                self.producer.produce(self.topic, key="1", value=json.dumps(like_data))
                self.producer.flush()
                print("Produced:", like_data)
            else:
                print("No data to produce")

            time.sleep(1)


if __name__ == "__main__":
    print("LikeService started!")
    like_producer = LikeProducer()
    like_producer.produce_like_data()
