from flask import Flask, request, jsonify, render_template
from kafka import KafkaProducer
import json

app = Flask(__name__)

producer = KafkaProducer(
    bootstrap_servers='kafka:9092', 
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Planet Discovery Form</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .container {
                background-color: #fff;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
            }
            .container h1 {
                margin-bottom: 20px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            .form-group label {
                display: block;
                margin-bottom: 5px;
            }
            .form-group input, .form-group select {
                width: 100%;
                padding: 8px;
                box-sizing: border-box;
            }
            .form-group button {
                background-color: #007BFF;
                color: #fff;
                border: none;
                padding: 10px 20px;
                cursor: pointer;
                border-radius: 4px;
            }
            .form-group button:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
   <div class="container">
    <h1>Planet Information Form</h1>
    <form id="planetForm">
        <div class="form-group">
            <label for="name">Name</label>
            <input type="text" id="name" name="name" required>
        </div>
        <div class="form-group">
            <label for="num_moons">Number of Moons</label>
            <input type="number" id="num_moons" name="num_moons" required>
        </div>
        <div class="form-group">
            <label for="minerals">Minerals</label>
            <input type="text" id="minerals" name="minerals" required>
        </div>
        <div class="form-group">
            <label for="gravity">Gravity (m/s²)</label>
            <input type="number" step="0.01" id="gravity" name="gravity" required>
        </div>
        <div class="form-group">
            <label for="sunlight_hours">Sunlight Hours</label>
            <input type="number" step="0.1" id="sunlight_hours" name="sunlight_hours" required>
        </div>
        <div class="form-group">
            <label for="temperature">Temperature (°C)</label>
            <input type="number" step="0.1" id="temperature" name="temperature" required>
        </div>
        <div class="form-group">
            <label for="rotation_time">Rotation Time (hours)</label>
            <input type="number" step="0.1" id="rotation_time" name="rotation_time" required>
        </div>
        <div class="form-group">
            <label for="water_presence">Water Presence</label>
            <select id="water_presence" name="water_presence" required>
                <option value="yes">Yes</option>
                <option value="no">No</option>
            </select>
        </div>
        <div class="form-group">
            <button type="submit">Submit</button>
        </div>
    </form>
</div>

    <script>
        document.getElementById('planetForm').addEventListener('submit', function(e) {
        e.preventDefault();  // Empêche la soumission classique du formulaire
        
        const formData = {
    name: document.getElementById('name').value,
    num_moons: document.getElementById('num_moons').value,
    minerals: document.getElementById('minerals').value,
    gravity: document.getElementById('gravity').value,
    sunlight_hours: document.getElementById('sunlight_hours').value,
    temperature: document.getElementById('temperature').value,
    rotation_time: document.getElementById('rotation_time').value,
    water_presence: document.getElementById('water_presence').value
};


        fetch('https://opulent-trout-9j7w44g96572vqq-5000.app.github.dev/discovery', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
            
        })
        .then(response => {
        console.log(response)
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            alert('Discovery sent successfully!');
            console.log(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
    </script>
    </body>
    </html>
    '''

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
