FROM python:3.9-slim

RUN pip install --no-cache-dir confluent-kafka nltk numpy

RUN python -m nltk.downloader vader_lexicon

WORKDIR /app

COPY . .

CMD ["python", "main.py"]
