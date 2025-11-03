# Exercise 11 Load Testing

This folder contains scaffolds to run basic HTTP and WebSocket load tests against the Child Growth Assistant backend.

## K6 (HTTP + WebSocket)

- Script: k6/coach_scenario.js
- Requirements: k6 CLI
- Run examples:
  - BASE_URL=http://localhost:8000 k6 run k6/coach_scenario.js
  - BASE_URL=http://localhost:8000 VUS=20 DURATION=1m k6 run k6/coach_scenario.js

## Locust (HTTP)

- Script: locust/locustfile.py
- Install: pip install -r locust/requirements.txt
- Run UI:
  - cd locust
  - locust --host http://localhost:8000
  - Open http://localhost:8089 and start a swarm
- Run headless example:
  - locust -f locust/locustfile.py --host http://localhost:8000 -u 50 -r 5 -t 1m --headless

Notes
- K6 script includes a basic WS round-trip: start session → connect → send → expect advice.
- Locust scaffold focuses on HTTP flows. Extend with websockets via plugins if needed.
