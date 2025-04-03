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

### ** Route: Create a Journal Entry**
@app.route("/add-journal", methods=["POST"])
def add_journal():
    data = request.json
    user_id = data.get("id")
    content = data.get("content")

    if not user_id or not content:
        return jsonify({"error": "Missing user ID or journal content"}), 400

    # Analyze emotions
    emotions = extract_emotions(content)
    dominant_emotion = dominant_emotion_analysis(content, emotions)
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


### ** Route: Analyze Emotions in Journal**
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


### ** Dominant Emotion Analysis Function**
def dominant_emotion_analysis(journal_entry: str, emotions: Dict) -> str:
    stress_keywords = ["stress", "overwhelmed", "pressure", "deadline", "too much", "can't handle"]
    sadness_keywords = ["sad", "unhappy", "depressed", "down", "blue", "miserable"]

    lower_entry = journal_entry.lower()

    if any(keyword in lower_entry for keyword in stress_keywords):
        return "stress"

    if any(keyword in lower_entry for keyword in sadness_keywords):
        emotions["sadness"] = emotions.get("sadness", 0.5) + 0.2  # Boost sadness score

    return max(emotions, key=emotions.get) if emotions else "neutral"


### ** Get All Journal Entries**
@app.route("/get-journals/<user_id>", methods=["GET"])
def get_journals(user_id):
    response = get_journal_entries(user_id)
    return jsonify(response), 200


### ** Get All Mood Entries**
@app.route("/get-moods", methods=["GET"])
def get_moods():
    response = get_mood_entries()
    return jsonify(response), 200


if __name__ == "__main__":
    app.run(debug=True)
