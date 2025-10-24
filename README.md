# BricksValuation

## Development scripts

- **Initialise stack**: `bin/dev_init.sh` copies the backend env file, builds the Docker images, and starts the containers.
- **Clean up**: `bin/dev_clear.sh` stops and removes the project's containers, images, volumes, and deletes `env/.backend-env`.

## Linter
To run the backend linter, use the following command:

```bash
./bin/lint_backend.sh
```

To run the frontend linter, use the following command:

```bash
./bin/lint_frontend.sh
```

## Backend Tests

To run the backend tests, execute:

```bash
./bin/test_backend.sh
```

## API Authentication

### Overview

BricksValuation uses JWT (JSON Web Tokens) stored in HttpOnly cookies for stateless authentication. The authentication system consists of:

1. **JWTCookieAuthentication** - Custom DRF authentication class that extracts and validates JWT tokens from cookies
2. **Token Provider Service** - Centralized service for token encoding/decoding with configurable expiration
3. **Global Configuration** - REST_FRAMEWORK configured to use JWT authentication across all endpoints

### Authentication Architecture

- **Token Storage**: JWT stored in `jwt_token` cookie with HttpOnly, Secure, and SameSite=Strict flags
- **Token Lifetime**: 24 hours (configured in `config/jwt_config.py`)
- **Token Algorithm**: HS256 (HMAC with SHA-256)
- **Error Handling**: Generic error messages to prevent user enumeration attacks

### Endpoints

#### 1. Registration: `POST /api/v1/auth/register`

Creates a new user account.

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Success Response (201 Created):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

**Error Responses:**
- `400 Bad Request` - Validation errors (missing fields, invalid format)
- `409 Conflict` - Username already exists

#### 2. Login: `POST /api/v1/auth/login`

Authenticates user and sets JWT cookie.

**Request:**
```json
{
  "username": "john_doe",
  "password": "SecurePassword123!"
}
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

**Response Headers:**
```
Set-Cookie: jwt_token=<JWT_TOKEN>; Path=/; Max-Age=86400; HttpOnly; Secure; SameSite=Strict
```

**Error Responses:**
- `400 Bad Request` - Validation errors
- `401 Unauthorized` - Invalid credentials (generic message: "Invalid username or password")

#### 3. Logout: `POST /api/v1/auth/logout`

Terminates user session by deleting JWT cookie.

**Request:**
- Requires authentication (JWT cookie must be present)

**Success Response (204 No Content):**
- Empty response body
- Cookie deletion header included

**Response Headers:**
```
Set-Cookie: jwt_token=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Strict
```

**Error Responses:**
- `401 Unauthorized` - No valid JWT token provided

### Testing Authentication

#### Unit Tests

Run all backend tests including authentication tests:

```bash
./bin/test_backend.sh
```

Test files:
- `account/tests/test_authentication.py` - JWT authentication class tests (10 tests)
- `account/views/tests/test_login_view.py` - Login endpoint tests (15 tests)
- `account/views/tests/test_logout_view.py` - Logout endpoint tests (9 tests)
- `account/services/tests/test_token_provider.py` - Token service tests (10 tests)

#### Integration Tests (cURL)

Test the complete authentication flow with cURL:

```bash
bash bin/tests/auth_api_tests.sh
```

Tests include:
- User registration
- Login with valid credentials
- Login with wrong password
- Login with missing fields
- JWT cookie attributes validation
- Logout without authentication (401)
- Logout with valid cookie (204)
- Cookie deletion verification
- Full flow: register → login → logout

### Security Features

1. **HttpOnly Cookies**: JWT tokens cannot be accessed by JavaScript (prevents XSS attacks)
2. **SameSite=Strict**: Prevents CSRF attacks by restricting cookie transmission to same-site requests
3. **Generic Error Messages**: "Invalid username or password" for both invalid credentials and non-existent users
4. **Secure Flag**: Cookie transmitted only over HTTPS in production
5. **Token Expiration**: 24-hour token lifetime with no server-side token blacklist (stateless)
6. **Password Hashing**: Django's PBKDF2 algorithm used for password storage

### Service Layer Architecture

Authentication uses a layered architecture:

```
HTTP Request
    ↓
APIView (Serializer validation)
    ↓
Service Layer (Business logic, transactions)
    ↓
Authentication/TokenProvider (JWT operations)
    ↓
User Model (Database)
```

#### Example: LoginService

```python
# Services coordinate business logic
service = LoginService()
user_dto = service.execute(login_command)  # Returns DTO, not model

# Commands are input structures
class LoginCommand:
    username: str
    password: str

# DTOs are output structures (filtered model data)
class UserRefDTO:
    id: int
    username: str
    email: str
```

### Configuration

JWT configuration is centralized in `config/jwt_config.py`:

```python
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "development-secret")
ALGORITHM = "HS256"
EXPIRATION_SECONDS = 24 * 60 * 60  # 24 hours
COOKIE_NAME = "jwt_token"
```

### Future Enhancements

1. **Token Refresh**: Implement refresh tokens for longer sessions
2. **Token Blacklist**: Add Redis-based token blacklist for logout revocation
3. **Rate Limiting**: Already implemented for login endpoint
4. **Permissions System**: Add role-based access control (RBAC)
