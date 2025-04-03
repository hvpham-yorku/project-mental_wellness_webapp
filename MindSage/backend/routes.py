import requests
import os
import uuid
import time
from dotenv import load_dotenv
from supabase import create_client, Client
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
from typing import Dict, Optional, List, Tuple

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Optional[Client] = None
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Error initializing Supabase client: {e}")

# Hugging Face API details
HF_API_KEY = os.getenv("HF_API_KEY")
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# Hugging Face model endpoints
EMOTION_MODEL_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
INSIGHT_MODEL_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
SUMMARY_MODEL_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

# Suicide prevention keywords
SUICIDE_KEYWORDS = [
    "want to die", "end my life", "no reason to live", "kill myself",
    "suicidal", "give up", "not worth living", "can't take it anymore",
    "better off dead", "goodbye forever"
]

# Activity suggestions based on dominant emotion
ACTIVITY_SUGGESTIONS = {
    "anger": {"low": "Try journaling about your feelings.", "moderate": "Practice deep breathing or count to ten.", "high": "Take a walk or exercise to release tension."},
    "fear": {"low": "Use positive affirmations.", "moderate": "Try 5-4-3-2-1 grounding technique.", "high": "Reach out to someone you trust for reassurance."},
    "sadness": {"low": "Listen to uplifting music.", "moderate": "Practice self-care activities you enjoy.", "high": "Connect with a supportive friend or family member."},
    "joy": {"low": "Write down what made you happy today.", "moderate": "Share your happiness with others.", "high": "Celebrate and fully embrace this positive feeling!"},
    "surprise": {"low": "Take a moment to reflect on the unexpected.", "moderate": "Journal about how this surprise affected you.", "high": "Share your experience with someone close to you."},
    "disgust": {"low": "Take a short mental break.", "moderate": "Practice mindfulness meditation.", "high": "Change your environment or surroundings temporarily."},
    "neutral": {"low": "Try a short mindfulness exercise.", "moderate": "Take a refreshing walk outside.", "high": "Engage in a creative activity you enjoy."},
    "stress": {"low": "Take five deep breaths.", "moderate": "Practice progressive muscle relaxation.", "high": "Consider talking to someone about what's causing stress."},
    "overwhelmed": {"low": "Make a prioritized to-do list.", "moderate": "Break large tasks into smaller, manageable steps.", "high": "Reach out for support and delegate if possible."},
    "anxious": {"low": "Practice box breathing.", "moderate": "Try a guided meditation for anxiety.", "high": "Consider talking to a mental health professional."}
}

def handle_huggingface_error(error_message: str) -> Dict:
    """Handle common Hugging Face API errors with appropriate responses."""
    if "currently loading" in error_message:
        return {"error": "Model is still loading. Please try again in a moment."}
    elif "rate limit" in error_message:
        return {"error": "Too many requests. Please try again later."}
    else:
        return {"error": f"API error: {error_message}"}

def query_huggingface_with_backoff(url: str, payload: Dict, max_retries: int = 3, initial_wait: float = 1.0) -> Optional[Dict]:
    """Query Hugging Face API with exponential backoff for reliability."""
    wait_time = initial_wait
    for attempt in range(max_retries):
        response = requests.post(url, headers=HEADERS, json=payload)
        # If successful, return the response
        if response.status_code == 200:
            return response.json()
        # Handle model loading status
        elif response.status_code == 503 and "loading" in response.text.lower():
            print(f"Model is loading. Waiting {wait_time}s before retry {attempt+1}/{max_retries}")
            time.sleep(wait_time)
            wait_time *= 2  # Exponential backoff
        # Handle rate limits
        elif response.status_code == 429:
            print(f"Rate limited. Waiting {wait_time}s before retry {attempt+1}/{max_retries}")
            time.sleep(wait_time)
            wait_time *= 2  # Exponential backoff
        # Other errors
        else:
            print(f"Error {response.status_code}: {response.text}")
            if attempt == max_retries - 1:  # Last attempt
                return None
            time.sleep(wait_time)
            wait_time *= 2  # Exponential backoff
    return None

def extract_emotions(journal_entry: str) -> Dict:
    """
    Extract emotions from a journal entry using Hugging Face API.
    Returns a dictionary of emotions and their scores.
    """
    if not journal_entry.strip():
        return {"neutral": 1.0}
    # Truncate text if too long (model likely has a token limit)
    max_length = 1024
    truncated_entry = journal_entry[:max_length]
    payload = {"inputs": truncated_entry}
    result = query_huggingface_with_backoff(EMOTION_MODEL_URL, payload)
    if not result:
        print("❌ Failed to extract emotions")
        return {"neutral": 1.0}
    try:
        emotions = result[0]
        return {e["label"]: e["score"] for e in emotions}
    except (KeyError, IndexError, TypeError) as e:
        print(f"🚨 Error parsing emotion response: {e}")
        return {"neutral": 1.0}

def dominant_emotion_analysis(journal_entry: str, emotions: Dict) -> Tuple[str, float]:
    """
    Determine dominant emotion with keyword analysis.
    Returns tuple of (emotion_name, intensity)
    """
    # Define keywords for different emotional states
    emotion_keywords = {
        "stress": ["stress", "overwhelmed", "pressure", "deadline", "too much", "can't handle", "stressed"],
        "sadness": ["sad", "unhappy", "depressed", "down", "blue", "miserable", "lonely", "grief"],
        "anger": ["angry", "annoyed", "mad", "furious", "upset", "frustrated", "irritated"],
        "fear": ["afraid", "scared", "fearful", "terrified", "anxious", "worried", "nervous"],
        "joy": ["happy", "excited", "joyful", "delighted", "thrilled", "pleased", "content"],
        "anxious": ["anxiety", "anxious", "panic", "worry", "tense", "uneasy"]
    }
    # If no emotions provided or empty dict, run text analysis
    if not emotions:
        emotions = {"neutral": 1.0}
    # Get the base dominant emotion from model output
    base_dominant = max(emotions, key=emotions.get)
    base_intensity = emotions.get(base_dominant, 0.5)
    # Check for keyword overrides
    lower_entry = journal_entry.lower()
    for emotion, keywords in emotion_keywords.items():
        matches = [keyword for keyword in keywords if keyword in lower_entry]
        if matches:
            # If we have explicit keyword matches, boost or create this emotion
            match_count = len(matches)
            keyword_boost = min(0.1 * match_count, 0.3)  # Cap the boost at 0.3
            if emotion in emotions:
                emotions[emotion] += keyword_boost
            else:
                emotions[emotion] = 0.6 + keyword_boost
    # Recalculate dominant after keyword analysis
    final_dominant = max(emotions, key=emotions.get)
    final_intensity = emotions.get(final_dominant, 0.5)
    return final_dominant, final_intensity

def check_suicidal_intent(journal_entry: str) -> bool:
    """
    Check if the journal entry contains suicide-related keywords.
    """
    lower_entry = journal_entry.lower()
    return any(keyword in lower_entry for keyword in SUICIDE_KEYWORDS)

def suggest_activity(dominant_emotion: str, intensity: float) -> str:
    """
    Suggest activities based on the dominant emotion and its intensity.
    """
    if dominant_emotion not in ACTIVITY_SUGGESTIONS:
        return "Try taking a short walk or practicing mindfulness."
    if intensity < 0.3:
        return ACTIVITY_SUGGESTIONS[dominant_emotion]["low"]
    elif intensity < 0.7:
        return ACTIVITY_SUGGESTIONS[dominant_emotion]["moderate"]
    else:
        return ACTIVITY_SUGGESTIONS[dominant_emotion]["high"]

def generate_insights(journal_entry: str, emotions: Dict = None) -> str:
    """
    Generate insights based on extracted emotions.
    """
    if not journal_entry.strip():
        return "Please provide more text to generate meaningful insights."
    if not emotions or len(emotions) == 0:
        emotions = extract_emotions(journal_entry)
    if not emotions or len(emotions) == 0:
        return "No insights available due to missing emotion data."
    dominant_emotion, intensity = dominant_emotion_analysis(journal_entry, emotions)
    # Create a prompt for the insight model
    prompt = (
        f"As a compassionate therapist, analyze this journal entry: '{journal_entry[:400]}...' "
        f"The writer's dominant emotion is {dominant_emotion} with {intensity:.2f} intensity. "
        f"Provide brief, empathetic insights about their emotional state and "
        f"one practical suggestion that could help them."
    )
    payload = {"inputs": prompt}
    result = query_huggingface_with_backoff(INSIGHT_MODEL_URL, payload)
    if not result:
        # Fallback insight generation
        return (f"I notice you're feeling {dominant_emotion} today. "
                f"This is a normal emotion that everyone experiences. "
                f"Consider trying: {suggest_activity(dominant_emotion, intensity)}")
    try:
        return result[0]["generated_text"]
    except (KeyError, IndexError, TypeError):
        return (f"I notice you're feeling {dominant_emotion} today. "
                f"Consider: {suggest_activity(dominant_emotion, intensity)}")

def summarize_journal(journal_entry: str) -> str:
    """
    Generate a brief summary of the journal entry using BART model.
    """
    if not journal_entry.strip() or len(journal_entry) < 50:
        return journal_entry  # Too short to summarize meaningfully
    max_length = 1024
    truncated_entry = journal_entry[:max_length]
    payload = {
        "inputs": truncated_entry,
        "parameters": {
            "max_length": 100,
            "min_length": 30,
            "do_sample": False
        }
    }
    result = query_huggingface_with_backoff(SUMMARY_MODEL_URL, payload)
    if not result:
        # Create a simple fallback summary
        words = journal_entry.split()
        if len(words) <= 20:
            return journal_entry
        return " ".join(words[:20]) + "..."
    try:
        return result[0]["summary_text"]
    except (KeyError, IndexError, TypeError):
        # Another fallback option
        return journal_entry[:100] + "..." if len(journal_entry) > 100 else journal_entry

def insert_journal_entry(user_id: str, content: str, mood: str):
    """
    Inserts a journal entry into Supabase.
    """
    if not supabase:
        return {"error": "Database connection not available"}
    try:
        data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "content": content,
            "mood": mood,
            "created_at": time.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        print("📌 Inserting journal entry for user:", user_id)  
        response = supabase.table("journal_entries").insert(data).execute()
        return response.data
    except Exception as e:
        print(f"🚨 Error inserting journal entry: {e}")
        return {"error": str(e)}

def get_journal_entries(user_id: str):
    """
    Retrieves all journal entries for a specific user.
    """
    if not supabase:
        return {"error": "Database connection not available"}
    try:
        response = supabase.table("journal_entries").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"🚨 Error retrieving journal entries: {e}")
        return {"error": str(e)}

def insert_mood_entry(user_id: str, happiness: int, anxiety: int, energy: int, stress: int, activity: str, notes: str = ""):
    """
    Inserts a mood entry into Supabase.
    """
    if not supabase:
        return {"error": "Database connection not available"}
    try:
        data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "happiness": happiness,
            "anxiety": anxiety,
            "energy": energy,
            "stress": stress,
            "activity": activity,
            "notes": notes,
            "created_at": time.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        print("📌 Inserting mood entry for user:", user_id)  
        response = supabase.table("mood_entries").insert(data).execute()
        return response.data
    except Exception as e:
        print(f"🚨 Error inserting mood entry: {e}")
        return {"error": str(e)}

def get_mood_entries(user_id: str):
    """
    Retrieves all mood entries for a specific user.
    """
    if not supabase:
        return {"error": "Database connection not available"}
    try:
        response = supabase.table("mood_entries").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"🚨 Error retrieving mood entries: {e}")
        return {"error": str(e)}

app = Flask(__name__)
# Configure CORS to accept requests from your React frontend
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint to verify API is running."""
    return jsonify({"status": "healthy", "message": "Journal Analysis API is running"}), 200

### ** Route: Create a Journal Entry **
@app.route("/add-journal", methods=["POST"])
def add_journal():
    """Add a new journal entry, analyze it, and store in database."""
    try:
        data = request.json
        user_id = data.get("user_id")
        content = data.get("content")
        
        # Validate required fields
        if not user_id or not content:
            return jsonify({"error": "Missing required fields: user_id and content"}), 400
        
        # Analyze emotions
        emotions = extract_emotions(content)
        dominant_emotion, intensity = dominant_emotion_analysis(content, emotions)
        
        # Generate helpful responses
        activity_suggestion = suggest_activity(dominant_emotion, intensity)
        suicide_risk = check_suicidal_intent(content)
        insights = generate_insights(content, emotions)
        summary = summarize_journal(content)
        
        # Store in database
        db_response = insert_journal_entry(user_id, content, dominant_emotion)
        
        # Check for database errors
        if isinstance(db_response, dict) and "error" in db_response:
            return jsonify({
                "message": "Journal analyzed but not saved",
                "error": db_response["error"],
                "summary": summary,
                "emotions": emotions,
                "dominant_emotion": dominant_emotion,
                "activity_suggestion": activity_suggestion,
                "suicide_risk": suicide_risk,
                "insights": insights
            }), 500
        
        return jsonify({
            "message": "Journal entry added successfully!",
            "summary": summary,
            "emotions": emotions,
            "dominant_emotion": dominant_emotion,
            "activity_suggestion": activity_suggestion,
            "suicide_risk": suicide_risk,
            "insights": insights,
            "database_response": db_response
        }), 200
        
    except Exception as e:
        print("❌ Error in add_journal:", str(e))
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

### ** Route: Analyze Journal Text Without Saving **
@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze journal text without saving to database."""
    try:
        data = request.json
        text = data.get("text", "")
        
        if not text.strip():
            return jsonify({"error": "Empty text provided"}), 400
        
        # Process the journal entry
        emotions = extract_emotions(text)
        dominant_emotion, intensity = dominant_emotion_analysis(text, emotions)
        activity_suggestion = suggest_activity(dominant_emotion, intensity)
        suicide_risk = check_suicidal_intent(text)
        insights = generate_insights(text, emotions)
        summary = summarize_journal(text)
        
        # Return analysis results
        return jsonify({
            "message": "Journal entry analyzed!",
            "summary": summary,
            "emotions": emotions,
            "dominant_emotion": dominant_emotion,
            "intensity": intensity,
            "activity_suggestion": activity_suggestion,
            "suicide_risk": suicide_risk,
            "insights": insights
        }), 200
        
    except Exception as e:
        print("❌ Error in analyze:", str(e))
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

### ** Route: Get Journal Entries **
@app.route("/get-journals/<user_id>", methods=["GET"])
def get_journals(user_id):
    """Retrieve all journal entries for a user."""
    try:
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        response = get_journal_entries(user_id)
        
        # Check for errors
        if isinstance(response, dict) and "error" in response:
            return jsonify({"error": response["error"]}), 500
            
        return jsonify({"journals": response}), 200
        
    except Exception as e:
        print("❌ Error in get_journals:", str(e))
        return jsonify({"error": f"Server error: {str(e)}"}), 500

### ** Route: Add Mood Entry **
@app.route("/add-mood", methods=["POST"])
def add_mood():
    """Add a new mood entry to the database."""
    try:
        data = request.json
        user_id = data.get("user_id")
        happiness = data.get("happiness")
        anxiety = data.get("anxiety")
        energy = data.get("energy")
        stress = data.get("stress")
        activity = data.get("activity", "")
        notes = data.get("notes", "")
        
        # Validate required fields
        if not user_id or happiness is None or anxiety is None or energy is None or stress is None:
            return jsonify({"error": "Missing required mood data"}), 400
            
        # Insert mood entry
        response = insert_mood_entry(user_id, happiness, anxiety, energy, stress, activity, notes)
        
        # Check for errors
        if isinstance(response, dict) and "error" in response:
            return jsonify({"error": response["error"]}), 500
            
        return jsonify({"message": "Mood entry added!", "response": response}), 200
        
    except Exception as e:
        print("❌ Error in add_mood:", str(e))
        return jsonify({"error": f"Server error: {str(e)}"}), 500

### ** Route: Get Mood Entries **
@app.route("/get-moods/<user_id>", methods=["GET"])
def get_moods(user_id):
    """Retrieve all mood entries for a user."""
    try:
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        response = get_mood_entries(user_id)
        
        # Check for errors
        if isinstance(response, dict) and "error" in response:
            return jsonify({"error": response["error"]}), 500
            
        return jsonify({"moods": response}), 200
        
    except Exception as e:
        print("❌ Error in get_moods:", str(e))
        return jsonify({"error": f"Server error: {str(e)}"}), 500

### ** Route: Track Mental Health Crisis **
@app.route("/crisis-alert", methods=["POST"])
def crisis_alert():
    """Handle mental health crisis alerts."""
    try:
        data = request.json
        user_id = data.get("user_id")
        journal_id = data.get("journal_id")
        crisis_type = data.get("crisis_type", "suicide_risk")
        
        # In a production app, you would implement:
        # 1. Log the crisis alert
        # 2. Send notifications to designated contacts if configured
        # 3. Provide emergency resources
        
        return jsonify({
            "message": "Crisis alert recorded",
            "resources": [
                {"name": "National Suicide Prevention Lifeline", "contact": "988"},
                {"name": "Crisis Text Line", "contact": "Text HOME to 741741"}
            ]
        }), 200
        
    except Exception as e:
        print("❌ Error in crisis_alert:", str(e))
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)