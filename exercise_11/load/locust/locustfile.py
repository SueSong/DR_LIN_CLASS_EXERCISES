from locust import HttpUser, task, between
import random
import string


def rand_name(prefix: str = "Parent"):
    return f"{prefix}_" + ''.join(random.choices(string.ascii_letters + string.digits, k=6))


class CoachUser(HttpUser):
    wait_time = between(1, 2)

    @task(2)
    def health(self):
        self.client.get("/healthz", name="GET /healthz")

    @task(1)
    def ready(self):
        self.client.get("/readyz", name="GET /readyz")

    @task(5)
    def start_session(self):
        payload = {"parent_name": rand_name()}
        with self.client.post("/api/coach/start", json=payload, name="POST /api/coach/start", catch_response=True) as resp:
            if resp.status_code != 200 or not resp.json().get("session_id"):
                resp.failure("no session_id returned")
            else:
                resp.success()
