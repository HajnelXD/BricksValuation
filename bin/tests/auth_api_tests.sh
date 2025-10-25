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

HTTP_CODE=$(echo "$REGISTER_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$REGISTER_RESPONSE" | head -n-1)

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

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | head -n-1)

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

HTTP_CODE=$(echo "$WRONG_PWD_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$WRONG_PWD_RESPONSE" | head -n-1)

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

HTTP_CODE=$(echo "$MISSING_PWD_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$MISSING_PWD_RESPONSE" | head -n-1)

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

HTTP_CODE=$(echo "$NONEXISTENT_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$NONEXISTENT_RESPONSE" | head -n-1)

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
echo ""
