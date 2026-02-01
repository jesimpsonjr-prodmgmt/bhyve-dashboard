#!/usr/bin/env python3
"""
B-Hyve Dashboard Server v1.0
A Flask-based backend for the B-Hyve sprinkler dashboard.
Handles authentication with Orbit's cloud API and proxies requests.
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
CORS(app)

API_BASE = "https://api.orbitbhyve.com/v1"

session_data = {
    "token": None,
    "user_id": None,
    "token_expiry": None,
    "devices": [],
    "email": None,
    "password": None
}

def get_headers():
    return {
        "Content-Type": "application/json",
        "orbit-api-key": session_data["token"],
        "orbit-app-id": "Orbit Support Dashboard"
    }

def is_token_valid():
    if not session_data["token"]:
        return False
    if session_data["token_expiry"] and datetime.now() > session_data["token_expiry"]:
        return False
    return True

def refresh_token():
    if not session_data["email"] or not session_data["password"]:
        return False
    return do_login(session_data["email"], session_data["password"])

def do_login(email, password):
    try:
        resp = requests.post(
            f"{API_BASE}/session",
            json={"session": {"email": email, "password": password}},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            session_data["token"] = data.get("orbit_api_key")
            session_data["user_id"] = data.get("user_id")
            session_data["email"] = email
            session_data["password"] = password
            session_data["token_expiry"] = datetime.now() + timedelta(hours=23)
            return True
        return False
    except Exception as e:
        print(f"Login error: {e}")
        return False

@app.route('/')
def serve_dashboard():
    return send_from_directory('.', 'bhyve_dashboard_v1.0.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password required"}), 400
    
    if do_login(email, password):
        return jsonify({"success": True, "user_id": session_data["user_id"]})
    else:
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session_data["token"] = None
    session_data["user_id"] = None
    session_data["token_expiry"] = None
    session_data["email"] = None
    session_data["password"] = None
    session_data["devices"] = []
    return jsonify({"success": True})

@app.route('/api/status')
def get_status():
    return jsonify({
        "authenticated": is_token_valid(),
        "user_id": session_data["user_id"]
    })

@app.route('/api/devices')
def get_devices():
    if not is_token_valid():
        if not refresh_token():
            return jsonify({"error": "Not authenticated"}), 401
    
    try:
        resp = requests.get(
            f"{API_BASE}/devices",
            params={"t": time.time()},
            headers=get_headers(),
            timeout=30
        )
        if resp.status_code == 200:
            devices = resp.json()
            session_data["devices"] = devices
            return jsonify(devices)
        return jsonify({"error": f"API error: {resp.status_code}"}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/device/<device_id>')
def get_device(device_id):
    if not is_token_valid():
        if not refresh_token():
            return jsonify({"error": "Not authenticated"}), 401
    
    try:
        resp = requests.get(
            f"{API_BASE}/devices/{device_id}",
            params={"t": time.time()},
            headers=get_headers(),
            timeout=30
        )
        if resp.status_code == 200:
            return jsonify(resp.json())
        return jsonify({"error": f"API error: {resp.status_code}"}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/watering_events/<device_id>')
def get_watering_events(device_id):
    if not is_token_valid():
        if not refresh_token():
            return jsonify({"error": "Not authenticated"}), 401
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        resp = requests.get(
            f"{API_BASE}/watering_events/{device_id}",
            params={"t": time.time(), "page": page, "per-page": per_page},
            headers=get_headers(),
            timeout=30
        )
        if resp.status_code == 200:
            return jsonify(resp.json())
        return jsonify({"error": f"API error: {resp.status_code}"}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/programs/<device_id>')
def get_programs(device_id):
    if not is_token_valid():
        if not refresh_token():
            return jsonify({"error": "Not authenticated"}), 401
    
    try:
        resp = requests.get(
            f"{API_BASE}/sprinkler_timer_programs",
            params={"device_id": device_id, "t": time.time()},
            headers=get_headers(),
            timeout=30
        )
        if resp.status_code == 200:
            return jsonify(resp.json())
        return jsonify({"error": f"API error: {resp.status_code}"}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/weather/<device_id>')
def get_weather(device_id):
    if not is_token_valid():
        if not refresh_token():
            return jsonify({"error": "Not authenticated"}), 401
    
    try:
        resp = requests.get(
            f"{API_BASE}/weather_forecast/{device_id}",
            params={"t": time.time()},
            headers=get_headers(),
            timeout=30
        )
        if resp.status_code == 200:
            return jsonify(resp.json())
        return jsonify([])
    except Exception as e:
        return jsonify([])

@app.route('/api/landscapes')
def get_landscapes():
    if not is_token_valid():
        if not refresh_token():
            return jsonify({"error": "Not authenticated"}), 401
    
    try:
        resp = requests.get(
            f"{API_BASE}/landscapes",
            params={"t": time.time()},
            headers=get_headers(),
            timeout=30
        )
        if resp.status_code == 200:
            return jsonify(resp.json())
        return jsonify([])
    except Exception as e:
        return jsonify([])

@app.route('/api/start_zone', methods=['POST'])
def start_zone():
    if not is_token_valid():
        if not refresh_token():
            return jsonify({"error": "Not authenticated"}), 401
    
    data = request.json
    device_id = data.get('device_id')
    zone_id = data.get('zone_id')
    duration = data.get('duration', 5)
    
    if not device_id or zone_id is None:
        return jsonify({"error": "device_id and zone_id required"}), 400
    
    try:
        payload = {
            "event": "change_mode",
            "mode": "manual",
            "device_id": device_id,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "stations": [{"station": zone_id, "run_time": duration}]
        }
        
        resp = requests.post(
            f"{API_BASE}/devices/{device_id}/manual_watering",
            json=payload,
            headers=get_headers(),
            timeout=30
        )
        
        if resp.status_code in [200, 201, 204]:
            return jsonify({"success": True})
        return jsonify({"error": f"API error: {resp.status_code}", "details": resp.text}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stop_zone', methods=['POST'])
def stop_zone():
    if not is_token_valid():
        if not refresh_token():
            return jsonify({"error": "Not authenticated"}), 401
    
    data = request.json
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({"error": "device_id required"}), 400
    
    try:
        payload = {
            "event": "change_mode",
            "mode": "auto",
            "device_id": device_id,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        resp = requests.post(
            f"{API_BASE}/devices/{device_id}/stop",
            json=payload,
            headers=get_headers(),
            timeout=30
        )
        
        if resp.status_code in [200, 201, 204]:
            return jsonify({"success": True})
        return jsonify({"error": f"API error: {resp.status_code}", "details": resp.text}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rain_delay', methods=['POST'])
def set_rain_delay():
    if not is_token_valid():
        if not refresh_token():
            return jsonify({"error": "Not authenticated"}), 401
    
    data = request.json
    device_id = data.get('device_id')
    hours = data.get('hours', 24)
    
    if not device_id:
        return jsonify({"error": "device_id required"}), 400
    
    try:
        payload = {
            "event": "rain_delay",
            "device_id": device_id,
            "delay": hours,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        resp = requests.post(
            f"{API_BASE}/devices/{device_id}/rain_delay",
            json=payload,
            headers=get_headers(),
            timeout=30
        )
        
        if resp.status_code in [200, 201, 204]:
            return jsonify({"success": True})
        return jsonify({"error": f"API error: {resp.status_code}"}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear_rain_delay', methods=['POST'])
def clear_rain_delay():
    if not is_token_valid():
        if not refresh_token():
            return jsonify({"error": "Not authenticated"}), 401
    
    data = request.json
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({"error": "device_id required"}), 400
    
    try:
        payload = {
            "event": "rain_delay",
            "device_id": device_id,
            "delay": 0,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        resp = requests.post(
            f"{API_BASE}/devices/{device_id}/rain_delay",
            json=payload,
            headers=get_headers(),
            timeout=30
        )
        
        if resp.status_code in [200, 201, 204]:
            return jsonify({"success": True})
        return jsonify({"error": f"API error: {resp.status_code}"}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/run_program', methods=['POST'])
def run_program():
    if not is_token_valid():
        if not refresh_token():
            return jsonify({"error": "Not authenticated"}), 401
    
    data = request.json
    device_id = data.get('device_id')
    program_id = data.get('program_id')
    
    if not device_id or not program_id:
        return jsonify({"error": "device_id and program_id required"}), 400
    
    try:
        payload = {
            "event": "run_program",
            "device_id": device_id,
            "program_id": program_id,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        resp = requests.post(
            f"{API_BASE}/devices/{device_id}/run",
            json=payload,
            headers=get_headers(),
            timeout=30
        )
        
        if resp.status_code in [200, 201, 204]:
            return jsonify({"success": True})
        return jsonify({"error": f"API error: {resp.status_code}"}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/toggle_program', methods=['POST'])
def toggle_program():
    if not is_token_valid():
        if not refresh_token():
            return jsonify({"error": "Not authenticated"}), 401
    
    data = request.json
    program_id = data.get('program_id')
    enabled = data.get('enabled', True)
    
    if not program_id:
        return jsonify({"error": "program_id required"}), 400
    
    try:
        resp = requests.patch(
            f"{API_BASE}/sprinkler_timer_programs/{program_id}",
            json={"enabled": enabled},
            headers=get_headers(),
            timeout=30
        )
        
        if resp.status_code in [200, 201, 204]:
            return jsonify({"success": True})
        return jsonify({"error": f"API error: {resp.status_code}"}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("  B-Hyve Dashboard Server v1.0")
    print("  Starting on http://0.0.0.0:5678")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5678, debug=False)
