from flask import request, jsonify
from app import app, db
from models import MoodEntry

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