from locust import HttpUser, between, task


class ShortenerUser(HttpUser):
    wait_time = between(0.1, 1.0)

    @task(3)
    def create_short_link(self) -> None:
        self.client.post(
            "/api/links",
            json={"original_url": "https://example.com/system-design/url-shortener"},
        )

    @task(7)
    def redirect_hot_link(self) -> None:
        self.client.get("/1", allow_redirects=False, name="/{code}")
