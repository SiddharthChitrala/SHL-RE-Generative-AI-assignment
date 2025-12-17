from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

print("GET /health ->", client.get("/health").status_code, client.get("/health").json())

resp = client.post("/recommend", json={
    "query":"I need a Java developer with communication skills",
    "max_duration": 60,
    "preferred_test_types": ["Knowledge & Skills", "Personality & Behavior"]
})
print("POST /recommend ->", resp.status_code)
if resp.status_code == 200:
    data = resp.json()
    print("recommendations:", len(data.get("recommended_assessments", [])))
    if data.get("recommended_assessments"):
        print(data["recommended_assessments"][0])
else:
    print(resp.text)
