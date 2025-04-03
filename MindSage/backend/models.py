import requests
import os
import uuid
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Dict

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Hugging Face API details
HF_API_KEY = os.getenv("HF_API_KEY")  # Store in .env file
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# Hugging Face model endpoints
EMOTION_MODEL_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
INSIGHT_MODEL_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

# Suicide prevention keywords
SUICIDE_KEYWORDS = [
    "want to die", "end my life", "no reason to live", "kill myself",
    "suicidal", "give up", "not worth living", "can't take it anymore",
    "better off dead", "goodbye forever"
]

# Activity suggestions based on dominant emotion
ACTIVITY_SUGGESTIONS = {
    "anger": {"low": "Try journaling.", "moderate": "Practice deep breathing.", "high": "Take a walk."},
    "fear": {"low": "Use affirmations.", "moderate": "Try grounding techniques.", "high": "Seek reassurance."},
    "sadness": {"low": "Listen to music.", "moderate": "Practice self-care.", "high": "Reach out to a friend."},
    "joy": {"low": "Write about happiness.", "moderate": "Engage in social activities.", "high": "Celebrate your joy!"},
    "surprise": {"low": "Take a moment to reflect.", "moderate": "Journal about the unexpected.", "high": "Share with a friend."},
    "disgust": {"low": "Step away briefly.", "moderate": "Practice mindfulness.", "high": "Change your environment."},
    "neutral": {"low": "Try mindful meditation.", "moderate": "Take a short walk.", "high": "Do something creative."},
    "stress": {"low": "Take deep breaths.", "moderate": "Practice progressive relaxation.", "high": "Consider speaking with someone."},
    "overwhelmed": {"low": "Make a to-do list.", "moderate": "Break tasks into smaller steps.", "high": "Reach out for support."}
}

### ** Emotion & Insight Extraction (Hugging Face)**
def extract_emotions(journal_entry: str) -> Dict:
    """
    Extract emotions from a journal entry using Hugging Face API.
    """
    payload = {"inputs": journal_entry}
    response = requests.post(EMOTION_MODEL_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        emotions = response.json()[0]
        return {e["label"]: e["score"] for e in emotions}

    print(f"🚨 Error {response.status_code}: {response.text}")
    return {}

def check_suicidal_intent(journal_entry: str) -> bool:
    """
    Check if the journal entry contains any suicide-related keywords.
    """
    return any(keyword in journal_entry.lower() for keyword in SUICIDE_KEYWORDS)

def suggest_activity(dominant_emotion: str, intensity: float) -> str:
    """
    Suggest activities based on the dominant emotion and its intensity.
    """
    if dominant_emotion not in ACTIVITY_SUGGESTIONS:
        return "No specific suggestions available."

    if intensity < 0.3:
        return ACTIVITY_SUGGESTIONS[dominant_emotion]["low"]
    elif intensity < 0.6:
        return ACTIVITY_SUGGESTIONS[dominant_emotion]["moderate"]
    else:
        return ACTIVITY_SUGGESTIONS[dominant_emotion]["high"]

def generate_insights(journal_entry: str, emotions: Dict) -> str:
    """
    Generate insights based on extracted emotions using Hugging Face API.
    """
    if not emotions:
        return "No insights available due to missing emotion data."

    dominant_emotion = max(emotions, key=emotions.get)
    prompt = (
        f"Analyze the following journal entry and provide meaningful insights:\n\n"
        f"Journal Entry: {journal_entry}\n"
        f"The writer is feeling emotions with the following intensities:\n"
    )

    for emotion, score in emotions.items():
        prompt += f"- {emotion.capitalize()}: {score:.2f}\n"

    prompt += f"\nBased on this, identify emotional patterns, trends over time, and provide actionable advice. "
    prompt += f"Focus on their dominant emotion, which is {dominant_emotion}."

    payload = {"inputs": prompt}
    response = requests.post(INSIGHT_MODEL_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        return response.json()[0]["generated_text"]

    print(f"🚨 Error {response.status_code}: {response.text}")
    return "Error generating insights."

def summarize_journal(journal_entry: str) -> str:
    """
    Generate a brief summary of the journal entry.
    """
    prompt = f"Summarize the following journal entry in a few sentences:\n\n{journal_entry}"
    payload = {"inputs": prompt}
    response = requests.post(INSIGHT_MODEL_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        return response.json()[0]["generated_text"]

    print(f"🚨 Error {response.status_code}: {response.text}")
    return "Error generating summary."

### ** Supabase Database Integration**
def insert_journal_entry(user_id: str, content: str, mood: str):
    """
    Inserts a journal entry into Supabase.
    """
    data = {
        "id": str(uuid.uuid4()),  # Generate unique UUID
        "user_id": user_id,
        "content": content,
        "mood": mood
    }

    print("📌 Inserting journal entry:", data)  
    response = supabase.table("journal_entries").insert(data).execute()
    return response.data

def get_journal_entries(user_id: str):
    """
    Retrieves all journal entries for a specific user.
    """
    response = supabase.table("journal_entries").select("*").eq("user_id", user_id).execute()
    return response.data  

def insert_mood_entry(user_id: str, happiness: int, anxiety: int, energy: int, stress: int, activity: str, notes: str = ""):
    """
    Inserts a mood entry into Supabase.
    """
    data = {
        "id": str(uuid.uuid4()),  # Generate a unique UUID
        "user_id": user_id,
        "happiness": happiness,
        "anxiety": anxiety,
        "energy": energy,
        "stress": stress,
        "activity": activity,
        "notes": notes
    }

    print("📌 Inserting mood entry:", data)  
    response = supabase.table("mood_entries").insert(data).execute()
    return response.data

def get_mood_entries(user_id: str):
    """
    Retrieves all mood entries for a specific user.
    """
    response = supabase.table("mood_entries").select("*").eq("user_id", user_id).execute()
    return response.data 

def get_mood_history(user_id: str):
    """
    Retrieves mood history for a specific user.
    """
    response = supabase.table("mood_entries").select("*").eq("user_id", user_id).execute()
    return response.data  

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