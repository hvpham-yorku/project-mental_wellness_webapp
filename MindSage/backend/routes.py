from flask import Flask, request, jsonify
from models import insert_journal_entry, get_journal_history, get_journal_entry, insert_mood_entry, get_mood_entry, get_mood_history, user_registration, user_login, token_verification, user_logout, get_authenticated_user
from flask_cors import CORS
from flasgger import Swagger
import uuid

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

@app.route('/api/add-journal', methods=['POST'])
def add_journal_entry():
    """
    Add a new journal entry for the authenticated user.
    ---
    parameters:
      - name: content
        in: body
        type: string
        required: true
        description: Content of the journal entry
    responses:
      201:
        description: Journal entry successfully added
        schema:
          type: object
          properties:
            success:
              type: boolean
              description: Success status
            error:
              type: string
              description: Error message
    """
    data = request.get_json()

    # Authenticate user
    user = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = user["id"]
    content = data.get('content')

    # Input validation
    if not content:
        return jsonify({"success": False, "error": "Content is required"}), 400

    result = insert_journal_entry(user_id, content)
    return jsonify(result), 201

# Fetch All Journal Entries for a User
@app.route('/journal', methods=['GET'])
def fetch_journal_entries():
    """
    Fetch all journal entries for the authenticated user.
    ---
    responses:
      200:
        description: A list of journal entries
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: Journal entry ID
              content:
                type: string
                description: Journal entry content
              date:
                type: string
                description: Date of the journal entry
    """
    user = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = user["id"]
    result = get_journal_history(user_id)
    return jsonify(result), 200

# Fetch Specific Journal Entry
@app.route('/journal/<entry_id>', methods=['GET'])
def fetch_journal_entry(entry_id):
    """
    Fetch a specific journal entry for the authenticated user.
    ---
    parameters:
      - name: entry_id
        in: path
        type: string
        required: true
        description: ID of the journal entry
    responses:
      200:
        description: Journal entry details
        schema:
          type: object
          properties:
            data:
              type: object
              description: Journal entry data
            success:
              type: boolean
              description: Success status
      404:
        description: Journal entry not found
    """
    user = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = user["id"]
    result = get_journal_entry(user_id, entry_id)
    if not result:
        return jsonify({"error": "Journal entry not found"}), 404

    return jsonify({"data": result, "success": True}), 200

# Add mood entries
@app.route('/api/add-mood-entry', methods=['POST'])
def add_mood_entry():
    """
    Add a mood entry for the authenticated user.
    ---
    parameters:
      - name: mood
        in: body
        schema:
          type: object
          properties:
            happiness:
              type: number
              format: float
              description: Happiness score
            anxiety:
              type: number
              format: float
              description: Anxiety score
            energy:
              type: number
              format: float
              description: Energy score
            stress:
              type: number
              format: float
              description: Stress score
            activity:
              type: string
              description: Activity description
            notes:
              type: string
              description: Additional notes
        required: true
    responses:
      201:
        description: Mood entry successfully added
    """
    data = request.get_json()

    # Authenticate user
    user = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = user["id"]

    try:
        mood_data = {
            "happiness": float(data.get('happiness', 0)),
            "anxiety": float(data.get('anxiety', 0)),
            "energy": float(data.get('energy', 0)),
            "stress": float(data.get('stress', 0)),
            "activity": str(data.get('activity', "")),
            "notes": str(data.get('notes', ""))
        }

        result = insert_mood_entry(user_id, **mood_data)
        return jsonify({"success": True, "data": result}), 201

    except ValueError as e:
        return jsonify({"error": f"Invalid data type: {e}"}), 400

# Fetch mood entry
@app.route('/mood/<entry_id>', methods=['GET'])
def fetch_mood_entry(entry_id):
    """
    Fetch a specific mood entry for the authenticated user.
    ---
    parameters:
      - name: entry_id
        in: path
        type: string
        required: true
        description: ID of the mood entry
    responses:
      200:
        description: Mood entry details
        schema:
          type: object
          properties:
            data:
              type: object
              description: Mood entry data
            success:
              type: boolean
              description: Success status
      404:
        description: Mood entry not found
    """
    user = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = user["id"]

    result = get_mood_entry(entry_id, user_id)
    if not result:
        return jsonify({"error": "Mood entry not found"}), 404

    return jsonify({"data": result, "success": True}), 200

@app.route('/mood/history', methods=['GET'])
def fetch_mood_history():
    """
    Fetch mood history for the authenticated user.
    ---
    responses:
      200:
        description: A list of mood entries
        schema:
          type: array
          items:
            type: object
            properties:
              happiness:
                type: number
                format: float
                description: Happiness score
              anxiety:
                type: number
                format: float
                description: Anxiety score
              energy:
                type: number
                format: float
                description: Energy score
              stress:
                type: number
                format: float
                description: Stress score
              activity:
                type: string
                description: Activity description
              notes:
                type: string
                description: Additional notes
    """
    user = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = user["id"]
    result = get_mood_history(user_id)

    return jsonify({"data": result, "success": True}), 200

# API for user signup
@app.route('/api/signup', methods=['POST'])
def signup():
    """
    Register a new user.
    ---
    parameters:
      - name: email
        in: body
        type: string
        required: true
        description: User email
      - name: password
        in: body
        type: string
        required: true
        description: User password
    responses:
      201:
        description: User successfully created
      400:
        description: Error during user creation
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    result = user_registration(email, password)
    return jsonify(result), 201 if result.get("success") else 400

# API for user login
@app.route('/api/login', methods=['POST'])
def login():
    """
    Login user with email and password.
    ---
    parameters:
      - name: email
        in: body
        type: string
        required: true
        description: User email
      - name: password
        in: body
        type: string
        required: true
        description: User password
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    result = user_login(email, password)
    return jsonify(result), 200 if result.get("success") else 401

# API for protected routes
@app.route('/api/protected-data', methods=['GET'])
def protected_data():
    """
    Access protected data with a valid token.
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authorization
    responses:
      200:
        description: Protected data accessed
      401:
        description: Unauthorized access
    """
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"error": "Missing token"}), 401

    if token.startswith("Bearer "):
        parts = token.split(" ")
        if len(parts) == 2:
            token = parts[1]
        else:
            return jsonify({"error": "Invalid token format"}), 401

    user = token_verification(token)  

    if "error" in user:
        return jsonify(user), 401

    return jsonify({"message": "You do not have the authorization to access this.", "user": user}), 200

# API to logout
@app.route('/api/logout', methods=['POST'])
def logout():
    """
    Logout the authenticated user.
    ---
    responses:
      200:
        description: Logout successful
      400:
        description: Error during logout
    """
    result = user_logout()
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)
