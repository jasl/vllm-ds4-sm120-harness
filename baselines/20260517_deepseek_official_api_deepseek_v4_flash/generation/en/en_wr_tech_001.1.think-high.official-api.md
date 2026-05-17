# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-v4-flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `official-api`
- OK: `True`
- Status: PASS
- Check: expectation checks skipped
- Detail: `expectation checks skipped`
- Elapsed seconds: 33.546755
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "completion_tokens": 3227, "total_tokens": 3379, "prompt_tokens_details": {"cached_tokens": 128}, "completion_tokens_details": {"reasoning_tokens": 930}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 24}`
- Prompt tokens: 152
- Completion tokens: 3227
- Total tokens: 3379

## Prompt

```markdown
Write an 800–1,000 word technical article for backend engineers titled by you. Topic: designing rate limiting for a multi-tenant API used by small teams and enterprise customers.

You must cover:
1. The difference between authentication, authorization, quotas, and rate limits.
2. Token bucket vs. fixed window vs. sliding window at a practical level.
3. How to avoid punishing an entire tenant for one noisy integration.
4. What headers and error messages should be returned to API clients.
5. Observability: metrics, logs, and alerts that show whether limits are protecting reliability without blocking legitimate use.

Constraints: no code; no vendor-specific services; include a short “recommended baseline design” section at the end.
```

## Reasoning Content

```text
We need to write a technical article for backend engineers on designing rate limiting for a multi-tenant API. The article should be 800-1000 words, no code, no vendor-specific services. Cover: 1) difference between auth, authz, quotas, rate limits; 2) token bucket vs fixed window vs sliding window; 3) avoid punishing entire tenant for one noisy integration; 4) headers and error messages; 5) observability. End with "recommended baseline design" section.

Outline:

- Title: "Rate Limiting for Multi-Tenant APIs: Balancing Fairness, Isolation, and Reliability"

- Introduction: multi-tenant API serving small teams and enterprise customers. Need for rate limiting to protect system, but must not harm legitimate use.

1. Distinguishing auth, authz, quotas, rate limits:
   - Authentication: who you are (API key, OAuth)
   - Authorization: what you can do (scopes, permissions)
   - Quotas: long-term allowance (e.g., 10k requests/month) often tied to billing
   - Rate limits: short-term control (requests per second/minute) to prevent overload

2. Algorithm comparison:
   - Token bucket: allows bursts, smooth out. "A bucket that refills at a constant rate." Practical: start with burst capacity, then refill. Good for variable traffic.
   - Fixed window: e.g., 1000 requests per hour. Reset at boundary. Problem: traffic spikes at window edges can cause double bursts.
   - Sliding window: e.g., sliding window counter (logs or rolling time). More accurate, but more memory/cost. Practical trade-off: sliding window log (precise but expensive) vs sliding window counter (approximate but efficient). For multi-tenant, need per-tenant state.

3. Avoiding punishing entire tenant for one noisy integration:
   - Use per-key or per-integration rate limits within a tenant. E.g., separate limits per API key, or per endpoint, or per "sub-tenant" (like a project or app). Enterprise customers may have multiple integrations.
   - Hierarchical limits: tenant-level limit as a cap, but individual sub-limits for each key. If one key spikes, it gets throttled, but other keys for same tenant unaffected.
   - Use "concurrency limits" to prevent a single slow consumer from holding many connections.
   - Consider "fairness" with weighted queues.

4. Headers and error messages:
   - Standard: RateLimit-Limit, RateLimit-Remaining, RateLimit-Reset (or Retry-After).
   - For multi-tenant: include scope info (e.g., X-RateLimit-KeyId or tenantId in response? careful with security. Better to have generic headers).
   - Error: 429 Too Many Requests with JSON body: error code, message, retry_after seconds, maybe limit type (global vs per-key).
   - Retry-After header in seconds (or HTTP-date). Must be clear.

5. Observability:
   - Metrics: per-tenant request rate, throttle rate, error rate (429), latency. Track burst usage. Alerts on high throttle rates (e.g., >5% of requests throttled for a tenant) or on a single key causing high global load.
   - Logs: throttle events with tenant, key, limit type, timestamp, request path. Not too verbose to avoid cost.
   - Dashboards: top noisy tenants, top throttled keys, remaining capacity.
   - Alerts: if global or tenant-level rate limit is nearly exhausted, or if a key is constantly hitting limits (bad integration). Also alert on sudden drop in rate (possible misconfiguration).

6. Recommended baseline design:
   - Use sliding window counter (e.g., Redis sorted sets or in-memory with fixed windows and sliding via bucketing). Trade-off accuracy vs cost.
   - Implement two-tier limits: per-API-key (or per-integration) and per-tenant cap. The cap is enforced only if total tenant traffic exceeds it; otherwise key limits apply.
   - Use token bucket variant for burst handling: allow short bursts (e.g., 2x refill rate) but smooth.
   - Return 429 with clear headers and body.
   - Monitor and alert on key-level throttling.

Make sure article is technical but not code. Use practical examples. Keep within 800-1000 words.

Now write the article.
```

## Assistant

```markdown
# Rate Limiting for Multi-Tenant APIs: Balancing Fairness, Isolation, and Reliability

Building an API that serves both small teams and enterprise customers introduces a fundamental tension: how do you protect your backend from overload without punishing the majority of users for the behavior of a few? The answer lies in a rate‑limiting architecture that is tenant‑aware, algorithmically deliberate, and instrumented for observability. This article walks through the core concepts, algorithm trade‑offs, isolation strategies, client communication, and monitoring that backend engineers need to design a robust multi‑tenant rate limiter.

## 1. Authentication, Authorization, Quotas, and Rate Limits – What’s Different?

These four concepts are often conflated, but each serves a distinct purpose in a multi‑tenant API:

- **Authentication** verifies *who* the caller is – typically via an API key, OAuth token, or service ID. It establishes the tenant and the specific integration (key) making the request.
- **Authorization** determines *what* the caller is allowed to do – e.g., read vs. write, access to specific resources. It is scoped to the authenticated identity and often enforced by a policy engine.
- **Quotas** grant a long‑term allowance, usually tied to a billing plan (10,000 requests/month, 1 GB storage). Quotas are typically decremented as requests are made and reset on a monthly or billing cycle. They are about *capacity planning* and *fair use*.
- **Rate limits** control the *short‑term* rate of requests – requests per second, per minute, or per hour. Their purpose is to protect backend resources from sudden traffic spikes, abuse, or misconfigured clients. Unlike quotas, rate limits reset frequently (often seconds or minutes) and are independent of billing tiers.

In a multi‑tenant system, quotas are often per‑tenant (or per‑subscription), while rate limits should be applied at a finer granularity – per API key, per endpoint, or per integration – to avoid a single noisy consumer degrading service for the rest of the tenant.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window – Practical Trade‑Offs

Each algorithm offers different burst characteristics and memory/accuracy trade‑offs. For multi‑tenant APIs with thousands of keys, the choice directly affects operational cost and user experience.

### Fixed Window

Simplest to implement: divide time into discrete windows (e.g., one minute) and allow a fixed number of requests per window. The major drawback is *edge burst*: if a client sends 100 requests just before the window boundary and another 100 just after, they effectively double the allowed rate for that brief moment. This can defeat the protection goal. Fixed windows are cheap in memory (one counter per key per window) but poor at smoothing traffic.

### Token Bucket

Conceptually, a bucket holds tokens that refill at a constant rate (e.g., 10 tokens per second). Each request consumes one token. Bursts are allowed up to the bucket capacity (e.g., 30 tokens). This naturally absorbs spikes while limiting sustained load. Implementation is straightforward: for each key, store the current token count and last refill timestamp. The bucket resets only on depletion, not on calendar time. Token bucket is ideal for APIs where clients benefit from short bursts (e.g., a CI/CD tool pushing commits). The cost is slightly higher – two values per key – but still cheap.

### Sliding Window (Counter / Log)

A true sliding window tracks all request timestamps within the window (e.g., last 60 seconds). This yields perfect accuracy but can require significant memory for high‑volume keys (e.g., storing 10,000 timestamps per key). The *sliding window counter* approximation divides the window into small buckets (e.g., 1‑second slots) and aggregates counts, requiring only a few integers per key. It offers near‑perfect accuracy with low memory, making it the pragmatic choice for multi‑tenant systems where per‑key state must be kept in a distributed cache (Redis).

**Recommendation**: For most multi‑tenant backends, a sliding window counter is the best balance. It avoids edge bursts, supports smooth rate enforcement, and scales to thousands of tenants and hundreds of thousands of keys.

## 3. Avoiding Tenant‑Wide Punishment from a Noisy Integration

An enterprise customer may have dozens of API keys – one for each team, service, or environment. If one misbehaving key triggers a tenant‑level limit, all other keys from that customer are unfairly blocked. The solution is **hierarchical rate limiting**.

Design two tiers:

- **Per‑key (or per‑integration) limit**: Each API key gets its own sliding window counter (e.g., 100 requests per minute). This enforces fairness *within* a tenant.
- **Per‑tenant cap**: A separate counter tracks total requests across all keys for that tenant. The cap should be higher than any single key’s limit (e.g., 500 requests per minute for a tenant with 10 keys). The tenant cap acts as a safety net, preventing one tenant from overwhelming the system even if its keys are well‑distributed.

**Enforcement order**: For every request, check the key‑level limit first. If that key is over its limit, reject immediately *without* decrementing the tenant cap. Only when a request passes its key limit should the tenant cap be checked. If the tenant is over its global limit, reject regardless of the key’s status.

This design ensures that a noisy key cannot starve other keys in the same tenant – each key operates independently until the tenant cap is hit. The cap may only be reached if the sum of all keys exceeds it, which usually requires near‑simultaneous spikes across many keys.

Additionally, consider **concurrency limits** (e.g., maximum parallel requests per key) to protect against a single slow consumer holding many connections. Concurrency limits operate at the request‑in‑flight level and complement rate limits.

## 4. Headers and Error Messages – Communicating Limits to Clients

Clients need clear, machine‑readable information to self‑regulate. The API should return these standard headers on every response:

- `X-RateLimit-Limit`: The maximum number of requests allowed per window (e.g., 100).
- `X-RateLimit-Remaining`: The number of requests remaining in the current window.
- `X-RateLimit-Reset`: The Unix timestamp when the window resets, or when the next token will be available (for token bucket).

When a request is rejected, return HTTP `429 Too Many Requests` with:

- `Retry-After` header: seconds until the client can retry (e.g., `Retry-After: 30`).
- A JSON body containing:
  - `error.code`: `"rate_limit_exceeded"`
  - `error.message`: Human‑readable explanation, optionally scoped to the limit type (e.g., “per‑key limit for API key `abc123` exceeded. Retry after 30 seconds.”)
  - `error.retry_after_seconds`: Integer for programmatic handling.

**Important**: Do not leak the tenant’s internal limits (e.g., the exact tenant cap) in error messages for security reasons – exposing the total tenant capacity could reveal billing plan details or internal capacity. Stick to key‑level information.

## 5. Observability – Ensuring Limits Protect Without Blocking Legitimate Use

Rate limits are only useful if you can see their effect. Build a dashboard and alerting around three categories:

### Metrics
- **Per‑tenant request rate** (requests/second), **throttle rate** (429s/second), and **latency**. Track both total and per‑key.
- **Burst utilization**: percentage of the window’s capacity used at any moment. A key repeatedly hitting 100% suggests the limit is too low.
- **Throttle ratio**: percentage of requests rejected for each key/tenant. Alert when this exceeds 5% for a key over a 5‑minute window – it indicates a misconfigured client or anomalous spike.
- **Tenant‑cap exhaustion**: count how often the tenant cap is hit per day. A high number may mean the global cap is too tight or one key’s burst is consuming shared capacity.

### Logs
- Log every rate‑limit rejection with structured fields: `tenant_id`, `key_id`, `limit_type` (`key` or `tenant`), `limit_value`, `remaining`, `retry_after_seconds`, `request_path`. Avoid logging the request body for privacy, but log enough to trace the integration.
- Aggressive log sampling? No – rate‑limit events should be logged at full fidelity because they are relatively rare (compared to successful requests) and highly diagnostic.

### Alerts
- **Key‑level throttling spike**: if a single key’s throttle ratio jumps above a threshold, notify the tenant’s support contact (or the API team) – the client may have a bug or be under attack.
- **Tenant‑cap hit**: indicates that multiple keys are coordinating (or one key is using many sub‑accounts). Investigate whether the tenant’s capacity needs adjustment.
- **System‑wide 429 surge**: if the global throttle rate exceeds, say, 10%, it could signal a DDoS or a cascading failure. This demands immediate pager action.

A well‑monitored rate limiter becomes a diagnostic tool rather than a hard wall – it tells you which integrations need tuning and whether your infrastructure is coping.

## Recommended Baseline Design

Based on the above, here is a configuration that works for a multi‑tenant API with both small teams and enterprises:

- **Algorithm**: Sliding window counter per API key, implemented in a distributed cache (Redis with small buckets). Allow bursts up to 2× the sustained rate.
- **Tiering**:
  - Per‑key limit: 100 requests/minute (adjustable per plan).
  - Per‑tenant cap: 500 requests/minute for a basic plan, 2,000 for enterprise – decoupled from key limits.
- **Enforcement order**: Check key limit → if exceeded, reject → else check tenant cap → if exceeded, reject → else allow and decrement both counters.
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` with window duration. On 429: `Retry-After` + JSON body with `error.code`, `error.retry_after_seconds`.
- **Observability**: Prometheus‑style metrics exported per tenant and per key (top‑K by throttle rate). Log all rejections. Alert on key throttle >5%, tenant cap hit, global spike >10%.

This design protects your backend from overload while ensuring that one noisy integration cannot degrade the experience for the rest of the tenant – or for the whole platform.
```
