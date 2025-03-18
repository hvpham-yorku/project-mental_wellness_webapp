from supabase import create_client, Client
import os
from dotenv import load_dotenv
import uuid
import jwt
from flask import request

# Load environment variables
load_dotenv()

# Supabase credentials (store in a .env file)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_JWT_SECRET = os.getenv(("SUPABASE_JWT_SECRET"))

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to register a user
def user_registration(email, password):
    try:
        print(f"Attempting to register: {email}")  
        auth_response = supabase.auth.sign_up({"email": email, "password": password})

        # Extract relevant user data from the response
        user_data = {
            "id": auth_response.user.id if auth_response.user else None,
            "email": auth_response.user.email if auth_response.user else None,
            "access_token": auth_response.session.access_token if auth_response.session else None,
            "refresh_token": auth_response.session.refresh_token if auth_response.session else None
        }


        print(f"Supabase response: {user_data}")  # Debugging
        return {"success": True, "user": user_data}

    except Exception as e:
        print(f"Error: {e}")  # Debugging
        return {"error": str(e)}

# Function to authenticate user and return JWT token
def user_login(email, password):
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        if user.user is None:  # If login fails
            return {"error": "Invalid credentials"}

        return {
            "success": True,
            "access_token": user.session.access_token,  # Extract JWT token
            "refresh_token": user.session.refresh_token,  
            "user": {"id": user.user.id, "email": user.user.email}
        }

    except Exception as e:
        return {"error": str(e)}

#Function for user logout
def user_logout():
    try:
        user = supabase.auth.sign_out()  # Supabase sign out
        return {"success": True, "message": "User logged out successfully"}
    except Exception as e:
        return {"error": str(e)}

def token_verification(token):
    if not token:
        return {"error": "Missing token"}

    try:
        print("Received Token:", token)  # Print the raw token

        # Decode JWT 
        decoded_token = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,   
            algorithms=["HS256"],
            audience="authenticated"  
        )

        # Extract the user ID 
        supabase_user_id = decoded_token.get("sub", None)

        if not supabase_user_id:
            return {"error": "Invalid token - Missing 'sub' field"}

        return decoded_token  

    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}

#Function to get user from JWT token
def get_authenticated_user():
    """Extract and validate user from JWT token."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return None  # No token provided

    parts = auth_header.split(" ")
    token = parts[1] if len(parts) == 2 else auth_header  # Handle missing 'Bearer'
    
    verified_token = token_verification(token)
    if "error" in verified_token:
        return None  # Invalid token

    return {"id": verified_token.get("sub")}  # Extract user ID

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
def insert_mood_entry(user_id, happiness, anxiety, energy, stress, activity, notes=""):
    data = {
        "id": str(uuid.uuid4()),  # Unique ID for the entry
        "user_id": user_id,  # Store the authenticated user's ID
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

#Function to get specific mood entry
def get_mood_entry(entry_id, user_id):
    response = supabase.table("mood_entries").select("*")\
        .eq("id", entry_id)\
        .eq("user_id", user_id)\
        .execute()
    return response.data

#Function to get mood history
def get_mood_history(user_id):
    response = supabase.table("mood_entries").select("*")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .execute()
    return response.data



