FROM bde2020/spark-base:3.3.0-hadoop3.3

RUN pip install pyspark

WORKDIR /app

COPY ./app /app

CMD ["/spark/bin/spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1", "spark_kafka_consumer.py"]
