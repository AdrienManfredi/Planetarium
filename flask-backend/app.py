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
        <h1>Planet Discovery Form</h1>
        <form id="planetForm">
            <div class="form-group">
                <label for="id">ID</label>
                <input type="text" id="id" name="id" required>
            </div>
            <div class="form-group">
                <label for="nom">Nom</label>
                <input type="text" id="nom" name="nom" required>
            </div>
            <div class="form-group">
                <label for="decouvreur">Découvreur</label>
                <input type="text" id="decouvreur" name="decouvreur" required>
            </div>
            <div class="form-group">
                <label for="date_de_decouverte">Date de Découverte</label>
                <input type="date" id="date_de_decouverte" name="date_de_decouverte" required>
            </div>
            <div class="form-group">
                <label for="masse">Masse</label>
                <input type="number" step="0.01" id="masse" name="masse" required>
            </div>
            <div class="form-group">
                <label for="rayon">Rayon</label>
                <input type="number" step="0.01" id="rayon" name="rayon" required>
            </div>
            <div class="form-group">
                <label for="distance">Distance (en années-lumière)</label>
                <input type="number" step="0.01" id="distance" name="distance" required>
            </div>
            <div class="form-group">
                <label for="type">Type</label>
                <input type="text" id="type" name="type" required>
            </div>
            <div class="form-group">
                <label for="statut">Statut</label>
                <input type="text" id="statut" name="statut" required>
            </div>
            <div class="form-group">
                <label for="atmosphere">Atmosphère</label>
                <input type="text" id="atmosphere" name="atmosphere" required>
            </div>
            <div class="form-group">
                <label for="temperature_moyenne">Température Moyenne (°C)</label>
                <input type="number" step="0.1" id="temperature_moyenne" name="temperature_moyenne" required>
            </div>
            <div class="form-group">
                <label for="periode_orbitale">Période Orbitale (jours)</label>
                <input type="number" step="0.1" id="periode_orbitale" name="periode_orbitale" required>
            </div>
            <div class="form-group">
                <label for="nombre_de_satellites">Nombre de Satellites</label>
                <input type="number" id="nombre_de_satellites" name="nombre_de_satellites" required>
            </div>
            <div class="form-group">
                <label for="presence_deau">Présence d’Eau</label>
                <select id="presence_deau" name="presence_deau" required>
                    <option value="oui">Oui</option>
                    <option value="non">Non</option>
                </select>
            </div>
            <div class="form-group">
                <button type="submit">Envoyer</button>
            </div>
        </form>
    </div>
    <script>
        document.getElementById('planetForm').addEventListener('submit', function(e) {
        e.preventDefault();  // Empêche la soumission classique du formulaire
        
        const formData = {
            id: document.getElementById('id').value,
            nom: document.getElementById('nom').value,
            decouvreur: document.getElementById('decouvreur').value,
            date_de_decouverte: document.getElementById('date_de_decouverte').value,
            masse: document.getElementById('masse').value,
            rayon: document.getElementById('rayon').value,
            distance: document.getElementById('distance').value,
            type: document.getElementById('type').value,
            statut: document.getElementById('statut').value,
            atmosphere: document.getElementById('atmosphere').value,
            temperature_moyenne: document.getElementById('temperature_moyenne').value,
            periode_orbitale: document.getElementById('periode_orbitale').value,
            nombre_de_satellites: document.getElementById('nombre_de_satellites').value,
            presence_deau: document.getElementById('presence_deau').value
        };

        fetch('http://localhost:5000/discovery', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
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

    required_fields = ["id", "nom", "decouvreur", "date_de_decouverte", "masse", "rayon", "distance", "type", "statut", "atmosphere", "temperature_moyenne", "periode_orbitale", "nombre_de_satellites", "presence_deau"]
    
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
