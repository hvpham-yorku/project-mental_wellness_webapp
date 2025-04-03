import requests
import os
import uuid
import time
from dotenv import load_dotenv
from supabase import create_client, Client
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
HF_API_KEY = os.getenv("HF_API_KEY")  # Make sure this is properly set in .env
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# Hugging Face model endpoints
EMOTION_MODEL_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
INSIGHT_MODEL_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
SUMMARY_MODEL_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

# Suicide prevention keywords
SUICIDE_KEYWORDS = [
    "want to die", "end my life","no meaning in life","want to end it", "no reason to live", "kill myself",
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

def query_huggingface_with_backoff(url: str, payload: Dict, max_retries: int = 3, initial_wait: float = 1.0) -> Optional[Dict]:
    """Query Hugging Face API with exponential backoff for reliability."""
    wait_time = initial_wait
    
    # Ensure we have a valid API key
    if not HF_API_KEY or HF_API_KEY.strip() == "":
        print("❌ Missing Hugging Face API key")
        return None
        
    # Ensure headers are properly formatted
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload)
            
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
                
            # Handle auth errors specifically
            elif response.status_code == 401:
                print(f"Authorization error: {response.text}")
                print(f"Using API key: {HF_API_KEY[:5]}...{HF_API_KEY[-5:] if HF_API_KEY else 'None'}")
                print("Check that your Hugging Face API key is correct in .env file")
                return None
            
            # Other errors
            else:
                print(f"Error {response.status_code}: {response.text}")
                if attempt == max_retries - 1:  # Last attempt
                    return None
                time.sleep(wait_time)
                wait_time *= 2  # Exponential backoff
                
        except Exception as e:
            print(f"Exception during API call: {e}")
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
    if not journal_entry or not journal_entry.strip():
        return {"neutral": 1.0}
    
    # Truncate text if too long (model likely has a token limit)
    max_length = 1024
    truncated_entry = journal_entry[:max_length]
    
    payload = {"inputs": truncated_entry}
    
    # Use the same headers that worked in the first file
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    try:
        # First try the direct approach from the original file
        response = requests.post(EMOTION_MODEL_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            emotions = response.json()[0]
            return {e["label"]: e["score"] for e in emotions}
        else:
            print(f"Direct emotion extraction failed: {response.status_code}: {response.text}")
            
            # Fall back to the backoff method
            result = query_huggingface_with_backoff(EMOTION_MODEL_URL, payload)
            
            if not result:
                print("❌ Failed to extract emotions with backoff method")
                return {"neutral": 1.0}
            
            emotions = result[0]
            return {e["label"]: e["score"] for e in emotions}
            
    except (KeyError, IndexError, TypeError, Exception) as e:
        print(f"🚨 Error in emotion extraction: {e}")
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
    
    # If no emotions provided or empty dict, use neutral
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

    # Try direct approach first (from first file)
    try:
        response = requests.post(INSIGHT_MODEL_URL, headers=HEADERS, json={"inputs": prompt})
        
        if response.status_code == 200:
            return response.json()[0]["generated_text"]
    except Exception as e:
        print(f"Direct insight generation failed: {e}")
    
    # Fall back to backoff method
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
    
    # Try direct approach first (similar to first file)
    try:
        payload = {
            "inputs": truncated_entry,
            "parameters": {
                "max_length": 100,
                "min_length": 30,
                "do_sample": False
            }
        }
        
        response = requests.post(SUMMARY_MODEL_URL, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            return response.json()[0]["summary_text"]
    except Exception as e:
        print(f"Direct summary generation failed: {e}")
    
    # Fall back to backoff method
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

### ** Supabase Database Integration **
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

# Additional helper function for debugging
def test_huggingface_connection():
    """Test the connection to Hugging Face API and print diagnostic information."""
    print(f"Testing Hugging Face API connection...")
    print(f"API Key: {HF_API_KEY[:3]}...{HF_API_KEY[-3:] if HF_API_KEY else 'None'}")
    
    test_payload = {"inputs": "I feel happy today"}
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    try:
        response = requests.post(EMOTION_MODEL_URL, headers=headers, json=test_payload)
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Connection successful!")
            return True
        else:
            print("❌ Connection failed!")
            return False
    except Exception as e:
        print(f"❌ Exception during test: {e}")
        return False