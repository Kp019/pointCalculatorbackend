import requests
import json

url = "http://localhost:9000/api/v1/games/"
payload = {
    "name": "Test Game",
    "config": {
        "winMetric": "rounds",
        "targetRounds": 10,
        "targetPoints": 100,
        "winCondition": "highest",
        "gameMode": "sudden-death"
    },
    "players": [
        {"id": "player-0", "name": "test1", "scores": [], "totalScore": 0},
        {"id": "player-1", "name": "test2", "scores": [], "totalScore": 0}
    ],
    "rounds": [],
    "currentRound": 1,
    "winner": None
}

# Add a fake token or skip auth if possible (but the endpoint Depends(get_current_user))
# Since I can't easily get a token, I'll just see what the 422 says if I send it without token
# Actually, if token is missing it would be 401. 
# But I can see if 422 happens before or after auth.

headers = {"Content-Type": "application/json"}
response = requests.post(url, json=payload, headers=headers)
print(f"Status: {response.status_code}")
try:
    print(json.dumps(response.json(), indent=2))
except:
    print(response.text)
