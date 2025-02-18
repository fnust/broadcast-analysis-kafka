FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir confluent-kafka 

CMD ["python", "main.py"]