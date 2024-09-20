from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, FloatType

spark = SparkSession.builder \
    .appName("PlanetDiscoveryConsumer") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

schema = StructType([
    StructField("name", StringType(), True),
    StructField("num_moons", FloatType(), True),
    StructField("minerals", StringType(), True),
    StructField("gravity", FloatType(), True),
    StructField("sunlight_hours", FloatType(), True),
    StructField("temperature", FloatType(), True),
    StructField("rotation_time", FloatType(), True),
    StructField("water_presence", StringType(), True)
])

spark.sparkContext.setLogLevel("WARN")

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "planet_discoveries") \
    .load()

df_parsed = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

df_parsed.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# Calculer la moyenne des masses des planètes et l'afficher dans la console
mass_avg = df_parsed.selectExpr("AVG(masse) as avg_masse")

mass_avg.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start() \
    .awaitTermination()