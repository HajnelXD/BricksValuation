# Feature Specification: BrickSet Duplicate Detection (US-005)

## Executive Summary

This document extends the BrickSet Create View implementation plan with detailed specifications for duplicate set detection as defined in **US-005: Wykrycie duplikatu zestawu** (BrickSet Duplicate Detection).

The feature ensures that users receive clear feedback when attempting to create a BrickSet with the same critical attribute combination as an existing set, preventing database duplicates and maintaining data integrity. The duplicate check is performed on the global unique constraint: `(number, production_status, completeness, has_instructions, has_box, is_factory_sealed)`.

---

## 1. Functional Requirements

### FR-05: Unikanie duplikatów (Duplicate Avoidance)

**Definition**: Before adding a new BrickSet, the system checks for the existence of a set using the combination:
- `number` (set number)
- `production_status` (ACTIVE or RETIRED)
- `completeness` (COMPLETE or INCOMPLETE)
- `has_instructions` (boolean)
- `has_box` (boolean)
- `is_factory_sealed` (boolean)

**Constraint**: Global uniqueness across all users on this 6-field combination (not per-user).

### FR-20: Obsługa błędów walidacji (Error Handling)

The system must return clear, user-friendly messages when validation fails, including the duplicate detection case.

---

## 2. User Story Acceptance Criteria (US-005)

### Criteria 1: Duplicate Detection Message
**When**: User attempts to add a BrickSet with an existing critical field combination
**Then**: System displays a clear message indicating the set already exists

**Implementation Detail**:
- API returns HTTP 409 CONFLICT status
- Response includes message: "BrickSet with this combination already exists."
- Response includes constraint identifier: `"brickset_global_identity"`
- Frontend parses and displays user-friendly notification in Polish

### Criteria 2: Prevent Duplicate Record Creation
**When**: A duplicate combination is detected
**Then**: No second identical record is created in the database

**Implementation Detail**:
- Database enforces UNIQUE constraint at the model level
- Service layer catches `IntegrityError` and maps to `BrickSetDuplicateError`
- Transaction rollback ensures no partial writes
- No record is created if constraint is violated

---

## 3. Duplicate Detection Architecture

### 3.1 Layers of Validation

#### Layer 1: Frontend Pre-submission Check (Optional Enhancement)
- **Purpose**: Provide immediate user feedback without waiting for API response
- **Implementation**: Query existing bricksets before form submission
- **Benefit**: Better UX with instant feedback
- **Status**: Optional (not required for MVP, can be added in future)

#### Layer 2: Database Constraint (Primary Defense)
- **Type**: UNIQUE constraint at database level
- **Constraint Name**: `brickset_global_identity`
- **Fields**: `(number, production_status, completeness, has_instructions, has_box, is_factory_sealed)`
- **Enforcement**: PostgreSQL enforces at INSERT/UPDATE time
- **Benefit**: Prevents duplicates even if application layer is bypassed

#### Layer 3: Backend Service Layer (Active Detection)
- **Type**: Application-level exception handling
- **Method**: Catch `django.db.IntegrityError` during `brickset.save()`
- **Response**: Raise `BrickSetDuplicateError` domain exception
- **Benefit**: Provides application context and custom error messages

#### Layer 4: API Response Mapping (User Communication)
- **Status Code**: 409 CONFLICT (HTTP standard for resource already exists)
- **Response Format**: Structured JSON with detail message and constraint identifier
- **Localization**: Message can be localized or combined with frontend translations

#### Layer 5: Frontend Error Display (User Experience)
- **Component**: BrickSetCreateView with duplicate modal/toast
- **Behavior**: Show user-friendly message with option to navigate to existing set
- **Action**: Allow user to view the duplicate set or modify their input

### 3.2 Data Flow for Duplicate Detection

```
User Submits Form
        ↓
Frontend Validation (client-side check of required fields)
        ↓
API Request: POST /api/v1/bricksets
        ↓
Backend Authentication Check (JWT validation)
        ↓
Serializer Validation (field types, ranges, enums)
        ↓
Service Layer Build BrickSet Instance
        ↓
Model Validation (full_clean() - CHECK constraints)
        ↓
Database INSERT Attempt
        ↓
    [UNIQUE Constraint Check]
        ↓
    ┌─────────────────────────────┐
    │ Constraint Violation?       │
    └─────────────────────────────┘
         ↙              ↖
      YES             NO
       ↓               ↓
  IntegrityError   Success (201)
       ↓               ↓
Catch & Map      Build DTO
       ↓               ↓
BrickSetDuplicateError  Return DTO
       ↓               ↓
409 CONFLICT      201 Created
    Response        Response
       ↓               ↓
Frontend Modal    Success Toast
"Zestaw już       "Zestaw dodany"
istnieje"         ↓
       ↓          Redirect
Navigate or
Modify Form
```

---

## 4. Backend Implementation Details

### 4.1 Database Constraint Definition

**PostgreSQL Definition** (from db-plan.md):

```sql
CREATE TABLE catalog_brickset (
  id BIGSERIAL PRIMARY KEY,
  owner_id BIGINT NOT NULL REFERENCES account_user(id) ON DELETE CASCADE,
  number INTEGER NOT NULL CHECK (number >= 0 AND number <= 9999999),
  production_status production_status_enum NOT NULL,
  completeness completeness_enum NOT NULL,
  has_instructions BOOLEAN NOT NULL DEFAULT FALSE,
  has_box BOOLEAN NOT NULL DEFAULT FALSE,
  is_factory_sealed BOOLEAN NOT NULL DEFAULT FALSE,
  owner_initial_estimate INTEGER NULL CHECK (owner_initial_estimate > 0 AND owner_initial_estimate < 1000000),
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  -- THIS IS THE KEY CONSTRAINT FOR DUPLICATE DETECTION:
  UNIQUE (number, production_status, completeness, has_instructions, has_box, is_factory_sealed)
);
```

**Django Model Definition**:

```python
class BrickSet(models.Model):
    owner = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    number = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(9999999)])
    production_status = models.CharField(max_length=20, choices=[('ACTIVE', 'Active'), ('RETIRED', 'Retired')])
    completeness = models.CharField(max_length=20, choices=[('COMPLETE', 'Complete'), ('INCOMPLETE', 'Incomplete')])
    has_instructions = models.BooleanField(default=False)
    has_box = models.BooleanField(default=False)
    is_factory_sealed = models.BooleanField(default=False)
    owner_initial_estimate = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(999999)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ('number', 'production_status', 'completeness', 'has_instructions', 'has_box', 'is_factory_sealed')
        ]
```

### 4.2 Domain Exception

**File**: `backend/catalog/exceptions.py`

```python
class BrickSetDuplicateError(Exception):
    """Raised when attempting to create a BrickSet with a duplicate global identity combination.

    The global identity is defined by the unique constraint:
    (number, production_status, completeness, has_instructions, has_box, is_factory_sealed)
    """

    def __init__(self, constraint: str = 'brickset_global_identity'):
        self.constraint = constraint
        self.message = "BrickSet with this combination already exists."
        super().__init__(self.message)

    def to_dict(self):
        """Serialize exception to response format."""
        return {
            'detail': self.message,
            'constraint': self.constraint,
        }
```

### 4.3 Service Layer Implementation

**File**: `backend/catalog/services/brickset_create_service.py`

```python
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from catalog.models import BrickSet
from catalog.exceptions import BrickSetDuplicateError, BrickSetValidationError

class CreateBrickSetService:
    """Service for creating new BrickSets with duplicate detection."""

    def execute(self, command: CreateBrickSetCommand, owner):
        """
        Create a new BrickSet with automatic duplicate detection.

        Args:
            command: CreateBrickSetCommand with set attributes
            owner: User object (set owner)

        Returns:
            BrickSetListItemDTO: The created set data

        Raises:
            BrickSetDuplicateError: If combination already exists (409)
            BrickSetValidationError: If validation fails (400)
        """
        # Step 1: Build BrickSet instance from command
        brickset = self._build_brickset(command, owner)

        # Step 2: Validate model (CHECK constraints, field validators)
        try:
            brickset.full_clean()
        except DjangoValidationError as e:
            raise BrickSetValidationError(e.error_dict)

        # Step 3: Persist with UNIQUE constraint enforcement
        try:
            with transaction.atomic():
                brickset.save()
        except IntegrityError as e:
            # Parse IntegrityError to determine constraint that was violated
            if 'brickset_global_identity' in str(e) or 'unique' in str(e).lower():
                raise BrickSetDuplicateError(constraint='brickset_global_identity')
            else:
                # Some other constraint was violated - re-raise
                raise

        # Step 4: Build and return DTO
        return self._build_dto(brickset)

    def _build_brickset(self, command: CreateBrickSetCommand, owner):
        """Create BrickSet model instance from command."""
        return BrickSet(
            owner=owner,
            number=command.number,
            production_status=command.production_status,
            completeness=command.completeness,
            has_instructions=command.has_instructions,
            has_box=command.has_box,
            is_factory_sealed=command.is_factory_sealed,
            owner_initial_estimate=command.owner_initial_estimate,
        )

    def _build_dto(self, brickset: BrickSet) -> BrickSetListItemDTO:
        """Convert saved BrickSet to DTO."""
        return BrickSetListItemDTO(
            id=brickset.id,
            number=brickset.number,
            production_status=brickset.production_status,
            completeness=brickset.completeness,
            has_instructions=brickset.has_instructions,
            has_box=brickset.has_box,
            is_factory_sealed=brickset.is_factory_sealed,
            owner_initial_estimate=brickset.owner_initial_estimate,
            owner_id=brickset.owner_id,
            valuations_count=0,
            total_likes=0,
            top_valuation=None,
            created_at=brickset.created_at.isoformat(),
            updated_at=brickset.updated_at.isoformat(),
        )
```

### 4.4 API View Error Handling

**File**: `backend/catalog/views/brickset_create.py`

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED
from rest_framework.permissions import IsAuthenticated
from catalog.serializers import CreateBrickSetSerializer, BrickSetListItemSerializer
from catalog.services import CreateBrickSetService
from catalog.exceptions import BrickSetDuplicateError, BrickSetValidationError

class CreateBrickSetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create a new BrickSet with duplicate detection."""
        # Step 1: Deserialize and validate input
        serializer = CreateBrickSetSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=HTTP_400_BAD_REQUEST
            )

        # Step 2: Convert to command
        command = serializer.to_command()

        # Step 3: Execute service with duplicate detection
        service = CreateBrickSetService()

        try:
            brickset_dto = service.execute(command, request.user)
        except BrickSetDuplicateError as e:
            # 409: Duplicate set already exists
            return Response(
                e.to_dict(),
                status=HTTP_409_CONFLICT
            )
        except BrickSetValidationError as e:
            # 400: Validation failed
            return Response(
                {'errors': e.errors},
                status=HTTP_400_BAD_REQUEST
            )

        # Step 4: Return success response
        response_serializer = BrickSetListItemSerializer(data=asdict(brickset_dto))
        response_serializer.is_valid()

        return Response(
            response_serializer.data,
            status=HTTP_201_CREATED
        )
```

---

## 5. Frontend Implementation Details

### 5.1 API Response Handling

**File**: `src/services/api/bricksetService.ts`

```typescript
export interface DuplicateError {
  detail: string;
  constraint: string;
}

export async function createBrickSet(
  data: CreateBrickSetRequest
): Promise<CreateBrickSetResponse | never> {
  const response = await fetch('/api/v1/bricksets', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(data),
  });

  if (response.status === 201) {
    return response.json();
  }

  if (response.status === 409) {
    const error: DuplicateError = await response.json();
    throw {
      type: 'DUPLICATE',
      ...error,
    };
  }

  if (response.status === 400) {
    const error = await response.json();
    throw {
      type: 'VALIDATION',
      errors: error.errors,
    };
  }

  throw new Error(`Unexpected response: ${response.status}`);
}
```

### 5.2 Duplicate Modal Component

**File**: `src/components/modals/BrickSetDuplicateModal.vue`

```vue
<template>
  <div v-if="isOpen" class="modal-overlay" @click="onClose">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">{{ $t('brickset.duplicate.title') }}</h2>
        <button class="modal-close-btn" @click="onClose" :aria-label="$t('common.close')">
          ✕
        </button>
      </div>

      <div class="modal-body">
        <p class="duplicate-message">{{ $t('brickset.duplicate.message') }}</p>

        <div class="duplicate-set-info">
          <h3 class="info-title">{{ $t('brickset.duplicate.existingSet') }}</h3>
          <div class="info-item">
            <span class="label">{{ $t('brickset.fields.number') }}:</span>
            <span class="value">{{ duplicateSetInfo.setNumber }}</span>
          </div>
          <div class="info-item">
            <span class="label">{{ $t('brickset.fields.productionStatus') }}:</span>
            <span class="value">{{ $t(`enum.productionStatus.${duplicateSetInfo.productionStatus}`) }}</span>
          </div>
          <div class="info-item">
            <span class="label">{{ $t('brickset.fields.completeness') }}:</span>
            <span class="value">{{ $t(`enum.completeness.${duplicateSetInfo.completeness}`) }}</span>
          </div>
          <div class="attributes">
            <span v-if="duplicateSetInfo.hasInstructions" class="attribute-badge">
              {{ $t('brickset.fields.hasInstructions') }}
            </span>
            <span v-if="duplicateSetInfo.hasBox" class="attribute-badge">
              {{ $t('brickset.fields.hasBox') }}
            </span>
            <span v-if="duplicateSetInfo.isFactorySealed" class="attribute-badge">
              {{ $t('brickset.fields.isFactorySealed') }}
            </span>
          </div>
        </div>

        <p class="help-text">{{ $t('brickset.duplicate.helpText') }}</p>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="onClose">
          {{ $t('common.close') }}
        </button>
        <button class="btn btn-primary" @click="onNavigateToExisting">
          {{ $t('brickset.duplicate.viewExisting') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';

interface Props {
  isOpen: boolean;
  duplicateSetInfo: {
    setId?: number;
    setNumber: number;
    productionStatus: string;
    completeness: string;
    hasInstructions: boolean;
    hasBox: boolean;
    isFactorySealed: boolean;
  };
}

interface Emits {
  (e: 'close'): void;
  (e: 'navigate'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();
const router = useRouter();
const { t } = useI18n();

const onClose = () => emit('close');

const onNavigateToExisting = async () => {
  if (props.duplicateSetInfo.setId) {
    await router.push({
      name: 'brickset-detail',
      params: { id: props.duplicateSetInfo.setId },
    });
  } else {
    await router.push({
      name: 'brickset-list',
      query: { search: props.duplicateSetInfo.setNumber.toString() },
    });
  }
  emit('navigate');
  emit('close');
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-width: 500px;
  width: 90%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
}

.modal-body {
  padding: 20px;
}

.duplicate-message {
  margin: 0 0 16px 0;
  color: #374151;
}

.duplicate-set-info {
  background: #f3f4f6;
  border-left: 4px solid #f59e0b;
  padding: 16px;
  border-radius: 4px;
  margin: 16px 0;
}

.info-title {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 12px 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.label {
  font-weight: 500;
  color: #4b5563;
}

.value {
  color: #111827;
  font-weight: 600;
}

.attributes {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.attribute-badge {
  display: inline-block;
  background: #d1d5db;
  color: #1f2937;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
}

.help-text {
  margin: 16px 0 0 0;
  color: #6b7280;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: 1px solid transparent;
  cursor: pointer;
  font-weight: 500;
}

.btn-secondary {
  background: #e5e7eb;
  color: #1f2937;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}
</style>
```

---

## 6. i18n Messages

**File**: `src/i18n.ts` or `src/locales/pl.json`

```json
{
  "brickset": {
    "duplicate": {
      "title": "Zestaw już istnieje",
      "message": "Próba dodania zestawu z taką samą kombinacją cech (numer, status produkcji, kompletność, instrukcja, pudełko, zapieczętowanie) nie jest możliwa.",
      "existingSet": "Istniejący zestaw",
      "helpText": "Możesz przejść do istniejącego zestawu, aby sprawdzić jego szczegóły i wyceny.",
      "viewExisting": "Przejdź do istniejącego zestawu"
    }
  }
}
```

---

## 7. Testing Scenarios

### Backend Tests

```python
def test_duplicate_api_returns_409():
    """Test that API returns 409 CONFLICT on duplicate."""
    # Create first brickset
    brickset1 = BrickSet.objects.create(
        owner=user1,
        number=12345,
        production_status='ACTIVE',
        completeness='COMPLETE',
        has_instructions=True,
        has_box=True,
        is_factory_sealed=False,
    )

    # Attempt to create identical
    response = client.post('/api/v1/bricksets', {
        'number': 12345,
        'production_status': 'ACTIVE',
        'completeness': 'COMPLETE',
        'has_instructions': True,
        'has_box': True,
        'is_factory_sealed': False,
    })

    assert response.status_code == 409
    assert response.json()['constraint'] == 'brickset_global_identity'
    assert BrickSet.objects.count() == 1  # No second record created
```

---

## 8. Edge Cases

**Global Uniqueness**: The constraint applies globally across all users. User B cannot create an identical combination even if User A created it first.

**Boolean Fields**: All boolean fields default to FALSE, never NULL. This is critical for the unique constraint.

**Enum Values**: `production_status` and `completeness` must exactly match enum values (case-sensitive, uppercase).

---

## 9. Acceptance Criteria Checklist (US-005)

- [ ] Attempting to add set with existing combination shows modal
- [ ] Message is clear and in Polish
- [ ] User can navigate to existing set from modal
- [ ] Form state is preserved after duplicate detection
- [ ] No database duplicates are created
- [ ] API returns 409 CONFLICT status
- [ ] Database constraint prevents second record
- [ ] Transaction rollback ensures atomicity

---

## Conclusion

The Duplicate Detection feature (US-005) ensures data integrity through multiple layers of validation: database constraints, application-level exception handling, and user-friendly error communication. By enforcing global uniqueness on the critical attribute combination, the system maintains a single canonical representation of each BrickSet variant while allowing users to understand why their submission was rejected and how to navigate to the existing set.
