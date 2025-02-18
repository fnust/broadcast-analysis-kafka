FROM python:3.9-slim

RUN pip install --no-cache-dir nltk confluent-kafka

RUN python -m nltk.downloader stopwords wordnet

WORKDIR /app

COPY . .

CMD ["python", "main.py"]
