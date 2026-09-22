"""
Gritbi Project #7: IoT Environment Monitor (Simulated Sensors)
A Flask app that simulates a Raspberry Pi + sensor setup, generating realistic
temperature/humidity/motion readings on a background thread, and displaying them
on a live-updating dashboard with threshold-based alerts.

This is a SIMULATION -- no physical hardware required. It's designed so that the
exact same dashboard/alerting code would work with real sensor data; only the
`generate_reading()` function would be replaced with actual sensor reads (e.g.
via a DHT11 sensor + MQTT broker on a real Raspberry Pi).

Teaching goals for students:
- Background thread scheduling (simulating a continuous data source)
- In-memory time-series storage (a simplified version of what a real IoT
  pipeline would send to a database or MQTT broker)
- Threshold-based alerting (same pattern as Project #8!)
- Building dashboards that poll/refresh for "live" data without WebSockets
- Understanding the difference between simulation and real hardware integration
"""

from flask import Flask, render_template, jsonify
import random
import threading
import time
from datetime import datetime
from collections import deque

app = Flask(__name__)

MAX_READINGS = 30  # keep the last 30 readings in memory (like a rolling window)
readings = deque(maxlen=MAX_READINGS)
lock = threading.Lock()

# Alert thresholds
TEMP_HIGH = 32.0   # Celsius
TEMP_LOW = 15.0
HUMIDITY_HIGH = 80.0
HUMIDITY_LOW = 20.0

# Simulation state -- gives the fake data some realistic "drift" instead of pure random noise
sim_state = {"temp": 24.0, "humidity": 50.0}


def generate_reading():
    """
    Simulates one sensor reading. Uses small random drift from the previous
    value (instead of pure randomness) to mimic realistic sensor behavior --
    temperature/humidity don't jump wildly between readings in real life.

    NOTE FOR STUDENTS: In a real deployment, this function would be replaced with:
        import Adafruit_DHT
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    and the reading would typically be published to an MQTT broker instead of
    stored directly in memory.
    """
    sim_state["temp"] += random.uniform(-0.8, 0.8)
    sim_state["temp"] = max(10, min(40, sim_state["temp"]))

    sim_state["humidity"] += random.uniform(-3, 3)
    sim_state["humidity"] = max(10, min(95, sim_state["humidity"]))

    motion = random.random() < 0.15  # 15% chance motion detected

    return {
        "time": datetime.now().strftime("%H:%M:%S"),
        "temperature": round(sim_state["temp"], 1),
        "humidity": round(sim_state["humidity"], 1),
        "motion": motion,
    }


def sensor_loop():
    """Background thread that generates a new reading every 3 seconds."""
    while True:
        reading = generate_reading()
        with lock:
            readings.append(reading)
        time.sleep(3)


def check_alerts(reading):
    alerts = []
    if reading["temperature"] >= TEMP_HIGH:
        alerts.append({"level": "critical", "text": f"High temperature: {reading['temperature']}°C"})
    elif reading["temperature"] <= TEMP_LOW:
        alerts.append({"level": "warning", "text": f"Low temperature: {reading['temperature']}°C"})

    if reading["humidity"] >= HUMIDITY_HIGH:
        alerts.append({"level": "warning", "text": f"High humidity: {reading['humidity']}%"})
    elif reading["humidity"] <= HUMIDITY_LOW:
        alerts.append({"level": "warning", "text": f"Low humidity: {reading['humidity']}%"})

    if reading["motion"]:
        alerts.append({"level": "info", "text": "Motion detected"})

    return alerts


@app.route("/")
def index():
    with lock:
        current_readings = list(readings)
    return render_template("index.html", has_data=len(current_readings) > 0)


@app.route("/api/readings")
def api_readings():
    """JSON endpoint the frontend polls periodically to update the dashboard live."""
    with lock:
        current_readings = list(readings)

    latest_alerts = check_alerts(current_readings[-1]) if current_readings else []

    return jsonify({
        "readings": current_readings,
        "alerts": latest_alerts,
        "thresholds": {
            "temp_high": TEMP_HIGH, "temp_low": TEMP_LOW,
            "humidity_high": HUMIDITY_HIGH, "humidity_low": HUMIDITY_LOW,
        }
    })


# Start the background sensor simulation thread once, when the app starts
sensor_thread = threading.Thread(target=sensor_loop, daemon=True)
sensor_thread.start()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5007)
