import json
import os
import re

from confluent_kafka import Consumer, Producer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


class ProcessingCommentConsumer:
    def __init__(self):
        self.bootstrap_servers = os.getenv("INPUT_BOOTSTRAP_SERVERS", "localhost:9095")
        self.topic = os.getenv("INPUT_TOPIC", "new_comment")
        self.consumer = Consumer(
            {"bootstrap.servers": self.bootstrap_servers, "group.id": "my_consumers"}
        )
        self.consumer.subscribe([self.topic])

    def poll(self):
        return self.consumer.poll(500)


class ProcessingCommentProducer:
    def __init__(self):
        self.bootstrap_servers = os.getenv("OUTPUT_BOOTSTRAP_SERVERS", "localhost:9095")
        self.topic = os.getenv("OUTPUT_TOPIC", "processed_comment")
        self.producer = Producer({"bootstrap.servers": self.bootstrap_servers})

    def produce(self, key, value):
        self.producer.produce(self.topic, key=key, value=value)
        self.producer.flush()


def preprocess_comment(comment_data):
    comment = comment_data["text"]
    comment = re.sub(r"[^a-zA-Z#]", " ", comment).lower()
    comment = " ".join([word for word in comment.split() if len(word) > 3])

    wnl = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))
    tokenized = [
        wnl.lemmatize(word) for word in comment.split() if word not in stop_words
    ]

    comment_data["text"] = " ".join(tokenized)

    return comment_data


if __name__ == "__main__":
    consumer = ProcessingCommentConsumer()
    producer = ProcessingCommentProducer()

    print("CommentProcessorService started!")
    while True:
        message = consumer.poll()
        if message is not None and message.value() is not None:
            print("Received data:", message.value().decode("utf-8"))
            comment_data = json.loads(message.value().decode("utf-8"))
            processed_data = preprocess_comment(comment_data)

            print("Processed data:", processed_data)
            producer.produce(key="1", value=json.dumps(processed_data))
