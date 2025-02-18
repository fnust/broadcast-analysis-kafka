import json
import os
import random
import time

import numpy as np
import pandas as pd
from confluent_kafka import Producer


class CommentProducer:
    def __init__(self, csv_file):
        self.bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS", "localhost:9095")
        self.topic = os.getenv("TOPIC", "new_comment")
        self.csv_file = csv_file
        self.conf = {"bootstrap.servers": self.bootstrap_servers}
        self.producer = Producer(self.conf)

    def generate_comment_data(self, text):
        mu = 5
        sigma = 1

        return {
            "text": text,
            "subscribers": int(np.round(np.random.lognormal(mean=mu, sigma=sigma))),
            "timestamp": int(time.time()),
        }

    def produce_comment_data(self):
        comments_df = pd.read_csv(self.csv_file)

        for index, row in comments_df.iterrows():
            comment_text = row["comment_text"]
            comment_data = self.generate_comment_data(comment_text)
            self.producer.produce(
                self.topic, key=str(index), value=json.dumps(comment_data)
            )
            self.producer.flush()
            print("Produced:", comment_data)
            time.sleep(random.uniform(1, 4))


if __name__ == "__main__":
    print("CommentService started!")
    csv_file = os.path.join("data", "comments.csv")
    comment_producer = CommentProducer(csv_file)
    comment_producer.produce_comment_data()
