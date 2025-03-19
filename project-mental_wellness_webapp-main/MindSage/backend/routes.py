from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict
from models import (
    extract_emotions, check_suicidal_intent, suggest_activity,
    generate_insights, summarize_journal, insert_journal_entry,
    get_journal_entries, insert_mood_entry, get_mood_entries
)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

### ** Route: Create a journal entry**
@app.route("/add-journal", methods=["POST"])
def add_journal():
    data = request.json
    user_id = data.get("id")
    content = data.get("content")

    if not user_id or not content:
        return jsonify({"error": "Missing user ID or journal content"}), 400

    # Analyze emotions
    emotions = extract_emotions(content)
    dominant_emotion = max(emotions, key=emotions.get) if emotions else "neutral"
    intensity = emotions.get(dominant_emotion, 0.0)
    activity_suggestion = suggest_activity(dominant_emotion, intensity)
    suicide_risk = check_suicidal_intent(content)
    insights = generate_insights(content)
    summary = summarize_journal(content)

    # Save to Supabase
    response = insert_journal_entry(user_id, content, dominant_emotion)

    return jsonify({
        "message": "Journal entry added!",
        "summary": summary,
        "emotions": emotions,
        "dominant_emotion": dominant_emotion,
        "activity_suggestion": activity_suggestion,
        "suicide_risk": suicide_risk,
        "insights": insights,
        "database_response": response
    }), 200
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        text = data.get("text", "")

        emotions = extract_emotions(text)
        dominant_emotion = dominant_emotion_analysis(text, emotions)
        
        intensity = emotions.get(dominant_emotion, 0.5)  # Default to moderate intensity
        activity_suggestion = suggest_activity(dominant_emotion, intensity)
        suicide_risk = check_suicidal_intent(text)
        insights = generate_insights(text, emotions)
        summary = summarize_journal(text)

        return jsonify({
            "message": "Journal entry analyzed!",
            "summary": summary,
            "emotions": emotions,
            "dominant_emotion": dominant_emotion,
            "activity_suggestion": activity_suggestion,
            "suicide_risk": suicide_risk,
            "insights": insights
        }), 200

    except Exception as e:
        print("Error in analyze():", str(e))
        return jsonify({"error": str(e)}), 500

    
def dominant_emotion_analysis(journal_entry: str, emotions: Dict) -> str:
    """
    Determine dominant emotion with additional keyword analysis.
    """
    # Keywords for common emotional states
    stress_keywords = ["stress", "overwhelmed", "pressure", "deadline", "too much", "can't handle"]
    sadness_keywords = ["sad", "unhappy", "depressed", "down", "blue", "miserable"]
    
    # Check for keywords in text
    lower_entry = journal_entry.lower()
    
    # If strong stress indicators are present, override the model
    if any(keyword in lower_entry for keyword in stress_keywords):
        return "stress"
        
    # If strong sadness indicators are present, consider them
    if any(keyword in lower_entry for keyword in sadness_keywords):
        if "sadness" in emotions:
            emotions["sadness"] += 0.2  # Boost sadness score
        else:
            emotions["sadness"] = 0.7
    
    # If no emotions detected or empty dict
    if not emotions:
        return "neutral"
        
    return max(emotions, key=emotions.get)


### **📌 Route: Get all journal entries for a user**
@app.route("/get-journals/<user_id>", methods=["GET"])
def get_journals(user_id):
    response = get_journal_entries(user_id)
    return jsonify(response), 200

### **📌 Route: Add a mood entry**
@app.route("/add-mood", methods=["POST"])
def add_mood():
    data = request.json
    happiness = data.get("happiness")
    anxiety = data.get("anxiety")
    energy = data.get("energy")
    stress = data.get("stress")
    activity = data.get("activity")
    notes = data.get("notes", "")

    if None in [happiness, anxiety, energy, stress, activity]:
        return jsonify({"error": "Missing required mood data"}), 400

    response = insert_mood_entry(happiness, anxiety, energy, stress, activity, notes)
    return jsonify({"message": "Mood entry added!", "database_response": response}), 200

### **📌 Route: Get all mood entries**
@app.route("/get-moods", methods=["GET"])
def get_moods():
    response = get_mood_entries()
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)
