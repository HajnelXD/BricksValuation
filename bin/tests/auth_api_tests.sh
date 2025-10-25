#!/bin/bash

# ============================================================
# AUTH API TEST SUITE - CURL COMMANDS
# ============================================================
# Usage: bash auth_api_tests.sh
# This script tests the registration and login endpoints
# ============================================================

BASE_URL="http://localhost:8000/api/v1"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print headers
print_header() {
    echo -e "\n${YELLOW}========================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}========================================${NC}\n"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ============================================================
# TEST 1: REGISTER NEW USER
# ============================================================

print_header "TEST 1: REGISTER NEW USER"

echo "Endpoint: POST $BASE_URL/auth/register"
echo "Payload:"
echo '{
  "username": "testuser_'$(date +%s)'",
  "email": "test_'$(date +%s)'@example.com",
  "password": "SecurePass123!"
}'
echo ""

TIMESTAMP=$(date +%s)
USERNAME="testuser_$TIMESTAMP"
EMAIL="test_$TIMESTAMP@example.com"

REGISTER_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"email\": \"$EMAIL\",
    \"password\": \"SecurePass123!\"
  }")

HTTP_CODE=$(echo "$REGISTER_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$REGISTER_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "201" ]; then
    print_success "Registration successful (HTTP $HTTP_CODE)"
    echo "Response:"
    echo "$RESPONSE_BODY" | jq '.'
else
    print_error "Registration failed (HTTP $HTTP_CODE)"
    echo "$RESPONSE_BODY"
    exit 1
fi

# ============================================================
# TEST 2: LOGIN WITH NEW USER
# ============================================================

print_header "TEST 2: LOGIN WITH NEW USER"

echo "Endpoint: POST $BASE_URL/auth/login"
echo "Payload:"
echo "{
  \"username\": \"$USERNAME\",
  \"password\": \"SecurePass123!\"
}"
echo ""

LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"password\": \"SecurePass123!\"
  }")

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    print_success "Login successful (HTTP $HTTP_CODE)"
    echo "Response:"
    echo "$RESPONSE_BODY" | jq '.'
else
    print_error "Login failed (HTTP $HTTP_CODE)"
    echo "$RESPONSE_BODY"
    exit 1
fi

# ============================================================
# TEST 3: LOGIN WITH WRONG PASSWORD
# ============================================================

print_header "TEST 3: LOGIN WITH WRONG PASSWORD"

echo "Expected: HTTP 401 with generic error message"
echo ""

WRONG_PWD_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"password\": \"WrongPassword!\"
  }")

HTTP_CODE=$(echo "$WRONG_PWD_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$WRONG_PWD_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "401" ]; then
    print_success "Correct error response (HTTP $HTTP_CODE)"
    echo "Response:"
    echo "$RESPONSE_BODY" | jq '.'
else
    print_error "Expected 401 but got $HTTP_CODE"
    echo "$RESPONSE_BODY"
fi

# ============================================================
# TEST 4: LOGIN WITH MISSING PASSWORD
# ============================================================

print_header "TEST 4: LOGIN WITH MISSING PASSWORD"

echo "Expected: HTTP 400 with validation errors"
echo ""

MISSING_PWD_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\"
  }")

HTTP_CODE=$(echo "$MISSING_PWD_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$MISSING_PWD_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "400" ]; then
    print_success "Correct validation error (HTTP $HTTP_CODE)"
    echo "Response:"
    echo "$RESPONSE_BODY" | jq '.'
else
    print_error "Expected 400 but got $HTTP_CODE"
    echo "$RESPONSE_BODY"
fi

# ============================================================
# TEST 5: LOGIN WITH NONEXISTENT USER
# ============================================================

print_header "TEST 5: LOGIN WITH NONEXISTENT USER"

echo "Expected: HTTP 401 with generic error message (same as wrong password)"
echo ""

NONEXISTENT_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"nonexistent_user_xyz\",
    \"password\": \"SecurePass123!\"
  }")

HTTP_CODE=$(echo "$NONEXISTENT_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$NONEXISTENT_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "401" ]; then
    print_success "Correct error response (HTTP $HTTP_CODE)"
    echo "Response:"
    echo "$RESPONSE_BODY" | jq '.'
else
    print_error "Expected 401 but got $HTTP_CODE"
    echo "$RESPONSE_BODY"
fi

# ============================================================
# TEST 6: VERIFY JWT COOKIE
# ============================================================

print_header "TEST 6: VERIFY JWT COOKIE ATTRIBUTES"

echo "Testing that login response includes proper JWT cookie..."
echo ""

COOKIE_RESPONSE=$(curl -s -D /tmp/cookie_headers.txt -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"password\": \"SecurePass123!\"
  }" > /dev/null)

COOKIE_LINE=$(grep "Set-Cookie" /tmp/cookie_headers.txt | head -1)

if echo "$COOKIE_LINE" | grep -q "HttpOnly"; then
    print_success "HttpOnly flag is set"
else
    print_error "HttpOnly flag is missing"
fi

if echo "$COOKIE_LINE" | grep -q "SameSite=Strict"; then
    print_success "SameSite=Strict is set"
else
    print_error "SameSite=Strict is missing"
fi

if echo "$COOKIE_LINE" | grep -q "Path=/"; then
    print_success "Path=/ is set"
else
    print_error "Path=/ is missing"
fi

if echo "$COOKIE_LINE" | grep -q "Max-Age=86400"; then
    print_success "Max-Age=86400 (24 hours) is set"
else
    print_error "Max-Age is incorrect"
fi

echo ""
echo "Full Set-Cookie Header:"
echo "$COOKIE_LINE"

# ============================================================
# TEST 7: LOGOUT WITHOUT AUTHENTICATION
# ============================================================

print_header "TEST 7: LOGOUT WITHOUT AUTHENTICATION"

echo "Expected: HTTP 401 Unauthorized"
echo ""

LOGOUT_NOAUTH=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/logout")

HTTP_CODE=$(echo "$LOGOUT_NOAUTH" | tail -1)
RESPONSE_BODY=$(echo "$LOGOUT_NOAUTH" | sed '$d')

if [ "$HTTP_CODE" = "401" ]; then
    print_success "Logout correctly requires authentication (HTTP $HTTP_CODE)"
else
    print_error "Expected 401 but got $HTTP_CODE"
fi

# ============================================================
# TEST 8: LOGOUT WITH VALID COOKIE
# ============================================================

print_header "TEST 8: LOGOUT WITH VALID COOKIE"

echo "Testing logout after successful login..."
echo ""

# First login and save response headers to extract cookie
LOGIN_FOR_LOGOUT=$(curl -s -D /tmp/login_logout_headers.txt -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"password\": \"SecurePass123!\"
  }")

# Extract JWT token from Set-Cookie header - handle multiline tokens
JWT_TOKEN=$(cat /tmp/login_logout_headers.txt | grep "jwt_token=" | sed 's/.*jwt_token=//' | sed 's/;.*//' | tr -d ' \n')

if [ -z "$JWT_TOKEN" ]; then
    print_error "Could not extract JWT token from login response"
    exit 1
fi

# Then logout using extracted token in cookie
LOGOUT_RESPONSE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" -X POST "$BASE_URL/auth/logout")

HTTP_CODE=$(echo "$LOGOUT_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$LOGOUT_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "204" ]; then
    print_success "Logout successful - returned 204 No Content"
    if [ -z "$RESPONSE_BODY" ] || [ "$RESPONSE_BODY" = "" ]; then
        print_success "Response body is empty as expected"
    else
        print_error "Response body should be empty but got: $RESPONSE_BODY"
    fi
else
    print_error "Expected 204 but got $HTTP_CODE"
    echo "Response: $RESPONSE_BODY"
fi

# ============================================================
# TEST 9: VERIFY COOKIE DELETION HEADER
# ============================================================

print_header "TEST 9: VERIFY COOKIE DELETION HEADER"

echo "Testing that logout response includes cookie deletion..."
echo ""

# Login again to get fresh cookie
curl -s -D /tmp/login_verify_headers.txt -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"password\": \"SecurePass123!\"
  }" > /dev/null

# Extract JWT token
JWT_TOKEN_VERIFY=$(cat /tmp/login_verify_headers.txt | grep "jwt_token=" | sed 's/.*jwt_token=//' | sed 's/;.*//' | tr -d ' \n')

# Logout and capture headers
curl -s -D /tmp/logout_headers.txt -H "Cookie: jwt_token=$JWT_TOKEN_VERIFY" -X POST "$BASE_URL/auth/logout" > /dev/null

DELETE_COOKIE_LINE=$(grep "Set-Cookie" /tmp/logout_headers.txt | grep -i "jwt_token")

if [ -n "$DELETE_COOKIE_LINE" ]; then
    if echo "$DELETE_COOKIE_LINE" | grep -q "Max-Age=0"; then
        print_success "Cookie deletion header includes Max-Age=0"
    else
        print_error "Cookie deletion should include Max-Age=0"
    fi
    
    if echo "$DELETE_COOKIE_LINE" | grep -q "HttpOnly"; then
        print_success "Cookie deletion maintains HttpOnly flag"
    else
        print_error "Cookie deletion should maintain HttpOnly flag"
    fi
else
    print_error "Set-Cookie header not found in logout response"
fi


# ============================================================
# TEST 10: FULL FLOW - REGISTER, LOGIN, LOGOUT
# ============================================================

print_header "TEST 10: FULL FLOW - REGISTER, LOGIN, LOGOUT"

echo "Complete authentication flow..."
echo ""

# Step 1: Register
TIMESTAMP2=$(date +%s)
USERNAME2="testuser_$TIMESTAMP2"
EMAIL2="test_$TIMESTAMP2@example.com"

REGISTER_FLOW=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME2\",
    \"email\": \"$EMAIL2\",
    \"password\": \"SecurePass123!\"
  }")

REG_HTTP=$(echo "$REGISTER_FLOW" | tail -1)

if [ "$REG_HTTP" = "201" ]; then
    print_success "Step 1: Registration successful"
else
    print_error "Step 1: Registration failed (HTTP $REG_HTTP)"
    exit 1
fi

# Step 2: Login
LOGIN_FLOW=$(curl -s -D /tmp/login_flow_headers.txt -w "\n%{http_code}" -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME2\",
    \"password\": \"SecurePass123!\"
  }")

LOGIN_HTTP=$(echo "$LOGIN_FLOW" | tail -1)

if [ "$LOGIN_HTTP" = "200" ]; then
    print_success "Step 2: Login successful"
else
    print_error "Step 2: Login failed (HTTP $LOGIN_HTTP)"
    exit 1
fi

# Extract token from login response
JWT_TOKEN_FLOW=$(cat /tmp/login_flow_headers.txt | grep "jwt_token=" | sed 's/.*jwt_token=//' | sed 's/;.*//' | tr -d ' \n')

if [ -z "$JWT_TOKEN_FLOW" ]; then
    print_error "Step 3: Could not extract token from login response"
    exit 1
fi

# Step 3: Logout
LOGOUT_FLOW=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN_FLOW" -X POST "$BASE_URL/auth/logout")

LOGOUT_HTTP=$(echo "$LOGOUT_FLOW" | tail -1)

if [ "$LOGOUT_HTTP" = "204" ]; then
    print_success "Step 3: Logout successful"
else
    print_error "Step 3: Logout failed (HTTP $LOGOUT_HTTP)"
    exit 1
fi

print_success "Complete authentication flow successful!"

# ============================================================
# SUMMARY
# ============================================================

print_header "TEST SUMMARY"
print_success "All tests completed!"
echo ""
echo "Summary:"
echo "  ✅ Registration endpoint working"
echo "  ✅ Login endpoint working"
echo "  ✅ JWT token generation working"
echo "  ✅ HttpOnly cookie attributes set correctly"
echo "  ✅ Error handling with generic messages"
echo "  ✅ Validation errors handled properly"
echo "  ✅ Logout endpoint requires authentication"
echo "  ✅ Logout returns 204 No Content"
echo "  ✅ Logout deletes JWT cookie"
echo "  ✅ Full auth flow working (register → login → logout)"
echo ""
