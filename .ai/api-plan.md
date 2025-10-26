# REST API Plan

API Version: v1  
Base Path: `/api/v1`  
Format: JSON (UTF-8)  
Auth: JWT (HTTP-only secure cookie + optional `Authorization: Bearer <token>` header)  
Pagination: Cursor or offset (default: limit/offset style using DRF PageNumberPagination)  
Rate Limiting: DRF throttling (User & Anonymous) – assumptions documented below.

## 1. Resources
| Resource | DB Table | Description |
|----------|----------|-------------|
| User | `account_account` (custom AbstractUser) | Registered application user (login, email, password hash). |
| BrickSet | `catalog_brickset` | LEGO set record with defined physical/completeness attributes; globally unique combination of feature columns. |
| Valuation | `valuation_valuation` | A user's price estimate for a BrickSet (one per user-set pair). |
| Like | `valuation_like` | A user's like for a valuation (cannot like own valuation, unique per user & valuation). |
| Metrics | `valuation_metrics` (named as `valuation_metrics` in model layer) | Aggregated system counts (single-row table id=1). |
| Auth Token | (not persisted beyond JWT claims) | JWT used for stateless authentication. |

## 2. Endpoints

Conventions:
- All protected endpoints require authentication (FR-18) except registration & login.
- Error responses use a consistent envelope: `{ "detail": "message", "code": "ERROR_CODE" }` or validation: `{ "errors": { "field": ["message"] }, "code": "VALIDATION_ERROR" }`.
- Timestamps ISO 8601 with timezone (UTC): `2025-10-21T12:34:56Z`.
- Enumerations:
  - `production_status`: `ACTIVE`, `RETIRED`
  - `completeness`: `COMPLETE`, `INCOMPLETE`
  - `currency`: currently only `PLN`

### 2.1 Authentication & User Session

#### POST /api/v1/auth/register
Create a new user.
- Request (JSON):
```
{
  "username": "string (3-50 chars)",
  "email": "string (valid email)",
  "password": "string (>=8 chars)"
}
```
- Success 201:
```
{
  "id": 123,
  "username": "user123",
  "email": "user@example.com",
  "created_at": "2025-10-21T12:34:56Z"
}
```
  - Sets auth cookie if auto-login desired (optional; assumption: require explicit login -> do NOT auto-login by default).
- Errors:
  - 400 VALIDATION_ERROR (invalid email/length)
  - 409 USERNAME_TAKEN / EMAIL_TAKEN

#### POST /api/v1/auth/login
Authenticate user; returns JWT in HttpOnly secure cookie and optionally in body.
- Request:
```
{
  "username": "string",
  "password": "string"
}
```
- Success 200:
```
{
  "user": {"id": 123, "username": "user123", "email": "user@example.com"},
  "token": "<jwt>"
}
```
- Errors:
  - 400 VALIDATION_ERROR (missing fields)
  - 401 INVALID_CREDENTIALS

#### POST /api/v1/auth/logout
Invalidate client session (delete cookie).
- Success 204 (no body)
- Errors: 401 NOT_AUTHENTICATED

#### GET /api/v1/auth/me
Fetch current authenticated user profile.
- Success 200:
```
{
  "id": 123,
  "username": "user123",
  "email": "user@example.com",
  "created_at": "2025-10-21T12:34:56Z"
}
```
- Errors: 401 NOT_AUTHENTICATED

### 2.2 BrickSets

#### GET /api/v1/bricksets
List & search BrickSets (paginated). (FR-08)
- Query Params:
  - `q` (string, optional) partial numeric search on `number`.
  - `production_status` (enum)
  - `completeness` (enum)
  - `has_instructions` (bool)
  - `has_box` (bool)
  - `is_factory_sealed` (bool)
  - `ordering` (string) allowed: `-created_at`, `created_at`, `-popular` (maps to likes_count max among valuations), `-valuations` (count valuations desc). Default: `-created_at`.
  - `page` (int ≥1)
  - `page_size` (int 1-100, default 20)
- Success 200:
```
{
  "count": 57,
  "next": "https://.../bricksets?page=2",
  "previous": null,
  "results": [
    {
      "id": 10,
      "number": 12345,
      "production_status": "ACTIVE",
      "completeness": "COMPLETE",
      "has_instructions": true,
      "has_box": false,
      "is_factory_sealed": false,
      "owner_id": 42,
      "owner_initial_estimate": 350,
      "valuations_count": 5,
      "total_likes": 12,
      "top_valuation": {
        "id": 77,
        "value": 400,
        "currency": "PLN",
        "likes_count": 9,
        "user_id": 99
      },
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```
- Errors: 401 NOT_AUTHENTICATED (if enforcing login for search per FR-18) / 400 VALIDATION_ERROR

#### POST /api/v1/bricksets
Create BrickSet (FR-04, FR-05).
- Request:
```
{
  "number": 12345,
  "production_status": "ACTIVE",
  "completeness": "COMPLETE",
  "has_instructions": true,
  "has_box": true,
  "is_factory_sealed": false,
  "owner_initial_estimate": 360  // optional
}
```
- Success 201:
```
{
  "id": 10,
  "number": 12345,
  "production_status": "ACTIVE",
  "completeness": "COMPLETE",
  "has_instructions": true,
  "has_box": true,
  "is_factory_sealed": false,
  "owner_initial_estimate": 360,
  "owner_id": 42,
  "valuations_count": 0,
  "total_likes": 0,
  "created_at": "...",
  "updated_at": "..."
}
```
- Errors:
  - 400 VALIDATION_ERROR (ranges, types)
  - 409 BRICKSET_DUPLICATE (unique combination violation)
  - 401 NOT_AUTHENTICATED

#### GET /api/v1/bricksets/{id}
BrickSet detail with valuations summary (FR-09).
- Success 200:
```
{
  "id": 10,
  "number": 12345,
  "production_status": "ACTIVE",
  "completeness": "COMPLETE",
  "has_instructions": true,
  "has_box": true,
  "is_factory_sealed": false,
  "owner_initial_estimate": 360,
  "owner_id": 42,
  "valuations": [
    {
      "id": 77,
      "user_id": 99,
      "value": 400,
      "currency": "PLN",
      "comment": "Looks complete",
      "likes_count": 9,
      "created_at": "..."
    }
  ],
  "valuations_count": 5,
  "total_likes": 12,
  "created_at": "...",
  "updated_at": "..."
}
```
- Errors: 404 BRICKSET_NOT_FOUND / 401 NOT_AUTHENTICATED

#### PATCH /api/v1/bricksets/{id}
Edit BrickSet if rule allows (FR-06, RB-01). Only owner can edit and only if: no valuation by other users AND owner's valuation (if exists) has zero likes.
- Request (partial accepted):
```
{
  "has_box": true,
  "owner_initial_estimate": 370
}
```
- Success 200: returns updated BrickSet detail.
- Errors:
  - 403 BRICKSET_EDIT_FORBIDDEN (rule violation)
  - 404 BRICKSET_NOT_FOUND
  - 400 VALIDATION_ERROR
  - 401 NOT_AUTHENTICATED

#### DELETE /api/v1/bricksets/{id}
Remove BrickSet (FR-07, RB-01) same constraints as edit.
- Success 204 (no body)
- Errors:
  - 403 BRICKSET_DELETE_FORBIDDEN
  - 404 BRICKSET_NOT_FOUND
  - 401 NOT_AUTHENTICATED

### 2.3 Valuations

#### POST /api/v1/bricksets/{brickset_id}/valuations
Create valuation for a BrickSet (FR-10, FR-11). One per user-set.
- Request:
```
{
  "value": 400,
  "currency": "PLN",   // optional; default PLN
  "comment": "Looks complete"
}
```
- Success 201:
```
{
  "id": 77,
  "brickset_id": 10,
  "user_id": 99,
  "value": 400,
  "currency": "PLN",
  "comment": "Looks complete",
  "likes_count": 0,
  "created_at": "...",
  "updated_at": "..."
}
```
- Errors:
  - 409 VALUATION_DUPLICATE (already exists for user-set)
  - 400 VALIDATION_ERROR (value range 1..999999)
  - 404 BRICKSET_NOT_FOUND
  - 401 NOT_AUTHENTICATED

#### GET /api/v1/bricksets/{brickset_id}/valuations
List valuations of a BrickSet (sorted: likes_count desc then created_at asc) (FR-09).
- Query Params: `page`, `page_size` (if large). Default show all for detail; may paginate if > threshold.
- Success 200:
```
{
  "count": 5,
  "results": [
    {
      "id": 77,
      "user_id": 99,
      "value": 400,
      "currency": "PLN",
      "comment": "Looks complete",
      "likes_count": 9,
      "created_at": "..."
    }
  ]
}
```
- Errors: 404 BRICKSET_NOT_FOUND / 401 NOT_AUTHENTICATED

#### GET /api/v1/valuations/{id}
Fetch a single valuation.
- Success 200:
```
{
  "id": 77,
  "brickset_id": 10,
  "user_id": 99,
  "value": 400,
  "currency": "PLN",
  "comment": "Looks complete",
  "likes_count": 9,
  "created_at": "...",
  "updated_at": "..."
}
```
- Errors: 404 VALUATION_NOT_FOUND / 401 NOT_AUTHENTICATED

(Note: No update/delete per MVP scope.)

### 2.4 Likes

#### POST /api/v1/valuations/{valuation_id}/likes
Like a valuation (FR-12, FR-13). Body optional; can be empty.
- Success 201:
```
{
  "valuation_id": 77,
  "user_id": 42,
  "created_at": "..."
}
```
- Errors:
  - 403 LIKE_OWN_VALUATION_FORBIDDEN
  - 409 LIKE_DUPLICATE
  - 404 VALUATION_NOT_FOUND
  - 401 NOT_AUTHENTICATED

#### DELETE /api/v1/valuations/{valuation_id}/likes
Remove your like (optional convenience; not explicitly in PRD but added for completeness). If MVP chooses not to implement, mark 405 METHOD_NOT_ALLOWED.
- Success 204
- Errors: 404 LIKE_NOT_FOUND / 401 NOT_AUTHENTICATED

#### GET /api/v1/valuations/{valuation_id}/likes (optional)
List users who liked a valuation (privacy trade-off; can be deferred). Returns minimal user refs.
- Success 200:
```
{
  "count": 9,
  "results": [{"user_id": 42, "liked_at": "..."}]
}
```
- Errors: 404 VALUATION_NOT_FOUND / 401 NOT_AUTHENTICATED

### 2.5 User-Owned Collections

#### GET /api/v1/users/me/bricksets
List my BrickSets with stats (FR-14).
- Query Params: `page`, `page_size`, optional `ordering` (`-created_at`, `-valuations`, `-likes`).
- Success 200:
```
{
  "count": 3,
  "results": [
    {
      "id": 10,
      "number": 12345,
      "production_status": "ACTIVE",
      "completeness": "COMPLETE",
      "valuations_count": 5,
      "total_likes": 12,
      "editable": true  // derived by RB-01 rule
    }
  ]
}
```
- Errors: 401 NOT_AUTHENTICATED

#### GET /api/v1/users/me/valuations
List my valuations (FR-15).
- Success 200:
```
{
  "count": 7,
  "results": [
    {
      "id": 77,
      "brickset": {
        "id": 10,
        "number": 12345
      },
      "value": 400,
      "currency": "PLN",
      "likes_count": 9,
      "created_at": "..."
    }
  ]
}
```
- Errors: 401 NOT_AUTHENTICATED

### 2.7 Error Handling Summary
| HTTP | Code | Message Example |
|------|------|-----------------|
| 400 | VALIDATION_ERROR | Field 'number' must be 0-9999999 |
| 401 | NOT_AUTHENTICATED | Authentication credentials were not provided |
| 401 | INVALID_CREDENTIALS | Incorrect username or password |
| 403 | BRICKSET_EDIT_FORBIDDEN | BrickSet locked due to external valuation or liked owner valuation |
| 403 | BRICKSET_DELETE_FORBIDDEN | BrickSet locked; cannot delete |
| 403 | LIKE_OWN_VALUATION_FORBIDDEN | Cannot like own valuation |
| 404 | BRICKSET_NOT_FOUND | BrickSet not found |
| 404 | VALUATION_NOT_FOUND | Valuation not found |
| 404 | LIKE_NOT_FOUND | Like not found |
| 409 | BRICKSET_DUPLICATE | BrickSet with identical attributes already exists |
| 409 | VALUATION_DUPLICATE | Valuation already exists for this BrickSet and user |
| 409 | LIKE_DUPLICATE | Already liked this valuation |
| 422 | RULE_VIOLATION | Business rule violation (alternative to 403) |
| 405 | METHOD_NOT_ALLOWED | Endpoint does not support DELETE |

## 3. Authentication and Authorization

Mechanism: JWT-based stateless auth.
- Registration creates user record; password hashed via Django's password hasher (PBKDF2).
- Login issues JWT (HS256 or RS256). Claims: `sub` (user id), `iat`, `exp` (e.g., 24h), `username`.
- Token delivered in HttpOnly `Set-Cookie: bv_token=<jwt>; Secure; SameSite=Strict` and optionally response body. Clients may store in memory; avoid localStorage.
- DRF custom authentication class extracts token from cookie or `Authorization` header.
- Permissions:
  - BrickSet modify/delete: owner only + RB-01 rule evaluation.
  - Valuation create: authenticated.
  - Like create/delete: authenticated + user != valuation.user.
  - Metrics: authenticated (MVP) – future: staff/admin.
- Optional refresh token design deferred (MVP scope minimal). If needed: add `/auth/refresh` returning new short-lived access token.
- Logout: instruct client to delete cookie; server can maintain denylist if refresh tokens introduced later.

## 4. Validation and Business Logic

### 4.1 Field Validation Rules
| Field | Constraints |
|-------|-------------|
| User.username | Required, unique, length 3..50, regex optional `[A-Za-z0-9._-]+` |
| User.email | Required, unique, email format, length >2 |
| User.password | Required, length ≥8 (complexity optional) |
| BrickSet.number | Required integer 0..9999999 |
| BrickSet.production_status | Enum {ACTIVE, RETIRED} |
| BrickSet.completeness | Enum {COMPLETE, INCOMPLETE} |
| BrickSet.has_instructions | Bool |
| BrickSet.has_box | Bool |
| BrickSet.is_factory_sealed | Bool |
| BrickSet.owner_initial_estimate | Optional int 1..999999 (strictly < 1,000,000) |
| Valuation.value | Required int 1..999999 |
| Valuation.currency | Default 'PLN', length 3 upper-case, restricted set {PLN} |
| Valuation.comment | Optional text (sanitize length, e.g., ≤2000 chars) |

### 4.2 Business Rules Mapping
| Rule (PRD / DB Plan) | Enforcement Strategy |
|----------------------|----------------------|
| RB-01 Edit/Delete BrickSet only if no external valuation and owner's valuation has no likes | Pre-update hook / serializer `validate()` fetch valuations; if any valuation with user != owner exists OR owner's valuation has likes_count>0 -> deny. Efficient: annotated query or cached flags. |
| FR-05 Unique BrickSet combination | DB unique constraint; catch IntegrityError -> 409 BRICKSET_DUPLICATE. Pre-check via query to return early. |
| FR-11 One valuation per user-set | DB unique constraint + pre-existence check -> 409 VALUATION_DUPLICATE. |
| FR-12/FR-13 Like only once & not own valuation | DB unique constraint; plus validation comparing valuation.user_id with request.user.id. |
| RB-04 Serviced set definition | DB triggers maintain counts; API read metrics. Optionally compute on-demand if triggers not yet implemented. |
| FR-08 Search partial number | `number__icontains` or `CAST(number AS TEXT) ILIKE '%q%'`; consider trigram index later. |
| FR-09 Sorting valuations by popularity | Query ordering `-likes_count, created_at`. |
| FR-14 Stats (valuations_count, total_likes) per BrickSet | Aggregation via annotation or cached denormalized likes_count per valuation then sum. |
| FR-18 Authentication for protected operations | DRF permission classes: `IsAuthenticated`. |
| FR-20 Clear validation errors | Serializer error formatting; custom exception handler unify structure. |

### 4.3 Derived / Computed Fields
- `valuations_count`: COUNT valuations where `brickset_id = id`.
- `total_likes`: SUM `likes_count` of valuations for the brickset.
- `editable`: boolean derived from RB-01 rule.
- `serviced_sets_ratio`: `serviced_sets / total_sets` (float with rounding). 

### 4.4 Consistency & Concurrency
- Likes increment via DB triggers updating `likes_count`; API trusts DB value after refresh.
- In race conditions for create duplicate BrickSet or valuation, rely on unique constraint; return conflict.
- Use transactions around create operations to ensure atomicity (Django atomic). 

### 4.5 Pagination Strategy
- Default page size 20; max 100.
- Provide `count`, `next`, `previous`, `results` structure.
- Consider cursor pagination for valuations if like count sorting becomes large.

### 4.6 Filtering & Sorting
- Whitelist `ordering` parameters; reject unknown values with 400.
- Multi-filter combination uses AND semantics.
- For search `q`, ensure sanitized integer-like input; fallback to partial string match.

### 4.7 Rate Limiting (Assumptions)
- Anonymous (register/login) endpoints: 30 req/min per IP.
- Authenticated endpoints: 120 req/min per user.
- Like creation (possible abuse) sub-scope throttle: 60 likes/hour.
- Implementation: DRF throttling classes + custom throttle for likes.

### 4.8 Security Considerations
- Input sanitization: strip comments, enforce length limits.
- Prevent HTML/JS injection in comments (escape on output).
- CORS restricted to frontend origin (e.g., `https://frontend.localhost` in dev).
- HTTPS enforced (Secure cookie). 
- Future: add refresh token rotation & CSRF double-submit token if using cookie+header pattern.

### 4.9 Error Standardization Examples
- Validation:
```
HTTP 400
{
  "errors": {
    "value": ["Must be between 1 and 999999"]
  },
  "code": "VALIDATION_ERROR"
}
```
- Conflict:
```
HTTP 409
{
  "detail": "BrickSet with identical attributes already exists",
  "code": "BRICKSET_DUPLICATE"
}
```
- Forbidden (rule):
```
HTTP 403
{
  "detail": "BrickSet locked due to external valuation",
  "code": "BRICKSET_EDIT_FORBIDDEN"
}
```

## 5. Endpoint Implementation Notes (DRF)
| Endpoint | View Type | Serializer | Permissions | Throttles |
|----------|-----------|-----------|-------------|-----------|
| /auth/register | APIView | RegisterSerializer | AllowAny | RegisterThrottle |
| /auth/login | APIView | LoginSerializer | AllowAny | LoginThrottle |
| /auth/logout | APIView | - | IsAuthenticated | UserThrottle |
| /auth/me | RetrieveAPIView | UserSerializer | IsAuthenticated | UserThrottle |
| /bricksets (GET/POST) | ListCreateAPIView | BrickSetListSerializer / BrickSetCreateSerializer | IsAuthenticated | UserThrottle |
| /bricksets/{id} (GET/PATCH/DELETE) | RetrieveUpdateDestroyAPIView | BrickSetDetailSerializer | IsAuthenticated + IsOwnerForEdit | UserThrottle |
| /bricksets/{id}/valuations (POST/GET) | ListCreateAPIView | ValuationSerializer | IsAuthenticated | UserThrottle + ValuationThrottle |
| /valuations/{id} | RetrieveAPIView | ValuationSerializer | IsAuthenticated | UserThrottle |
| /valuations/{id}/likes (POST/DELETE/GET) | APIView | LikeSerializer | IsAuthenticated | LikeThrottle |
| /users/me/bricksets | ListAPIView | BrickSetOwnedSerializer | IsAuthenticated | UserThrottle |
| /users/me/valuations | ListAPIView | ValuationOwnedSerializer | IsAuthenticated | UserThrottle |
| /metrics/system | RetrieveAPIView | MetricsSerializer | IsAuthenticated | UserThrottle |

## 6. Versioning & Backward Compatibility
- Prefix all endpoints with `/api/v1`.
- Introduce `/api/v2` for breaking changes (field renames, enum expansion requiring mapping). 
- Deprecation strategy: Sunset headers `Deprecation` & `Link` with documentation.

## 7. Monitoring & Metrics Exposure
- Application metrics in DB accessible via `/metrics/system`.
- Future extension: add `/metrics/extended` for distribution stats (deferred).
- Operational metrics (health) endpoint: `/health` (simple 200 + version) – not in PRD but recommended.

## 8. Assumptions & Deferred Items
| Assumption | Rationale |
|-----------|-----------|
| Search requires authentication (FR-18) | PRD indicates all operations except register/login require login. |
| No valuation editing/deletion | Out-of-scope (PRD section 4.2). |
| Likes can be removed | Added for usability; if not desired mark DELETE as 405. |
| Metrics visible to all authenticated users | Simplicity for MVP; can restrict later. |
| JWT chosen over session cookie | Easier SPA integration (Vue + API). |
| `account_account` naming | Based on Django custom user; if actual table differs (e.g., `account_user`), adapt. |
| Pagination default size 20 | Standard REST pattern. |
| Rate limits values | Not specified in PRD; safe conservative defaults. |
| Use offset pagination initially | Simpler; upgrade to cursor when scale demands. |

## 9. Future Extensions (Non-MVP)
- Refresh token & rotation endpoint (`/auth/refresh`).
- Admin moderation endpoints.
- Extended search (trigram, fuzzy) with `pg_trgm` index.
- Photo upload endpoints (`/bricksets/{id}/images`).
- Reputation scores or ranking endpoints.
- Internationalization of content & multi-language support for comments.

## 10. Data Model to API Field Mapping
| Model Field | API Field | Notes |
|-------------|-----------|-------|
| id | id | Primary key |
| owner_id (BrickSet) | owner_id | Not expanded in list; may embed owner username in detail. |
| number | number | Int; textual search converts to string. |
| production_status | production_status | Enum uppercase. |
| completeness | completeness | Enum uppercase. |
| has_instructions | has_instructions | Bool |
| has_box | has_box | Bool |
| is_factory_sealed | is_factory_sealed | Bool |
| owner_initial_estimate | owner_initial_estimate | Optional |
| likes_count (Valuation) | likes_count | Denormalized, used for ordering. |
| Metrics fields | total_sets, serviced_sets, active_users | Derived ratios added at API layer. |

## 11. Security & Privacy Recap
- Password hashing using Django's recommended algorithm (PBKDF2 + salt). (FR-17)
- Email & username uniqueness enforced; conflicts -> 409. (FR-01)
- Prevent enumeration by generic messages on login (still differentiate invalid credentials). Could unify errors later for heightened security.
- Logging: Avoid logging passwords or full tokens.
- Input validation prevents extremely large integers or strings, reducing risk of DoS.

## 12. Testing Recommendations (Adjunct)
- Unit tests: serializers validation (value ranges, duplicate prevention).
- Integration tests: endpoint flows (register -> login -> create brickset -> valuation -> like -> metrics). Map to US stories.
- Permission tests: attempt edit/delete after external valuation added -> expect 403.
- Load test (future): search endpoint with filters performance under moderate dataset.

---
This REST API plan comprehensively maps PRD functional requirements (FR-01..FR-20) and business rules (RB-01..RB-04) to resource-oriented endpoints, including validation, error semantics, and extensibility considerations for the BricksValuation MVP.
