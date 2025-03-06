from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mood_data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Define MoodEntry model
class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    happiness = db.Column(db.Float, nullable=False)
    anxiety = db.Column(db.Float, nullable=False)
    energy = db.Column(db.Float, nullable=False)
    stress = db.Column(db.Float, nullable=False)
    activity = db.Column(db.String(100))
    notes = db.Column(db.String(500))

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
    new_entry = MoodEntry(
        happiness=data["happiness"],
        anxiety=data["anxiety"],
        energy=data["energy"],
        stress=data["stress"],
        activity=data.get("activity", ""),
        notes=data.get("notes", ""),
    )
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"message": "Mood entry added successfully!"}), 201

# API endpoint to get mood data
@app.route("/api/get-mood-data", methods=["GET"])
def get_mood_data():
    entries = MoodEntry.query.all()
    data = [
        {
            "id": entry.id,
            "happiness": entry.happiness,
            "anxiety": entry.anxiety,
            "energy": entry.energy,
            "stress": entry.stress,
            "activity": entry.activity,
            "notes": entry.notes,
        }
        for entry in entries
    ]
    return jsonify(data), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)