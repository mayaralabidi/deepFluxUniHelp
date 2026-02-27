import requests
import traceback
import sys

try:
    print("Testing /chat...")
    res = requests.post("http://localhost:8000/chat", json={"message": "bonjour"})
    print(res.status_code, res.text)
except Exception as e:
    print("Error doing /chat:", e)

try:
    print("Testing /generate/...")
    res = requests.post("http://localhost:8000/generate/", json={"doc_type": "attestation", "params": {}})
    print(res.status_code, res.text)
except Exception as e:
    print("Error doing /generate/:", e)
