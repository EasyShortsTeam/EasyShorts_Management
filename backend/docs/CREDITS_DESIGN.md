# Credits (Admin) Backend Design Notes

This document is written to help backend implementation converge with the current admin frontend + the `feat/admin-credits` PR.

## What the Admin Frontend Calls

Frontend page: `frontend/src/pages/CreditsPage.tsx`

Required endpoints (current scaffold):
- `GET /api/admin/credits/users?q=...`
  - Returns: `[{ user_id, email, username, credits_balance, updated_at }]`
- `GET /api/admin/credits/users/{user_id}`
  - Returns: `{ user_id, email, username, credits_balance, updated_at, ledger: [...] }`
- `POST /api/admin/credits/users/{user_id}/adjust`
  - Body: `{ delta: number, reason: string }`
  - Returns: `{ status: 'ok', user: CreditUserDetail }`

## Domain Decisions (Recommended)

### Credit model
- Credits are an integer.
- Balance is derived from a ledger OR stored as a cached column.
- All changes must be recorded as immutable ledger entries.

### Admin-only
- All `/api/admin/*` routes should require an admin role.
- At minimum: JWT validation + `role=admin`.

### Constraints
- Option A: allow negative balances (simpler for MVP).
- Option B: disallow negative balances (recommended): reject `delta` if it would drop below 0.

### Idempotency
- Credit adjustments should support idempotency key to prevent double-charging on retries.
  - Header: `Idempotency-Key: <uuid>`

## Suggested Database Schema (PostgreSQL)

### users
Assumes a main user table exists (or will exist). Minimal fields referenced by admin:
- `id (uuid or bigint)`
- `email (text, unique)`
- `username (text)`
- `role (text)`

### user_credit_balances (optional cache)
If you want fast reads without aggregating ledger each time:
- `user_id (pk, fk users.id)`
- `balance (int not null default 0)`
- `updated_at (timestamptz not null)`

### credit_ledger
Immutable history of changes:
- `id (uuid pk)`
- `user_id (fk users.id, index)`
- `delta (int not null)`
- `reason (text not null)`
- `actor_admin_id (fk users.id, nullable)`
- `idempotency_key (text, nullable, unique per user)`
- `created_at (timestamptz not null)`

Indexes:
- `(user_id, created_at desc)`
- `(user_id, idempotency_key)` unique

## Transaction Logic (Important)

When applying an adjustment:
1) Begin transaction
2) (Optional) verify `idempotency_key` not used
3) Lock the user balance row (or lock via `SELECT ... FOR UPDATE`)
4) Validate constraints (e.g., no negative)
5) Insert ledger row
6) Update cached balance row
7) Commit

If you do not maintain a cached balance, use aggregation + locking carefully.

## Response Contract

Keep current response shape (matches frontend expectations):
- `CreditUserSummary` and `CreditUserDetail` as in `backend/app/schemas/credits.py`

## Security / Audit

- Include `actor` (admin identifier) in ledger.
- Log IP/user-agent for admin actions if needed.
- Consider a dedicated admin token audience.

## Future Extensions

- `GET /api/admin/credits/users/{user_id}/ledger?cursor=...`
- Batch adjustments
- Credit usage (spending) endpoints for jobs/render pipeline
