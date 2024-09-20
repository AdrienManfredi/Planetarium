from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, FloatType

spark = SparkSession.builder \
    .appName("PlanetDiscoveryConsumer") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

schema = StructType([
    StructField("id", StringType(), True),
    StructField("nom", StringType(), True),
    StructField("decouvreur", StringType(), True),
    StructField("date_de_decouverte", StringType(), True),
    StructField("masse", FloatType(), True),
    StructField("rayon", FloatType(), True),
    StructField("distance", FloatType(), True),
    StructField("type", StringType(), True),
    StructField("statut", StringType(), True),
    StructField("atmosphere", StringType(), True),
    StructField("temperature_moyenne", FloatType(), True),
    StructField("periode_orbitale", FloatType(), True),
    StructField("nombre_de_satellites", FloatType(), True),
    StructField("presence_deau", StringType(), True)
])

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "planet_discoveries") \
    .load()

df_parsed = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

df_parsed.createOrReplaceTempView("planet_discoveries")

mass_avg = spark.sql("SELECT AVG(masse) as avg_masse FROM planet_discoveries")

mass_avg.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start() \
    .awaitTermination()