import json
import os

from confluent_kafka import Consumer, Producer
from connect import CommentDB
from nltk.sentiment.vader import SentimentIntensityAnalyzer


class SentimentAnalysisConsumer:
    def __init__(self, bootstrap_servers, topic):
        self.consumer = Consumer(
            {"bootstrap.servers": bootstrap_servers, "group.id": topic}
        )
        self.consumer.subscribe([topic])

    def poll(self):
        return self.consumer.poll(200)


class SentimentAnalysisProducer:
    def __init__(self, bootstrap_servers, topic):
        self.producer = Producer({"bootstrap.servers": bootstrap_servers})
        self.topic = topic

    def produce(self, key, value):
        self.producer.produce(self.topic, key=key, value=value)
        self.producer.flush()


def calculate_sentiment_score(data, comment_db):
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(data["text"])["compound"]
    comment_db.insert_record(score, data["subscribers"], data["timestamp"])


def get_current_data(comment_db):
    return comment_db.get_current_data()


if __name__ == "__main__":
    bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS", "localhost:9095")
    comment_topic = os.getenv("COMMENTS_TOPIC", "processed_comment")
    likes_topic = os.getenv("LIKES_TOPIC", "new_like")
    replies_topic = os.getenv("REPLIES_TOPIC", "new_reply")
    output_topic = os.getenv("OUTPUT_TOPIC", "semantic_score")

    commentConsumer = SentimentAnalysisConsumer(bootstrap_servers, comment_topic)
    likeConsumer = SentimentAnalysisConsumer(bootstrap_servers, likes_topic)
    replyConsumer = SentimentAnalysisConsumer(bootstrap_servers, replies_topic)

    producer = SentimentAnalysisProducer(bootstrap_servers, output_topic)
    comment_db = CommentDB("data/comments.db")

    print("SentimentAnalysisService started!")
    while True:
        comment_message = commentConsumer.poll()
        if comment_message is not None and comment_message.value() is not None:
            print("Received data:", comment_message.value().decode("utf-8"))
            comment_data = json.loads(comment_message.value().decode("utf-8"))

            calculate_sentiment_score(comment_data, comment_db)
            broadcast_data = get_current_data(comment_db)
            print("Processed data:", broadcast_data)
            producer.produce(key="1", value=json.dumps(broadcast_data))

        like_message = likeConsumer.poll()
        if like_message is not None and like_message.value() is not None:
            print("Received data:", like_message.value().decode("utf-8"))
            like_data = json.loads(like_message.value().decode("utf-8"))

            broadcast_data = comment_db.increment_likes(like_data["comment_id"])
            broadcast_data = get_current_data(comment_db)
            print("Processed data:", broadcast_data)
            producer.produce(key="1", value=json.dumps(broadcast_data))

        reply_message = replyConsumer.poll()
        if reply_message is not None and reply_message.value() is not None:
            print("Received data:", reply_message.value().decode("utf-8"))
            reply_data = json.loads(reply_message.value().decode("utf-8"))

            broadcast_data = comment_db.increment_replies(reply_data["comment_id"])
            broadcast_data = get_current_data(comment_db)
            print("Processed data:", broadcast_data)
            producer.produce(key="1", value=json.dumps(broadcast_data))
