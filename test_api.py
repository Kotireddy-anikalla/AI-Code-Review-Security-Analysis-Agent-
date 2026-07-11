import requests
import json

BASE = "http://localhost:8000"

def test():
    resp = requests.post(f"{BASE}/api/submit", data={
        "code": "def add(a, b): return a + b",
        "language": "python"
    })
    data = resp.json()
    assert data["status"] == "success"
    sub_id = data["submission_id"]
    print("Submission OK:", sub_id)

    resp = requests.post(f"{BASE}/api/chat", json={
        "question": "How to prevent SQL injection?",
        "submission_id": sub_id
    })
    data = resp.json()
    assert "answer" in data
    print("Chat answer:", data["answer"][:100])
    print("Sources:", len(data["sources"]))

if __name__ == "__main__":
    test()
    print("All tests passed.")
