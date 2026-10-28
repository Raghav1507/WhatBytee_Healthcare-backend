"""End-to-end smoke test against a running dev server.

Usage:
    python scripts/smoke_test.py [base_url]

Exercises every required endpoint and prints a PASS/FAIL summary.
"""
import json
import sys
import time
import urllib.error
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
RESULTS = []


def call(method, path, payload=None, token=None):
    """Make an HTTP request and return (status, parsed_json)."""
    url = f"{BASE}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"raw": body}


def check(name, cond, extra=""):
    RESULTS.append((name, bool(cond), extra))
    mark = "PASS" if cond else "FAIL"
    print(f"[{mark}] {name} {extra}")


def main():
    # Unique email per run so the suite is repeatable against a persistent DB.
    email = f"smoke.user.{int(time.time())}@example.com"
    password = "Sup3rSecret!Pass"

    # ---------------------------------------------------------------- auth
    status, body = call(
        "POST",
        "/api/auth/register/",
        {"name": "Smoke User", "email": email, "password": password,
         "password2": password},
    )
    check("POST /api/auth/register/", status == 201 and body.get("success"),
          f"-> {status}")

    # duplicate register should 400
    status, body = call(
        "POST", "/api/auth/register/",
        {"name": "Dup", "email": email, "password": password,
         "password2": password},
    )
    check("POST /api/auth/register/ (duplicate -> 400)", status == 400,
          f"-> {status}")

    status, body = call(
        "POST", "/api/auth/login/", {"email": email, "password": password}
    )
    check("POST /api/auth/login/", status == 200 and "access" in body.get("data", {}),
          f"-> {status}")
    token = body["data"]["access"]
    refresh = body["data"]["refresh"]

    status, body = call("POST", "/api/auth/token/refresh/", {"refresh": refresh})
    check("POST /api/auth/token/refresh/", status == 200, f"-> {status}")
    new_access = body["data"]["access"]
    token = new_access or token

    status, body = call("GET", "/api/auth/me/", token=token)
    check("GET /api/auth/me/", status == 200 and body["data"]["email"] == email,
          f"-> {status}")

    status, _ = call("GET", "/api/patients/")
    check("GET /api/patients/ without token -> 401", status == 401, f"-> {status}")

    # ------------------------------------------------------------- patients
    status, body = call(
        "POST", "/api/patients/",
        {"name": "John Patient", "age": 45, "gender": "male",
         "phone": "+1 555 1234", "email": "john.p@example.com",
         "address": "42 Wellness Ave"},
        token=token,
    )
    check("POST /api/patients/", status == 201 and body.get("success"),
          f"-> {status}")
    patient_id = body["data"]["id"]

    status, body = call(
        "POST", "/api/patients/",
        {"name": "Bad", "age": -5, "gender": "nope"}, token=token,
    )
    check("POST /api/patients/ (invalid -> 400)", status == 400, f"-> {status}")

    status, body = call("GET", "/api/patients/", token=token)
    check("GET /api/patients/", status == 200 and body["data"]["count"] >= 1,
          f"-> {status}, count={body.get('data', {}).get('count')}")

    status, body = call("GET", f"/api/patients/{patient_id}/", token=token)
    check("GET /api/patients/<id>/", status == 200, f"-> {status}")

    status, body = call(
        "PUT", f"/api/patients/{patient_id}/",
        {"name": "John Updated", "age": 46, "gender": "male"}, token=token,
    )
    check("PUT /api/patients/<id>/", status == 200 and
          body["data"]["name"] == "John Updated", f"-> {status}")

    # -------------------------------------------------------------- doctors
    license_no = f"LIC-{int(time.time())}"
    status, body = call(
        "POST", "/api/doctors/",
        {"name": "Sarah House", "specialization": "Cardiology",
         "email": f"s.house.{int(time.time())}@example.com", "phone": "+1 555 9999",
         "license_number": license_no, "years_of_experience": 14,
         "hospital": "City General"},
        token=token,
    )
    check("POST /api/doctors/", status == 201 and body.get("success"),
          f"-> {status}")
    doctor_id = body["data"]["id"]

    status, body = call("GET", "/api/doctors/", token=token)
    check("GET /api/doctors/", status == 200 and body["data"]["count"] >= 1,
          f"-> {status}")

    status, body = call("GET", f"/api/doctors/{doctor_id}/", token=token)
    check("GET /api/doctors/<id>/", status == 200, f"-> {status}")

    status, body = call(
        "PUT", f"/api/doctors/{doctor_id}/",
        {"name": "Sarah House", "specialization": "Cardiology",
         "license_number": license_no, "years_of_experience": 15},
        token=token,
    )
    check("PUT /api/doctors/<id>/", status == 200 and
          body["data"]["years_of_experience"] == 15, f"-> {status}")

    # ------------------------------------------------------------- mappings
    status, body = call(
        "POST", "/api/mappings/",
        {"patient": patient_id, "doctor": doctor_id}, token=token,
    )
    check("POST /api/mappings/", status == 201 and body.get("success"),
          f"-> {status}")
    mapping_id = body["data"]["id"]

    status, body = call(
        "POST", "/api/mappings/",
        {"patient": patient_id, "doctor": doctor_id}, token=token,
    )
    check("POST /api/mappings/ (duplicate -> 400)", status == 400, f"-> {status}")

    status, body = call("GET", "/api/mappings/", token=token)
    check("GET /api/mappings/", status == 200 and body["data"]["count"] >= 1,
          f"-> {status}")

    status, body = call("GET", f"/api/mappings/{patient_id}/", token=token)
    check("GET /api/mappings/<patient_id>/", status == 200 and
          body["data"]["count"] == 1, f"-> {status}")

    status, body = call("DELETE", f"/api/mappings/{mapping_id}/", token=token)
    check("DELETE /api/mappings/<id>/", status == 200, f"-> {status}")

    status, body = call("GET", f"/api/mappings/{patient_id}/", token=token)
    check("GET /api/mappings/<patient_id>/ (after delete -> 0)",
          status == 200 and body["data"]["count"] == 0, f"-> {status}")

    # ------------------------------------------------- cleanup + auth edges
    status, body = call("POST", "/api/auth/logout/", {"refresh": refresh},
                        token=token)
    check("POST /api/auth/logout/", status == 200, f"-> {status}")

    status, body = call("POST", "/api/auth/login/",
                        {"email": email, "password": "wrong-password"})
    check("POST /api/auth/login/ (bad password -> 401)", status == 401,
          f"-> {status}")

    status, body = call("DELETE", f"/api/patients/{patient_id}/", token=token)
    check("DELETE /api/patients/<id>/", status == 200, f"-> {status}")

    status, body = call("DELETE", f"/api/doctors/{doctor_id}/", token=token)
    check("DELETE /api/doctors/<id>/", status == 200, f"-> {status}")

    # ------------------------------------------------------------- summary
    failed = [r for r in RESULTS if not r[1]]
    print("\n" + "=" * 60)
    print(f"TOTAL: {len(RESULTS)}  PASSED: {len(RESULTS) - len(failed)}  "
          f"FAILED: {len(failed)}")
    if failed:
        for name, _, extra in failed:
            print(f"  FAILED: {name} {extra}")
        sys.exit(1)
    print("All smoke tests passed against PostgreSQL.")


if __name__ == "__main__":
    main()
