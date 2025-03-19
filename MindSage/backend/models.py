from supabase import create_client, Client
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

# Supabase credentials (store in a .env file)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to insert a journal entry
def insert_journal_entry(user_id, content):
    data = {
        "id": str(uuid.uuid4()),  # Unique ID for each journal entry
        "user_id": user_id,
        "content": content.strip(),
       # "mood": mood, #do we need this with journal?
        #"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    print("INSERTING JOURNAL ENTRY:", data) 

    #response = supabase.table("journal_entries").insert(data).execute()
    #return response
    try:
        response = supabase.table("journal_entries").insert(data).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        print("ERROR inserting journal entry:", e)
        return {"success": False, "error": str(e)}

# Fetch Journal Entries for a Specific User
def get_journal_history(user_id):
    try:
        response = supabase.table("journal_entries").select("*").eq("user_id", user_id).execute()
        if not response.data:  # Handle cases where no entries are found
            return {"success": False, "error": "No journal entries found for this user."}
        return {"success": True, "data": response.data}

    except Exception as e:
        print("ERROR fetching journal entries for user:", e)
        return {"success": False, "error": str(e)}
    
# Fetch a Specific Journal Entry of a user by ID of the journal
def get_journal_entry(user_id, entry_id):
    try:
        response = (
            supabase
            .table("journal_entries")
            .select("*")
            .eq("user_id", user_id)
            .eq("id", entry_id)
            .execute()
        )

        if not response.data:
            return {"success": False, "error": "Journal entry not found."}

        return {"success": True, "data": response.data[0]}  # Return the single entry

    except Exception as e:
        print("ERROR fetching journal entry:", e)
        return {"success": False, "error": str(e)}
    
# Fetch All Journal Entries
def get_journal_entries():
    try:
        response = supabase.table("journal_entries").select("*").execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        print("ERROR fetching journal entries:", e)
        return {"success": False, "error": str(e)}
    
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

    print("INSERTING DATA:", data) 
    response = supabase.table("mood_entries").insert(data).execute()
    return response.data

def get_mood_entries():
    try:
        response = supabase.table("mood_entries").select("*").execute()
        return response.data  
    except Exception as e:
        print("ERROR:", e)
        return None

# Function to get mood history for a user
def get_mood_history(id):
    response = supabase.table("mood_entries").select("*").eq("id", id).execute()
    return response

# Function to get mood history
def get_mood_history(id):
    response = supabase.table("mood_entries").select("*").eq("id", id).execute()
    return response
