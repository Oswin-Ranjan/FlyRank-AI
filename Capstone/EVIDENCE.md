# EVIDENCE

## Definition of Done Evidence

Evidence will be added continuously as each requirement is completed.

---

## Phase 1

### Project starts successfully
Status: In progress

Planned proof:
- `docker compose up --build`
- `GET /health`
- FastAPI `/docs` loads successfully

### Database schema
Status: Complete

Command:

```bash
alembic upgrade head
```

Evidence:
- Alembic migration completed successfully.
- PostgreSQL tables verified:
  - tenants
  - plans
  - subscriptions
  - usage_events
  - stripe_events
  - alembic_version

### Seed Data

Status: Complete

Command:

```bash
python -m app.seed
```

Evidence:
- Free plan created
- Pro plan created
- Demo tenant created
- Demo tenant assigned a Free subscription

Terminal output:

  Database seeded successfully.
  
  Free Plan ID: 1
  
  Pro Plan ID: 2
  
  Demo Tenant ID: 1

### Design Document  

Status: Complete

Evidence:

- DESIGN.md documents:
  - Problem
  - Scope
  - Plans and quotas
  - Data model
  - API surface
  - Idempotency strategy
  - Quota strategy
  - Layered architecture
  - Explicit non-goal

### API contract

Status: Complete

Defined API surface:
- POST /generate
- GET /usage
- POST /billing/checkout
- POST /webhooks/stripe

### Idempotency strategy

Status: Complete

Evidence:
- usage_events contains idempotency_key.
- A unique constraint exists on (tenant_id, idempotency_key).
- Detailed behavior is documented in DESIGN.md.

### Idempotency
Status: Not started

### Quota enforcement
Status: Not started

### Cost calculation
Status: Not started

### Stripe integration
Status: Not started

### Testing
Status: Not started

---

## Phase 2

### Idempotent usage metering

Status: In Progress

Evidence:

- Same `Idempotency-Key` returned the same usage event.
- Database contained only one usage event for the repeated request.

### Quota enforcement

Status: In Progress

Evidence:

- Request taking usage exactly to the configured limit was allowed.
- Request exceeding the configured limit returned HTTP 429.
- Response explained current usage, requested quantity, and limit.