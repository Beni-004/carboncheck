# Architecture One-Pager: CarbonCheck Technical Design

**Audience**: Technical judges, backend engineers, CTOs  
**Goal**: Demonstrate architectural rigor and hackathon-appropriate trade-offs  
**Read Time**: 3 minutes

---

## System Overview

CarbonCheck is a trust-scoring API for carbon credits with three primary flows:

1. **Single-ID verification**: `POST /api/verify` with one credit ID → Trust Score in <5 seconds
2. **Bulk verification**: `POST /api/verify` with up to 50 credit IDs → Ranked fraud report in <20 seconds
3. **Public leaderboard**: `GET /api/leaderboard` → Most-flagged credits by type, cached, no auth

**Core Design Constraint**: Never return HTTP 500. System must degrade gracefully under upstream failure.

---

## Architecture Diagram

```
┌─────────────┐
│   Browser   │
│  (Next.js)  │
└──────┬──────┘
       │ HTTPS
       ↓
┌─────────────────────────────────────────────┐
│          Vercel Edge (Frontend)             │
│   • Server-side rendering                   │
│   • API route proxying                      │
│   • Static leaderboard caching              │
└──────┬──────────────────────────────────────┘
       │ HTTPS
       ↓
┌─────────────────────────────────────────────┐
│       Railway (FastAPI Backend)             │
│                                             │
│  ┌────────────────────────────────────┐   │
│  │  POST /api/verify                  │   │
│  │  • Pydantic request validation     │   │
│  │  • Parallel 4-source fetch         │   │
│  │  • 3-second per-source timeout     │   │
│  │  • Deterministic scoring engine    │   │
│  │  • Fallback to Supabase cache      │   │
│  └────────────────────────────────────┘   │
│                                             │
│  ┌────────────────────────────────────┐   │
│  │  GET /api/leaderboard              │   │
│  │  • Read from leaderboard_cache     │   │
│  │  • 5-minute refresh cycle          │   │
│  │  • No auth required (public read)  │   │
│  └────────────────────────────────────┘   │
│                                             │
│  ┌────────────────────────────────────┐   │
│  │  Middleware: Error Envelope        │   │
│  │  • Catch all exceptions            │   │
│  │  • Map to domain error codes       │   │
│  │  • Return 200/400/422/429/503      │   │
│  │  • NEVER return 500                │   │
│  └────────────────────────────────────┘   │
└──────┬──────────────────────────────────────┘
       │
       ├──→ Ember API (3s timeout)
       ├──→ CEA Registry (3s timeout)
       ├──→ Grid-India (3s timeout)
       ├──→ REC Registry (3s timeout)
       │
       ↓ (fallback when upstream fails)
┌─────────────────────────────────────────────┐
│        Supabase Postgres (Cache)            │
│                                             │
│  Tables:                                    │
│  • carbon_credits (metadata)                │
│  • trust_scores (verification history)      │
│  • leaderboard_cache (aggregated ranks)     │
│                                             │
│  Indexes:                                   │
│  • carbon_credits(credit_id) UNIQUE         │
│  • trust_scores(credit_id, created_at)      │
│  • leaderboard_cache(rank_global, type)     │
└─────────────────────────────────────────────┘
```

---

## Key Design Decisions

### 1. Deterministic Scoring Formula

**Requirement**: Same input + same source snapshot = identical score every time.

**Implementation**:
```python
# Weighted scoring formula (fixed in constants.py)
WEIGHTS = {
    "baseline_match": 0.30,
    "additionality": 0.25,
    "permanence_risk": 0.25,
    "double_counting": 0.20
}

def compute_trust_score(checks: Dict[str, float]) -> float:
    return sum(checks[key] * WEIGHTS[key] for key in checks)

# Source snapshot hash for cache key
def snapshot_hash(sources: Dict[str, SourceData]) -> str:
    timestamps = [s.fetched_at.isoformat() for s in sources.values()]
    return hashlib.sha256("|".join(sorted(timestamps)).encode()).hexdigest()
```

**Why**: Reproducibility is critical for audit trails and legal defensibility.

---

### 2. Per-Source Timeout Enforcement

**Requirement**: External APIs capped at 3 seconds; system must not wait indefinitely.

**Implementation**:
```python
import httpx

async def fetch_source(source_name: str, credit_id: str) -> SourceData:
    async with httpx.AsyncClient(timeout=3.0) as client:
        try:
            response = await client.get(f"{SOURCE_URLS[source_name]}/{credit_id}")
            return parse_response(response)
        except httpx.TimeoutException:
            return fallback_from_cache(source_name, credit_id)
```

**Why**: Upstream registries are unreliable. Fixed timeout prevents cascading delays.

---

### 3. Fallback to Supabase Cache

**Requirement**: If upstream source fails, serve cached data; never return "no score available."

**Implementation**:
```python
def fallback_from_cache(source_name: str, credit_id: str) -> SourceData:
    cached = supabase.table("trust_scores") \
        .select("*") \
        .eq("credit_id", credit_id) \
        .eq("source", source_name) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()
    
    if cached.data:
        return SourceData(
            source=source_name,
            fetched_at=cached.data[0]["created_at"],
            freshness_state="stale",
            from_cache=True,
            data=cached.data[0]["data"]
        )
    else:
        return SourceData(source=source_name, freshness_state="missing", from_cache=True)
```

**Why**: Demo must not fail during live presentation. Cache provides continuity.

---

### 4. Never Return HTTP 500

**Requirement**: All errors wrapped in domain-specific envelopes with 200/4xx/503 status codes.

**Implementation**:
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, ValidationError):
        return JSONResponse(status_code=422, content={
            "status": "error",
            "code": "VALIDATION_FAILED",
            "message": str(exc),
            "request_id": str(uuid.uuid4())
        })
    
    # Unknown errors → 503 with degraded state (not 500)
    return JSONResponse(status_code=503, content={
        "status": "degraded",
        "code": "UNKNOWN_ERROR",
        "message": "Service temporarily degraded; please retry.",
        "request_id": str(uuid.uuid4())
    })
```

**Why**: HTTP 500 indicates unhandled failure. We handle all failure modes explicitly.

---

### 5. Bulk Verification Parallelism

**Requirement**: Process up to 50 IDs in one request without sequential bottlenecks.

**Implementation**:
```python
import asyncio

async def verify_bulk(credit_ids: List[str]) -> List[VerifyResult]:
    tasks = [verify_single(credit_id) for credit_id in credit_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Separate successes from errors
    successes = [r for r in results if isinstance(r, VerifyResult)]
    errors = [{"credit_id": credit_ids[i], "error": str(results[i])}
              for i in range(len(results)) if isinstance(results[i], Exception)]
    
    # Rank successes by trust_score (lowest = highest risk)
    ranked = sorted(successes, key=lambda r: r.trust_score)
    for rank, result in enumerate(ranked, start=1):
        result.rank = rank
    
    return {"results": ranked, "errors": errors}
```

**Why**: Sequential processing would take 50 × 5s = 250 seconds. Parallel execution: ~5 seconds.

---

## Tech Stack Rationale

| Technology | Why Chosen | Alternative Considered |
|------------|-----------|------------------------|
| **FastAPI** | Native async support, Pydantic validation, OpenAPI auto-generation | Flask (no async), Django (too heavy) |
| **Next.js 14** | Server-side rendering, API routes, Vercel edge deploy | React SPA (worse SEO), Vue (smaller ecosystem) |
| **Supabase** | Postgres with real-time subscriptions, generous free tier, fast setup | MongoDB (schema flexibility not needed), Firebase (vendor lock-in) |
| **Railway** | Simple FastAPI deployment, free tier, good DX | Heroku (expensive), AWS Lambda (cold start latency) |
| **Pydantic v2** | Strict validation, automatic OpenAPI schema sync | Marshmallow (slower), manual validation (error-prone) |

---

## Performance Targets

| Metric | Target | How Measured |
|--------|--------|--------------|
| **Single-ID p95 latency** | <5 seconds | Locust load test with 100 concurrent users |
| **Bulk-50 p95 latency** | <20 seconds | Locust load test with 20 concurrent bulk requests |
| **Leaderboard p95 latency** | <3 seconds | Static cache hit rate >95% |
| **Cache fallback success rate** | >99% | Simulate upstream outage, verify non-500 responses |
| **Deterministic scoring** | 100% | Unit test: same input → same score across 1000 runs |

---

## Security Considerations

### Rate Limiting
- **Freemium**: 10 verifications/month, 1 req/sec burst.
- **Pro**: 500 verifications/month, 5 req/sec burst.
- **Enterprise**: Unlimited, 50 req/sec burst.

**Implementation**: Nginx rate-limit module on Railway reverse proxy.

---

### Input Validation
- **Credit ID format**: Regex `^[A-Z]{3,4}-\d{4}-[A-Z]{3}-\d{4}$`
- **Bulk payload max**: 50 IDs (enforced at Pydantic schema level)
- **No SQL injection risk**: Supabase client uses parameterized queries

---

### API Key Management
- **Upstream sources**: API keys stored in Railway environment variables (not in code)
- **Supabase**: Anon key for public leaderboard reads, service role key for backend writes

---

## Failure Mode Handling

| Failure Scenario | System Behavior | HTTP Status |
|------------------|-----------------|-------------|
| **All 4 sources timeout** | Serve cached data, mark `fallback_used: true` | 200 (degraded) |
| **Supabase down** | Return 503 with "cache unavailable" message | 503 |
| **Invalid credit ID format** | Return validation error with example | 422 |
| **Rate limit exceeded** | Return 429 with `Retry-After` header | 429 |
| **Unknown exception** | Log error, return generic 503 | 503 (never 500) |

---

## Testing Strategy

### Unit Tests (pytest)
- Deterministic scoring: same input → same output
- Fallback logic: mock source timeout → verify cache hit
- Error envelope: raise exception → verify 503 response

### Integration Tests (pytest + Supabase)
- End-to-end single verify: API call → DB persist → response contract
- End-to-end bulk verify: 50 IDs → ranked output → partial error handling

### Contract Tests (Pydantic + OpenAPI)
- Request/response schemas match `openapi.yaml`
- No schema drift between docs and implementation

### Smoke Tests (Playwright)
- Critical path: verify page → paste ID → see score <5s
- Leaderboard: public page loads without auth <3s

---

## Deployment Pipeline

```
git push → GitHub Actions
  ↓
  1. Run pytest (unit + integration)
  2. Run Pydantic schema validation
  3. Deploy API to Railway (staging)
  4. Run Playwright smoke tests (staging)
  5. Deploy frontend to Vercel (production)
  6. Deploy API to Railway (production)
  7. Send Slack notification
```

**Rollback**: Railway keeps last 10 deployments; one-click rollback in dashboard.

---

## Scalability Considerations (Post-MVP)

- **Horizontal scaling**: Railway auto-scales FastAPI instances based on CPU >70%.
- **Database connection pooling**: Supabase pooler (PgBouncer) handles 1000+ concurrent connections.
- **CDN for leaderboard**: Cloudflare caches leaderboard JSON for 5 minutes, reduces DB load.
- **Async job queue**: Add Celery + Redis for batch processing >50 IDs.

---

## Known Limitations (Hackathon Scope)

1. **No user authentication** (MVP uses anonymous freemium tier; Pro/Enterprise auth is roadmap).
2. **Fixed scoring weights** (custom weight profiles deferred to Month 2).
3. **No real-time leaderboard** (5-minute cache refresh is acceptable for MVP).
4. **No blockchain registry integrations** (Verra, Gold Standard deferred to Week 2).

---

## Judge Q&A Prep

### Q: "Why FastAPI over Flask?"

**Answer:**
> "FastAPI gives us native async support for parallel source calls, automatic OpenAPI schema generation, and Pydantic validation baked in. Flask would require third-party libraries for all three. For a 24-hour hackathon, FastAPI's batteries-included approach saved us 4 hours of boilerplate."

---

### Q: "What's your plan if Supabase has an outage during the live demo?"

**Answer:**
> "We pre-seed the local database with demo data before going on stage. If Supabase is down, we switch the connection string to a local Postgres instance running on the demo laptop. Judges won't notice the difference—same API behavior, just different backing store."

---

### Q: "How do you prevent one slow upstream source from blocking the other three?"

**Answer:**
> "Each source call is an independent async task with a 3-second hard timeout. We use `asyncio.gather()` with `return_exceptions=True`, so if one source times out, the other three still complete. The timeout source falls back to cache, and we mark it as stale in the response."

---

## Success Metrics

- **Technical judges nod at "deterministic scoring"** → They recognize the rigor.
- **Backend judges ask follow-up questions about fallback logic** → They're engaged with the architecture.
- **At least one judge asks "Can I see the OpenAPI spec?"** → They appreciate contract-first design.
- **No judge asks "What happens if it crashes?"** → Failure modes are well-explained upfront.
