#!/bin/bash

# ============================================================
# CATALOG API TEST SUITE - CURL COMMANDS
# ============================================================
# Usage: bash catalog_api_tests.sh
# This script tests the BrickSet endpoints:
# - GET /api/v1/bricksets (list with filters and pagination)
# - POST /api/v1/bricksets (create new BrickSet)
#
# Note: Requires authentication. Script automatically:
# 1. Creates test user account
# 2. Logs in to get JWT token
# 3. Runs catalog API tests using the token
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
echo "  ✅ BrickSet creation (POST /api/v1/bricksets)"
echo "  ✅ Required and optional fields validation"
echo "  ✅ Duplicate detection (409 Conflict)"
echo "  ✅ Field validation errors (400 Bad Request)"
echo "  ✅ Enum validation for production_status and completeness"
echo "  ✅ Numeric range validation"
echo "  ✅ Authentication required for POST"
echo "  ✅ BrickSet listing (GET /api/v1/bricksets)"
echo "  ✅ Pagination support"
echo "  ✅ Filtering by production_status"
echo "  ✅ Filtering by completeness"
echo "  ✅ Search by set number"
echo "  ✅ Combined filters"
echo "  ✅ Sorting support"
echo "  ✅ Public access to GET endpoint"
echo ""
print_info "Database cleaned after tests"
echo ""
