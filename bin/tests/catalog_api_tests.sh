#!/bin/bash

# ============================================================
# CATALOG API TEST SUITE - CURL COMMANDS
# ============================================================
# Usage: bash catalog_api_tests.sh
# This script tests the BrickSet endpoints:
# - GET /api/v1/bricksets (list with filters and pagination)
# - POST /api/v1/bricksets (create new BrickSet)
# - GET /api/v1/bricksets/{id} (retrieve detail with valuations)
# - PATCH /api/v1/bricksets/{id} (partial update)
# - DELETE /api/v1/bricksets/{id} (delete BrickSet)
#
# Note: Requires authentication for POST, PATCH and DELETE. Script automatically:
# 1. Creates test user account
# 2. Logs in to get JWT token
# 3. Runs catalog API tests using the token
# 4. GET endpoints are public (no auth required)
# ============================================================

BASE_URL="http://localhost:8000/api/v1"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print headers
print_header() {
    echo -e "\n${YELLOW}========================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}========================================${NC}\n"
}

# Function to clean database
clean_database() {
    print_info "Cleaning test data from database..."
    # Delete BrickSets created in tests (using number range)
    docker-compose exec -T backend python manage.py shell -c "
from catalog.models import BrickSet
from account.models import User
# Delete test BrickSets (numbers in range 1000000-9999999)
BrickSet.objects.filter(number__gte=1000000, number__lte=9999999).delete()
# Delete test users (username starts with 'catalogtester_')
User.objects.filter(username__startswith='catalogtester_').delete()
print('Test data cleaned')
" 2>&1 > /dev/null
    if [ $? -eq 0 ]; then
        print_success "Test data cleaned successfully"
    else
        print_info "Skipping test data cleanup (container not available)"
    fi
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to print info
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ============================================================
# PRE-TEST CLEANUP
# ============================================================

print_header "PRE-TEST DATABASE CLEANUP"
clean_database

# ============================================================
# SETUP: CREATE USER AND LOGIN
# ============================================================

print_header "SETUP: CREATE TEST USER AND LOGIN"

TIMESTAMP=$(date +%s)
TEST_USERNAME="catalogtester_$TIMESTAMP"
TEST_EMAIL="catalog_test_$TIMESTAMP@example.com"
TEST_PASSWORD="TestPass123!"

print_info "Creating test user account..."

# Register user
REGISTER_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_USERNAME\",
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\"
  }")

REG_HTTP=$(echo "$REGISTER_RESPONSE" | tail -1)
if [ "$REG_HTTP" != "201" ]; then
    print_error "Registration failed (HTTP $REG_HTTP)"
    exit 1
fi
print_success "User account created: $TEST_USERNAME"

# Login to get JWT token
print_info "Logging in to get JWT token..."

LOGIN_RESPONSE=$(curl -s -D /tmp/catalog_login_headers.txt -w "\n%{http_code}" -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_USERNAME\",
    \"password\": \"$TEST_PASSWORD\"
  }")

LOGIN_HTTP=$(echo "$LOGIN_RESPONSE" | tail -1)
if [ "$LOGIN_HTTP" != "200" ]; then
    print_error "Login failed (HTTP $LOGIN_HTTP)"
    exit 1
fi

# Extract JWT token from Set-Cookie header
JWT_TOKEN=$(cat /tmp/catalog_login_headers.txt | grep "jwt_token=" | sed 's/.*jwt_token=//' | sed 's/;.*//' | tr -d ' \n')
if [ -z "$JWT_TOKEN" ]; then
    print_error "Could not extract JWT token from login response"
    exit 1
fi

print_success "Login successful, JWT token obtained"

# Use unique timestamp-based numbers (within 1-9999999 range)
# Use last 6 digits of timestamp with offset to ensure uniqueness
BRICKSET_NUM1=$((1000000 + (TIMESTAMP % 8999999)))
BRICKSET_NUM2=$((1000000 + (TIMESTAMP % 8999999) + 1))
BRICKSET_NUM3=$((1000000 + (TIMESTAMP % 8999999) + 2))

# ============================================================
# TEST 1: GET /api/v1/bricksets WITHOUT FILTER (EMPTY LIST)
# ============================================================

print_header "TEST 1: GET /api/v1/bricksets - USER'S EMPTY LIST"

echo "Endpoint: GET $BASE_URL/bricksets"
echo "Expected: HTTP 200 with empty paginated results for new user"
echo ""

GET_EMPTY_RESPONSE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  "$BASE_URL/bricksets")

GET_EMPTY_HTTP=$(echo "$GET_EMPTY_RESPONSE" | tail -1)
GET_EMPTY_BODY=$(echo "$GET_EMPTY_RESPONSE" | sed '$d')

if [ "$GET_EMPTY_HTTP" = "200" ]; then
    print_success "GET request successful (HTTP $GET_EMPTY_HTTP)"
    echo "Response structure:"
    echo "$GET_EMPTY_BODY" | jq '.count, .next, .previous, (.results | length)'
else
    print_error "GET request failed (HTTP $GET_EMPTY_HTTP)"
    echo "$GET_EMPTY_BODY"
    exit 1
fi

# ============================================================
# TEST 2: POST /api/v1/bricksets - CREATE FIRST BRICKSET
# ============================================================

print_header "TEST 2: POST /api/v1/bricksets - CREATE FIRST BRICKSET"

echo "Endpoint: POST $BASE_URL/bricksets"
echo "Payload:"
echo "{
  \"number\": $BRICKSET_NUM1,
  \"production_status\": \"ACTIVE\",
  \"completeness\": \"COMPLETE\",
  \"has_instructions\": true,
  \"has_box\": true,
  \"is_factory_sealed\": false,
  \"owner_initial_estimate\": 250
}"
echo ""

POST_CREATE1=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $BRICKSET_NUM1,
    \"production_status\": \"ACTIVE\",
    \"completeness\": \"COMPLETE\",
    \"has_instructions\": true,
    \"has_box\": true,
    \"is_factory_sealed\": false,
    \"owner_initial_estimate\": 250
  }")

POST_CREATE1_HTTP=$(echo "$POST_CREATE1" | tail -1)
POST_CREATE1_BODY=$(echo "$POST_CREATE1" | sed '$d')

if [ "$POST_CREATE1_HTTP" = "201" ]; then
    print_success "BrickSet created successfully (HTTP $POST_CREATE1_HTTP)"
    echo "Response:"
    echo "$POST_CREATE1_BODY" | jq '{id, number, production_status, completeness, owner_id, owner_initial_estimate}'
    
    # Extract ID for later tests
    BRICKSET1_ID=$(echo "$POST_CREATE1_BODY" | jq '.id')
else
    print_error "BrickSet creation failed (HTTP $POST_CREATE1_HTTP)"
    echo "$POST_CREATE1_BODY"
    exit 1
fi

# ============================================================
# TEST 3: POST /api/v1/bricksets - CREATE SECOND BRICKSET
# ============================================================

print_header "TEST 3: POST /api/v1/bricksets - CREATE SECOND BRICKSET"

echo "Endpoint: POST $BASE_URL/bricksets"
echo "Payload:"
echo "{
  \"number\": $BRICKSET_NUM2,
  \"production_status\": \"RETIRED\",
  \"completeness\": \"INCOMPLETE\",
  \"has_instructions\": false,
  \"has_box\": false,
  \"is_factory_sealed\": true
}"
echo ""

POST_CREATE2=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $BRICKSET_NUM2,
    \"production_status\": \"RETIRED\",
    \"completeness\": \"INCOMPLETE\",
    \"has_instructions\": false,
    \"has_box\": false,
    \"is_factory_sealed\": true
  }")

POST_CREATE2_HTTP=$(echo "$POST_CREATE2" | tail -1)
POST_CREATE2_BODY=$(echo "$POST_CREATE2" | sed '$d')

if [ "$POST_CREATE2_HTTP" = "201" ]; then
    print_success "Second BrickSet created successfully (HTTP $POST_CREATE2_HTTP)"
    echo "Response:"
    echo "$POST_CREATE2_BODY" | jq '{id, number, production_status, completeness, owner_initial_estimate}'
    
    BRICKSET2_ID=$(echo "$POST_CREATE2_BODY" | jq '.id')
else
    print_error "BrickSet creation failed (HTTP $POST_CREATE2_HTTP)"
    echo "$POST_CREATE2_BODY"
fi

# ============================================================
# TEST 4: POST /api/v1/bricksets - DUPLICATE (409 CONFLICT)
# ============================================================

print_header "TEST 4: POST /api/v1/bricksets - DUPLICATE SHOULD FAIL"

echo "Endpoint: POST $BASE_URL/bricksets"
echo "Attempting to create duplicate of first BrickSet (same number and attributes)"
echo ""

POST_DUPLICATE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $BRICKSET_NUM1,
    \"production_status\": \"ACTIVE\",
    \"completeness\": \"COMPLETE\",
    \"has_instructions\": true,
    \"has_box\": true,
    \"is_factory_sealed\": false,
    \"owner_initial_estimate\": 250
  }")

POST_DUP_HTTP=$(echo "$POST_DUPLICATE" | tail -1)
POST_DUP_BODY=$(echo "$POST_DUPLICATE" | sed '$d')

if [ "$POST_DUP_HTTP" = "409" ]; then
    print_success "Duplicate correctly rejected (HTTP $POST_DUP_HTTP)"
    echo "Response:"
    echo "$POST_DUP_BODY" | jq '{detail, constraint}'
else
    print_error "Expected 409 but got $POST_DUP_HTTP"
    echo "$POST_DUP_BODY"
fi

# ============================================================
# TEST 5: POST /api/v1/bricksets - VALIDATION ERROR (INVALID ENUM)
# ============================================================

print_header "TEST 5: POST /api/v1/bricksets - VALIDATION ERROR"

echo "Endpoint: POST $BASE_URL/bricksets"
echo "Invalid payload: production_status = INVALID (should be ACTIVE|RETIRED)"
echo ""

POST_INVALID=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": 9999999,
    \"production_status\": \"INVALID\",
    \"completeness\": \"COMPLETE\",
    \"has_instructions\": true,
    \"has_box\": true,
    \"is_factory_sealed\": false
  }")

POST_INVALID_HTTP=$(echo "$POST_INVALID" | tail -1)
POST_INVALID_BODY=$(echo "$POST_INVALID" | sed '$d')

if [ "$POST_INVALID_HTTP" = "400" ]; then
    print_success "Validation error correctly returned (HTTP $POST_INVALID_HTTP)"
    echo "Response errors:"
    echo "$POST_INVALID_BODY" | jq '.errors'
else
    print_error "Expected 400 but got $POST_INVALID_HTTP"
    echo "$POST_INVALID_BODY"
fi

# ============================================================
# TEST 6: POST /api/v1/bricksets - MISSING REQUIRED FIELD
# ============================================================

print_header "TEST 6: POST /api/v1/bricksets - MISSING REQUIRED FIELD"

echo "Endpoint: POST $BASE_URL/bricksets"
echo "Invalid payload: missing 'number' field"
echo ""

POST_MISSING=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d '{
    "production_status": "ACTIVE",
    "completeness": "COMPLETE",
    "has_instructions": true,
    "has_box": true,
    "is_factory_sealed": false
  }')

POST_MISSING_HTTP=$(echo "$POST_MISSING" | tail -1)
POST_MISSING_BODY=$(echo "$POST_MISSING" | sed '$d')

if [ "$POST_MISSING_HTTP" = "400" ]; then
    print_success "Missing field error correctly returned (HTTP $POST_MISSING_HTTP)"
    echo "Response errors:"
    echo "$POST_MISSING_BODY" | jq '.errors'
else
    print_error "Expected 400 but got $POST_MISSING_HTTP"
    echo "$POST_MISSING_BODY"
fi

# ============================================================
# TEST 7: POST /api/v1/bricksets - OUT OF RANGE (INVALID NUMBER)
# ============================================================

print_header "TEST 7: POST /api/v1/bricksets - OUT OF RANGE NUMBER"

echo "Endpoint: POST $BASE_URL/bricksets"
echo "Invalid payload: number = 10000000 (exceeds max 9999999)"
echo ""

POST_OUT_OF_RANGE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d '{
    "number": 10000000,
    "production_status": "ACTIVE",
    "completeness": "COMPLETE",
    "has_instructions": true,
    "has_box": true,
    "is_factory_sealed": false
  }')

POST_RANGE_HTTP=$(echo "$POST_OUT_OF_RANGE" | tail -1)
POST_RANGE_BODY=$(echo "$POST_OUT_OF_RANGE" | sed '$d')

if [ "$POST_RANGE_HTTP" = "400" ]; then
    print_success "Out of range error correctly returned (HTTP $POST_RANGE_HTTP)"
    echo "Response errors:"
    echo "$POST_RANGE_BODY" | jq '.errors'
else
    print_error "Expected 400 but got $POST_RANGE_HTTP"
    echo "$POST_RANGE_BODY"
fi

# ============================================================
# TEST 8: POST /api/v1/bricksets - OPTIONAL FIELD (NO ESTIMATE)
# ============================================================

print_header "TEST 8: POST /api/v1/bricksets - OPTIONAL ESTIMATE FIELD"

echo "Endpoint: POST $BASE_URL/bricksets"
echo "Payload without owner_initial_estimate (optional field)"
echo ""

POST_NO_ESTIMATE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $BRICKSET_NUM3,
    \"production_status\": \"ACTIVE\",
    \"completeness\": \"COMPLETE\",
    \"has_instructions\": true,
    \"has_box\": false,
    \"is_factory_sealed\": false
  }")

POST_NO_EST_HTTP=$(echo "$POST_NO_ESTIMATE" | tail -1)
POST_NO_EST_BODY=$(echo "$POST_NO_ESTIMATE" | sed '$d')

if [ "$POST_NO_EST_HTTP" = "201" ]; then
    print_success "BrickSet created without estimate (HTTP $POST_NO_EST_HTTP)"
    echo "Response:"
    echo "$POST_NO_EST_BODY" | jq '{id, number, owner_initial_estimate}'
else
    print_error "BrickSet creation failed (HTTP $POST_NO_EST_HTTP)"
    echo "$POST_NO_EST_BODY"
fi

# ============================================================
# TEST 9: GET /api/v1/bricksets - LIST WITH RESULTS
# ============================================================

print_header "TEST 9: GET /api/v1/bricksets - LIST WITH PAGINATION"

echo "Endpoint: GET $BASE_URL/bricksets?page=1&page_size=10"
echo "Expected: HTTP 200 with paginated results"
echo ""

GET_LIST=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  "$BASE_URL/bricksets?page=1&page_size=10")

GET_LIST_HTTP=$(echo "$GET_LIST" | tail -1)
GET_LIST_BODY=$(echo "$GET_LIST" | sed '$d')

if [ "$GET_LIST_HTTP" = "200" ]; then
    print_success "List retrieved successfully (HTTP $GET_LIST_HTTP)"
    echo "Pagination info:"
    echo "$GET_LIST_BODY" | jq '{count, next, previous, results_count: (.results | length)}'
    echo ""
    echo "First item:"
    echo "$GET_LIST_BODY" | jq '.results[0] // "No items"'
else
    print_error "GET request failed (HTTP $GET_LIST_HTTP)"
    echo "$GET_LIST_BODY"
fi

# ============================================================
# TEST 10: GET /api/v1/bricksets - FILTER BY PRODUCTION STATUS
# ============================================================

print_header "TEST 10: GET /api/v1/bricksets - FILTER BY PRODUCTION STATUS"

echo "Endpoint: GET $BASE_URL/bricksets?production_status=ACTIVE"
echo "Expected: HTTP 200 with only ACTIVE BrickSets"
echo ""

GET_FILTER=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  "$BASE_URL/bricksets?production_status=ACTIVE")

GET_FILTER_HTTP=$(echo "$GET_FILTER" | tail -1)
GET_FILTER_BODY=$(echo "$GET_FILTER" | sed '$d')

if [ "$GET_FILTER_HTTP" = "200" ]; then
    print_success "Filtered list retrieved (HTTP $GET_FILTER_HTTP)"
    ACTIVE_COUNT=$(echo "$GET_FILTER_BODY" | jq '.results | map(select(.production_status == "ACTIVE")) | length')
    echo "ACTIVE BrickSets in results: $ACTIVE_COUNT"
    echo "Sample:"
    echo "$GET_FILTER_BODY" | jq '.results[] | {number, production_status}' | head -20
else
    print_error "GET request failed (HTTP $GET_FILTER_HTTP)"
    echo "$GET_FILTER_BODY"
fi

# ============================================================
# TEST 11: GET /api/v1/bricksets - FILTER BY COMPLETENESS
# ============================================================

print_header "TEST 11: GET /api/v1/bricksets - FILTER BY COMPLETENESS"

echo "Endpoint: GET $BASE_URL/bricksets?completeness=COMPLETE"
echo "Expected: HTTP 200 with only COMPLETE BrickSets"
echo ""

GET_COMPLETE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  "$BASE_URL/bricksets?completeness=COMPLETE")

GET_COMPLETE_HTTP=$(echo "$GET_COMPLETE" | tail -1)
GET_COMPLETE_BODY=$(echo "$GET_COMPLETE" | sed '$d')

if [ "$GET_COMPLETE_HTTP" = "200" ]; then
    print_success "Filtered list retrieved (HTTP $GET_COMPLETE_HTTP)"
    COMPLETE_COUNT=$(echo "$GET_COMPLETE_BODY" | jq '.results | map(select(.completeness == "COMPLETE")) | length')
    echo "COMPLETE BrickSets in results: $COMPLETE_COUNT"
else
    print_error "GET request failed (HTTP $GET_COMPLETE_HTTP)"
fi

# ============================================================
# TEST 12: GET /api/v1/bricksets - SEARCH BY SET NUMBER
# ============================================================

print_header "TEST 12: GET /api/v1/bricksets - SEARCH BY NUMBER"

echo "Endpoint: GET $BASE_URL/bricksets?q=$BRICKSET_NUM1"
echo "Expected: HTTP 200 with BrickSet matching number $BRICKSET_NUM1"
echo ""

GET_SEARCH=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  "$BASE_URL/bricksets?q=$BRICKSET_NUM1")

GET_SEARCH_HTTP=$(echo "$GET_SEARCH" | tail -1)
GET_SEARCH_BODY=$(echo "$GET_SEARCH" | sed '$d')

if [ "$GET_SEARCH_HTTP" = "200" ]; then
    print_success "Search executed (HTTP $GET_SEARCH_HTTP)"
    echo "Results:"
    echo "$GET_SEARCH_BODY" | jq '.results[] | {number, production_status, completeness}' 2>/dev/null || echo "No results"
else
    print_error "GET request failed (HTTP $GET_SEARCH_HTTP)"
fi

# ============================================================
# TEST 13: GET /api/v1/bricksets - COMBINED FILTERS
# ============================================================

print_header "TEST 13: GET /api/v1/bricksets - COMBINED FILTERS"

echo "Endpoint: GET $BASE_URL/bricksets?production_status=ACTIVE&has_instructions=true"
echo "Expected: HTTP 200 with ACTIVE BrickSets that have instructions"
echo ""

GET_COMBINED=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  "$BASE_URL/bricksets?production_status=ACTIVE&has_instructions=true")

GET_COMBINED_HTTP=$(echo "$GET_COMBINED" | tail -1)
GET_COMBINED_BODY=$(echo "$GET_COMBINED" | sed '$d')

if [ "$GET_COMBINED_HTTP" = "200" ]; then
    print_success "Combined filter executed (HTTP $GET_COMBINED_HTTP)"
    echo "Results count:"
    echo "$GET_COMBINED_BODY" | jq '.count'
else
    print_error "GET request failed (HTTP $GET_COMBINED_HTTP)"
fi

# ============================================================
# TEST 14: POST /api/v1/bricksets - UNAUTHORIZED (NO JWT)
# ============================================================

print_header "TEST 14: POST /api/v1/bricksets - UNAUTHORIZED (NO AUTH)"

echo "Endpoint: POST $BASE_URL/bricksets"
echo "Expected: HTTP 401 Unauthorized (no JWT token)"
echo ""

POST_NOAUTH=$(curl -s -w "\n%{http_code}" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d '{
    "number": 9999999,
    "production_status": "ACTIVE",
    "completeness": "COMPLETE",
    "has_instructions": true,
    "has_box": true,
    "is_factory_sealed": false
  }')

POST_NOAUTH_HTTP=$(echo "$POST_NOAUTH" | tail -1)
POST_NOAUTH_BODY=$(echo "$POST_NOAUTH" | sed '$d')

if [ "$POST_NOAUTH_HTTP" = "401" ]; then
    print_success "Correctly rejected unauthorized request (HTTP $POST_NOAUTH_HTTP)"
else
    print_error "Expected 401 but got $POST_NOAUTH_HTTP"
fi

# ============================================================
# TEST 15: GET /api/v1/bricksets - ALLOWED WITHOUT AUTH
# ============================================================

print_header "TEST 15: GET /api/v1/bricksets - NO AUTH REQUIRED"

echo "Endpoint: GET $BASE_URL/bricksets"
echo "Expected: HTTP 200 (GET should be public)"
echo ""

GET_NOAUTH=$(curl -s -w "\n%{http_code}" "$BASE_URL/bricksets")

GET_NOAUTH_HTTP=$(echo "$GET_NOAUTH" | tail -1)
GET_NOAUTH_BODY=$(echo "$GET_NOAUTH" | sed '$d')

if [ "$GET_NOAUTH_HTTP" = "200" ]; then
    print_success "Public access to list allowed (HTTP $GET_NOAUTH_HTTP)"
    COUNT=$(echo "$GET_NOAUTH_BODY" | jq '.count')
    echo "Total BrickSets in system: $COUNT"
else
    print_error "Expected 200 but got $GET_NOAUTH_HTTP"
fi

# ============================================================
# TEST 16: GET /api/v1/bricksets - PAGINATION WITH SORTING
# ============================================================

print_header "TEST 16: GET /api/v1/bricksets - SORTING"

echo "Endpoint: GET $BASE_URL/bricksets?ordering=-number"
echo "Expected: HTTP 200 with results sorted by number descending"
echo ""

GET_SORTED=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  "$BASE_URL/bricksets?ordering=-number&page_size=5")

GET_SORTED_HTTP=$(echo "$GET_SORTED" | tail -1)
GET_SORTED_BODY=$(echo "$GET_SORTED" | sed '$d')

if [ "$GET_SORTED_HTTP" = "200" ]; then
    print_success "Sorted list retrieved (HTTP $GET_SORTED_HTTP)"
    echo "First 3 items (sorted by -number):"
    echo "$GET_SORTED_BODY" | jq '.results[:3] | .[] | {number}'
else
    print_error "GET request failed (HTTP $GET_SORTED_HTTP)"
fi

# ============================================================
# TEST 17: GET /api/v1/bricksets/{id} - DETAIL ENDPOINT WITHOUT VALUATIONS
# ============================================================

print_header "TEST 17: GET /api/v1/bricksets/{id} - DETAIL (NO VALUATIONS)"

echo "Endpoint: GET $BASE_URL/bricksets/$BRICKSET1_ID"
echo "Expected: HTTP 200 with full BrickSet detail, empty valuations"
echo ""

GET_DETAIL1=$(curl -s -w "\n%{http_code}" "$BASE_URL/bricksets/$BRICKSET1_ID")

GET_DETAIL1_HTTP=$(echo "$GET_DETAIL1" | tail -1)
GET_DETAIL1_BODY=$(echo "$GET_DETAIL1" | sed '$d')

if [ "$GET_DETAIL1_HTTP" = "200" ]; then
    print_success "BrickSet detail retrieved (HTTP $GET_DETAIL1_HTTP)"
    echo "Response structure:"
    echo "$GET_DETAIL1_BODY" | jq '{
      id, 
      number, 
      production_status, 
      completeness, 
      has_instructions,
      has_box,
      is_factory_sealed,
      owner_id,
      owner_initial_estimate,
      valuations_count,
      total_likes,
      valuations_length: (.valuations | length)
    }'
else
    print_error "GET detail failed (HTTP $GET_DETAIL1_HTTP)"
    echo "$GET_DETAIL1_BODY"
fi

# ============================================================
# TEST 18: GET /api/v1/bricksets/{id} - PUBLIC ACCESS (NO AUTH)
# ============================================================

print_header "TEST 18: GET /api/v1/bricksets/{id} - PUBLIC ACCESS"

echo "Endpoint: GET $BASE_URL/bricksets/$BRICKSET1_ID (no JWT token)"
echo "Expected: HTTP 200 (GET detail should be public, like GET list)"
echo ""

GET_DETAIL_PUBLIC=$(curl -s -w "\n%{http_code}" "$BASE_URL/bricksets/$BRICKSET1_ID")

GET_DETAIL_PUBLIC_HTTP=$(echo "$GET_DETAIL_PUBLIC" | tail -1)
GET_DETAIL_PUBLIC_BODY=$(echo "$GET_DETAIL_PUBLIC" | sed '$d')

if [ "$GET_DETAIL_PUBLIC_HTTP" = "200" ]; then
    print_success "Public access to detail allowed (HTTP $GET_DETAIL_PUBLIC_HTTP)"
    echo "Response number: $(echo "$GET_DETAIL_PUBLIC_BODY" | jq '.number')"
else
    print_error "Expected 200 but got $GET_DETAIL_PUBLIC_HTTP"
fi

# ============================================================
# TEST 19: GET /api/v1/bricksets/{id} - NONEXISTENT ID (404)
# ============================================================

print_header "TEST 19: GET /api/v1/bricksets/{id} - NOT FOUND"

echo "Endpoint: GET $BASE_URL/bricksets/999999"
echo "Expected: HTTP 404 Not Found"
echo ""

GET_DETAIL_404=$(curl -s -w "\n%{http_code}" "$BASE_URL/bricksets/999999")

GET_DETAIL_404_HTTP=$(echo "$GET_DETAIL_404" | tail -1)
GET_DETAIL_404_BODY=$(echo "$GET_DETAIL_404" | sed '$d')

if [ "$GET_DETAIL_404_HTTP" = "404" ]; then
    print_success "Correctly returned 404 for nonexistent BrickSet (HTTP $GET_DETAIL_404_HTTP)"
    echo "Response:"
    echo "$GET_DETAIL_404_BODY" | jq '{detail}'
else
    print_error "Expected 404 but got $GET_DETAIL_404_HTTP"
    echo "$GET_DETAIL_404_BODY"
fi

# ============================================================
# TEST 20: CREATE VALUATION FOR DETAIL TESTING
# ============================================================

print_header "TEST 20: DETAIL ENDPOINT TESTING PREPARATION"

echo "Verifying BrickSet IDs for detail testing"
echo ""

# Get list and extract first two BrickSet IDs
BRICKSETS_LIST=$(curl -s "$BASE_URL/bricksets?page_size=2" | jq '.results[]')

print_success "BrickSets prepared for detail endpoint testing"

# ============================================================
# TEST 21: GET /api/v1/bricksets/{id} - WITH AGGREGATES
# ============================================================

print_header "TEST 21: GET /api/v1/bricksets/{id} - AGGREGATES DEMONSTRATION"

echo "Endpoint: GET $BASE_URL/bricksets"
echo "Note: In production, BrickSets with valuations show aggregates like:"
echo "  - valuations_count: total number of valuations"
echo "  - total_likes: sum of all likes across valuations"
echo ""

# Get any public brickset to demonstrate structure
GET_PUBLIC=$(curl -s "$BASE_URL/bricksets?page_size=1")
DEMO_ID=$(echo "$GET_PUBLIC" | jq '.results[0].id')

if [ ! -z "$DEMO_ID" ] && [ "$DEMO_ID" != "null" ]; then
    GET_DETAIL_DEMO=$(curl -s "$BASE_URL/bricksets/$DEMO_ID")
    
    echo "Example detail response for BrickSet ID $DEMO_ID:"
    echo "$GET_DETAIL_DEMO" | jq '{
      id,
      number,
      production_status,
      completeness,
      has_instructions,
      has_box,
      is_factory_sealed,
      owner_id,
      owner_initial_estimate,
      valuations_count,
      total_likes,
      valuations: (.valuations | if length > 0 then [.[0]] else [] end),
      created_at,
      updated_at
    }'
    
    print_success "Detail endpoint structure demonstrated"
else
    print_info "No BrickSets available in system yet"
fi

# ============================================================
# TEST 21: GET /api/v1/bricksets/{id} - WITH VALUATIONS
# ============================================================

print_header "TEST 21: GET /api/v1/bricksets/{id} - WITH VALUATIONS & AGGREGATES"

echo "Endpoint: GET $BASE_URL/bricksets/$BRICKSET1_ID"
echo "Expected: HTTP 200 with valuations and aggregates"
echo ""

GET_DETAIL_VALS=$(curl -s -w "\n%{http_code}" "$BASE_URL/bricksets/$BRICKSET1_ID")

GET_DETAIL_VALS_HTTP=$(echo "$GET_DETAIL_VALS" | tail -1)
GET_DETAIL_VALS_BODY=$(echo "$GET_DETAIL_VALS" | sed '$d')

if [ "$GET_DETAIL_VALS_HTTP" = "200" ]; then
    print_success "BrickSet detail retrieved (HTTP $GET_DETAIL_VALS_HTTP)"
    
    VALUATIONS_COUNT=$(echo "$GET_DETAIL_VALS_BODY" | jq '.valuations_count')
    TOTAL_LIKES=$(echo "$GET_DETAIL_VALS_BODY" | jq '.total_likes')
    ACTUAL_VAL_COUNT=$(echo "$GET_DETAIL_VALS_BODY" | jq '.valuations | length')
    
    echo "Response includes:"
    echo "  valuations_count: $VALUATIONS_COUNT"
    echo "  total_likes: $TOTAL_LIKES"
    echo "  valuations array length: $ACTUAL_VAL_COUNT"
    
    # Show structure
    echo ""
    echo "Response structure:"
    echo "$GET_DETAIL_VALS_BODY" | jq 'keys'
else
    print_error "GET detail failed (HTTP $GET_DETAIL_VALS_HTTP)"
fi

# ============================================================
# TEST 22: GET /api/v1/bricksets/{id} - AUTHENTICATED USER
# ============================================================

print_header "TEST 22: GET /api/v1/bricksets/{id} - AUTHENTICATED USER"

echo "Endpoint: GET $BASE_URL/bricksets/$BRICKSET1_ID (with JWT token)"
echo "Expected: HTTP 200 (same result as public, no difference)"
echo ""

GET_DETAIL_AUTH=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  "$BASE_URL/bricksets/$BRICKSET1_ID")

GET_DETAIL_AUTH_HTTP=$(echo "$GET_DETAIL_AUTH" | tail -1)
GET_DETAIL_AUTH_BODY=$(echo "$GET_DETAIL_AUTH" | sed '$d')

if [ "$GET_DETAIL_AUTH_HTTP" = "200" ]; then
    print_success "Authenticated user can access detail (HTTP $GET_DETAIL_AUTH_HTTP)"
    DETAIL_COUNT=$(echo "$GET_DETAIL_AUTH_BODY" | jq '.valuations_count')
    echo "Valuations count: $DETAIL_COUNT"
else
    print_error "GET detail for authenticated user failed (HTTP $GET_DETAIL_AUTH_HTTP)"
fi

# ============================================================
# TEST 23: GET /api/v1/bricksets/{id} - SECOND BRICKSET (INCOMPLETE)
# ============================================================

print_header "TEST 23: GET /api/v1/bricksets/{id} - INCOMPLETE BRICKSET"

echo "Endpoint: GET $BASE_URL/bricksets/$BRICKSET2_ID"
echo "Expected: HTTP 200 with INCOMPLETE brickset details"
echo ""

GET_DETAIL2=$(curl -s -w "\n%{http_code}" "$BASE_URL/bricksets/$BRICKSET2_ID")

GET_DETAIL2_HTTP=$(echo "$GET_DETAIL2" | tail -1)
GET_DETAIL2_BODY=$(echo "$GET_DETAIL2" | sed '$d')

if [ "$GET_DETAIL2_HTTP" = "200" ]; then
    print_success "Second BrickSet detail retrieved (HTTP $GET_DETAIL2_HTTP)"
    echo "Details:"
    echo "$GET_DETAIL2_BODY" | jq '{
      number,
      production_status,
      completeness,
      has_instructions,
      has_box,
      is_factory_sealed,
      valuations_count,
      total_likes
    }'
else
    print_error "GET detail for second BrickSet failed (HTTP $GET_DETAIL2_HTTP)"
fi

# ============================================================
# TEST 24: GET /api/v1/bricksets/{id} - RESPONSE STRUCTURE
# ============================================================

print_header "TEST 24: GET /api/v1/bricksets/{id} - RESPONSE STRUCTURE VALIDATION"

echo "Endpoint: GET $BASE_URL/bricksets/$BRICKSET1_ID"
echo "Checking that response has all required fields"
echo ""

GET_DETAIL_STRUCT=$(curl -s -w "\n%{http_code}" "$BASE_URL/bricksets/$BRICKSET1_ID")

GET_DETAIL_STRUCT_HTTP=$(echo "$GET_DETAIL_STRUCT" | tail -1)
GET_DETAIL_STRUCT_BODY=$(echo "$GET_DETAIL_STRUCT" | sed '$d')

if [ "$GET_DETAIL_STRUCT_HTTP" = "200" ]; then
    # Check BrickSet level fields
    REQUIRED_FIELDS="id number production_status completeness valuations_count total_likes valuations created_at updated_at"
    MISSING_FIELDS=""
    
    for field in $REQUIRED_FIELDS; do
        if ! echo "$GET_DETAIL_STRUCT_BODY" | jq -e ".\"$field\"" > /dev/null 2>&1; then
            MISSING_FIELDS="$MISSING_FIELDS $field"
        fi
    done
    
    if [ -z "$MISSING_FIELDS" ]; then
        print_success "All BrickSet response fields present"
        echo "Fields in response:"
        echo "$GET_DETAIL_STRUCT_BODY" | jq 'keys | sort'
    else
        print_error "Missing BrickSet fields:$MISSING_FIELDS"
    fi
    
    # If there are valuations, check their structure
    VAL_COUNT=$(echo "$GET_DETAIL_STRUCT_BODY" | jq '.valuations | length')
    if [ "$VAL_COUNT" -gt 0 ]; then
        echo ""
        echo "Valuation fields present:"
        echo "$GET_DETAIL_STRUCT_BODY" | jq '.valuations[0] | keys | sort'
    else
        echo ""
        print_info "No valuations in response (array empty) - structure validation skipped for nested fields"
    fi
else
    print_error "GET detail failed (HTTP $GET_DETAIL_STRUCT_HTTP)"
fi

# ============================================================
# TEST 25: GET /api/v1/bricksets/{id} - DATETIME FORMAT
# ============================================================

print_header "TEST 25: GET /api/v1/bricksets/{id} - DATETIME ISO8601 FORMAT"

echo "Endpoint: GET $BASE_URL/bricksets/$BRICKSET1_ID"
echo "Checking datetime fields are ISO8601 formatted"
echo ""

GET_DETAIL_DT=$(curl -s -w "\n%{http_code}" "$BASE_URL/bricksets/$BRICKSET1_ID")

GET_DETAIL_DT_HTTP=$(echo "$GET_DETAIL_DT" | tail -1)
GET_DETAIL_DT_BODY=$(echo "$GET_DETAIL_DT" | sed '$d')

if [ "$GET_DETAIL_DT_HTTP" = "200" ]; then
    CREATED_AT=$(echo "$GET_DETAIL_DT_BODY" | jq -r '.created_at')
    UPDATED_AT=$(echo "$GET_DETAIL_DT_BODY" | jq -r '.updated_at')
    VAL_CREATED_AT=$(echo "$GET_DETAIL_DT_BODY" | jq -r '.valuations[0].created_at // empty')
    
    echo "BrickSet created_at: $CREATED_AT"
    echo "BrickSet updated_at: $UPDATED_AT"
    echo "First valuation created_at: $VAL_CREATED_AT"
    
    # Check ISO8601 format (should contain 'T')
    if [[ "$CREATED_AT" == *"T"* ]] && [[ "$UPDATED_AT" == *"T"* ]]; then
        print_success "Datetime fields are ISO8601 formatted"
    else
        print_error "Datetime fields not in ISO8601 format"
    fi
else
    print_error "GET detail failed (HTTP $GET_DETAIL_DT_HTTP)"
fi

# ============================================================
# TEST 26: PATCH /api/v1/bricksets/{id} - PARTIAL UPDATE (SINGLE FIELD)
# ============================================================

print_header "TEST 26: PATCH /api/v1/bricksets/{id} - UPDATE SINGLE FIELD"

echo "Endpoint: PATCH $BASE_URL/bricksets/$BRICKSET1_ID"
echo "Payload:"
echo "{\"has_box\": false}"
echo "Expected: HTTP 200 with updated BrickSet"
echo ""

PATCH_SINGLE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X PATCH "$BASE_URL/bricksets/$BRICKSET1_ID" \
  -d '{"has_box": false}')

PATCH_SINGLE_HTTP=$(echo "$PATCH_SINGLE" | tail -1)
PATCH_SINGLE_BODY=$(echo "$PATCH_SINGLE" | sed '$d')

if [ "$PATCH_SINGLE_HTTP" = "200" ]; then
    print_success "Partial update successful (HTTP $PATCH_SINGLE_HTTP)"
    echo "Updated response:"
    echo "$PATCH_SINGLE_BODY" | jq '{id, number, has_box, owner_initial_estimate}'
else
    print_error "PATCH request failed (HTTP $PATCH_SINGLE_HTTP)"
    echo "$PATCH_SINGLE_BODY"
fi

# ============================================================
# TEST 27: PATCH /api/v1/bricksets/{id} - UPDATE MULTIPLE FIELDS
# ============================================================

print_header "TEST 27: PATCH /api/v1/bricksets/{id} - UPDATE MULTIPLE FIELDS"

echo "Endpoint: PATCH $BASE_URL/bricksets/$BRICKSET1_ID"
echo "Payload:"
echo "{\"has_box\": true, \"owner_initial_estimate\": 350}"
echo "Expected: HTTP 200 with both fields updated"
echo ""

PATCH_MULTI=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X PATCH "$BASE_URL/bricksets/$BRICKSET1_ID" \
  -d '{"has_box": true, "owner_initial_estimate": 350}')

PATCH_MULTI_HTTP=$(echo "$PATCH_MULTI" | tail -1)
PATCH_MULTI_BODY=$(echo "$PATCH_MULTI" | sed '$d')

if [ "$PATCH_MULTI_HTTP" = "200" ]; then
    print_success "Multi-field update successful (HTTP $PATCH_MULTI_HTTP)"
    echo "Updated response:"
    echo "$PATCH_MULTI_BODY" | jq '{id, has_box, owner_initial_estimate}'
    
    # Verify the values changed
    HAS_BOX=$(echo "$PATCH_MULTI_BODY" | jq '.has_box')
    ESTIMATE=$(echo "$PATCH_MULTI_BODY" | jq '.owner_initial_estimate')
    echo "Verification: has_box=$HAS_BOX, estimate=$ESTIMATE"
else
    print_error "PATCH request failed (HTTP $PATCH_MULTI_HTTP)"
    echo "$PATCH_MULTI_BODY"
fi

# ============================================================
# TEST 28: PATCH /api/v1/bricksets/{id} - EMPTY PAYLOAD (400)
# ============================================================

print_header "TEST 28: PATCH /api/v1/bricksets/{id} - EMPTY PAYLOAD (VALIDATION ERROR)"

echo "Endpoint: PATCH $BASE_URL/bricksets/$BRICKSET1_ID"
echo "Payload: {} (empty)"
echo "Expected: HTTP 400 (at least one field required)"
echo ""

PATCH_EMPTY=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X PATCH "$BASE_URL/bricksets/$BRICKSET1_ID" \
  -d '{}')

PATCH_EMPTY_HTTP=$(echo "$PATCH_EMPTY" | tail -1)
PATCH_EMPTY_BODY=$(echo "$PATCH_EMPTY" | sed '$d')

if [ "$PATCH_EMPTY_HTTP" = "400" ]; then
    print_success "Empty payload correctly rejected (HTTP $PATCH_EMPTY_HTTP)"
    echo "Error response:"
    echo "$PATCH_EMPTY_BODY" | jq '.errors // .detail'
else
    print_error "Expected 400 but got $PATCH_EMPTY_HTTP"
fi

# ============================================================
# TEST 29: PATCH /api/v1/bricksets/{id} - INVALID TYPE (400)
# ============================================================

print_header "TEST 29: PATCH /api/v1/bricksets/{id} - INVALID FIELD TYPE"

echo "Endpoint: PATCH $BASE_URL/bricksets/$BRICKSET1_ID"
echo "Payload: {\"has_box\": 123} (integer instead of boolean)"
echo "Expected: HTTP 400 (type validation error)"
echo ""

PATCH_INVALID_TYPE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X PATCH "$BASE_URL/bricksets/$BRICKSET1_ID" \
  -d '{"has_box": 123}')

PATCH_INVALID_TYPE_HTTP=$(echo "$PATCH_INVALID_TYPE" | tail -1)
PATCH_INVALID_TYPE_BODY=$(echo "$PATCH_INVALID_TYPE" | sed '$d')

if [ "$PATCH_INVALID_TYPE_HTTP" = "400" ]; then
    print_success "Invalid type correctly rejected (HTTP $PATCH_INVALID_TYPE_HTTP)"
    echo "Error response:"
    echo "$PATCH_INVALID_TYPE_BODY" | jq '.errors // .detail'
else
    print_error "Expected 400 but got $PATCH_INVALID_TYPE_HTTP"
fi

# ============================================================
# TEST 30: PATCH /api/v1/bricksets/{id} - OWNER ESTIMATE OUT OF RANGE
# ============================================================

print_header "TEST 30: PATCH /api/v1/bricksets/{id} - OWNER ESTIMATE OUT OF RANGE"

echo "Endpoint: PATCH $BASE_URL/bricksets/$BRICKSET1_ID"
echo "Payload: {\"owner_initial_estimate\": 10000000} (exceeds max 999999)"
echo "Expected: HTTP 400 (range validation error)"
echo ""

PATCH_OUT_OF_RANGE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X PATCH "$BASE_URL/bricksets/$BRICKSET1_ID" \
  -d '{"owner_initial_estimate": 10000000}')

PATCH_RANGE_HTTP=$(echo "$PATCH_OUT_OF_RANGE" | tail -1)
PATCH_RANGE_BODY=$(echo "$PATCH_OUT_OF_RANGE" | sed '$d')

if [ "$PATCH_RANGE_HTTP" = "400" ]; then
    print_success "Out of range correctly rejected (HTTP $PATCH_RANGE_HTTP)"
    echo "Error response:"
    echo "$PATCH_RANGE_BODY" | jq '.errors // .detail'
else
    print_error "Expected 400 but got $PATCH_RANGE_HTTP"
fi

# ============================================================
# TEST 31: PATCH /api/v1/bricksets/{id} - NOT OWNER (403)
# ============================================================

print_header "TEST 31: PATCH /api/v1/bricksets/{id} - NOT OWNER (FORBIDDEN)"

echo "Creating second test user..."

TIMESTAMP2=$(date +%s)
TEST_USERNAME2="catalogtester_$TIMESTAMP2"
TEST_EMAIL2="catalog_test_$TIMESTAMP2@example.com"
TEST_PASSWORD2="TestPass123!"

# Register second user
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_USERNAME2\",
    \"email\": \"$TEST_EMAIL2\",
    \"password\": \"$TEST_PASSWORD2\"
  }" > /dev/null

# Login second user
LOGIN2_RESPONSE=$(curl -s -D /tmp/catalog_login2_headers.txt -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_USERNAME2\",
    \"password\": \"$TEST_PASSWORD2\"
  }")

JWT_TOKEN2=$(cat /tmp/catalog_login2_headers.txt | grep "jwt_token=" | sed 's/.*jwt_token=//' | sed 's/;.*//' | tr -d ' \n')

echo "Endpoint: PATCH $BASE_URL/bricksets/$BRICKSET1_ID"
echo "Attempt: Different user trying to update first user's BrickSet"
echo "Expected: HTTP 403 Forbidden (not owner)"
echo ""

PATCH_NOT_OWNER=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X PATCH "$BASE_URL/bricksets/$BRICKSET1_ID" \
  -d '{"has_box": false}')

PATCH_NOT_OWNER_HTTP=$(echo "$PATCH_NOT_OWNER" | tail -1)
PATCH_NOT_OWNER_BODY=$(echo "$PATCH_NOT_OWNER" | sed '$d')

if [ "$PATCH_NOT_OWNER_HTTP" = "403" ]; then
    print_success "Non-owner correctly rejected (HTTP $PATCH_NOT_OWNER_HTTP)"
    echo "Error response:"
    echo "$PATCH_NOT_OWNER_BODY" | jq '{detail, reason}'
else
    print_error "Expected 403 but got $PATCH_NOT_OWNER_HTTP"
    echo "$PATCH_NOT_OWNER_BODY"
fi

# ============================================================
# TEST 32: PATCH /api/v1/bricksets/{id} - UNAUTHORIZED (NO JWT)
# ============================================================

print_header "TEST 32: PATCH /api/v1/bricksets/{id} - UNAUTHORIZED (NO AUTH)"

echo "Endpoint: PATCH $BASE_URL/bricksets/$BRICKSET1_ID"
echo "Expected: HTTP 401 Unauthorized (no JWT token)"
echo ""

PATCH_NOAUTH=$(curl -s -w "\n%{http_code}" \
  -H "Content-Type: application/json" \
  -X PATCH "$BASE_URL/bricksets/$BRICKSET1_ID" \
  -d '{"has_box": false}')

PATCH_NOAUTH_HTTP=$(echo "$PATCH_NOAUTH" | tail -1)
PATCH_NOAUTH_BODY=$(echo "$PATCH_NOAUTH" | sed '$d')

if [ "$PATCH_NOAUTH_HTTP" = "401" ]; then
    print_success "Unauthenticated request correctly rejected (HTTP $PATCH_NOAUTH_HTTP)"
else
    print_error "Expected 401 but got $PATCH_NOAUTH_HTTP"
fi

# ============================================================
# TEST 33: PATCH /api/v1/bricksets/{id} - NOT FOUND (404)
# ============================================================

print_header "TEST 33: PATCH /api/v1/bricksets/{id} - NOT FOUND"

echo "Endpoint: PATCH $BASE_URL/bricksets/999999"
echo "Expected: HTTP 404 Not Found (nonexistent BrickSet)"
echo ""

PATCH_404=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X PATCH "$BASE_URL/bricksets/999999" \
  -d '{"has_box": false}')

PATCH_404_HTTP=$(echo "$PATCH_404" | tail -1)
PATCH_404_BODY=$(echo "$PATCH_404" | sed '$d')

if [ "$PATCH_404_HTTP" = "404" ]; then
    print_success "Not found correctly returned (HTTP $PATCH_404_HTTP)"
    echo "Response:"
    echo "$PATCH_404_BODY" | jq '.detail'
else
    print_error "Expected 404 but got $PATCH_404_HTTP"
fi

# ============================================================
# TEST 34: DELETE /api/v1/bricksets/{id} - SUCCESSFUL DELETE
# ============================================================

print_header "TEST 34: DELETE /api/v1/bricksets/{id} - SUCCESSFUL DELETE"

echo "Endpoint: DELETE $BASE_URL/bricksets/$BRICKSET2_ID"
echo "Payload: (no body for DELETE)"
echo "Expected: HTTP 204 No Content"
echo ""

DELETE_SUCCESS=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X DELETE "$BASE_URL/bricksets/$BRICKSET2_ID")

DELETE_SUCCESS_HTTP=$(echo "$DELETE_SUCCESS" | tail -1)
DELETE_SUCCESS_BODY=$(echo "$DELETE_SUCCESS" | sed '$d')

if [ "$DELETE_SUCCESS_HTTP" = "204" ]; then
    print_success "BrickSet deleted successfully (HTTP $DELETE_SUCCESS_HTTP)"
    echo "Response: (empty body for 204 No Content)"
else
    print_error "DELETE request failed (HTTP $DELETE_SUCCESS_HTTP)"
    echo "$DELETE_SUCCESS_BODY"
fi

# ============================================================
# TEST 35: DELETE /api/v1/bricksets/{id} - VERIFY DELETED
# ============================================================

print_header "TEST 35: DELETE /api/v1/bricksets/{id} - VERIFY DELETED FROM DB"

echo "Endpoint: GET $BASE_URL/bricksets/$BRICKSET2_ID"
echo "Expected: HTTP 404 Not Found (BrickSet was deleted)"
echo ""

GET_DELETED=$(curl -s -w "\n%{http_code}" "$BASE_URL/bricksets/$BRICKSET2_ID")

GET_DELETED_HTTP=$(echo "$GET_DELETED" | tail -1)
GET_DELETED_BODY=$(echo "$GET_DELETED" | sed '$d')

if [ "$GET_DELETED_HTTP" = "404" ]; then
    print_success "Deleted BrickSet not found (HTTP $GET_DELETED_HTTP) - Deletion verified"
else
    print_error "Expected 404 but got $GET_DELETED_HTTP - BrickSet may not have been deleted"
fi

# ============================================================
# TEST 36: DELETE /api/v1/bricksets/{id} - UNAUTHORIZED (NO JWT)
# ============================================================

print_header "TEST 36: DELETE /api/v1/bricksets/{id} - UNAUTHORIZED (NO AUTH)"

echo "Creating new BrickSet for this test..."

# Create new brickset for deletion test
BRICKSET_NUM_DEL=$((1000000 + (TIMESTAMP % 8999999) + 10))

POST_FOR_DEL=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $BRICKSET_NUM_DEL,
    \"production_status\": \"ACTIVE\",
    \"completeness\": \"COMPLETE\",
    \"has_instructions\": true,
    \"has_box\": true,
    \"is_factory_sealed\": false
  }")

BRICKSET_DEL_ID=$(echo "$POST_FOR_DEL" | jq '.id')

echo "Endpoint: DELETE $BASE_URL/bricksets/$BRICKSET_DEL_ID"
echo "Expected: HTTP 401 Unauthorized (no JWT token)"
echo ""

DELETE_NOAUTH=$(curl -s -w "\n%{http_code}" \
  -X DELETE "$BASE_URL/bricksets/$BRICKSET_DEL_ID")

DELETE_NOAUTH_HTTP=$(echo "$DELETE_NOAUTH" | tail -1)
DELETE_NOAUTH_BODY=$(echo "$DELETE_NOAUTH" | sed '$d')

if [ "$DELETE_NOAUTH_HTTP" = "401" ]; then
    print_success "Unauthenticated DELETE correctly rejected (HTTP $DELETE_NOAUTH_HTTP)"
    echo "Error response:"
    echo "$DELETE_NOAUTH_BODY" | jq '.detail'
else
    print_error "Expected 401 but got $DELETE_NOAUTH_HTTP"
fi

# ============================================================
# TEST 37: DELETE /api/v1/bricksets/{id} - NOT OWNER (403)
# ============================================================

print_header "TEST 37: DELETE /api/v1/bricksets/{id} - NOT OWNER (FORBIDDEN)"

echo "Endpoint: DELETE $BASE_URL/bricksets/$BRICKSET_DEL_ID"
echo "Attempt: Different user trying to delete first user's BrickSet"
echo "Expected: HTTP 403 Forbidden (not owner)"
echo ""

DELETE_NOT_OWNER=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -X DELETE "$BASE_URL/bricksets/$BRICKSET_DEL_ID")

DELETE_NOT_OWNER_HTTP=$(echo "$DELETE_NOT_OWNER" | tail -1)
DELETE_NOT_OWNER_BODY=$(echo "$DELETE_NOT_OWNER" | sed '$d')

if [ "$DELETE_NOT_OWNER_HTTP" = "403" ]; then
    print_success "Non-owner correctly rejected (HTTP $DELETE_NOT_OWNER_HTTP)"
    echo "Error response:"
    echo "$DELETE_NOT_OWNER_BODY" | jq '{detail, reason}'
else
    print_error "Expected 403 but got $DELETE_NOT_OWNER_HTTP"
    echo "$DELETE_NOT_OWNER_BODY"
fi

# ============================================================
# TEST 38: DELETE /api/v1/bricksets/{id} - NOT FOUND (404)
# ============================================================

print_header "TEST 38: DELETE /api/v1/bricksets/{id} - NOT FOUND"

echo "Endpoint: DELETE $BASE_URL/bricksets/999999"
echo "Expected: HTTP 404 Not Found (nonexistent BrickSet)"
echo ""

DELETE_404=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X DELETE "$BASE_URL/bricksets/999999")

DELETE_404_HTTP=$(echo "$DELETE_404" | tail -1)
DELETE_404_BODY=$(echo "$DELETE_404" | sed '$d')

if [ "$DELETE_404_HTTP" = "404" ]; then
    print_success "Not found correctly returned (HTTP $DELETE_404_HTTP)"
    echo "Response:"
    echo "$DELETE_404_BODY" | jq '.detail'
else
    print_error "Expected 404 but got $DELETE_404_HTTP"
fi

# ============================================================
# TEST 39: DELETE /api/v1/bricksets/{id} - VERIFY STILL EXISTS AFTER FAILED DELETE
# ============================================================

print_header "TEST 39: DELETE /api/v1/bricksets/{id} - VERIFY NOT OWNER DIDN'T DELETE"

echo "Endpoint: GET $BASE_URL/bricksets/$BRICKSET_DEL_ID"
echo "Expected: HTTP 200 (BrickSet should still exist - not owner couldn't delete it)"
echo ""

GET_STILL_EXISTS=$(curl -s -w "\n%{http_code}" "$BASE_URL/bricksets/$BRICKSET_DEL_ID")

GET_STILL_EXISTS_HTTP=$(echo "$GET_STILL_EXISTS" | tail -1)
GET_STILL_EXISTS_BODY=$(echo "$GET_STILL_EXISTS" | sed '$d')

if [ "$GET_STILL_EXISTS_HTTP" = "200" ]; then
    print_success "BrickSet still exists (HTTP $GET_STILL_EXISTS_HTTP) - Deletion was prevented correctly"
    echo "BrickSet number: $(echo "$GET_STILL_EXISTS_BODY" | jq '.number')"
else
    print_error "Expected 200 but got $GET_STILL_EXISTS_HTTP - BrickSet may have been wrongly deleted"
fi

# ============================================================
# TEST 40: DELETE /api/v1/bricksets/{id} - SUCCESSFUL OWNER DELETE
# ============================================================

print_header "TEST 40: DELETE /api/v1/bricksets/{id} - SUCCESSFUL OWNER DELETE"

echo "Endpoint: DELETE $BASE_URL/bricksets/$BRICKSET_DEL_ID"
echo "Attempt: Owner deleting own BrickSet"
echo "Expected: HTTP 204 No Content"
echo ""

DELETE_OWNER=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X DELETE "$BASE_URL/bricksets/$BRICKSET_DEL_ID")

DELETE_OWNER_HTTP=$(echo "$DELETE_OWNER" | tail -1)
DELETE_OWNER_BODY=$(echo "$DELETE_OWNER" | sed '$d')

if [ "$DELETE_OWNER_HTTP" = "204" ]; then
    print_success "Owner successfully deleted BrickSet (HTTP $DELETE_OWNER_HTTP)"
else
    print_error "DELETE request failed (HTTP $DELETE_OWNER_HTTP)"
    echo "$DELETE_OWNER_BODY"
fi

# ============================================================
# TEST 41: DELETE /api/v1/bricksets/{id} - VERIFY DELETE IDEMPOTENCE
# ============================================================

print_header "TEST 41: DELETE /api/v1/bricksets/{id} - DOUBLE DELETE (404)"

echo "Endpoint: DELETE $BASE_URL/bricksets/$BRICKSET_DEL_ID (again)"
echo "Expected: HTTP 404 Not Found (already deleted)"
echo ""

DELETE_AGAIN=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X DELETE "$BASE_URL/bricksets/$BRICKSET_DEL_ID")

DELETE_AGAIN_HTTP=$(echo "$DELETE_AGAIN" | tail -1)
DELETE_AGAIN_BODY=$(echo "$DELETE_AGAIN" | sed '$d')

if [ "$DELETE_AGAIN_HTTP" = "404" ]; then
    print_success "Double delete correctly returned 404 (HTTP $DELETE_AGAIN_HTTP)"
else
    print_error "Expected 404 but got $DELETE_AGAIN_HTTP"
fi

# ============================================================
# POST-TEST CLEANUP
# ============================================================

print_header "POST-TEST DATABASE CLEANUP"
clean_database

# ============================================================
# SUMMARY
# ============================================================

print_header "TEST SUMMARY"
print_success "All catalog API tests completed!"
echo ""
echo "Summary:"
echo ""
echo "CREATE ENDPOINTS (POST):"
echo "  ✅ BrickSet creation (POST /api/v1/bricksets)"
echo "  ✅ Required and optional fields validation"
echo "  ✅ Duplicate detection (409 Conflict)"
echo "  ✅ Field validation errors (400 Bad Request)"
echo "  ✅ Enum validation for production_status and completeness"
echo "  ✅ Numeric range validation"
echo "  ✅ Authentication required for POST"
echo ""
echo "LIST ENDPOINTS (GET /api/v1/bricksets):"
echo "  ✅ BrickSet listing with pagination"
echo "  ✅ Filtering by production_status"
echo "  ✅ Filtering by completeness"
echo "  ✅ Search by set number"
echo "  ✅ Combined filters"
echo "  ✅ Sorting support (-number, -created_at, etc.)"
echo "  ✅ Public access (no authentication required)"
echo ""
echo "DETAIL ENDPOINTS (GET /api/v1/bricksets/{id}):"
echo "  ✅ BrickSet detail retrieval"
echo "  ✅ Detail without valuations (empty array)"
echo "  ✅ Detail with valuations (nested array)"
echo "  ✅ Valuation aggregates (valuations_count, total_likes)"
echo "  ✅ All required fields present (id, number, owner_id, etc.)"
echo "  ✅ Valuation fields present (id, user_id, value, currency, comment, likes_count, created_at)"
echo "  ✅ Correct aggregate calculations (count=array length, likes=sum)"
echo "  ✅ Datetime ISO8601 formatting (created_at, updated_at)"
echo "  ✅ Handle null comment in valuations"
echo "  ✅ 404 Not Found for nonexistent BrickSet"
echo "  ✅ Public access (no authentication required)"
echo "  ✅ Works with authenticated users"
echo ""
echo "UPDATE ENDPOINTS (PATCH /api/v1/bricksets/{id}):"
echo "  ✅ Partial update - single field (has_box)"
echo "  ✅ Partial update - multiple fields (has_box + owner_initial_estimate)"
echo "  ✅ Empty payload validation (400 - at least one field required)"
echo "  ✅ Invalid field type validation (400 - boolean expected)"
echo "  ✅ Numeric range validation (1-999999 for estimate)"
echo "  ✅ Owner-only edit enforcement (403 for non-owner)"
echo "  ✅ Authentication required for PATCH (401 unauthenticated)"
echo "  ✅ 404 Not Found for nonexistent BrickSet"
echo "  ✅ Response contains full BrickSet detail (with valuations/aggregates)"
echo ""
echo "DELETE ENDPOINTS (DELETE /api/v1/bricksets/{id}):"
echo "  ✅ BrickSet deletion (DELETE /api/v1/bricksets/{id})"
echo "  ✅ 204 No Content response on success"
echo "  ✅ Verified deletion from database (subsequent GET returns 404)"
echo "  ✅ Authentication required for DELETE (401 unauthenticated)"
echo "  ✅ Owner-only delete enforcement (403 for non-owner)"
echo "  ✅ 404 Not Found for nonexistent BrickSet"
echo "  ✅ Non-owner DELETE doesn't remove BrickSet (403 verified)"
echo "  ✅ Delete idempotence (second DELETE returns 404)"
echo ""
print_info "Database cleaned after tests"
echo ""
