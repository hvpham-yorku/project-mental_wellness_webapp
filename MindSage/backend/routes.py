from flask import Flask, request, jsonify
from models import insert_journal_entry, get_journal_entries, get_journal_entry, insert_mood_entry, get_mood_entries, get_mood_history
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app) 

@app.route('/api/add-journal', methods=['POST'])
def add_journal_entry():
    data = request.get_json()

    user_id = data.get('user_id')
    content = data.get('content')
    mood = data.get('mood')  # Optional for journal entries

    print("📌 RECEIVED JSON:", data)  # ✅ Debugging Line

    # Input validation
    if not user_id or not content:
        return jsonify({"success": False, "error": "User ID and content are required"}), 400

    result = insert_journal_entry(user_id, content, mood)
    return jsonify(result), 201

# Fetch All Journal Entries for a User
@app.route('/journal/<user_id>', methods=['GET'])
def fetch_journal_entries(user_id):
    result = get_journal_entries(user_id)
    return jsonify(result), 200

# Fetch Specific Journal Entry
@app.route('/journal/<user_id>/<entry_id>', methods=['GET'])
def fetch_journal_entry(user_id, entry_id):
    result = get_journal_entry(user_id, entry_id)
    return jsonify(result), 200


@app.route('/api/add-mood-entry', methods=['POST'])
def add_mood_entry():
    data = request.get_json()

    print("📌 RECEIVED JSON:", data)  # ✅ Debugging Line

    try:
        happiness = float(data.get('happiness', 0))
        anxiety = float(data.get('anxiety', 0))
        energy = float(data.get('energy', 0))
        stress = float(data.get('stress', 0))
        activity = str(data.get('activity', ""))
        notes = str(data.get('notes', ""))

        result = insert_mood_entry(happiness, anxiety, energy, stress, activity, notes)
        return jsonify({"success": True, "data": result}), 201

    except ValueError as e:
        print("🚨 ERROR:", e)  # ✅ Print error message
        return jsonify({"error": f"Invalid data type: {e}"}), 400
    
@app.route('/mood', methods=['GET'])
def fetch_mood_entries():
    try:
        mood_data = get_mood_entries()
        if mood_data is None:
            return jsonify({"error": "Failed to fetch mood entries"}), 500
        
        return jsonify({"data": mood_data, "success": True}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/mood/<id>', methods=['GET'])
def fetch_mood_history(id):
    result = get_mood_history(id)
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)
