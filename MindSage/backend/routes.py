from flask import Flask, request, jsonify
from models import insert_journal_entry, get_journal_entries, insert_mood_entry, get_mood_entries, get_mood_history, user_registration, user_login, token_verification, user_logout
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app) 

@app.route('/journal', methods=['POST'])
def add_journal_entry():
    data = request.get_json()
    id = data.get('id')
    content = data.get('content')
    mood = data.get('mood')

    result = insert_journal_entry(id, content, mood)
    return jsonify(result), 201

@app.route('/api/journal/<id>', methods=['GET'])
def fetch_journal_entries(id):
    result = get_journal_entries(id)
    return jsonify(result), 200

#add mood entries to supabase database
@app.route('/api/add-mood-entry', methods=['POST'])
def add_mood_entry():
    data = request.get_json()

    print("RECEIVED JSON:", data)  

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
        print("ERROR:", e)  
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

# api for user signup
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    result = user_registration(email, password)
    return jsonify(result), 201 if result.get("success") else 400

# api for user login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    result = user_login(email, password)
    return jsonify(result), 200 if result.get("success") else 401

# API for protected routes
@app.route('/api/protected-data', methods=['GET'])
def protected_data():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"error": "Missing token"}), 401

    if token.startswith("Bearer "):
        parts = token.split(" ")
        if len(parts) == 2:
            token = parts[1]
        else:
            return jsonify({"error": "Invalid token format"}), 401

    # Verify the token
    user = token_verification(token)  

    if "error" in user:
        return jsonify(user), 401

    return jsonify({"message": "You do not have the authorization to access this.", "user": user}), 200

#api to logout
@app.route('/api/logout', methods=['POST'])
def logout():
    result = user_logout()
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)


