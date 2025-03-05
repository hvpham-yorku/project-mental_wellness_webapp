from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import os

app = Flask(__name__)
CORS(app)

# Configure Supabase
SUPABASE_URL = "https://evrttfoulruuijkvrexz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV2cnR0Zm91bHJ1dWlqa3ZyZXh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEyMDQzNTEsImV4cCI6MjA1Njc4MDM1MX0.Lu1CHljWsZTyElj3nTR_Yjtz96LYoiMQxqaajd5_H_c"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Root route
@app.route("/", methods=["GET"])
def home():
    return "Flask server is running!"

# Optional: Handle favicon requests
@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return "", 204  # No content

# API endpoint to add mood entry
@app.route("/api/add-mood-entry", methods=["POST"])
def add_mood_entry():
    data = request.json
    response = supabase.table("mood_entries").insert({
        "happiness": data["happiness"],
        "anxiety": data["anxiety"],
        "energy": data["energy"],
        "stress": data["stress"],
        "activity": data.get("activity", ""),
        "notes": data.get("notes", ""),
    }).execute()
   
    return jsonify({"message": "Mood entry added successfully!"}), 201

# API endpoint to get mood data
@app.route("/api/get-mood-data", methods=["GET"])
def get_mood_data():
    response = supabase.table("mood_entries").select("*").execute()
    return jsonify(response.data), 200

if __name__ == "__main__":
    app.run(debug=True)