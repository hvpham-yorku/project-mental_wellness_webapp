def validate_mood_data(data):
    required_fields = ["happiness", "anxiety", "energy", "stress"]
    for field in required_fields:
        if field not in data:
            return False
    return True