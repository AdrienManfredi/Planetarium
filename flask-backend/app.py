from flask import Flask, request, jsonify, render_template
from kafka import KafkaProducer
import json
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

producer = KafkaProducer(
    bootstrap_servers='kafka:9092', 
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/discovery', methods=['POST'])
def add_discovery():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ["name", "num_moons", "minerals", "gravity", "sunlight_hours", "temperature", "rotation_time", "water_presence"]
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing data fields"}), 400

    print(f"Received discovery: {data}")

    # Envoi des données à Kafka
    try:
        producer.send('planet_discoveries', value=data)
        producer.flush()
        print("Data sent to Kafka successfully")
    except Exception as e:
        print(f"Failed to send data to Kafka: {e}")
        return jsonify({"error": "Failed to send data to Kafka"}), 500

    return jsonify({"message": "Discovery sent to Kafka successfully", "data": data}), 200
