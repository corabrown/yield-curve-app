import os
import requests

API_BASE = os.environ.get("API_URL", "http://localhost:8000")


def get_latest():
    r = requests.get(f"{API_BASE}/yield-curve/latest", timeout=10)
    r.raise_for_status()
    return r.json()


def get_curve(curve_date: str):
    r = requests.get(f"{API_BASE}/yield-curve/{curve_date}", timeout=10)
    r.raise_for_status()
    return r.json()


def get_history(start: str | None = None, end: str | None = None):
    params = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    r = requests.get(f"{API_BASE}/yield-curve/history", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def get_dates():
    r = requests.get(f"{API_BASE}/yield-curve/dates", params={"limit": 500}, timeout=10)
    r.raise_for_status()
    return r.json()["dates"]


def get_users():
    r = requests.get(f"{API_BASE}/users", timeout=10)
    r.raise_for_status()
    return r.json()


def create_user(first_name: str):
    r = requests.post(f"{API_BASE}/users", json={"first_name": first_name}, timeout=10)
    r.raise_for_status()
    return r.json()


def get_user(user_id: int):
    r = requests.get(f"{API_BASE}/users/{user_id}", timeout=10)
    r.raise_for_status()
    return r.json()


def create_order(user_id: int, term: str, amount: float):
    r = requests.post(
        f"{API_BASE}/users/{user_id}/orders",
        json={"term": term, "amount": amount},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def get_user_orders(user_id: int):
    r = requests.get(f"{API_BASE}/users/{user_id}/orders", timeout=10)
    r.raise_for_status()
    return r.json()
