"""Lightweight smoke test to run against a running backend server.

Usage:
    python scripts/smoke_test.py --url http://localhost:8000

It checks health, dev provision (dev only), and admin institutions endpoint.
"""

import argparse
import requests


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://localhost:8000")
    args = p.parse_args()
    base = args.url.rstrip("/")
    print("Checking /api/v1/health")
    try:
        r = requests.get(f"{base}/api/v1/health")
        print("health:", r.status_code)
    except Exception as e:
        print("health check failed:", e)
    print("Attempting dev provision (may be blocked in non-dev)")
    admin_payload = {"email": "smoke@example.com", "name": "Smoke", "role": "admin"}
    try:
        r = requests.post(
            f"{base}/api/v1/dev/provision-user", json=admin_payload, timeout=5
        )
        print("/dev/provision-user:", r.status_code, r.text[:200])
        if r.status_code == 200:
            j = r.json()
            raw = j.get("raw_token")
            if raw:
                # Call admin endpoint with session cookie
                cookies = {"session_token": raw}
                print("Listing admin institutions (requires admin auth)")
                ar = requests.get(
                    f"{base}/api/v1/admin/institutions", cookies=cookies, timeout=5
                )
                print("/admin/institutions:", ar.status_code, ar.text[:200])
            else:
                print("No raw_token returned; cannot call admin endpoints.")
    except Exception as e:
        print("dev provision failed:", e)


if __name__ == "__main__":
    main()
