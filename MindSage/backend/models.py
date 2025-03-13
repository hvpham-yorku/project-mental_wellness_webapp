from supabase import create_client, Client
import os
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Supabase credentials (store in a .env file)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to insert a journal entry
def insert_journal_entry(id, content, mood):
    data = {
        "id": id,
        "content": content,
        "mood": mood
    }
    response = supabase.table("journal_entries").insert(data).execute()
    return response

# Function to get journal entries for a user
def get_journal_entries(id):
    response = supabase.table("journal_entries").select("*").eq("id", id).execute()
    return response

#  Function to insert a mood entry
def insert_mood_entry(happiness, anxiety, energy, stress, activity, notes=""):
    data = {
        "id": str(uuid.uuid4()),  # Generate a unique UUID
        "happiness": happiness,
        "anxiety": anxiety,
        "energy": energy,
        "stress": stress,
        "activity": activity,
        "notes": notes
    }

    print("📌 INSERTING DATA:", data)  # ✅ Debugging Line

    response = supabase.table("mood_entries").insert(data).execute()
    return response.data

def get_mood_entries():
    try:
        response = supabase.table("mood_entries").select("*").execute()
        return response.data  # ✅ Returns list of mood entries
    except Exception as e:
        print("🚨 ERROR:", e)
        return None

# Function to get mood history for a user
def get_mood_history(id):
    response = supabase.table("mood_entries").select("*").eq("id", id).execute()
    return response

# Function to get mood history
def get_mood_history(id):
    response = supabase.table("mood_entries").select("*").eq("id", id).execute()
    return response
