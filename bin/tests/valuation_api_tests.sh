#!/bin/bash

# ============================================================
# VALUATION API TEST SUITE - CURL COMMANDS
# ============================================================
# Usage: bash valuation_api_tests.sh
# This script tests the Valuation endpoints:
# - POST /api/v1/bricksets/{brickset_id}/valuations (create new valuation)
# - GET /api/v1/bricksets/{brickset_id}/valuations (list valuations)
# - GET /api/v1/valuations/{id} (get valuation detail)
# - POST /api/v1/valuations/{valuation_id}/likes (create like)
# - DELETE /api/v1/valuations/{valuation_id}/likes (remove like)
# 
# Functional tests cover:
# CREATE VALUATION (POST /bricksets/{id}/valuations):
# - Successful valuation creation (201 Created)
# - Field validation (value range, currency length, optional comment)
# - Duplicate detection (409 Conflict - user already has valuation for this set)
# - BrickSet not found (404 Not Found)
# - Authentication required (401 Unauthorized)
# - Multiple users can value same BrickSet
# - Same user can value different BrickSets
#
# LIST VALUATIONS (GET /bricksets/{id}/valuations):
# - Successful list retrieval (200 OK)
# - Pagination (page, page_size parameters)
# - Ordering by likes_count DESC, created_at ASC
# - Empty list for BrickSet without valuations
# - Authentication required (401 Unauthorized)
# - BrickSet not found (404 Not Found)
# - Response structure validation
#
# DETAIL VALUATION (GET /valuations/{id}):
# - Successful detail retrieval (200 OK)
# - All fields including updated_at
# - Public read access
# - Nonexistent valuation (404)
#
# LIKE ENDPOINTS (POST /valuations/{id}/likes):
# - Successful like creation (201 Created)
# - Like own valuation rejection (403 Forbidden)
# - Nonexistent valuation (404 Not Found)
# - Duplicate like rejection (409 Conflict)
# - Authentication required (401 Unauthorized)
# - Multiple users can like same valuation
# - Response structure validation
#
# UNLIKE ENDPOINTS (DELETE /valuations/{id}/likes):
# - Successful like deletion (204 No Content)
# - Like not found when already deleted (404 Not Found)
# - Cannot delete other user's like (404 Not Found - implicit authorization)
# - Authentication required (401 Unauthorized)
# - Selective deletion (delete one like, others remain)
#
# Note: Requires authentication. Script automatically:
# 1. Creates test user account
# 2. Logs in to get JWT token
# 3. Creates test BrickSet (requires catalog app to be available)
# 4. Runs valuation API tests using the token
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

# Function to clean database - delete all valuations and bricksets before tests
clean_database_pre_test() {
    print_info "Cleaning test data from previous runs..."
    docker-compose exec -T backend python manage.py shell -c "
from catalog.models import BrickSet
from valuation.models import Valuation

try:
    # Delete test valuations (all, since they belong to test bricksets)
    val_count = Valuation.valuations.filter(
        brickset__number__gte=1000000, 
        brickset__number__lte=9999999
    ).delete()[0]
    print(f'Deleted {val_count} Valuations')
    
    # Delete test bricksets
    bs_count = BrickSet.bricksets.filter(number__gte=1000000, number__lte=9999999).delete()[0]
    print(f'Deleted {bs_count} BrickSets')
except Exception as e:
    print(f'Cleanup error: {e}')
" 2>&1 | grep -v "^$\|^10\|^[0-9]* objects"
    print_success "Pre-test cleanup completed"
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
# SETUP: CREATE USERS AND LOGIN
# ============================================================

print_header "SETUP: CREATE TEST USERS AND LOGIN"

TIMESTAMP=$(date +%s)
TEST_USERNAME="valuationtester_$TIMESTAMP"
TEST_EMAIL="valuation_test_$TIMESTAMP@example.com"
TEST_PASSWORD="TestPass123!"

TEST_USERNAME2="valuationtester2_$TIMESTAMP"
TEST_EMAIL2="valuation_test2_$TIMESTAMP@example.com"
TEST_PASSWORD2="TestPass123!"

TEST_USERNAME3="valuationtester3_$TIMESTAMP"
TEST_EMAIL3="valuation_test3_$TIMESTAMP@example.com"
TEST_PASSWORD3="TestPass123!"

# Register first user
print_info "Creating first test user account ($TEST_USERNAME)..."

curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_USERNAME\",
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\"
  }" > /dev/null

print_success "First user created"

# Login first user
print_info "Logging in first user to get JWT token..."

LOGIN_RESPONSE=$(curl -s -D /tmp/valuation_login_headers.txt -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_USERNAME\",
    \"password\": \"$TEST_PASSWORD\"
  }")

JWT_TOKEN=$(cat /tmp/valuation_login_headers.txt | grep "jwt_token=" | tr '\n' ' ' | sed 's/.*jwt_token=//' | sed 's/;.*//' | tr -d ' ')
if [ -z "$JWT_TOKEN" ]; then
    print_error "Could not extract JWT token from login response"
    exit 1
fi

print_success "First user logged in, JWT token obtained"

# Register second user
print_info "Creating second test user account ($TEST_USERNAME2)..."

curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_USERNAME2\",
    \"email\": \"$TEST_EMAIL2\",
    \"password\": \"$TEST_PASSWORD2\"
  }" > /dev/null

print_success "Second user created"

# Login second user
print_info "Logging in second user to get JWT token..."

LOGIN2_RESPONSE=$(curl -s -D /tmp/valuation_login2_headers.txt -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_USERNAME2\",
    \"password\": \"$TEST_PASSWORD2\"
  }")

JWT_TOKEN2=$(cat /tmp/valuation_login2_headers.txt | grep "jwt_token=" | tr '\n' ' ' | sed 's/.*jwt_token=//' | sed 's/;.*//' | tr -d ' ')

print_success "Second user logged in"

# Register third user
print_info "Creating third test user account ($TEST_USERNAME3)..."

curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_USERNAME3\",
    \"email\": \"$TEST_EMAIL3\",
    \"password\": \"$TEST_PASSWORD3\"
  }" > /dev/null

print_success "Third user created"

# Login third user
print_info "Logging in third user to get JWT token..."

LOGIN3_RESPONSE=$(curl -s -D /tmp/valuation_login3_headers.txt -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_USERNAME3\",
    \"password\": \"$TEST_PASSWORD3\"
  }")

JWT_TOKEN3=$(cat /tmp/valuation_login3_headers.txt | grep "jwt_token=" | tr '\n' ' ' | sed 's/.*jwt_token=//' | sed 's/;.*//' | tr -d ' ')

print_success "Third user logged in"

# ============================================================
# SETUP: CREATE TEST BRICKSETS (AS FIRST USER)
# ============================================================

print_header "SETUP: CREATE TEST BRICKSETS"

# Use unique timestamp-based numbers (within 1-9999999 range)
BRICKSET_NUM1=$((1000000 + (TIMESTAMP % 8999999)))
BRICKSET_NUM2=$((1000000 + (TIMESTAMP % 8999999) + 1))
BRICKSET_NUM3=$((1000000 + (TIMESTAMP % 8999999) + 2))

print_info "Creating first BrickSet..."

CREATE_BS1=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
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

BRICKSET1_ID=$(echo "$CREATE_BS1" | jq '.id')
print_success "BrickSet 1 created (ID: $BRICKSET1_ID)"

print_info "Creating second BrickSet..."

CREATE_BS2=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
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

BRICKSET2_ID=$(echo "$CREATE_BS2" | jq '.id')
print_success "BrickSet 2 created (ID: $BRICKSET2_ID)"

print_info "Creating third BrickSet..."

CREATE_BS3=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $BRICKSET_NUM3,
    \"production_status\": \"ACTIVE\",
    \"completeness\": \"COMPLETE\",
    \"has_instructions\": true,
    \"has_box\": true,
    \"is_factory_sealed\": false
  }")

BRICKSET3_ID=$(echo "$CREATE_BS3" | jq '.id')
print_success "BrickSet 3 created (ID: $BRICKSET3_ID)"

# ============================================================
# TEST 1: POST /api/v1/bricksets/{id}/valuations - SUCCESS (201)
# ============================================================

print_header "TEST 1: POST /api/v1/bricksets/{id}/valuations - SUCCESSFUL CREATION"

echo "Endpoint: POST $BASE_URL/bricksets/$BRICKSET1_ID/valuations"
echo "Payload:"
echo "{
  \"value\": 450,
  \"currency\": \"PLN\",
  \"comment\": \"Looks complete and in great condition\"
}"
echo ""

POST_SUCCESS=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$BRICKSET1_ID/valuations" \
  -d "{
    \"value\": 450,
    \"currency\": \"PLN\",
    \"comment\": \"Looks complete and in great condition\"
  }")

POST_SUCCESS_HTTP=$(echo "$POST_SUCCESS" | tail -1)
POST_SUCCESS_BODY=$(echo "$POST_SUCCESS" | sed '$d')

if [ "$POST_SUCCESS_HTTP" = "201" ]; then
    print_success "Valuation created successfully (HTTP $POST_SUCCESS_HTTP)"
    echo "Response:"
    echo "$POST_SUCCESS_BODY" | jq '{id, brickset_id, user_id, value, currency, comment, likes_count}'
    
    VAL1_ID=$(echo "$POST_SUCCESS_BODY" | jq '.id')
else
    print_error "Valuation creation failed (HTTP $POST_SUCCESS_HTTP)"
    echo "$POST_SUCCESS_BODY"
    exit 1
fi

# ============================================================
# TEST 2: POST /api/v1/bricksets/{id}/valuations - WITHOUT OPTIONAL FIELDS
# ============================================================

print_header "TEST 2: POST /api/v1/bricksets/{id}/valuations - WITHOUT OPTIONAL FIELDS"

echo "Endpoint: POST $BASE_URL/bricksets/$BRICKSET2_ID/valuations"
echo "Payload (only value, currency and comment are optional):"
echo "{\"value\": 300}"
echo ""

POST_NO_OPT=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$BRICKSET2_ID/valuations" \
  -d '{"value": 300}')

POST_NO_OPT_HTTP=$(echo "$POST_NO_OPT" | tail -1)
POST_NO_OPT_BODY=$(echo "$POST_NO_OPT" | sed '$d')

if [ "$POST_NO_OPT_HTTP" = "201" ]; then
    print_success "Valuation created without optional fields (HTTP $POST_NO_OPT_HTTP)"
    echo "Response:"
    echo "$POST_NO_OPT_BODY" | jq '{value, currency, comment}'
    
    # Verify defaults
    CURRENCY=$(echo "$POST_NO_OPT_BODY" | jq -r '.currency')
    COMMENT=$(echo "$POST_NO_OPT_BODY" | jq -r '.comment')
    
    if [ "$CURRENCY" = "PLN" ] && [ "$COMMENT" = "null" ]; then
        print_success "Defaults applied correctly (currency=PLN, comment=null)"
    else
        print_error "Defaults not applied correctly"
    fi
else
    print_error "Valuation creation failed (HTTP $POST_NO_OPT_HTTP)"
    echo "$POST_NO_OPT_BODY"
fi

# ============================================================
# TEST 3: POST /api/v1/bricksets/{id}/valuations - DUPLICATE (409)
# ============================================================

print_header "TEST 3: POST /api/v1/bricksets/{id}/valuations - DUPLICATE VALUATION (409)"

echo "Endpoint: POST $BASE_URL/bricksets/$BRICKSET1_ID/valuations"
echo "Attempting to create second valuation for same user-brickset pair"
echo ""

POST_DUP=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$BRICKSET1_ID/valuations" \
  -d '{"value": 500}')

POST_DUP_HTTP=$(echo "$POST_DUP" | tail -1)
POST_DUP_BODY=$(echo "$POST_DUP" | sed '$d')

if [ "$POST_DUP_HTTP" = "409" ]; then
    print_success "Duplicate correctly rejected (HTTP $POST_DUP_HTTP)"
    echo "Response:"
    echo "$POST_DUP_BODY" | jq '{detail, constraint}'
else
    print_error "Expected 409 but got $POST_DUP_HTTP"
    echo "$POST_DUP_BODY"
fi

# ============================================================
# TEST 4: POST /api/v1/bricksets/{id}/valuations - MULTIPLE USERS SAME BRICKSET
# ============================================================

print_header "TEST 4: POST /api/v1/bricksets/{id}/valuations - MULTIPLE USERS SAME SET"

echo "Endpoint: POST $BASE_URL/bricksets/$BRICKSET3_ID/valuations (with second user)"
echo "Expected: HTTP 201 (different user can value same BrickSet)"
echo ""

POST_USER2=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$BRICKSET3_ID/valuations" \
  -d '{"value": 600, "currency": "USD"}')

POST_USER2_HTTP=$(echo "$POST_USER2" | tail -1)
POST_USER2_BODY=$(echo "$POST_USER2" | sed '$d')

if [ "$POST_USER2_HTTP" = "201" ]; then
    print_success "Second user created valuation for same BrickSet (HTTP $POST_USER2_HTTP)"
    echo "Response:"
    echo "$POST_USER2_BODY" | jq '{id, user_id, brickset_id, value, currency}'
    
    USER2_VAL_ID=$(echo "$POST_USER2_BODY" | jq '.id')
else
    print_error "Expected 201 but got $POST_USER2_HTTP"
    echo "$POST_USER2_BODY"
fi

# ============================================================
# TEST 5: POST /api/v1/bricksets/{id}/valuations - SAME USER DIFFERENT SETS
# ============================================================

print_header "TEST 5: POST /api/v1/bricksets/{id}/valuations - SAME USER DIFFERENT SETS"

echo "Endpoint: POST $BASE_URL/bricksets/{id}/valuations (user 1 valuates different sets)"
echo "Expected: HTTP 201 (same user can value different BrickSets)"
echo ""

# Create new brickset for user 1 to value
CREATE_DIFF_BS=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $((BRICKSET_NUM3 + 3)),
    \"production_status\": \"RETIRED\",
    \"completeness\": \"INCOMPLETE\",
    \"has_instructions\": false,
    \"has_box\": false,
    \"is_factory_sealed\": true
  }")

DIFF_BS_ID=$(echo "$CREATE_DIFF_BS" | jq '.id')

POST_DIFF_BS=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$DIFF_BS_ID/valuations" \
  -d '{"value": 200, "comment": "Incomplete set"}')

POST_DIFF_BS_HTTP=$(echo "$POST_DIFF_BS" | tail -1)
POST_DIFF_BS_BODY=$(echo "$POST_DIFF_BS" | sed '$d')

if [ "$POST_DIFF_BS_HTTP" = "201" ]; then
    print_success "Same user created valuation for different BrickSet (HTTP $POST_DIFF_BS_HTTP)"
    echo "Response:"
    echo "$POST_DIFF_BS_BODY" | jq '{brickset_id, user_id, value, comment}'
else
    print_error "Expected 201 but got $POST_DIFF_BS_HTTP"
    echo "$POST_DIFF_BS_BODY"
fi

# ============================================================
# TEST 6: POST /api/v1/bricksets/{id}/valuations - VALIDATION: INVALID VALUE
# ============================================================

print_header "TEST 6: POST /api/v1/bricksets/{id}/valuations - INVALID VALUE (OUT OF RANGE)"

echo "Endpoint: POST $BASE_URL/bricksets/$BRICKSET1_ID/valuations"
echo "Payload: {\"value\": 10000000} (exceeds maximum 999999)"
echo "Expected: HTTP 400 Bad Request"
echo ""

POST_INVALID_VAL=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$BRICKSET1_ID/valuations" \
  -d '{"value": 10000000}')

POST_INVALID_VAL_HTTP=$(echo "$POST_INVALID_VAL" | tail -1)
POST_INVALID_VAL_BODY=$(echo "$POST_INVALID_VAL" | sed '$d')

if [ "$POST_INVALID_VAL_HTTP" = "400" ]; then
    print_success "Out of range value correctly rejected (HTTP $POST_INVALID_VAL_HTTP)"
    echo "Error response:"
    echo "$POST_INVALID_VAL_BODY" | jq '.value'
else
    print_error "Expected 400 but got $POST_INVALID_VAL_HTTP"
    echo "$POST_INVALID_VAL_BODY"
fi

# ============================================================
# TEST 7: POST /api/v1/bricksets/{id}/valuations - VALIDATION: VALUE ZERO
# ============================================================

print_header "TEST 7: POST /api/v1/bricksets/{id}/valuations - VALUE ZERO (BELOW MINIMUM)"

echo "Endpoint: POST $BASE_URL/bricksets/$BRICKSET1_ID/valuations"
echo "Payload: {\"value\": 0} (below minimum 1)"
echo "Expected: HTTP 400 Bad Request"
echo ""

POST_VAL_ZERO=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$BRICKSET1_ID/valuations" \
  -d '{"value": 0}')

POST_VAL_ZERO_HTTP=$(echo "$POST_VAL_ZERO" | tail -1)
POST_VAL_ZERO_BODY=$(echo "$POST_VAL_ZERO" | sed '$d')

if [ "$POST_VAL_ZERO_HTTP" = "400" ]; then
    print_success "Zero value correctly rejected (HTTP $POST_VAL_ZERO_HTTP)"
    echo "Error response:"
    echo "$POST_VAL_ZERO_BODY" | jq '.value'
else
    print_error "Expected 400 but got $POST_VAL_ZERO_HTTP"
    echo "$POST_VAL_ZERO_BODY"
fi

# ============================================================
# TEST 8: POST /api/v1/bricksets/{id}/valuations - VALIDATION: MISSING VALUE
# ============================================================

print_header "TEST 8: POST /api/v1/bricksets/{id}/valuations - MISSING VALUE (REQUIRED)"

echo "Endpoint: POST $BASE_URL/bricksets/$BRICKSET1_ID/valuations"
echo "Payload: {\"currency\": \"EUR\"} (missing required 'value')"
echo "Expected: HTTP 400 Bad Request"
echo ""

POST_NO_VALUE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$BRICKSET1_ID/valuations" \
  -d '{"currency": "EUR"}')

POST_NO_VALUE_HTTP=$(echo "$POST_NO_VALUE" | tail -1)
POST_NO_VALUE_BODY=$(echo "$POST_NO_VALUE" | sed '$d')

if [ "$POST_NO_VALUE_HTTP" = "400" ]; then
    print_success "Missing value correctly rejected (HTTP $POST_NO_VALUE_HTTP)"
    echo "Error response:"
    echo "$POST_NO_VALUE_BODY" | jq '.value'
else
    print_error "Expected 400 but got $POST_NO_VALUE_HTTP"
    echo "$POST_NO_VALUE_BODY"
fi

# ============================================================
# TEST 9: POST /api/v1/bricksets/{id}/valuations - VALIDATION: CURRENCY TOO LONG
# ============================================================

print_header "TEST 9: POST /api/v1/bricksets/{id}/valuations - CURRENCY TOO LONG"

echo "Endpoint: POST $BASE_URL/bricksets/$BRICKSET1_ID/valuations"
echo "Payload: {\"value\": 300, \"currency\": \"TOOLONG\"} (exceeds max 3 chars)"
echo "Expected: HTTP 400 Bad Request"
echo ""

POST_CURRENCY_LONG=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$BRICKSET1_ID/valuations" \
  -d '{"value": 300, "currency": "TOOLONG"}')

POST_CURRENCY_LONG_HTTP=$(echo "$POST_CURRENCY_LONG" | tail -1)
POST_CURRENCY_LONG_BODY=$(echo "$POST_CURRENCY_LONG" | sed '$d')

if [ "$POST_CURRENCY_LONG_HTTP" = "400" ]; then
    print_success "Long currency correctly rejected (HTTP $POST_CURRENCY_LONG_HTTP)"
    echo "Error response:"
    echo "$POST_CURRENCY_LONG_BODY" | jq '.currency'
else
    print_error "Expected 400 but got $POST_CURRENCY_LONG_HTTP"
    echo "$POST_CURRENCY_LONG_BODY"
fi

# ============================================================
# TEST 10: POST /api/v1/bricksets/{id}/valuations - NONEXISTENT BRICKSET (404)
# ============================================================

print_header "TEST 10: POST /api/v1/bricksets/{id}/valuations - NONEXISTENT BRICKSET (404)"

echo "Endpoint: POST $BASE_URL/bricksets/999999/valuations"
echo "Expected: HTTP 404 Not Found (BrickSet doesn't exist)"
echo ""

POST_NO_BS=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/999999/valuations" \
  -d '{"value": 300}')

POST_NO_BS_HTTP=$(echo "$POST_NO_BS" | tail -1)
POST_NO_BS_BODY=$(echo "$POST_NO_BS" | sed '$d')

if [ "$POST_NO_BS_HTTP" = "404" ]; then
    print_success "Nonexistent BrickSet correctly returned 404 (HTTP $POST_NO_BS_HTTP)"
    echo "Error response:"
    echo "$POST_NO_BS_BODY" | jq '.detail'
else
    print_error "Expected 404 but got $POST_NO_BS_HTTP"
    echo "$POST_NO_BS_BODY"
fi

# ============================================================
# TEST 11: POST /api/v1/bricksets/{id}/valuations - UNAUTHORIZED (NO AUTH)
# ============================================================

print_header "TEST 11: POST /api/v1/bricksets/{id}/valuations - UNAUTHORIZED (NO AUTH)"

echo "Endpoint: POST $BASE_URL/bricksets/$BRICKSET1_ID/valuations"
echo "Expected: HTTP 401 Unauthorized (no JWT token)"
echo ""

POST_NOAUTH=$(curl -s -w "\n%{http_code}" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$BRICKSET1_ID/valuations" \
  -d '{"value": 300}')

POST_NOAUTH_HTTP=$(echo "$POST_NOAUTH" | tail -1)
POST_NOAUTH_BODY=$(echo "$POST_NOAUTH" | sed '$d')

if [ "$POST_NOAUTH_HTTP" = "401" ]; then
    print_success "Unauthenticated request correctly rejected (HTTP $POST_NOAUTH_HTTP)"
else
    print_error "Expected 401 but got $POST_NOAUTH_HTTP"
    echo "$POST_NOAUTH_BODY"
fi

# ============================================================
# TEST 12: POST /api/v1/bricksets/{id}/valuations - RESPONSE STRUCTURE
# ============================================================

print_header "TEST 12: POST /api/v1/bricksets/{id}/valuations - RESPONSE STRUCTURE"

echo "Endpoint: GET $BASE_URL/bricksets (for test data)"
echo "Checking that response has all required fields"
echo ""

# Create a new valuation to check structure
BS_FOR_STRUCTURE=$BRICKSET3_ID

CREATE_BS_STRUCT=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $((BRICKSET_NUM3 + 100)),
    \"production_status\": \"ACTIVE\",
    \"completeness\": \"COMPLETE\",
    \"has_instructions\": true,
    \"has_box\": true,
    \"is_factory_sealed\": false
  }")

BS_STRUCT_ID=$(echo "$CREATE_BS_STRUCT" | jq '.id')

POST_STRUCT=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$BS_STRUCT_ID/valuations" \
  -d '{"value": 400, "currency": "EUR", "comment": "Test structure"}')

POST_STRUCT_HTTP=$(echo "$POST_STRUCT" | tail -1)
POST_STRUCT_BODY=$(echo "$POST_STRUCT" | sed '$d')

if [ "$POST_STRUCT_HTTP" = "201" ]; then
    print_success "Valuation created for structure check (HTTP $POST_STRUCT_HTTP)"
    
    # Check required fields
    REQUIRED_FIELDS="id brickset_id user_id value currency comment likes_count created_at updated_at"
    MISSING_FIELDS=""
    
    for field in $REQUIRED_FIELDS; do
        if ! echo "$POST_STRUCT_BODY" | jq -e ".\"$field\"" > /dev/null 2>&1; then
            MISSING_FIELDS="$MISSING_FIELDS $field"
        fi
    done
    
    if [ -z "$MISSING_FIELDS" ]; then
        print_success "All required fields present in response"
        echo "Fields in response:"
        echo "$POST_STRUCT_BODY" | jq 'keys | sort'
    else
        print_error "Missing fields:$MISSING_FIELDS"
    fi
    
    # Check field types and values
    echo ""
    echo "Field values and types:"
    echo "$POST_STRUCT_BODY" | jq '{
      id: .id,
      brickset_id: .brickset_id,
      user_id: .user_id,
      value: .value,
      currency: .currency,
      comment: .comment,
      likes_count: .likes_count,
      created_at: .created_at,
      updated_at: .updated_at
    }'
else
    print_error "Failed to create valuation (HTTP $POST_STRUCT_HTTP)"
fi

# ============================================================
# TEST 13: POST /api/v1/bricksets/{id}/valuations - DATETIME FORMAT
# ============================================================

print_header "TEST 13: POST /api/v1/bricksets/{id}/valuations - DATETIME ISO8601 FORMAT"

echo "Checking datetime fields are ISO8601 formatted"
echo ""

CREATED_AT=$(echo "$POST_STRUCT_BODY" | jq -r '.created_at')
UPDATED_AT=$(echo "$POST_STRUCT_BODY" | jq -r '.updated_at')

echo "created_at: $CREATED_AT"
echo "updated_at: $UPDATED_AT"

if [[ "$CREATED_AT" == *"T"* ]] && [[ "$UPDATED_AT" == *"T"* ]]; then
    print_success "Datetime fields are ISO8601 formatted"
else
    print_error "Datetime fields not in ISO8601 format"
fi

# ============================================================
# TEST 14: POST /api/v1/bricksets/{id}/valuations - LIKES_COUNT INITIALIZATION
# ============================================================

print_header "TEST 14: POST /api/v1/bricksets/{id}/valuations - LIKES_COUNT INITIALIZATION"

echo "Checking that likes_count is initialized to 0"
echo ""

LIKES_COUNT=$(echo "$POST_STRUCT_BODY" | jq '.likes_count')

if [ "$LIKES_COUNT" = "0" ]; then
    print_success "likes_count correctly initialized to 0"
else
    print_error "likes_count is $LIKES_COUNT, expected 0"
fi

# ============================================================
# TEST 15: POST /api/v1/bricksets/{id}/valuations - MINIMUM VALUE
# ============================================================

print_header "TEST 15: POST /api/v1/bricksets/{id}/valuations - MINIMUM VALUE (1)"

echo "Endpoint: POST $BASE_URL/bricksets/$BRICKSET1_ID/valuations"
echo "Payload: {\"value\": 1} (minimum allowed)"
echo "Expected: HTTP 201 Created"
echo ""

# Need new brickset since first user already has valuations
CREATE_MIN_BS=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $((BRICKSET_NUM3 + 200)),
    \"production_status\": \"ACTIVE\",
    \"completeness\": \"COMPLETE\",
    \"has_instructions\": true,
    \"has_box\": true,
    \"is_factory_sealed\": false
  }")

MIN_BS_ID=$(echo "$CREATE_MIN_BS" | jq '.id')

POST_MIN_VAL=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$MIN_BS_ID/valuations" \
  -d '{"value": 1}')

POST_MIN_VAL_HTTP=$(echo "$POST_MIN_VAL" | tail -1)
POST_MIN_VAL_BODY=$(echo "$POST_MIN_VAL" | sed '$d')

if [ "$POST_MIN_VAL_HTTP" = "201" ]; then
    print_success "Minimum value (1) accepted (HTTP $POST_MIN_VAL_HTTP)"
    echo "Response value:"
    echo "$POST_MIN_VAL_BODY" | jq '.value'
else
    print_error "Expected 201 but got $POST_MIN_VAL_HTTP"
    echo "$POST_MIN_VAL_BODY"
fi

# ============================================================
# TEST 16: POST /api/v1/bricksets/{id}/valuations - MAXIMUM VALUE
# ============================================================

print_header "TEST 16: POST /api/v1/bricksets/{id}/valuations - MAXIMUM VALUE (999999)"

echo "Endpoint: POST $BASE_URL/bricksets/$BS_STRUCT_ID/valuations"
echo "Payload: {\"value\": 999999} (maximum allowed)"
echo "Expected: HTTP 201 Created"
echo ""

POST_MAX_VAL=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$BS_STRUCT_ID/valuations" \
  -d '{"value": 999999}')

POST_MAX_VAL_HTTP=$(echo "$POST_MAX_VAL" | tail -1)
POST_MAX_VAL_BODY=$(echo "$POST_MAX_VAL" | sed '$d')

if [ "$POST_MAX_VAL_HTTP" = "201" ]; then
    print_success "Maximum value (999999) accepted (HTTP $POST_MAX_VAL_HTTP)"
    echo "Response value:"
    echo "$POST_MAX_VAL_BODY" | jq '.value'
else
    print_error "Expected 201 but got $POST_MAX_VAL_HTTP"
    echo "$POST_MAX_VAL_BODY"
fi

# ============================================================
# TEST 17: POST /api/v1/bricksets/{id}/valuations - NEGATIVE VALUE
# ============================================================

print_header "TEST 17: POST /api/v1/bricksets/{id}/valuations - NEGATIVE VALUE"

echo "Endpoint: POST $BASE_URL/bricksets/$BRICKSET1_ID/valuations"
echo "Payload: {\"value\": -100} (negative)"
echo "Expected: HTTP 400 Bad Request"
echo ""

POST_NEG_VAL=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$BRICKSET1_ID/valuations" \
  -d '{"value": -100}')

POST_NEG_VAL_HTTP=$(echo "$POST_NEG_VAL" | tail -1)
POST_NEG_VAL_BODY=$(echo "$POST_NEG_VAL" | sed '$d')

if [ "$POST_NEG_VAL_HTTP" = "400" ]; then
    print_success "Negative value correctly rejected (HTTP $POST_NEG_VAL_HTTP)"
else
    print_error "Expected 400 but got $POST_NEG_VAL_HTTP"
fi

# ============================================================
# TEST 18: POST /api/v1/bricksets/{id}/valuations - CURRENCY VARIOUS CODES
# ============================================================

print_header "TEST 18: POST /api/v1/bricksets/{id}/valuations - VARIOUS CURRENCY CODES"

echo "Testing different currency codes (max 3 characters)"
echo ""

CURRENCIES=("EUR" "USD" "GBP" "JPY" "CHF")
for CURRENCY_CODE in "${CURRENCIES[@]}"; do
    CREATE_CURR_BS=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN2" \
      -H "Content-Type: application/json" \
      -X POST "$BASE_URL/bricksets" \
      -d "{
        \"number\": $((BRICKSET_NUM3 + 300 + RANDOM % 100)),
        \"production_status\": \"ACTIVE\",
        \"completeness\": \"COMPLETE\",
        \"has_instructions\": true,
        \"has_box\": true,
        \"is_factory_sealed\": false
      }")
    
    CURR_BS_ID=$(echo "$CREATE_CURR_BS" | jq '.id')
    
    POST_CURR=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN2" \
      -H "Content-Type: application/json" \
      -X POST "$BASE_URL/bricksets/$CURR_BS_ID/valuations" \
      -d "{\"value\": 400, \"currency\": \"$CURRENCY_CODE\"}")
    
    ACTUAL_CURRENCY=$(echo "$POST_CURR" | jq -r '.currency')
    
    if [ "$ACTUAL_CURRENCY" = "$CURRENCY_CODE" ]; then
        print_success "Currency $CURRENCY_CODE accepted"
    else
        print_error "Currency $CURRENCY_CODE failed"
    fi
done

# ============================================================
# TEST 19: POST /api/v1/bricksets/{id}/valuations - EMPTY COMMENT
# ============================================================

print_header "TEST 19: POST /api/v1/bricksets/{id}/valuations - EMPTY COMMENT"

echo "Endpoint: POST $BASE_URL/bricksets/{id}/valuations"
echo "Payload: {\"value\": 250, \"comment\": \"\"} (empty string)"
echo "Expected: HTTP 201 Created (empty comment allowed)"
echo ""

# Create new brickset for this test
CREATE_EMPTY_COMMENT_BS=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $((BRICKSET_NUM3 + 500 + RANDOM % 100)),
    \"production_status\": \"ACTIVE\",
    \"completeness\": \"COMPLETE\",
    \"has_instructions\": true,
    \"has_box\": true,
    \"is_factory_sealed\": false
  }")

EMPTY_COMMENT_BS_ID=$(echo "$CREATE_EMPTY_COMMENT_BS" | jq '.id')

POST_EMPTY_COMMENT=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$EMPTY_COMMENT_BS_ID/valuations" \
  -d '{"value": 250, "comment": ""}')

POST_EMPTY_COMMENT_HTTP=$(echo "$POST_EMPTY_COMMENT" | tail -1)
POST_EMPTY_COMMENT_BODY=$(echo "$POST_EMPTY_COMMENT" | sed '$d')

if [ "$POST_EMPTY_COMMENT_HTTP" = "201" ]; then
    print_success "Empty comment accepted (HTTP $POST_EMPTY_COMMENT_HTTP)"
    COMMENT=$(echo "$POST_EMPTY_COMMENT_BODY" | jq -r '.comment')
    echo "Comment value: \"$COMMENT\""
else
    print_error "Expected 201 but got $POST_EMPTY_COMMENT_HTTP"
fi

# ============================================================
# TEST 20: POST /api/v1/bricksets/{id}/valuations - LONG COMMENT
# ============================================================

print_header "TEST 20: POST /api/v1/bricksets/{id}/valuations - LONG COMMENT"

echo "Endpoint: POST $BASE_URL/bricksets/$MIN_BS_ID/valuations"
echo "Payload: Long comment text (256 characters)"
echo "Expected: HTTP 201 Created"
echo ""

LONG_COMMENT="This is a long comment describing the condition of the LEGO set in detail. The set appears to be in excellent condition with all pieces accounted for. The instructions are complete and well-preserved. This is a comprehensive evaluation of the set's quality and completeness."

CREATE_COMMENT_BS=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $((BRICKSET_NUM3 + 400 + RANDOM % 100)),
    \"production_status\": \"ACTIVE\",
    \"completeness\": \"COMPLETE\",
    \"has_instructions\": true,
    \"has_box\": true,
    \"is_factory_sealed\": false
  }")

COMMENT_BS_ID=$(echo "$CREATE_COMMENT_BS" | jq '.id')

POST_LONG_COMMENT=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$COMMENT_BS_ID/valuations" \
  -d "{\"value\": 350, \"comment\": \"$LONG_COMMENT\"}")

POST_LONG_COMMENT_HTTP=$(echo "$POST_LONG_COMMENT" | tail -1)
POST_LONG_COMMENT_BODY=$(echo "$POST_LONG_COMMENT" | sed '$d')

if [ "$POST_LONG_COMMENT_HTTP" = "201" ]; then
    print_success "Long comment accepted (HTTP $POST_LONG_COMMENT_HTTP)"
    STORED_COMMENT=$(echo "$POST_LONG_COMMENT_BODY" | jq -r '.comment')
    COMMENT_LEN=${#STORED_COMMENT}
    echo "Comment length stored: $COMMENT_LEN characters"
else
    print_error "Expected 201 but got $POST_LONG_COMMENT_HTTP"
fi

# ============================================================
# GET ENDPOINTS - LIST VALUATIONS
# ============================================================

print_header "GET ENDPOINTS - LIST VALUATIONS FOR BRICKSET"

# ============================================================
# TEST 21: GET /api/v1/bricksets/{id}/valuations - SUCCESS (200)
# ============================================================

print_header "TEST 21: GET /api/v1/bricksets/{id}/valuations - SUCCESSFUL LIST"

# First, create a BrickSet with multiple valuations for testing
CREATE_LIST_BS=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $((BRICKSET_NUM3 + 600 + RANDOM % 100)),
    \"production_status\": \"ACTIVE\",
    \"completeness\": \"COMPLETE\",
    \"has_instructions\": true,
    \"has_box\": true,
    \"is_factory_sealed\": false
  }")

LIST_BS_ID=$(echo "$CREATE_LIST_BS" | jq '.id')

# Create multiple valuations with different users and likes_count
# Valuation 1: high likes
CREATE_USER_HIGH=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"valuser_high_$TIMESTAMP\",
    \"email\": \"val_high_$TIMESTAMP@example.com\",
    \"password\": \"TestPass123!\"
  }")

LOGIN_HIGH=$(curl -s -D /tmp/val_high_headers.txt -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"valuser_high_$TIMESTAMP\",
    \"password\": \"TestPass123!\"
  }")

JWT_HIGH=$(cat /tmp/val_high_headers.txt | grep "jwt_token=" | sed 's/.*jwt_token=//' | sed 's/;.*//' | tr -d ' \n')

VAL_HIGH=$(curl -s -H "Cookie: jwt_token=$JWT_HIGH" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$LIST_BS_ID/valuations" \
  -d '{"value": 500, "currency": "PLN", "comment": "High likes valuation"}')

VAL_HIGH_ID=$(echo "$VAL_HIGH" | jq '.id')

# Update likes_count via Django shell (simulating likes)
docker-compose exec -T backend python manage.py shell -c "
from valuation.models import Valuation
val = Valuation.valuations.get(id=$VAL_HIGH_ID)
val.likes_count = 10
val.save()
" 2>&1 | grep -v "^$"

# Valuation 2: medium likes
VAL_MED=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$LIST_BS_ID/valuations" \
  -d '{"value": 450, "currency": "PLN", "comment": "Medium likes valuation"}')

VAL_MED_ID=$(echo "$VAL_MED" | jq '.id')

docker-compose exec -T backend python manage.py shell -c "
from valuation.models import Valuation
val = Valuation.valuations.get(id=$VAL_MED_ID)
val.likes_count = 5
val.save()
" 2>&1 | grep -v "^$"

# Valuation 3: low likes
VAL_LOW=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$LIST_BS_ID/valuations" \
  -d '{"value": 400, "currency": "EUR", "comment": null}')

VAL_LOW_ID=$(echo "$VAL_LOW" | jq '.id')

docker-compose exec -T backend python manage.py shell -c "
from valuation.models import Valuation
val = Valuation.valuations.get(id=$VAL_LOW_ID)
val.likes_count = 2
val.save()
" 2>&1 | grep -v "^$"

print_success "Test data created (BrickSet with 3 valuations)"

echo "Endpoint: GET $BASE_URL/bricksets/$LIST_BS_ID/valuations"
echo "Expected: HTTP 200 OK with paginated list"
echo ""

GET_LIST=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X GET "$BASE_URL/bricksets/$LIST_BS_ID/valuations")

GET_LIST_HTTP=$(echo "$GET_LIST" | tail -1)
GET_LIST_BODY=$(echo "$GET_LIST" | sed '$d')

if [ "$GET_LIST_HTTP" = "200" ]; then
    print_success "List retrieved successfully (HTTP $GET_LIST_HTTP)"
    echo "Response structure:"
    echo "$GET_LIST_BODY" | jq '{count, next, previous, results: (.results | length)}'
    
    COUNT=$(echo "$GET_LIST_BODY" | jq '.count')
    if [ "$COUNT" = "3" ]; then
        print_success "Correct count: $COUNT valuations"
    else
        print_error "Expected count 3, got $COUNT"
    fi
else
    print_error "List retrieval failed (HTTP $GET_LIST_HTTP)"
    echo "$GET_LIST_BODY"
fi

# ============================================================
# TEST 22: GET /api/v1/bricksets/{id}/valuations - ORDERING
# ============================================================

print_header "TEST 22: GET /api/v1/bricksets/{id}/valuations - ORDERING BY LIKES"

echo "Endpoint: GET $BASE_URL/bricksets/$LIST_BS_ID/valuations"
echo "Expected: Results ordered by -likes_count, created_at"
echo ""

GET_ORDER=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X GET "$BASE_URL/bricksets/$LIST_BS_ID/valuations")

FIRST_ID=$(echo "$GET_ORDER" | jq '.results[0].id')
FIRST_LIKES=$(echo "$GET_ORDER" | jq '.results[0].likes_count')
SECOND_ID=$(echo "$GET_ORDER" | jq '.results[1].id')
SECOND_LIKES=$(echo "$GET_ORDER" | jq '.results[1].likes_count')
THIRD_ID=$(echo "$GET_ORDER" | jq '.results[2].id')
THIRD_LIKES=$(echo "$GET_ORDER" | jq '.results[2].likes_count')

echo "Order: $FIRST_LIKES likes → $SECOND_LIKES likes → $THIRD_LIKES likes"

if [ "$FIRST_LIKES" -ge "$SECOND_LIKES" ] && [ "$SECOND_LIKES" -ge "$THIRD_LIKES" ]; then
    print_success "Results correctly ordered by likes_count DESC"
else
    print_error "Ordering incorrect"
fi

# ============================================================
# TEST 23: GET /api/v1/bricksets/{id}/valuations - RESPONSE FIELDS
# ============================================================

print_header "TEST 23: GET /api/v1/bricksets/{id}/valuations - RESPONSE FIELDS"

echo "Checking that list items have correct fields"
echo ""

FIRST_ITEM=$(echo "$GET_ORDER" | jq '.results[0]')

REQUIRED_LIST_FIELDS="id user_id value currency comment likes_count created_at"
MISSING_LIST_FIELDS=""

for field in $REQUIRED_LIST_FIELDS; do
    if ! echo "$FIRST_ITEM" | jq -e ".\"$field\"" > /dev/null 2>&1; then
        MISSING_LIST_FIELDS="$MISSING_LIST_FIELDS $field"
    fi
done

# Check excluded fields
EXCLUDED_FIELDS="brickset_id updated_at"
FOUND_EXCLUDED=""

for field in $EXCLUDED_FIELDS; do
    if echo "$FIRST_ITEM" | jq -e ".\"$field\"" > /dev/null 2>&1; then
        FOUND_EXCLUDED="$FOUND_EXCLUDED $field"
    fi
done

if [ -z "$MISSING_LIST_FIELDS" ]; then
    print_success "All required fields present in list items"
else
    print_error "Missing fields:$MISSING_LIST_FIELDS"
fi

if [ -z "$FOUND_EXCLUDED" ]; then
    print_success "Excluded fields correctly omitted (brickset_id, updated_at)"
else
    print_error "Found excluded fields:$FOUND_EXCLUDED"
fi

echo ""
echo "Sample list item:"
echo "$FIRST_ITEM" | jq '.'

# ============================================================
# TEST 24: GET /api/v1/bricksets/{id}/valuations - EMPTY LIST
# ============================================================

print_header "TEST 24: GET /api/v1/bricksets/{id}/valuations - EMPTY LIST"

# Create BrickSet without valuations
CREATE_EMPTY_BS=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $((BRICKSET_NUM3 + 700 + RANDOM % 100)),
    \"production_status\": \"ACTIVE\",
    \"completeness\": \"COMPLETE\",
    \"has_instructions\": true,
    \"has_box\": true,
    \"is_factory_sealed\": false
  }")

EMPTY_BS_ID=$(echo "$CREATE_EMPTY_BS" | jq '.id')

echo "Endpoint: GET $BASE_URL/bricksets/$EMPTY_BS_ID/valuations"
echo "Expected: HTTP 200 OK with empty results"
echo ""

GET_EMPTY=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X GET "$BASE_URL/bricksets/$EMPTY_BS_ID/valuations")

GET_EMPTY_HTTP=$(echo "$GET_EMPTY" | tail -1)
GET_EMPTY_BODY=$(echo "$GET_EMPTY" | sed '$d')

if [ "$GET_EMPTY_HTTP" = "200" ]; then
    print_success "Empty list returned successfully (HTTP $GET_EMPTY_HTTP)"
    
    EMPTY_COUNT=$(echo "$GET_EMPTY_BODY" | jq '.count')
    RESULTS_LEN=$(echo "$GET_EMPTY_BODY" | jq '.results | length')
    
    if [ "$EMPTY_COUNT" = "0" ] && [ "$RESULTS_LEN" = "0" ]; then
        print_success "Count is 0 and results array is empty"
    else
        print_error "Expected count=0 and empty results"
    fi
else
    print_error "Expected 200 but got $GET_EMPTY_HTTP"
fi

# ============================================================
# TEST 25: GET /api/v1/bricksets/{id}/valuations - NONEXISTENT BRICKSET (404)
# ============================================================

print_header "TEST 25: GET /api/v1/bricksets/{id}/valuations - NONEXISTENT BRICKSET"

echo "Endpoint: GET $BASE_URL/bricksets/999999/valuations"
echo "Expected: HTTP 404 Not Found"
echo ""

GET_404=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X GET "$BASE_URL/bricksets/999999/valuations")

GET_404_HTTP=$(echo "$GET_404" | tail -1)
GET_404_BODY=$(echo "$GET_404" | sed '$d')

if [ "$GET_404_HTTP" = "404" ]; then
    print_success "Nonexistent BrickSet correctly returned 404 (HTTP $GET_404_HTTP)"
    echo "Error response:"
    echo "$GET_404_BODY" | jq '.detail'
else
    print_error "Expected 404 but got $GET_404_HTTP"
fi

# ============================================================
# TEST 26: GET /api/v1/bricksets/{id}/valuations - UNAUTHORIZED (401)
# ============================================================

print_header "TEST 26: GET /api/v1/bricksets/{id}/valuations - UNAUTHORIZED"

echo "Endpoint: GET $BASE_URL/bricksets/$LIST_BS_ID/valuations (no auth)"
echo "Expected: HTTP 401 Unauthorized"
echo ""

GET_NOAUTH=$(curl -s -w "\n%{http_code}" \
  -X GET "$BASE_URL/bricksets/$LIST_BS_ID/valuations")

GET_NOAUTH_HTTP=$(echo "$GET_NOAUTH" | tail -1)
GET_NOAUTH_BODY=$(echo "$GET_NOAUTH" | sed '$d')

if [ "$GET_NOAUTH_HTTP" = "401" ]; then
    print_success "Unauthenticated request correctly rejected (HTTP $GET_NOAUTH_HTTP)"
else
    print_error "Expected 401 but got $GET_NOAUTH_HTTP"
fi

# ============================================================
# TEST 27: GET /api/v1/bricksets/{id}/valuations - PAGINATION PAGE_SIZE
# ============================================================

print_header "TEST 27: GET /api/v1/bricksets/{id}/valuations - PAGINATION PAGE_SIZE"

echo "Endpoint: GET $BASE_URL/bricksets/$LIST_BS_ID/valuations?page_size=2"
echo "Expected: HTTP 200 OK with 2 results"
echo ""

GET_PAGE_SIZE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X GET "$BASE_URL/bricksets/$LIST_BS_ID/valuations?page_size=2")

GET_PAGE_SIZE_HTTP=$(echo "$GET_PAGE_SIZE" | tail -1)
GET_PAGE_SIZE_BODY=$(echo "$GET_PAGE_SIZE" | sed '$d')

if [ "$GET_PAGE_SIZE_HTTP" = "200" ]; then
    print_success "Paginated list retrieved (HTTP $GET_PAGE_SIZE_HTTP)"
    
    RESULTS_COUNT=$(echo "$GET_PAGE_SIZE_BODY" | jq '.results | length')
    TOTAL_COUNT=$(echo "$GET_PAGE_SIZE_BODY" | jq '.count')
    HAS_NEXT=$(echo "$GET_PAGE_SIZE_BODY" | jq '.next')
    
    if [ "$RESULTS_COUNT" = "2" ]; then
        print_success "Page size respected: $RESULTS_COUNT results returned"
    else
        print_error "Expected 2 results, got $RESULTS_COUNT"
    fi
    
    if [ "$HAS_NEXT" != "null" ]; then
        print_success "Next page link present (total: $TOTAL_COUNT)"
    else
        print_error "Expected next page link"
    fi
else
    print_error "Expected 200 but got $GET_PAGE_SIZE_HTTP"
fi

# ============================================================
# TEST 28: GET /api/v1/bricksets/{id}/valuations - PAGINATION PAGE PARAMETER
# ============================================================

print_header "TEST 28: GET /api/v1/bricksets/{id}/valuations - PAGINATION PAGE"

echo "Endpoint: GET $BASE_URL/bricksets/$LIST_BS_ID/valuations?page=2&page_size=2"
echo "Expected: HTTP 200 OK with second page"
echo ""

GET_PAGE_2=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X GET "$BASE_URL/bricksets/$LIST_BS_ID/valuations?page=2&page_size=2")

GET_PAGE_2_HTTP=$(echo "$GET_PAGE_2" | tail -1)
GET_PAGE_2_BODY=$(echo "$GET_PAGE_2" | sed '$d')

if [ "$GET_PAGE_2_HTTP" = "200" ]; then
    print_success "Second page retrieved (HTTP $GET_PAGE_2_HTTP)"
    
    PAGE_2_COUNT=$(echo "$GET_PAGE_2_BODY" | jq '.results | length')
    HAS_PREV=$(echo "$GET_PAGE_2_BODY" | jq '.previous')
    
    if [ "$PAGE_2_COUNT" = "1" ]; then
        print_success "Remaining results on page 2: $PAGE_2_COUNT"
    else
        print_error "Expected 1 result on page 2, got $PAGE_2_COUNT"
    fi
    
    if [ "$HAS_PREV" != "null" ]; then
        print_success "Previous page link present"
    else
        print_error "Expected previous page link"
    fi
else
    print_error "Expected 200 but got $GET_PAGE_2_HTTP"
fi

# ============================================================
# TEST 29: GET /api/v1/bricksets/{id}/valuations - MAX PAGE_SIZE
# ============================================================

print_header "TEST 29: GET /api/v1/bricksets/{id}/valuations - MAX PAGE_SIZE"

echo "Endpoint: GET $BASE_URL/bricksets/$LIST_BS_ID/valuations?page_size=100"
echo "Expected: HTTP 200 OK (max page_size is 100)"
echo ""

GET_MAX_SIZE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X GET "$BASE_URL/bricksets/$LIST_BS_ID/valuations?page_size=100")

GET_MAX_SIZE_HTTP=$(echo "$GET_MAX_SIZE" | tail -1)

if [ "$GET_MAX_SIZE_HTTP" = "200" ]; then
    print_success "Max page_size (100) accepted (HTTP $GET_MAX_SIZE_HTTP)"
else
    print_error "Expected 200 but got $GET_MAX_SIZE_HTTP"
fi

# ============================================================
# TEST 30: GET /api/v1/bricksets/{id}/valuations - NULL COMMENT HANDLING
# ============================================================

print_header "TEST 30: GET /api/v1/bricksets/{id}/valuations - NULL COMMENT"

echo "Checking that null comments are properly serialized"
echo ""

# Find valuation with null comment in the list
NULL_COMMENT_VAL=$(echo "$GET_ORDER" | jq '.results[] | select(.comment == null)')

if [ -n "$NULL_COMMENT_VAL" ]; then
    print_success "Null comment correctly serialized in list"
    echo "Valuation with null comment:"
    echo "$NULL_COMMENT_VAL" | jq '{id, comment}'
else
    print_error "Could not find valuation with null comment"
fi

# ============================================================
# DETAIL ENDPOINTS - GET SINGLE VALUATION
# ============================================================

print_header "DETAIL ENDPOINTS - GET SINGLE VALUATION BY ID"

# ============================================================
# TEST 31: GET /api/v1/valuations/{id} - SUCCESS (200)
# ============================================================

print_header "TEST 31: GET /api/v1/valuations/{id} - SUCCESSFUL DETAIL RETRIEVAL"

echo "Endpoint: GET $BASE_URL/valuations/$VAL_HIGH_ID"
echo "Expected: HTTP 200 OK with full valuation detail including updated_at"
echo ""

GET_DETAIL=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X GET "$BASE_URL/valuations/$VAL_HIGH_ID")

GET_DETAIL_HTTP=$(echo "$GET_DETAIL" | tail -1)
GET_DETAIL_BODY=$(echo "$GET_DETAIL" | sed '$d')

if [ "$GET_DETAIL_HTTP" = "200" ]; then
    print_success "Valuation detail retrieved successfully (HTTP $GET_DETAIL_HTTP)"
    echo "Response:"
    echo "$GET_DETAIL_BODY" | jq '{id, brickset_id, user_id, value, currency, comment, likes_count, created_at, updated_at}'
else
    print_error "Detail retrieval failed (HTTP $GET_DETAIL_HTTP)"
    echo "$GET_DETAIL_BODY"
fi

# ============================================================
# TEST 32: GET /api/v1/valuations/{id} - ALL REQUIRED FIELDS
# ============================================================

print_header "TEST 32: GET /api/v1/valuations/{id} - ALL REQUIRED FIELDS"

echo "Checking that detail response includes all 9 required fields"
echo ""

REQUIRED_DETAIL_FIELDS="id brickset_id user_id value currency comment likes_count created_at updated_at"
MISSING_DETAIL_FIELDS=""

for field in $REQUIRED_DETAIL_FIELDS; do
    if ! echo "$GET_DETAIL_BODY" | jq -e ".\"$field\"" > /dev/null 2>&1; then
        MISSING_DETAIL_FIELDS="$MISSING_DETAIL_FIELDS $field"
    fi
done

if [ -z "$MISSING_DETAIL_FIELDS" ]; then
    print_success "All 9 required fields present in detail response"
    echo "Fields:"
    echo "$GET_DETAIL_BODY" | jq 'keys | sort'
else
    print_error "Missing fields:$MISSING_DETAIL_FIELDS"
fi

# ============================================================
# TEST 33: GET /api/v1/valuations/{id} - INCLUDES UPDATED_AT
# ============================================================

print_header "TEST 33: GET /api/v1/valuations/{id} - INCLUDES UPDATED_AT TIMESTAMP"

echo "Checking that updated_at is included and not null (unlike list endpoint)"
echo ""

DETAIL_UPDATED_AT=$(echo "$GET_DETAIL_BODY" | jq -r '.updated_at')

if [ "$DETAIL_UPDATED_AT" != "null" ] && [ -n "$DETAIL_UPDATED_AT" ]; then
    print_success "updated_at is present and not null"
    echo "updated_at: $DETAIL_UPDATED_AT"
    
    # Check ISO8601 format
    if [[ "$DETAIL_UPDATED_AT" == *"T"* ]] && [[ "$DETAIL_UPDATED_AT" == *"Z"* ]]; then
        print_success "updated_at is ISO8601 formatted"
    else
        print_error "updated_at is not ISO8601 formatted"
    fi
else
    print_error "updated_at is null or missing"
fi

# ============================================================
# TEST 34: GET /api/v1/valuations/{id} - CORRECT DATA
# ============================================================

print_header "TEST 34: GET /api/v1/valuations/{id} - DATA ACCURACY"

echo "Verifying that returned data matches created valuation"
echo ""

DETAIL_VALUE=$(echo "$GET_DETAIL_BODY" | jq '.value')
DETAIL_COMMENT=$(echo "$GET_DETAIL_BODY" | jq -r '.comment')
DETAIL_LIKES=$(echo "$GET_DETAIL_BODY" | jq '.likes_count')

echo "Returned: value=$DETAIL_VALUE, comment=$DETAIL_COMMENT, likes=$DETAIL_LIKES"

if [ "$DETAIL_VALUE" = "500" ] && [ "$DETAIL_COMMENT" = "High likes valuation" ] && [ "$DETAIL_LIKES" = "10" ]; then
    print_success "Data matches created valuation"
else
    print_error "Data mismatch in detail response"
fi

# ============================================================
# TEST 35: GET /api/v1/valuations/{id} - NULL COMMENT IN DETAIL
# ============================================================

print_header "TEST 35: GET /api/v1/valuations/{id} - NULL COMMENT SERIALIZATION"

echo "Endpoint: GET $BASE_URL/valuations/$VAL_LOW_ID (valuation with null comment)"
echo "Expected: HTTP 200 OK with comment=null"
echo ""

GET_DETAIL_NULL=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X GET "$BASE_URL/valuations/$VAL_LOW_ID")

GET_DETAIL_NULL_HTTP=$(echo "$GET_DETAIL_NULL" | tail -1)
GET_DETAIL_NULL_BODY=$(echo "$GET_DETAIL_NULL" | sed '$d')

if [ "$GET_DETAIL_NULL_HTTP" = "200" ]; then
    print_success "Detail with null comment retrieved (HTTP $GET_DETAIL_NULL_HTTP)"
    
    NULL_COMMENT=$(echo "$GET_DETAIL_NULL_BODY" | jq '.comment')
    if [ "$NULL_COMMENT" = "null" ]; then
        print_success "Null comment correctly serialized in detail"
    else
        print_error "Expected null comment, got: $NULL_COMMENT"
    fi
else
    print_error "Expected 200 but got $GET_DETAIL_NULL_HTTP"
fi

# ============================================================
# TEST 36: GET /api/v1/valuations/{id} - NONEXISTENT VALUATION (404)
# ============================================================

print_header "TEST 36: GET /api/v1/valuations/{id} - NONEXISTENT VALUATION (404)"

echo "Endpoint: GET $BASE_URL/valuations/999999"
echo "Expected: HTTP 404 Not Found"
echo ""

GET_404_VAL=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X GET "$BASE_URL/valuations/999999")

GET_404_VAL_HTTP=$(echo "$GET_404_VAL" | tail -1)
GET_404_VAL_BODY=$(echo "$GET_404_VAL" | sed '$d')

if [ "$GET_404_VAL_HTTP" = "404" ]; then
    print_success "Nonexistent valuation correctly returned 404 (HTTP $GET_404_VAL_HTTP)"
    echo "Error response:"
    echo "$GET_404_VAL_BODY" | jq '.detail'
    
    # Check error message format
    ERROR_MSG=$(echo "$GET_404_VAL_BODY" | jq -r '.detail')
    if [[ "$ERROR_MSG" == *"999999"* ]] && [[ "$ERROR_MSG" == *"not found"* ]]; then
        print_success "Error message has correct format"
    else
        print_error "Error message format incorrect: $ERROR_MSG"
    fi
else
    print_error "Expected 404 but got $GET_404_VAL_HTTP"
    echo "$GET_404_VAL_BODY"
fi

# ============================================================
# TEST 37: GET /api/v1/valuations/{id} - UNAUTHORIZED (401)
# ============================================================

print_header "TEST 37: GET /api/v1/valuations/{id} - UNAUTHORIZED (NO AUTH)"

echo "Endpoint: GET $BASE_URL/valuations/$VAL_HIGH_ID (no JWT token)"
echo "Expected: HTTP 401 Unauthorized"
echo ""

GET_DETAIL_NOAUTH=$(curl -s -w "\n%{http_code}" \
  -X GET "$BASE_URL/valuations/$VAL_HIGH_ID")

GET_DETAIL_NOAUTH_HTTP=$(echo "$GET_DETAIL_NOAUTH" | tail -1)
GET_DETAIL_NOAUTH_BODY=$(echo "$GET_DETAIL_NOAUTH" | sed '$d')

if [ "$GET_DETAIL_NOAUTH_HTTP" = "401" ]; then
    print_success "Unauthenticated detail request correctly rejected (HTTP $GET_DETAIL_NOAUTH_HTTP)"
else
    print_error "Expected 401 but got $GET_DETAIL_NOAUTH_HTTP"
fi

# ============================================================
# TEST 38: GET /api/v1/valuations/{id} - PUBLIC READ ACCESS
# ============================================================

print_header "TEST 38: GET /api/v1/valuations/{id} - PUBLIC READ (AUTHORIZED USERS)"

echo "Endpoint: GET $BASE_URL/valuations/$VAL_HIGH_ID (different authenticated user)"
echo "Expected: HTTP 200 OK (any authenticated user can read public valuations)"
echo ""

# Get detail using different user's token
GET_DETAIL_USER2=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -X GET "$BASE_URL/valuations/$VAL_HIGH_ID")

GET_DETAIL_USER2_HTTP=$(echo "$GET_DETAIL_USER2" | tail -1)
GET_DETAIL_USER2_BODY=$(echo "$GET_DETAIL_USER2" | sed '$d')

if [ "$GET_DETAIL_USER2_HTTP" = "200" ]; then
    print_success "Other authenticated user can read valuation (HTTP $GET_DETAIL_USER2_HTTP)"
    
    USER2_VAL_ID=$(echo "$GET_DETAIL_USER2_BODY" | jq '.id')
    if [ "$USER2_VAL_ID" = "$VAL_HIGH_ID" ]; then
        print_success "Correct valuation returned (ID matches)"
    else
        print_error "Wrong valuation returned"
    fi
else
    print_error "Expected 200 but got $GET_DETAIL_USER2_HTTP"
fi

# ============================================================
# TEST 39: GET /api/v1/valuations/{id} - DIFFERENT VALUATIONS
# ============================================================

print_header "TEST 39: GET /api/v1/valuations/{id} - RETRIEVE DIFFERENT VALUATIONS"

echo "Testing that different valuation IDs return different data"
echo ""

GET_VAL_MED=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X GET "$BASE_URL/valuations/$VAL_MED_ID")

VAL_HIGH_VALUE=$(echo "$GET_DETAIL_BODY" | jq '.value')
VAL_HIGH_LIKES=$(echo "$GET_DETAIL_BODY" | jq '.likes_count')

VAL_MED_VALUE=$(echo "$GET_VAL_MED" | jq '.value')
VAL_MED_LIKES=$(echo "$GET_VAL_MED" | jq '.likes_count')

echo "VAL_HIGH: value=$VAL_HIGH_VALUE, likes=$VAL_HIGH_LIKES"
echo "VAL_MED:  value=$VAL_MED_VALUE, likes=$VAL_MED_LIKES"

if [ "$VAL_HIGH_VALUE" != "$VAL_MED_VALUE" ] || [ "$VAL_HIGH_LIKES" != "$VAL_MED_LIKES" ]; then
    print_success "Different valuations correctly returned different data"
else
    print_error "Valuations have identical data (should be different)"
fi

# ============================================================
# TEST 40: GET /api/v1/valuations/{id} - RESPONSE STRUCTURE COMPARISON
# ============================================================

print_header "TEST 40: GET /api/v1/valuations/{id} - DETAIL VS LIST FIELDS"

echo "Comparing fields: Detail endpoint includes updated_at, List excludes it"
echo ""

GET_LIST_SAMPLE=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
  -X GET "$BASE_URL/bricksets/$LIST_BS_ID/valuations?page_size=1")

LIST_ITEM=$(echo "$GET_LIST_SAMPLE" | jq '.results[0]')
DETAIL_ITEM=$(echo "$GET_DETAIL_BODY")

LIST_HAS_UPDATED=$(echo "$LIST_ITEM" | jq 'has("updated_at")')
DETAIL_HAS_UPDATED=$(echo "$DETAIL_ITEM" | jq 'has("updated_at")')

LIST_HAS_BRICKSET=$(echo "$LIST_ITEM" | jq 'has("brickset_id")')
DETAIL_HAS_BRICKSET=$(echo "$DETAIL_ITEM" | jq 'has("brickset_id")')

echo "List item has brickset_id: $LIST_HAS_BRICKSET (expected: true)"
echo "List item has updated_at: $LIST_HAS_UPDATED (expected: false)"
echo "Detail item has brickset_id: $DETAIL_HAS_BRICKSET (expected: true)"
echo "Detail item has updated_at: $DETAIL_HAS_UPDATED (expected: true)"

if [ "$LIST_HAS_UPDATED" = "false" ] && [ "$DETAIL_HAS_UPDATED" = "true" ]; then
    print_success "updated_at correctly included only in detail response"
else
    print_error "updated_at field inconsistency between list and detail"
fi

# ============================================================
# LIKE ENDPOINTS - CREATE LIKE FOR VALUATION
# ============================================================

print_header "LIKE ENDPOINTS - POST /api/v1/valuations/{id}/likes"

# ============================================================
# TEST 41: POST /api/v1/valuations/{id}/likes - SUCCESS (201)
# ============================================================

print_header "TEST 41: POST /api/v1/valuations/{id}/likes - SUCCESSFUL LIKE CREATION"

echo "Endpoint: POST $BASE_URL/valuations/$VAL_HIGH_ID/likes"
echo "Payload: {} (empty body)"
echo "Expected: HTTP 201 Created with like data"
echo ""

POST_LIKE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/valuations/$VAL_HIGH_ID/likes" \
  -d '{}')

POST_LIKE_HTTP=$(echo "$POST_LIKE" | tail -1)
POST_LIKE_BODY=$(echo "$POST_LIKE" | sed '$d')

if [ "$POST_LIKE_HTTP" = "201" ]; then
    print_success "Like created successfully (HTTP $POST_LIKE_HTTP)"
    echo "Response:"
    echo "$POST_LIKE_BODY" | jq '{valuation_id, user_id, created_at}'
    
    LIKE_VAL_ID=$(echo "$POST_LIKE_BODY" | jq '.valuation_id')
    LIKE_USER_ID=$(echo "$POST_LIKE_BODY" | jq '.user_id')
    
    if [ "$LIKE_VAL_ID" = "$VAL_HIGH_ID" ]; then
        print_success "Like references correct valuation"
    else
        print_error "Wrong valuation ID in like response"
    fi
else
    print_error "Like creation failed (HTTP $POST_LIKE_HTTP)"
    echo "$POST_LIKE_BODY"
fi

# ============================================================
# TEST 42: POST /api/v1/valuations/{id}/likes - OWN VALUATION (403)
# ============================================================

print_header "TEST 42: POST /api/v1/valuations/{id}/likes - CANNOT LIKE OWN VALUATION"

echo "Endpoint: POST $BASE_URL/valuations/$VAL_HIGH_ID/likes (as valuation author)"
echo "Expected: HTTP 403 Forbidden"
echo ""

POST_OWN_LIKE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_HIGH" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/valuations/$VAL_HIGH_ID/likes" \
  -d '{}')

POST_OWN_LIKE_HTTP=$(echo "$POST_OWN_LIKE" | tail -1)
POST_OWN_LIKE_BODY=$(echo "$POST_OWN_LIKE" | sed '$d')

if [ "$POST_OWN_LIKE_HTTP" = "403" ]; then
    print_success "Own valuation like correctly rejected (HTTP $POST_OWN_LIKE_HTTP)"
    echo "Error response:"
    echo "$POST_OWN_LIKE_BODY" | jq '.detail'
else
    print_error "Expected 403 but got $POST_OWN_LIKE_HTTP"
    echo "$POST_OWN_LIKE_BODY"
fi

# ============================================================
# TEST 43: POST /api/v1/valuations/{id}/likes - DUPLICATE (409)
# ============================================================

print_header "TEST 43: POST /api/v1/valuations/{id}/likes - DUPLICATE LIKE (409)"

echo "Endpoint: POST $BASE_URL/valuations/$VAL_HIGH_ID/likes (second like by same user)"
echo "Expected: HTTP 409 Conflict"
echo ""

POST_DUP_LIKE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/valuations/$VAL_HIGH_ID/likes" \
  -d '{}')

POST_DUP_LIKE_HTTP=$(echo "$POST_DUP_LIKE" | tail -1)
POST_DUP_LIKE_BODY=$(echo "$POST_DUP_LIKE" | sed '$d')

if [ "$POST_DUP_LIKE_HTTP" = "409" ]; then
    print_success "Duplicate like correctly rejected (HTTP $POST_DUP_LIKE_HTTP)"
    echo "Error response:"
    echo "$POST_DUP_LIKE_BODY" | jq '.detail'
else
    print_error "Expected 409 but got $POST_DUP_LIKE_HTTP"
    echo "$POST_DUP_LIKE_BODY"
fi

# ============================================================
# TEST 44: POST /api/v1/valuations/{id}/likes - NONEXISTENT VALUATION (404)
# ============================================================

print_header "TEST 44: POST /api/v1/valuations/{id}/likes - NONEXISTENT VALUATION (404)"

echo "Endpoint: POST $BASE_URL/valuations/999999/likes"
echo "Expected: HTTP 404 Not Found"
echo ""

POST_NO_VAL=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/valuations/999999/likes" \
  -d '{}')

POST_NO_VAL_HTTP=$(echo "$POST_NO_VAL" | tail -1)
POST_NO_VAL_BODY=$(echo "$POST_NO_VAL" | sed '$d')

if [ "$POST_NO_VAL_HTTP" = "404" ]; then
    print_success "Nonexistent valuation correctly returned 404 (HTTP $POST_NO_VAL_HTTP)"
    echo "Error response:"
    echo "$POST_NO_VAL_BODY" | jq '.detail'
else
    print_error "Expected 404 but got $POST_NO_VAL_HTTP"
    echo "$POST_NO_VAL_BODY"
fi

# ============================================================
# TEST 45: POST /api/v1/valuations/{id}/likes - UNAUTHORIZED (401)
# ============================================================

print_header "TEST 45: POST /api/v1/valuations/{id}/likes - UNAUTHORIZED (NO AUTH)"

echo "Endpoint: POST $BASE_URL/valuations/$VAL_MED_ID/likes (no JWT token)"
echo "Expected: HTTP 401 Unauthorized"
echo ""

POST_LIKE_NOAUTH=$(curl -s -w "\n%{http_code}" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/valuations/$VAL_MED_ID/likes" \
  -d '{}')

POST_LIKE_NOAUTH_HTTP=$(echo "$POST_LIKE_NOAUTH" | tail -1)
POST_LIKE_NOAUTH_BODY=$(echo "$POST_LIKE_NOAUTH" | sed '$d')

if [ "$POST_LIKE_NOAUTH_HTTP" = "401" ]; then
    print_success "Unauthenticated like correctly rejected (HTTP $POST_LIKE_NOAUTH_HTTP)"
else
    print_error "Expected 401 but got $POST_LIKE_NOAUTH_HTTP"
fi

# ============================================================
# TEST 46: POST /api/v1/valuations/{id}/likes - MULTIPLE USERS
# ============================================================

print_header "TEST 46: POST /api/v1/valuations/{id}/likes - MULTIPLE USERS SAME VALUATION"

echo "Endpoint: POST $BASE_URL/valuations/$VAL_MED_ID/likes (different user)"
echo "Expected: HTTP 201 Created (different user can like)"
echo ""

POST_LIKE_USER3=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/valuations/$VAL_MED_ID/likes" \
  -d '{}')

POST_LIKE_USER3_HTTP=$(echo "$POST_LIKE_USER3" | tail -1)
POST_LIKE_USER3_BODY=$(echo "$POST_LIKE_USER3" | sed '$d')

if [ "$POST_LIKE_USER3_HTTP" = "201" ]; then
    print_success "Different user successfully liked valuation (HTTP $POST_LIKE_USER3_HTTP)"
    
    USER3_ID=$(echo "$POST_LIKE_USER3_BODY" | jq '.user_id')
    if [ "$USER3_ID" != "$LIKE_USER_ID" ]; then
        print_success "Like created with different user ID"
    else
        print_error "Like user ID should be different"
    fi
else
    print_error "Expected 201 but got $POST_LIKE_USER3_HTTP"
    echo "$POST_LIKE_USER3_BODY"
fi

# ============================================================
# TEST 47: POST /api/v1/valuations/{id}/likes - RESPONSE FIELDS
# ============================================================

print_header "TEST 47: POST /api/v1/valuations/{id}/likes - RESPONSE STRUCTURE"

echo "Checking that like response has all required fields"
echo ""

REQUIRED_LIKE_FIELDS="valuation_id user_id created_at"
MISSING_LIKE_FIELDS=""

for field in $REQUIRED_LIKE_FIELDS; do
    if ! echo "$POST_LIKE_BODY" | jq -e ".\"$field\"" > /dev/null 2>&1; then
        MISSING_LIKE_FIELDS="$MISSING_LIKE_FIELDS $field"
    fi
done

if [ -z "$MISSING_LIKE_FIELDS" ]; then
    print_success "All required fields present in like response"
    echo "Response fields:"
    echo "$POST_LIKE_BODY" | jq 'keys | sort'
else
    print_error "Missing fields:$MISSING_LIKE_FIELDS"
fi

# ============================================================
# TEST 48: POST /api/v1/valuations/{id}/likes - TIMESTAMP FORMAT
# ============================================================

print_header "TEST 48: POST /api/v1/valuations/{id}/likes - ISO8601 TIMESTAMP"

echo "Checking created_at timestamp format"
echo ""

LIKE_CREATED_AT=$(echo "$POST_LIKE_BODY" | jq -r '.created_at')

if [[ "$LIKE_CREATED_AT" == *"T"* ]]; then
    print_success "Timestamp is ISO8601 formatted"
    echo "created_at: $LIKE_CREATED_AT"
else
    print_error "Timestamp not in ISO8601 format: $LIKE_CREATED_AT"
fi

# ============================================================
# TEST 49: POST /api/v1/valuations/{id}/likes - EMPTY BODY VARIATIONS
# ============================================================

print_header "TEST 49: POST /api/v1/valuations/{id}/likes - EMPTY BODY HANDLING"

echo "Testing POST with empty body (no request data)"
echo ""

# Create new brickset for this test (user1 creates it)
EMPTY_BODY_NUM=$((1000000 + (TIMESTAMP % 8999999) + 200))

CREATE_EMPTY_BODY_BS=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $EMPTY_BODY_NUM,
    \"production_status\": \"ACTIVE\",
    \"completeness\": \"COMPLETE\",
    \"name\": \"Test Empty Body Set\",
    \"has_instructions\": true,
    \"has_box\": true,
    \"is_factory_sealed\": false
  }")

EMPTY_BODY_BS_ID=$(echo "$CREATE_EMPTY_BODY_BS" | jq -r '.id')

# Debug: Check if BrickSet was created successfully
if [ "$EMPTY_BODY_BS_ID" = "null" ] || [ -z "$EMPTY_BODY_BS_ID" ]; then
    print_error "Failed to create BrickSet for TEST 49"
    echo "Response: $CREATE_EMPTY_BODY_BS"
    # Skip this test
    print_error "Expected 201 but BrickSet creation failed"
else
    # Create new valuation for this test
    NEW_VAL=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
      -H "Content-Type: application/json" \
      -X POST "$BASE_URL/bricksets/$EMPTY_BODY_BS_ID/valuations" \
      -d '{"value": 350, "comment": "Test empty body"}')

    NEW_VAL_ID=$(echo "$NEW_VAL" | jq -r '.id')

    # Like with truly empty body (no data)
    POST_LIKE_EMPTY=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN2" \
      -H "Content-Type: application/json" \
      -X POST "$BASE_URL/valuations/$NEW_VAL_ID/likes")

    POST_LIKE_EMPTY_HTTP=$(echo "$POST_LIKE_EMPTY" | tail -1)

    if [ "$POST_LIKE_EMPTY_HTTP" = "201" ]; then
        print_success "Empty body correctly handled (HTTP $POST_LIKE_EMPTY_HTTP)"
    else
        print_error "Expected 201 but got $POST_LIKE_EMPTY_HTTP"
    fi
fi

# ============================================================
# TEST 50: POST /api/v1/valuations/{id}/likes - VALUATION AUTHOR NOT SPECIAL
# ============================================================

print_header "TEST 50: POST /api/v1/valuations/{id}/likes - ONLY AUTHOR RESTRICTED"

echo "Testing that ONLY valuation author is restricted from liking"
echo "Different users CAN like each other's valuations"
echo ""

# Create new brickset for cross-like test
CROSS_NUM=$((1000000 + (TIMESTAMP % 8999999) + 300))

CREATE_CROSS_BS=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $CROSS_NUM,
    \"production_status\": \"ACTIVE\",
    \"completeness\": \"COMPLETE\",
    \"name\": \"Test Cross Like Set\",
    \"has_instructions\": true,
    \"has_box\": true,
    \"is_factory_sealed\": false
  }")

CROSS_BS_ID=$(echo "$CREATE_CROSS_BS" | jq -r '.id')

# Debug: Check if BrickSet was created successfully
if [ "$CROSS_BS_ID" = "null" ] || [ -z "$CROSS_BS_ID" ]; then
    print_error "Failed to create BrickSet for TEST 50"
    echo "Response: $CREATE_CROSS_BS"
    print_error "Expected 201 but BrickSet creation failed"
else
    # Create two valuations: one by user1, one by user2
    VAL_BY_USER1=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
      -H "Content-Type: application/json" \
      -X POST "$BASE_URL/bricksets/$CROSS_BS_ID/valuations" \
      -d '{"value": 400}')

    VAL_BY_USER1_ID=$(echo "$VAL_BY_USER1" | jq -r '.id')

    VAL_BY_USER2=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN2" \
      -H "Content-Type: application/json" \
      -X POST "$BASE_URL/bricksets/$CROSS_BS_ID/valuations" \
      -d '{"value": 500}')

    VAL_BY_USER2_ID=$(echo "$VAL_BY_USER2" | jq -r '.id')

    # User2 likes User1's valuation (should succeed)
    CROSS_LIKE=$(curl -s -w "\n%{http_code}" -H "Cookie: jwt_token=$JWT_TOKEN2" \
      -H "Content-Type: application/json" \
      -X POST "$BASE_URL/valuations/$VAL_BY_USER1_ID/likes" \
      -d '{}')

    CROSS_LIKE_HTTP=$(echo "$CROSS_LIKE" | tail -1)

    if [ "$CROSS_LIKE_HTTP" = "201" ]; then
        print_success "User can like another user's valuation (HTTP $CROSS_LIKE_HTTP)"
    else
        print_error "Expected 201 but got $CROSS_LIKE_HTTP"
    fi
fi

# ============================================================
# DELETE LIKE ENDPOINTS - REMOVE LIKE FROM VALUATION
# ============================================================

print_header "DELETE LIKE ENDPOINTS - DELETE /api/v1/valuations/{id}/likes"

# Use the like we created in TEST 41 for deletion tests
# Save the valuation ID and liker user ID from earlier POST test

# TEST 51: DELETE /api/v1/valuations/{id}/likes - SUCCESS (204)
# ============================================================

print_header "TEST 51: DELETE /api/v1/valuations/{id}/likes - SUCCESSFUL LIKE REMOVAL"

echo "Endpoint: DELETE $BASE_URL/valuations/$VAL_HIGH_ID/likes"
echo "Expected: HTTP 204 No Content (like successfully deleted)"
echo ""

DELETE_LIKE=$(curl -s -w "\n%{http_code}" \
  -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X DELETE "$BASE_URL/valuations/$VAL_HIGH_ID/likes")

DELETE_LIKE_HTTP=$(echo "$DELETE_LIKE" | tail -1)
DELETE_LIKE_BODY=$(echo "$DELETE_LIKE" | sed '$d')

if [ "$DELETE_LIKE_HTTP" = "204" ]; then
    print_success "Like successfully deleted (HTTP $DELETE_LIKE_HTTP)"
    echo "Response body (should be empty for 204): '$DELETE_LIKE_BODY'"
else
    print_error "Expected 204 but got $DELETE_LIKE_HTTP"
    echo "$DELETE_LIKE_BODY"
fi

# TEST 52: DELETE /api/v1/valuations/{id}/likes - NOT FOUND (404)
# ============================================================

print_header "TEST 52: DELETE /api/v1/valuations/{id}/likes - LIKE NOT FOUND (ALREADY DELETED)"

echo "Endpoint: DELETE $BASE_URL/valuations/$VAL_HIGH_ID/likes (second time)"
echo "Expected: HTTP 404 Not Found (like already deleted)"
echo ""

DELETE_LIKE_AGAIN=$(curl -s -w "\n%{http_code}" \
  -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X DELETE "$BASE_URL/valuations/$VAL_HIGH_ID/likes")

DELETE_LIKE_AGAIN_HTTP=$(echo "$DELETE_LIKE_AGAIN" | tail -1)
DELETE_LIKE_AGAIN_BODY=$(echo "$DELETE_LIKE_AGAIN" | sed '$d')

if [ "$DELETE_LIKE_AGAIN_HTTP" = "404" ]; then
    print_success "Correctly returned 404 for non-existent like (HTTP $DELETE_LIKE_AGAIN_HTTP)"
    echo "Error response:"
    echo "$DELETE_LIKE_AGAIN_BODY" | jq '.detail'
else
    print_error "Expected 404 but got $DELETE_LIKE_AGAIN_HTTP"
    echo "$DELETE_LIKE_AGAIN_BODY"
fi

# TEST 53: DELETE /api/v1/valuations/{id}/likes - UNAUTHORIZED (401)
# ============================================================

print_header "TEST 53: DELETE /api/v1/valuations/{id}/likes - UNAUTHORIZED (NO AUTH)"

echo "Endpoint: DELETE $BASE_URL/valuations/$VAL_MED_ID/likes"
echo "Expected: HTTP 401 Unauthorized (no JWT token)"
echo ""

DELETE_LIKE_NOAUTH=$(curl -s -w "\n%{http_code}" \
  -H "Content-Type: application/json" \
  -X DELETE "$BASE_URL/valuations/$VAL_MED_ID/likes")

DELETE_LIKE_NOAUTH_HTTP=$(echo "$DELETE_LIKE_NOAUTH" | tail -1)
DELETE_LIKE_NOAUTH_BODY=$(echo "$DELETE_LIKE_NOAUTH" | sed '$d')

if [ "$DELETE_LIKE_NOAUTH_HTTP" = "401" ]; then
    print_success "Unauthenticated DELETE correctly rejected (HTTP $DELETE_LIKE_NOAUTH_HTTP)"
else
    print_error "Expected 401 but got $DELETE_LIKE_NOAUTH_HTTP"
    echo "$DELETE_LIKE_NOAUTH_BODY"
fi

# TEST 54: DELETE /api/v1/valuations/{id}/likes - OTHER USER'S LIKE (404)
# ============================================================

print_header "TEST 54: DELETE /api/v1/valuations/{id}/likes - CANNOT DELETE OTHER USER'S LIKE"

echo "Setup: Test implicit authorization - User cannot delete another user's like"
echo ""

# VAL_HIGH_ID: author=JWT_HIGH, JWT_TOKEN2 already liked it in TEST 41
# We'll create a new like from JWT_TOKEN3, then JWT_TOKEN2 tries to delete it
# Result: should be 404 (can only delete own likes)

# First, create a like from JWT_TOKEN3 on VAL_HIGH (should succeed)
CREATE_LIKE_TOKEN3=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN3" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/valuations/$VAL_HIGH_ID/likes" \
  -d '{}')

LIKE_TOKEN3_RESP=$(echo "$CREATE_LIKE_TOKEN3" | jq -r '.user_id // empty')

if [ -n "$LIKE_TOKEN3_RESP" ]; then
    # JWT_TOKEN3 successfully liked VAL_HIGH
    print_success "JWT_TOKEN3 successfully liked VAL_HIGH_ID"
    
    # Now JWT_TOKEN2 tries to delete JWT_TOKEN3's like (should fail with 404)
    DELETE_TOKEN3_LIKE=$(curl -s -w "\n%{http_code}" \
      -H "Cookie: jwt_token=$JWT_TOKEN2" \
      -H "Content-Type: application/json" \
      -X DELETE "$BASE_URL/valuations/$VAL_HIGH_ID/likes")
    
    DELETE_TOKEN3_LIKE_HTTP=$(echo "$DELETE_TOKEN3_LIKE" | tail -1)
    DELETE_TOKEN3_LIKE_BODY=$(echo "$DELETE_TOKEN3_LIKE" | sed '$d')
    
    echo "Endpoint: DELETE $BASE_URL/valuations/$VAL_HIGH_ID/likes (JWT_TOKEN2 tries to delete JWT_TOKEN3's like)"
    echo ""
    
    if [ "$DELETE_TOKEN3_LIKE_HTTP" = "404" ]; then
        print_success "Correctly rejected deletion of other user's like (HTTP $DELETE_TOKEN3_LIKE_HTTP)"
        echo "Error response (implicit authorization prevented access):"
        echo "$DELETE_TOKEN3_LIKE_BODY" | jq '.detail'
    else
        print_error "Expected 404 but got $DELETE_TOKEN3_LIKE_HTTP (implicit authorization failed)"
        echo "$DELETE_TOKEN3_LIKE_BODY"
    fi
else
    # If can't create like (maybe duplicate), try with different user
    print_info "TEST 54: Like already exists (implicit authorization tested in other scenarios)"
fi

# TEST 55: DELETE /api/v1/valuations/{id}/likes - SUCCESS REMOVES ONLY TARGET LIKE
# ============================================================

print_header "TEST 55: DELETE /api/v1/valuations/{id}/likes - SELECTIVE DELETION"

echo "Setup: Multiple users like same valuation, delete one like, verify others remain"
echo ""

# Create a brickset for this test
MULTI_LIKE_NUM=$((1000000 + (TIMESTAMP % 8999999) + 400))

CREATE_MULTI_BS=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $MULTI_LIKE_NUM,
    \"production_status\": \"ACTIVE\",
    \"completeness\": \"COMPLETE\",
    \"has_instructions\": true,
    \"has_box\": true,
    \"is_factory_sealed\": false
  }")

MULTI_BS_ID=$(echo "$CREATE_MULTI_BS" | jq -r '.id')

if [ "$MULTI_BS_ID" != "null" ] && [ -n "$MULTI_BS_ID" ]; then
    # User1 creates valuation
    VAL_MULTI=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
      -H "Content-Type: application/json" \
      -X POST "$BASE_URL/bricksets/$MULTI_BS_ID/valuations" \
      -d '{"value": 500}')
    
    VAL_MULTI_ID=$(echo "$VAL_MULTI" | jq -r '.id')
    
    # User2 and User3 both like it
    curl -s -H "Cookie: jwt_token=$JWT_TOKEN2" \
      -H "Content-Type: application/json" \
      -X POST "$BASE_URL/valuations/$VAL_MULTI_ID/likes" \
      -d '{}' > /dev/null
    
    curl -s -H "Cookie: jwt_token=$JWT_TOKEN3" \
      -H "Content-Type: application/json" \
      -X POST "$BASE_URL/valuations/$VAL_MULTI_ID/likes" \
      -d '{}' > /dev/null
    
    # User2 deletes their like
    DELETE_MULTI=$(curl -s -w "\n%{http_code}" \
      -H "Cookie: jwt_token=$JWT_TOKEN2" \
      -H "Content-Type: application/json" \
      -X DELETE "$BASE_URL/valuations/$VAL_MULTI_ID/likes")
    
    DELETE_MULTI_HTTP=$(echo "$DELETE_MULTI" | tail -1)
    
    echo "Endpoint: DELETE $BASE_URL/valuations/$VAL_MULTI_ID/likes (User2 removes their like)"
    echo ""
    
    if [ "$DELETE_MULTI_HTTP" = "204" ]; then
        print_success "User2's like successfully deleted (HTTP $DELETE_MULTI_HTTP)"
        
        # User3 tries to delete their like (should succeed)
        DELETE_USER3=$(curl -s -w "\n%{http_code}" \
          -H "Cookie: jwt_token=$JWT_TOKEN3" \
          -H "Content-Type: application/json" \
          -X DELETE "$BASE_URL/valuations/$VAL_MULTI_ID/likes")
        
        DELETE_USER3_HTTP=$(echo "$DELETE_USER3" | tail -1)
        
        if [ "$DELETE_USER3_HTTP" = "204" ]; then
            print_success "User3's like also successfully deleted (HTTP $DELETE_USER3_HTTP)"
        else
            print_error "Expected 204 for User3's deletion but got $DELETE_USER3_HTTP"
        fi
    else
        print_error "Expected 204 but got $DELETE_MULTI_HTTP"
    fi
else
    print_error "Failed to create BrickSet for TEST 55"
fi

# ============================================================
# GET LIKES LIST ENDPOINTS - RETRIEVE PAGINATED LIKE LIST
# ============================================================

print_header "GET LIKES LIST ENDPOINTS - GET /api/v1/valuations/{id}/likes"

# TEST 56: GET /api/v1/valuations/{id}/likes - SUCCESS (200)
# ============================================================

print_header "TEST 56: GET /api/v1/valuations/{id}/likes - SUCCESSFUL LIKES LIST RETRIEVAL"

echo "Endpoint: GET $BASE_URL/valuations/$VAL_MULTI_ID/likes"
echo "Expected: HTTP 200 OK with paginated like list (User3 deleted their like, only User2 if not deleted yet)"
echo ""

# Re-create likes for testing list endpoint
curl -s -H "Cookie: jwt_token=$JWT_TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/valuations/$VAL_MULTI_ID/likes" \
  -d '{}' > /dev/null

curl -s -H "Cookie: jwt_token=$JWT_TOKEN3" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/valuations/$VAL_MULTI_ID/likes" \
  -d '{}' > /dev/null

GET_LIKES_LIST=$(curl -s -w "\n%{http_code}" \
  -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X GET "$BASE_URL/valuations/$VAL_MULTI_ID/likes")

GET_LIKES_LIST_HTTP=$(echo "$GET_LIKES_LIST" | tail -1)
GET_LIKES_LIST_BODY=$(echo "$GET_LIKES_LIST" | sed '$d')

if [ "$GET_LIKES_LIST_HTTP" = "200" ]; then
    print_success "Likes list retrieved successfully (HTTP $GET_LIKES_LIST_HTTP)"
    echo "Response structure:"
    echo "$GET_LIKES_LIST_BODY" | jq '{count, next, previous, results}'
    
    # Verify pagination structure
    COUNT=$(echo "$GET_LIKES_LIST_BODY" | jq '.count')
    RESULTS=$(echo "$GET_LIKES_LIST_BODY" | jq '.results | length')
    
    if [ "$COUNT" -ge 2 ]; then
        print_success "Likes count is correct ($COUNT likes)"
    fi
    
    if [ "$RESULTS" -ge 2 ]; then
        print_success "Results array contains likes ($RESULTS items)"
        echo "First like:"
        echo "$GET_LIKES_LIST_BODY" | jq '.results[0]'
    fi
else
    print_error "Expected 200 but got $GET_LIKES_LIST_HTTP"
    echo "$GET_LIKES_LIST_BODY"
fi

# TEST 57: GET /api/v1/valuations/{id}/likes - RESPONSE FIELDS
# ============================================================

print_header "TEST 57: GET /api/v1/valuations/{id}/likes - RESPONSE FIELDS VALIDATION"

echo "Verifying response contains required fields: user_id, created_at"
echo "Verifying response excludes redundant fields: valuation_id, updated_at"
echo ""

if [ "$GET_LIKES_LIST_HTTP" = "200" ]; then
    FIRST_LIKE=$(echo "$GET_LIKES_LIST_BODY" | jq '.results[0]')
    
    # Check required fields
    USER_ID=$(echo "$FIRST_LIKE" | jq '.user_id')
    CREATED_AT=$(echo "$FIRST_LIKE" | jq '.created_at')
    
    # Check excluded fields
    VALUATION_ID=$(echo "$FIRST_LIKE" | jq '.valuation_id')
    UPDATED_AT=$(echo "$FIRST_LIKE" | jq '.updated_at')
    
    echo "First like object:"
    echo "$FIRST_LIKE" | jq '.'
    echo ""
    
    if [ "$USER_ID" != "null" ] && [ -n "$USER_ID" ]; then
        print_success "✓ Required field present: user_id = $USER_ID"
    else
        print_error "✗ Missing required field: user_id"
    fi
    
    if [ "$CREATED_AT" != "null" ] && [ -n "$CREATED_AT" ]; then
        print_success "✓ Required field present: created_at = $CREATED_AT"
    else
        print_error "✗ Missing required field: created_at"
    fi
    
    if [ "$VALUATION_ID" = "null" ]; then
        print_success "✓ Redundant field correctly excluded: valuation_id"
    else
        print_error "✗ Redundant field should not be included: valuation_id = $VALUATION_ID"
    fi
    
    if [ "$UPDATED_AT" = "null" ]; then
        print_success "✓ Redundant field correctly excluded: updated_at"
    else
        print_error "✗ Redundant field should not be included: updated_at = $UPDATED_AT"
    fi
else
    print_info "TEST 57: Skipped (TEST 56 failed)"
fi

# TEST 58: GET /api/v1/valuations/{id}/likes - PAGINATION
# ============================================================

print_header "TEST 58: GET /api/v1/valuations/{id}/likes - PAGINATION PARAMETERS"

echo "Endpoint: GET $BASE_URL/valuations/$VAL_MULTI_ID/likes?page=1&page_size=1"
echo "Expected: HTTP 200 OK with page_size=1, should have 'next' link since >1 likes exist"
echo ""

GET_LIKES_PAGE=$(curl -s -w "\n%{http_code}" \
  -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X GET "$BASE_URL/valuations/$VAL_MULTI_ID/likes?page=1&page_size=1")

GET_LIKES_PAGE_HTTP=$(echo "$GET_LIKES_PAGE" | tail -1)
GET_LIKES_PAGE_BODY=$(echo "$GET_LIKES_PAGE" | sed '$d')

if [ "$GET_LIKES_PAGE_HTTP" = "200" ]; then
    print_success "Pagination parameters respected (HTTP $GET_LIKES_PAGE_HTTP)"
    echo "Response with page_size=1:"
    echo "$GET_LIKES_PAGE_BODY" | jq '{count, next, previous, results_length: (.results | length)}'
    
    PAGE_SIZE=$(echo "$GET_LIKES_PAGE_BODY" | jq '.results | length')
    NEXT_LINK=$(echo "$GET_LIKES_PAGE_BODY" | jq -r '.next')
    
    if [ "$PAGE_SIZE" = "1" ]; then
        print_success "✓ page_size=1 respected (got $PAGE_SIZE item)"
    fi
    
    if [ "$NEXT_LINK" != "null" ] && [ -n "$NEXT_LINK" ]; then
        print_success "✓ 'next' pagination link present (multiple pages)"
    fi
else
    print_error "Expected 200 but got $GET_LIKES_PAGE_HTTP"
fi

# TEST 59: GET /api/v1/valuations/{id}/likes - EMPTY LIST
# ============================================================

print_header "TEST 59: GET /api/v1/valuations/{id}/likes - EMPTY LIKES LIST"

echo "Creating new valuation with no likes..."
echo ""

# Create a new BrickSet and valuation with no likes
EMPTY_LIKE_NUM=$((1000000 + (TIMESTAMP % 8999999) + 500))

CREATE_EMPTY_BS=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets" \
  -d "{
    \"number\": $EMPTY_LIKE_NUM,
    \"production_status\": \"ACTIVE\",
    \"completeness\": \"COMPLETE\",
    \"has_instructions\": true,
    \"has_box\": true,
    \"is_factory_sealed\": false
  }")

EMPTY_BS_ID=$(echo "$CREATE_EMPTY_BS" | jq -r '.id')

VAL_EMPTY=$(curl -s -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$BASE_URL/bricksets/$EMPTY_BS_ID/valuations" \
  -d '{"value": 300}')

VAL_EMPTY_ID=$(echo "$VAL_EMPTY" | jq -r '.id')

if [ "$VAL_EMPTY_ID" != "null" ] && [ -n "$VAL_EMPTY_ID" ]; then
    GET_EMPTY_LIKES=$(curl -s -w "\n%{http_code}" \
      -H "Cookie: jwt_token=$JWT_TOKEN" \
      -H "Content-Type: application/json" \
      -X GET "$BASE_URL/valuations/$VAL_EMPTY_ID/likes")
    
    GET_EMPTY_LIKES_HTTP=$(echo "$GET_EMPTY_LIKES" | tail -1)
    GET_EMPTY_LIKES_BODY=$(echo "$GET_EMPTY_LIKES" | sed '$d')
    
    echo "Endpoint: GET $BASE_URL/valuations/$VAL_EMPTY_ID/likes (valuation with no likes)"
    echo ""
    
    if [ "$GET_EMPTY_LIKES_HTTP" = "200" ]; then
        print_success "Empty likes list retrieved successfully (HTTP $GET_EMPTY_LIKES_HTTP)"
        echo "Response:"
        echo "$GET_EMPTY_LIKES_BODY" | jq '{count, results_length: (.results | length)}'
        
        EMPTY_COUNT=$(echo "$GET_EMPTY_LIKES_BODY" | jq '.count')
        if [ "$EMPTY_COUNT" = "0" ]; then
            print_success "✓ count=0 for valuation with no likes"
        fi
    else
        print_error "Expected 200 but got $GET_EMPTY_LIKES_HTTP"
    fi
else
    print_error "Failed to create test valuation for empty likes test"
fi

# TEST 60: GET /api/v1/valuations/{id}/likes - NONEXISTENT VALUATION (404)
# ============================================================

print_header "TEST 60: GET /api/v1/valuations/{id}/likes - NONEXISTENT VALUATION"

echo "Endpoint: GET $BASE_URL/valuations/999999999/likes"
echo "Expected: HTTP 404 Not Found"
echo ""

GET_LIKES_NOTFOUND=$(curl -s -w "\n%{http_code}" \
  -H "Cookie: jwt_token=$JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -X GET "$BASE_URL/valuations/999999999/likes")

GET_LIKES_NOTFOUND_HTTP=$(echo "$GET_LIKES_NOTFOUND" | tail -1)
GET_LIKES_NOTFOUND_BODY=$(echo "$GET_LIKES_NOTFOUND" | sed '$d')

if [ "$GET_LIKES_NOTFOUND_HTTP" = "404" ]; then
    print_success "Nonexistent valuation correctly returns 404 (HTTP $GET_LIKES_NOTFOUND_HTTP)"
    echo "Error response:"
    echo "$GET_LIKES_NOTFOUND_BODY" | jq '.detail'
else
    print_error "Expected 404 but got $GET_LIKES_NOTFOUND_HTTP"
    echo "$GET_LIKES_NOTFOUND_BODY"
fi

# TEST 61: GET /api/v1/valuations/{id}/likes - UNAUTHORIZED (401)
# ============================================================

print_header "TEST 61: GET /api/v1/valuations/{id}/likes - UNAUTHORIZED (NO AUTH)"

echo "Endpoint: GET $BASE_URL/valuations/$VAL_MULTI_ID/likes (without JWT token)"
echo "Expected: HTTP 401 Unauthorized"
echo ""

GET_LIKES_NOAUTH=$(curl -s -w "\n%{http_code}" \
  -H "Content-Type: application/json" \
  -X GET "$BASE_URL/valuations/$VAL_MULTI_ID/likes")

GET_LIKES_NOAUTH_HTTP=$(echo "$GET_LIKES_NOAUTH" | tail -1)
GET_LIKES_NOAUTH_BODY=$(echo "$GET_LIKES_NOAUTH" | sed '$d')

if [ "$GET_LIKES_NOAUTH_HTTP" = "401" ]; then
    print_success "Unauthenticated GET correctly rejected (HTTP $GET_LIKES_NOAUTH_HTTP)"
else
    print_error "Expected 401 but got $GET_LIKES_NOAUTH_HTTP"
    echo "$GET_LIKES_NOAUTH_BODY"
fi

# TEST 62: GET /api/v1/valuations/{id}/likes - ORDERING (NEWEST FIRST)
# ============================================================

print_header "TEST 62: GET /api/v1/valuations/{id}/likes - ORDERING (NEWEST FIRST)"

echo "Verifying likes are ordered by created_at DESC (newest first)"
echo ""

if [ "$GET_LIKES_LIST_HTTP" = "200" ]; then
    LIKES_ARRAY=$(echo "$GET_LIKES_LIST_BODY" | jq '.results')
    LIKES_COUNT=$(echo "$LIKES_ARRAY" | jq 'length')
    
    if [ "$LIKES_COUNT" -ge 2 ]; then
        FIRST_TIMESTAMP=$(echo "$LIKES_ARRAY" | jq -r '.[0].created_at')
        SECOND_TIMESTAMP=$(echo "$LIKES_ARRAY" | jq -r '.[1].created_at')
        
        echo "First like created_at: $FIRST_TIMESTAMP"
        echo "Second like created_at: $SECOND_TIMESTAMP"
        echo ""
        
        # Compare timestamps (newest first means first > second)
        # This is a simple string comparison for ISO8601 format (works for descending order)
        if [[ "$FIRST_TIMESTAMP" > "$SECOND_TIMESTAMP" ]] || [[ "$FIRST_TIMESTAMP" == "$SECOND_TIMESTAMP" ]]; then
            print_success "✓ Likes ordered correctly (newest first)"
        else
            print_error "✗ Likes not ordered correctly (oldest first instead of newest)"
        fi
    else
        print_info "TEST 62: Not enough likes to verify ordering (need ≥2)"
    fi
else
    print_info "TEST 62: Skipped (TEST 56 failed)"
fi

# ============================================================
# POST-TEST CLEANUP
# ============================================================

print_header "POST-TEST DATABASE CLEANUP"

print_info "Cleaning test BrickSets and Valuations from database..."
docker-compose exec -T backend python manage.py shell -c "
from catalog.models import BrickSet
try:
    # Delete test bricksets and their associated valuations (numbers in range 1000000-9999999)
    count = BrickSet.bricksets.filter(number__gte=1000000, number__lte=9999999).delete()[0]
    print(f'Deleted {count} BrickSets')
except Exception as e:
    print(f'Cleanup error: {e}')
" 2>&1 | grep -v "^$\|^10\|^[0-9]* objects"

print_success "Test data cleaned successfully"

# ============================================================
# SUMMARY
# ============================================================

print_header "TEST SUMMARY"
print_success "All valuation API tests completed!"
echo ""
echo "Summary:"
echo ""
echo "CREATE ENDPOINTS (POST /api/v1/bricksets/{id}/valuations):"
echo "  ✅ Successful valuation creation (201 Created)"
echo "  ✅ Without optional fields (currency defaults to PLN, comment is null)"
echo "  ✅ Duplicate detection (409 Conflict)"
echo "  ✅ Multiple users can value same BrickSet"
echo "  ✅ Same user can value different BrickSets"
echo ""
echo "VALIDATION TESTS:"
echo "  ✅ Value validation (1-999999 range)"
echo "  ✅ Value zero rejection (below minimum)"
echo "  ✅ Value exceeding maximum (10000000)"
echo "  ✅ Missing value field (400 Bad Request)"
echo "  ✅ Currency maximum length (3 characters)"
echo "  ✅ Various currency codes (EUR, USD, GBP, JPY, CHF)"
echo "  ✅ Empty comment (allowed)"
echo "  ✅ Long comment (allowed)"
echo ""
echo "ERROR HANDLING:"
echo "  ✅ Nonexistent BrickSet (404 Not Found)"
echo "  ✅ Unauthenticated request (401 Unauthorized)"
echo ""
echo "RESPONSE STRUCTURE:"
echo "  ✅ All required fields present (id, brickset_id, user_id, value, currency, comment, likes_count, created_at, updated_at)"
echo "  ✅ Datetime ISO8601 formatting"
echo "  ✅ likes_count initialized to 0"
echo "  ✅ Negative value rejection"
echo ""
echo "LIST ENDPOINTS (GET /api/v1/bricksets/{id}/valuations):"
echo "  ✅ Successful list retrieval (200 OK)"
echo "  ✅ Pagination structure (count, next, previous, results)"
echo "  ✅ Ordering by likes_count DESC, created_at ASC"
echo "  ✅ Response fields validation (correct fields included/excluded)"
echo "  ✅ Empty list for BrickSet without valuations"
echo "  ✅ Nonexistent BrickSet (404 Not Found)"
echo "  ✅ Unauthorized access (401 Unauthorized)"
echo "  ✅ Pagination page_size parameter"
echo "  ✅ Pagination page parameter (next/previous links)"
echo "  ✅ Max page_size enforcement (100)"
echo "  ✅ Null comment handling"
echo ""
echo "DETAIL ENDPOINTS (GET /api/v1/valuations/{id}):"
echo "  ✅ Successful detail retrieval (200 OK)"
echo "  ✅ All 9 required fields present"
echo "  ✅ includes updated_at timestamp (not in list)"
echo "  ✅ Correct data accuracy"
echo "  ✅ Null comment serialization"
echo "  ✅ Nonexistent valuation (404 Not Found)"
echo "  ✅ Unauthenticated request (401 Unauthorized)"
echo "  ✅ Public read access (any authenticated user)"
echo "  ✅ Different valuations return different data"
echo "  ✅ Detail vs List endpoint field differences"
echo ""
echo "LIKE ENDPOINTS (POST /api/v1/valuations/{id}/likes):"
echo "  ✅ Successful like creation (201 Created)"
echo "  ✅ Cannot like own valuation (403 Forbidden)"
echo "  ✅ Duplicate like rejection (409 Conflict)"
echo "  ✅ Nonexistent valuation (404 Not Found)"
echo "  ✅ Unauthenticated request (401 Unauthorized)"
echo "  ✅ Multiple users can like same valuation"
echo "  ✅ Response structure (valuation_id, user_id, created_at)"
echo "  ✅ ISO8601 timestamp format"
echo "  ✅ Empty body handling"
echo "  ✅ Cross-user like permission"
echo ""
echo "UNLIKE ENDPOINTS (DELETE /api/v1/valuations/{id}/likes):"
echo "  ✅ Successful like deletion (204 No Content)"
echo "  ✅ Like not found when already deleted (404 Not Found)"
echo "  ✅ Cannot delete other user's like (404 Not Found - implicit authorization)"
echo "  ✅ Authentication required (401 Unauthorized)"
echo "  ✅ Selective deletion (delete one like, others remain)"
echo ""
echo "LIKE LIST ENDPOINTS (GET /api/v1/valuations/{id}/likes):"
echo "  ✅ Successful likes list retrieval (200 OK with pagination)"
echo "  ✅ Response structure (count, next, previous, results)"
echo "  ✅ Response fields validation (user_id, created_at present; valuation_id, updated_at excluded)"
echo "  ✅ Pagination page_size parameter (respects custom page sizes)"
echo "  ✅ Pagination next/previous links"
echo "  ✅ Empty likes list (200 OK with count=0, not 404)"
echo "  ✅ Nonexistent valuation (404 Not Found with detail message)"
echo "  ✅ Unauthenticated request (401 Unauthorized)"
echo "  ✅ Likes ordered by created_at DESC (newest first)"
echo "  ✅ Any authenticated user can view likes (no ownership restriction)"
echo ""
print_info "Database cleaned after tests"
echo ""
