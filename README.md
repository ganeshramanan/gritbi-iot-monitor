# IoT Environment Monitor (Simulated Sensors) — Gritbi Project #7 (Tier 2)

A live-updating environment monitoring dashboard built with **Flask**. Simulates a Raspberry Pi + temperature/humidity sensor setup — no physical hardware required to learn the concepts.

## Important: This is a simulation
This project **does not require any physical hardware**. A background thread generates realistic temperature, humidity, and motion readings that drift naturally over time (instead of pure random noise), mimicking what a real sensor would report. This lets you learn the full dashboard/alerting architecture without needing a Raspberry Pi, sensors, or wiring.

**The dashboard and alerting code are identical to what you'd use with real hardware** — only the data source changes. See "Going from Simulation to Real Hardware" below.

## Features
- Live dashboard auto-refreshing every 3 seconds (polling, not WebSockets — a simpler alternative pattern)
- Temperature, humidity, and motion readings with a rolling 30-point line chart
- Automatic threshold-based alerts (high/low temperature, high/low humidity, motion detected)
- Background thread continuously generating new simulated readings

## Tech Stack
- **Backend**: Python, Flask, `threading` (standard library — for the background simulation loop)
- **Frontend**: HTML, CSS, Chart.js, vanilla JS polling (`fetch` + `setInterval`)
- **Deployment**: Render (gunicorn + Procfile)

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5007` — wait a few seconds for the first simulated readings to appear.

## What students will learn
1. **Background threads** — running a continuous data-generating process alongside a web server
2. **Polling vs. WebSockets** — a simpler real-time-ish pattern (`setInterval` + `fetch`) compared to Project #4's true WebSocket approach; understanding the tradeoffs of each
3. **In-memory rolling windows** — using Python's `deque(maxlen=N)` to keep only the most recent N readings, a common pattern in real monitoring systems
4. **Threshold-based alerting** — same core pattern as Project #8, applied to a different domain
5. **Simulation-first development** — a real, common practice: building and testing dashboard/alert logic against fake data before real hardware is available or connected

## Going from Simulation to Real Hardware
To connect this to a real Raspberry Pi + DHT11 temperature/humidity sensor:
1. Install `Adafruit_DHT` on the Raspberry Pi: `pip install Adafruit_DHT`
2. Replace the `generate_reading()` function's simulation logic with:
   ```python
   import Adafruit_DHT
   humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, pin=4)
   ```
3. For motion, wire a PIR motion sensor to a GPIO pin and read it with the `RPi.GPIO` library
4. (Optional, more advanced) Publish readings to an MQTT broker (like Mosquitto) instead of storing them directly in memory, so multiple dashboards or services could subscribe to the same sensor feed

## Suggested customizations (for uniqueness per student)
- Add more sensor types (light level, air quality, sound)
- Add historical data persistence (SQLite) instead of only keeping the last 30 readings
- Add email/SMS alerts when a critical threshold is crossed
- Add configurable thresholds via a settings page
- Add multiple "rooms"/locations, each with their own simulated sensor feed

## Viva prep — common questions to expect
- Why use polling (`setInterval`) here instead of WebSockets like the chat app?
- How does the background thread avoid blocking the main Flask web server?
- What is a `deque(maxlen=N)` and why is it useful here instead of a regular list?
- How would you adapt this code to work with a real sensor instead of simulated data?
- What is MQTT, and why is it commonly used in real IoT systems instead of direct HTTP calls?
- What are the risks of storing sensor data only in memory (not a database)?

---
Built as part of **Gritbi** — learn to build, understand, and defend real projects.
