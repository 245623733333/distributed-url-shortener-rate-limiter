# LinkForge System Design

## Goal

Build a URL shortener that creates compact links, redirects users with low latency, tracks click analytics, and protects write endpoints with rate limiting.

## Functional Requirements

- Create short URLs
- Support custom aliases
- Support optional expiry
- Redirect short URLs to destination URLs
- Track click events
- Show analytics dashboard
- Apply rate limits to prevent abuse

## Non-Functional Requirements

- Low-latency redirects
- High read availability
- Collision-safe short code generation
- Horizontally scalable API instances
- Durable storage for links and analytics
- Cache hot links with Redis

## High-Level Architecture

```text
Client
  |
  v
Load Balancer
  |
  v
FastAPI App Instances
  |        |
  |        +--> Redis cache and rate limiter
  |
  +--> PostgreSQL links and analytics
```

## Data Model

### short_links

- `id`: primary key
- `code`: Base62 short code
- `original_url`: destination URL
- `custom_alias`: optional user-defined alias
- `expires_at`: optional expiry timestamp
- `click_count`: aggregate click counter
- `created_at`, `updated_at`

### click_events

- `id`: primary key
- `link_id`: foreign key
- `ip_address`
- `user_agent`
- `referer`
- `country`
- `created_at`

## Short Code Generation

The system uses Base62 encoding over the database id. For example:

```text
1 -> 1
61 -> Z
62 -> 10
```

This gives short, URL-safe identifiers. If a collision occurs, the service appends a small random suffix and checks again.

## Rate Limiting

The create-link endpoint uses a fixed-window limiter:

```text
key = rate-limit:create:{client_ip}
window = 60 seconds
limit = 20 requests
```

Redis is used when available. If Redis is not configured, the app falls back to an in-memory limiter for local development.

## Redirect Path

1. User requests `/{code}`.
2. API checks whether the short link exists, is active, and is not expired.
3. API increments aggregate click count.
4. API schedules click-event persistence as a background task.
5. API returns HTTP 307 redirect to the original URL.

## Analytics Path

The analytics endpoint returns:

- Total clicks
- Clicks in the last 24 hours
- Top referrers
- Recent click events

For higher scale, click events should be sent to a queue and processed asynchronously by workers.

## Scaling Plan

- Add Redis read-through cache for `code -> original_url`.
- Move click analytics writes to Kafka, RabbitMQ, Celery, or RQ.
- Partition click events by time.
- Add CDN or edge redirects for very hot links.
- Add abuse detection and account-based quotas.
- Use read replicas for analytics queries.

## Tradeoffs

- Base62 from sequential ids is simple and compact, but it reveals approximate creation order.
- Random codes hide ordering better, but require stronger collision handling.
- Synchronous click count increments are simple, but async event streams scale better.
