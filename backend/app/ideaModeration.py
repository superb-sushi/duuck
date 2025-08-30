import requests
import os
import json
from dotenv import load_dotenv

def moderate_idea(video_idea: str) -> dict:
    url = os.getenv("IDEA_MODERATION_URL") + "/duuck/moderate_idea"
    payload = {
        "video_idea": video_idea
    }
    response = requests.post(url, json=payload).json()
    return json.loads(response)

def find_similar_idea(video_idea: str, database_ideas: list[str]) -> dict:
    url = os.getenv("IDEA_MODERATION_URL") + "/duuck/similar_idea"
    payload = {
        "video_idea": video_idea,
        "database_ideas": database_ideas
    }
    response = requests.post(url, json=payload).json()
    return json.loads(response)

# Example usage
if __name__ == "__main__":
    load_dotenv()
    video_idea = "A new way to teach programming"
    database_ideas = ["Interactive coding tutorials", "Gamified learning platforms"]

    # Moderate the idea
    moderation_response = moderate_idea(video_idea)
    print("Moderation Response:", moderation_response)

    # Find similar ideas
    similar_response = find_similar_idea(video_idea, database_ideas)
    print("Similar Ideas Response:", similar_response)
