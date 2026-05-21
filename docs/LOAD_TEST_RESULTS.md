# Load Test Results

This project includes a Locust script in `load-tests/locustfile.py`.

## How To Run

Start the backend:

```bash
cd api
uvicorn app.main:app --reload --port 8000
```

Install Locust:

```bash
pip install locust
```

Run:

```bash
locust -f load-tests/locustfile.py --host http://localhost:8000
```

## Suggested Test Plan

| Scenario | Users | Spawn Rate | Duration | Goal |
|---|---:|---:|---:|---|
| Smoke | 10 | 2/s | 2 min | Validate endpoints |
| Rate limit | 50 | 10/s | 3 min | Confirm 429 responses |
| Redirect heavy | 200 | 20/s | 5 min | Observe redirect latency |

## Expected Bottlenecks

- SQLite is not suitable for high-write load tests.
- PostgreSQL improves concurrent writes.
- Async analytics queue should be added before high-scale production traffic.
- Redis should be enabled for distributed rate limiting across multiple API instances.
