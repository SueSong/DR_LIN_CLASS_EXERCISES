import http from 'k6/http';
import ws from 'k6/ws';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8011';
const WS_BASE = BASE_URL.replace(/^http/i, 'ws');

export const options = {
  vus: Number(__ENV.VUS || 10),
  duration: __ENV.DURATION || '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<2500'],
  },
};

export default function () {
  // Health check
  const health = http.get(`${BASE_URL}/healthz`);
  check(health, { 'health 200': (r) => r.status === 200 });

  // Start session
  const name = `Parent_${Math.floor(Math.random() * 1e6)}`;
  const start = http.post(
    `${BASE_URL}/api/coach/start`,
    JSON.stringify({ parent_name: name }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(start, { 'start 200': (r) => r.status === 200 });

  const session_id = (start.json() || {}).session_id;
  if (!session_id) {
    return;
  }

  // WebSocket round-trip
  const url = `${WS_BASE}/ws/coach/${session_id}`;
  const res = ws.connect(url, {}, function (socket) {
    socket.on('open', function () {
      socket.send(JSON.stringify({ type: 'text', text: 'How to handle bedtime resistance?' }));
    });

    socket.on('message', function (message) {
      try {
        const data = JSON.parse(message);
        if (data && data.type === 'advice') {
          socket.close();
        }
      } catch (e) {
        // ignore
      }
    });

    socket.on('close', function () {});

    socket.setTimeout(function () {
      try { socket.close(); } catch (e) {}
    }, 5000);
  });

  check(res, { 'ws connected/closed': (r) => r && (r.status === 101 || r.status === 1000 || r.status === 0) });

  sleep(1);
}
