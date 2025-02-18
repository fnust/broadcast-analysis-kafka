FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir pandas confluent-kafka numpy

CMD ["python", "main.py"]