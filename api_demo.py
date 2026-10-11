"""Runs the whole flow against a running server and prints each response.
Usage:  python api_demo.py            (server must be running on 127.0.0.1:8000)
Screenshot the output for your submission."""
import json
import urllib.error
import urllib.request
import uuid

BASE = "http://127.0.0.1:8000/api"
token = None


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as r:
            status, raw = r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read().decode()
    try:
        out = json.loads(raw) if raw else ""
    except ValueError:
        out = raw[:300]
    print(f"\n{method} {path}  ->  {status}")
    if body:
        print("  body:", json.dumps(body))
    print("  resp:", json.dumps(out, indent=2)[:700])
    return status, out


email = f"demo_{uuid.uuid4().hex[:6]}@test.com"
pw = "StrongPass#123"

call("POST", "/auth/register/", {"name": "Demo User", "email": email, "password": pw})
call("POST", "/auth/register/", {"name": "Dup", "email": email, "password": pw})  # expect 400
call("POST", "/auth/login/", {"email": email, "password": "wrong"})  # expect 401
_, login = call("POST", "/auth/login/", {"email": email, "password": pw})
token = login["access"]

call("GET", "/patients/")
_, p = call("POST", "/patients/", {"name": "Ravi", "age": 40, "gender": "M", "phone": "9876543210"})
call("POST", "/patients/", {"name": "", "age": 999, "gender": "Z"})  # expect 400
call("GET", f"/patients/{p['id']}/")
call("PUT", f"/patients/{p['id']}/", {"name": "Ravi K", "age": 41, "gender": "M", "phone": "9876543210"})

_, d = call("POST", "/doctors/", {"name": "Meera", "specialization": "Cardiology",
                                  "email": f"{uuid.uuid4().hex[:6]}@hospital.com", "experience_years": 8})
call("GET", "/doctors/")
call("GET", f"/doctors/{d['id']}/")
call("PUT", f"/doctors/{d['id']}/", {"name": "Meera S", "specialization": "Cardiology",
                                     "email": d["email"], "experience_years": 9})

_, m = call("POST", "/mappings/", {"patient": p["id"], "doctor": d["id"]})
call("POST", "/mappings/", {"patient": p["id"], "doctor": d["id"]})  # expect 400 duplicate
call("GET", "/mappings/")
call("GET", f"/mappings/{p['id']}/")
call("DELETE", f"/mappings/{m['id']}/")
call("DELETE", f"/doctors/{d['id']}/")
call("DELETE", f"/patients/{p['id']}/")

token = None
call("GET", "/patients/")  # expect 401 without token
