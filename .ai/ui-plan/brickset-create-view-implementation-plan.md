# View Implementation Plan: BrickSet Create View

## 1. Overview

The BrickSet Create View is a form-based interface that enables authenticated users to add new LEGO brick sets to the BricksValuation system. The view provides a comprehensive form with fields for set number, production status, completeness, and physical attributes (instructions, box, factory sealed state). It includes an optional owner's initial estimate of the set's value. The view handles real-time field validation, user-friendly error messages, conflict detection (409 status code for duplicate sets), and protection against multiple form submissions.

## 2. View Routing

- **Path**: `/app/bricksets/new`
- **Route name**: `brickset-create`
- **Accessibility**: Protected (authenticated users only)
- **Meta**: `{ requiresAuth: true }` - Redirect to login if not authenticated
- **Guard**: Router guard checks user authentication before rendering

## 3. Component Structure

```
BrickSetCreateView (Page Component)
└── BrickSetFormLayout (Wrapper - optional custom layout)
    ├── BrickSetForm (Smart Form Component - reusable)
    │   ├── FormActionsBar (Header with title, back button, submit button)
    │   ├── ValidationErrorList (Top-level error display)
    │   └── Form element
    │       ├── BaseInput (number field)
    │       │   └── InlineError
    │       ├── BaseSelect (production_status)
    │       │   └── InlineError
    │       ├── BaseSelect (completeness)
    │       │   └── InlineError
    │       ├── BaseCheckbox (has_instructions)
    │       ├── BaseCheckbox (has_box)
    │       ├── BaseCheckbox (is_factory_sealed)
    │       ├── BaseInput (owner_initial_estimate - optional)
    │       │   └── InlineError
    │       └── Button (type="submit", text="Dodaj zestaw")
    └── DuplicateModal (Conditional - shown on 409 conflict)
        ├── Message with conflict details
        ├── Link to existing set
        └── "Close" button
```

## 4. Component Details

### BrickSetCreateView (Page Component)

- **Component description**: Main page component that serves as the container for the BrickSet creation interface. Manages the overall page flow including navigation, form submission, and error handling. Provides page-level state management and coordination between child components.

- **Main elements**:
  - Page wrapper (div with appropriate spacing/padding)
  - BrickSetForm component with full form implementation
  - Optional BrickSetFormLayout for consistent styling (can use existing layout components)
  - Toast notification container for success/error messages
  - Navigation (breadcrumbs or back button)

- **Handled interactions**:
  - `@submit="handleCreateBrickSet"` - Form submission with API call
  - `@error="handleFormError"` - Error handling from child components
  - `@duplicate-found="handleDuplicate"` - 409 conflict response handling
  - `@cancel="navigateBack"` - Cancel/back navigation
  - `@success="handleSuccess"` - Successful creation navigation

- **Handled validation**:
  - All field-level validations delegated to BrickSetForm
  - Page-level error state management for API errors
  - 409 Conflict handling with option to navigate to existing set

- **Types**:
  - `BrickSetFormData` (ViewModel)
  - `CreateBrickSetRequest` (DTO)
  - `CreateBrickSetResponse` (DTO)
  - `BrickSetValidationError` (Error DTO)
  - `DuplicateSetInfo` (ViewModel for conflict modal)

- **Props**: None (page component)

### BrickSetForm (Reusable Smart Form Component)

- **Component description**: Core form component that encapsulates all form logic, validation, and submission handling. Designed to be reusable for both create and edit operations (edit mode can be implemented later by passing a `mode` prop or `brickset` prop). Manages form state, field-level validation, and API integration.

- **Main elements**:
  - Form wrapper (HTML `<form>` element)
  - FormActionsBar (header with title, navigation, submit button)
  - ValidationErrorList (displays top-level form errors)
  - Field sections organized logically:
    - Set Identity: number input
    - Set Status: production_status and completeness selects
    - Set Attributes: has_instructions, has_box, is_factory_sealed checkboxes
    - Owner Estimate: owner_initial_estimate input (optional)
  - Submit and Cancel buttons in footer

- **Handled interactions**:
  - `@input` on each field: Updates form data and clears field-specific errors
  - `@blur` on each field: Triggers field validation
  - `@change` on checkboxes: Updates boolean fields
  - `@submit`: Form submission with comprehensive validation
  - `@cancel`: Emits cancel event to parent
  - Keyboard support: Enter key triggers submit (when valid)

- **Handled validation**:
  - **number**:
    - Required (non-empty)
    - Integer type validation
    - Range: 0 to 9999999 (7 digits maximum)
    - Custom validation on blur and submit
  - **production_status**:
    - Required (non-empty)
    - Must be one of: 'ACTIVE', 'RETIRED'
    - Validated via enum constraint
  - **completeness**:
    - Required (non-empty)
    - Must be one of: 'COMPLETE', 'INCOMPLETE'
    - Validated via enum constraint
  - **has_instructions, has_box, is_factory_sealed**:
    - Boolean type validation
    - No additional validation required
  - **owner_initial_estimate**:
    - Optional field (can be null/undefined)
    - When provided: Must be integer > 0 and < 1000000
    - Range: 1 to 999999
    - Custom validation on blur and submit
  - **Form-level validation**:
    - All required fields must be filled before submission
    - At least one field change before submit allowed (tracks form dirty state)
    - Duplicate detection: API returns 409 on duplicate combination
    - API response validation errors mapped to field errors

- **Types**:
  - `BrickSetFormData` (ViewModel)
  - `FieldErrors` (ViewModel)
  - `CreateBrickSetRequest` (DTO)
  - `CreateBrickSetResponse` (DTO)
  - `BrickSetValidationError` (Error DTO)
  - `BrickSetFormProps` (Component props interface)

- **Props**:
  - `initialData?: BrickSetFormData` - Pre-filled form data (for edit mode in future)
  - `mode?: 'create' | 'edit'` - Form mode (default: 'create')
  - `isLoading?: boolean` - Disable form during submission
  - `isSubmitting?: boolean` - Show loading spinner on submit button
  - `onSubmit?: (data: CreateBrickSetRequest) => Promise<CreateBrickSetResponse>` - API call handler

### FormActionsBar (Header Component)

- **Component description**: Reusable header component for forms displaying title, action buttons, and navigation controls. Provides consistent UX across different forms.

- **Main elements**:
  - Title/heading (usually h1 or h2)
  - Back/Cancel button (left side)
  - Submit button (right side)
  - Optional breadcrumbs or navigation context

- **Handled interactions**:
  - `@back` or `@cancel`: Navigates back or cancels form
  - `@submit`: Triggers form submission
  - Button states: normal, loading, disabled

- **Handled validation**: None (presentation component)

- **Types**:
  - `FormActionsBarProps` (Component props interface)

- **Props**:
  - `title: string` - Form title
  - `submitText?: string` - Submit button text (default: "Dodaj zestaw")
  - `cancelText?: string` - Cancel button text (default: "Anuluj")
  - `isSubmitting?: boolean` - Disable buttons during submission
  - `showBackButton?: boolean` - Show/hide back button
  - `submitDisabled?: boolean` - Disable submit button

### ValidationErrorList (Error Display Component)

- **Component description**: Displays top-level form validation errors or server errors in a user-friendly format. Can show multiple errors for different fields or general form errors.

- **Main elements**:
  - Error container (styled alert box)
  - Error list (ul or div with error items)
  - Each error item with icon and message
  - Optional close/dismiss button

- **Handled interactions**:
  - `@dismiss`: Closes error message
  - Auto-dismissal after timeout (optional)

- **Handled validation**: None (presentation component)

- **Types**: None specific

- **Props**:
  - `errors: string[]` - Array of error messages
  - `isDismissible?: boolean` - Allow user to close errors
  - `type?: 'error' | 'warning' | 'info'` - Error severity

### BaseInput (Form Field Component - Reusable)

- **Component description**: Generic input field component with label, validation support, and error display. Used for number and optional estimate fields.

- **Main elements**:
  - Label element
  - Input element (various types: text, number, email)
  - InlineError component for field errors
  - Optional helper text

- **Handled interactions**:
  - `@input`: Emits `update:modelValue` event
  - `@blur`: Emits `blur` event for field validation
  - `@focus`: Emits `focus` event
  - `@change`: Emits `change` event

- **Handled validation**:
  - Displays error message when `error` prop is provided
  - Visual feedback (red border, error color) when invalid
  - Placeholder text for guidance

- **Types**:
  - `BaseInputProps` (Component props interface)
  - `modelValue: string | number`

- **Props**:
  - `modelValue: string | number` - Input value
  - `label: string` - Field label text
  - `type?: string` - Input type (default: "text")
  - `placeholder?: string` - Placeholder text
  - `error?: string` - Error message to display
  - `hint?: string` - Helper text below input
  - `disabled?: boolean` - Disable input
  - `required?: boolean` - Required field indicator
  - `min?: number` - Minimum value (for number type)
  - `max?: number` - Maximum value (for number type)

### BaseSelect (Dropdown Component - Reusable)

- **Component description**: Dropdown/select field component for choosing from predefined options. Used for production_status and completeness fields.

- **Main elements**:
  - Label element
  - Select element
  - Option elements for each choice
  - InlineError component for validation errors

- **Handled interactions**:
  - `@change`: Emits `update:modelValue` event
  - `@blur`: Emits `blur` event for validation
  - `@focus`: Emits `focus` event

- **Handled validation**:
  - Displays error message when `error` prop is provided
  - Ensures selected value is in allowed options
  - Visual feedback when invalid

- **Types**:
  - `BaseSelectProps` (Component props interface)
  - `SelectOption` (DTO for option structure)

- **Props**:
  - `modelValue: string` - Selected value
  - `label: string` - Field label text
  - `options: SelectOption[]` - Array of available options
  - `error?: string` - Error message to display
  - `placeholder?: string` - Placeholder option text
  - `disabled?: boolean` - Disable select
  - `required?: boolean` - Required field indicator

### BaseCheckbox (Checkbox Component - Reusable)

- **Component description**: Checkbox input component for boolean fields. Used for instructions, box, and factory sealed attributes.

- **Main elements**:
  - Checkbox input element
  - Label element (clickable to toggle checkbox)
  - Optional helper text

- **Handled interactions**:
  - `@change`: Emits `update:modelValue` event (boolean value)
  - `@focus` / `@blur`: Emits focus/blur events

- **Handled validation**: None (always valid boolean)

- **Types**:
  - `BaseCheckboxProps` (Component props interface)

- **Props**:
  - `modelValue: boolean` - Checked state
  - `label: string` - Label text
  - `description?: string` - Additional description text
  - `disabled?: boolean` - Disable checkbox
  - `hint?: string` - Helper text

### InlineError (Validation Message Component)

- **Component description**: Small component that displays inline validation error messages below form fields. Appears only when error prop is provided.

- **Main elements**:
  - Error icon
  - Error message text

- **Handled interactions**: None (presentation component)

- **Handled validation**: None

- **Types**: None specific

- **Props**:
  - `message?: string` - Error message to display
  - `show?: boolean` - Whether to show error (default: !!message)

## 5. Types

### BrickSetFormData (ViewModel)

```typescript
interface BrickSetFormData {
  number: string;                    // String representation for input binding
  productionStatus: 'ACTIVE' | 'RETIRED';
  completeness: 'COMPLETE' | 'INCOMPLETE';
  hasInstructions: boolean;
  hasBox: boolean;
  isFactorySealed: boolean;
  ownerInitialEstimate: string | null;  // String for input binding, null when empty
  isDirty: boolean;                   // Tracks if form has been modified
}
```

### FieldErrors (ViewModel)

```typescript
interface FieldErrors {
  number?: string;
  productionStatus?: string;
  completeness?: string;
  hasInstructions?: string;
  hasBox?: string;
  isFactorySealed?: string;
  ownerInitialEstimate?: string;
  general?: string[];
}
```

### CreateBrickSetRequest (DTO)

```typescript
interface CreateBrickSetRequest {
  number: number;
  production_status: 'ACTIVE' | 'RETIRED';
  completeness: 'COMPLETE' | 'INCOMPLETE';
  has_instructions: boolean;
  has_box: boolean;
  is_factory_sealed: boolean;
  owner_initial_estimate?: number | null;
}
```

### CreateBrickSetResponse (DTO)

```typescript
interface CreateBrickSetResponse {
  id: number;
  number: number;
  production_status: 'ACTIVE' | 'RETIRED';
  completeness: 'COMPLETE' | 'INCOMPLETE';
  has_instructions: boolean;
  has_box: boolean;
  is_factory_sealed: boolean;
  owner_initial_estimate: number | null;
  owner_id: number;
  valuations_count: number;
  total_likes: number;
  top_valuation: TopValuation | null;
  created_at: string;  // ISO 8601 timestamp
  updated_at: string;  // ISO 8601 timestamp
}
```

### BrickSetValidationError (Error DTO)

```typescript
interface BrickSetValidationError {
  errors: {
    [fieldName: string]: string[];
  };
}
```

Example:
```json
{
  "errors": {
    "number": ["Ensure this value is less than or equal to 9999999."],
    "owner_initial_estimate": ["Ensure this value is greater than 0."]
  }
}
```

### BrickSetDuplicateError (Error DTO)

```typescript
interface BrickSetDuplicateError {
  detail: string;  // "BrickSet with this combination already exists."
  constraint: string;  // "brickset_global_identity"
  status: 409;
}
```

### DuplicateSetInfo (ViewModel)

```typescript
interface DuplicateSetInfo {
  setId: number;
  setNumber: number;
  productionStatus: 'ACTIVE' | 'RETIRED';
  completeness: 'COMPLETE' | 'INCOMPLETE';
  hasInstructions: boolean;
  hasBox: boolean;
  isFactorySealed: boolean;
  ownerName: string;
}
```

### TopValuation (DTO)

```typescript
interface TopValuation {
  id: number;
  value: number;
  user_id: number;
  likes_count: number;
  created_at: string;
}
```

### SelectOption (DTO)

```typescript
interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}
```

## 6. State Management

### Form State (Reactive)

The form state should be managed using Vue 3's Composition API with `ref()` and `reactive()` functions. A custom composable `useBrickSetForm` should be created to encapsulate form logic and make it reusable.

```typescript
interface FormState {
  formData: BrickSetFormData;
  fieldErrors: FieldErrors;
  generalErrors: string[];
  isSubmitting: boolean;
  isLoading: boolean;
  isFormDirty: boolean;
  duplicateSetInfo: DuplicateSetInfo | null;
  showDuplicateModal: boolean;
}
```

### Custom Composable: `useBrickSetForm`

**Purpose**: Centralize form logic including initialization, validation, submission, and error handling.

**What it provides**:
- `formData` (reactive): Current form state
- `fieldErrors` (reactive): Validation errors per field
- `generalErrors` (reactive): Form-level errors
- `isSubmitting` (ref): Submission state flag
- `isDirty` (computed): Whether form has unsaved changes
- `resetForm()`: Reset to initial state
- `setFieldValue(fieldName, value)`: Update single field
- `validateField(fieldName)`: Validate individual field
- `validateForm()`: Validate entire form
- `submitForm(onSubmit)`: Handle form submission with API call
- `mapApiErrorsToForm(error)`: Convert API errors to field errors
- `handleDuplicateError(error)`: Extract duplicate set info from 409 response

**Usage**:
```typescript
const {
  formData,
  fieldErrors,
  isSubmitting,
  isDirty,
  validateField,
  submitForm,
} = useBrickSetForm();
```

### Store (Pinia)

Create a new store module for brickset operations:

**Module**: `stores/modules/bricksetStore.ts` or `stores/brickset.ts`

**State**:
- `createdBrickSet: CreateBrickSetResponse | null` - Last created brickset
- `creatingBrickSet: boolean` - Loading state during creation
- `creationError: BrickSetValidationError | BrickSetDuplicateError | null` - Last creation error

**Actions**:
- `createBrickSet(data: CreateBrickSetRequest): Promise<CreateBrickSetResponse>` - Create new brickset via API
- `clearCreationState()` - Reset creation state after successful creation or navigation away

**Getters**:
- `isCreating: () => boolean` - Whether creation is in progress
- `createdBrickSetId: () => number | null` - ID of created brickset

### Local Component State vs Store

- **Local component state** (ref/reactive): Form input values, field errors, form dirty state - these are form-specific and don't need to persist after navigation
- **Pinia store**: Created brickset data (for potential redirect to detail view), creation error history (for debugging)

**Rationale**: Keep the form completely self-contained to avoid store pollution and make the form component reusable for future edit operations.

## 7. API Integration

### Endpoint: POST /api/v1/bricksets

**Request**:
- Method: POST
- URL: `/api/v1/bricksets`
- Authentication: JWT cookie (from login)
- Content-Type: application/json

**Request Payload** (CreateBrickSetRequest):
```json
{
  "number": 12345,
  "production_status": "ACTIVE",
  "completeness": "COMPLETE",
  "has_instructions": true,
  "has_box": true,
  "is_factory_sealed": false,
  "owner_initial_estimate": 360
}
```

**Response Success** (201 Created):
```json
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
  "top_valuation": null,
  "created_at": "2025-10-25T12:34:56.789Z",
  "updated_at": "2025-10-25T12:34:56.789Z"
}
```

**Response Error 400 (Validation Error)**:
```json
{
  "errors": {
    "number": ["Ensure this value is less than or equal to 9999999."],
    "owner_initial_estimate": ["Ensure this value is greater than 0."]
  }
}
```

**Response Error 409 (Duplicate)**:
```json
{
  "detail": "BrickSet with this combination already exists.",
  "constraint": "brickset_global_identity"
}
```

**Response Error 401 (Unauthorized)**:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### API Service Function

Create `src/services/api/bricksetService.ts`:

```typescript
export async function createBrickSet(
  data: CreateBrickSetRequest
): Promise<CreateBrickSetResponse> {
  const response = await fetch('/api/v1/bricksets', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',  // Include JWT cookie
    body: JSON.stringify(data),
  });

  if (response.status === 201) {
    return response.json();
  } else if (response.status === 400) {
    const error = await response.json();
    throw new ValidationError(error.errors);
  } else if (response.status === 409) {
    const error = await response.json();
    throw new DuplicateError(error.detail, error.constraint);
  } else if (response.status === 401) {
    throw new UnauthorizedError('Please log in to create a brickset');
  } else {
    throw new Error(`Unexpected status: ${response.status}`);
  }
}
```

### Error Handling Classes

Create `src/services/errors/BrickSetErrors.ts`:

```typescript
export class ValidationError extends Error {
  constructor(public errors: Record<string, string[]>) {
    super('Validation failed');
  }
}

export class DuplicateError extends Error {
  constructor(
    message: string,
    public constraint: string
  ) {
    super(message);
  }
}

export class UnauthorizedError extends Error {
  constructor(message: string) {
    super(message);
  }
}
```

## 8. User Interactions

### Primary Flow: Create New BrickSet

1. **User navigates to** `/app/bricksets/new`
   - Router guard checks authentication
   - If not authenticated, redirects to `/login`
   - If authenticated, renders BrickSetCreateView

2. **User sees the form** with empty fields
   - All required fields are clearly marked
   - Optional field (owner_initial_estimate) has helper text
   - Submit button is enabled

3. **User enters set number** (e.g., "12345")
   - Field shows as active (blue border, focus state)
   - Number is validated on blur:
     - Must be 0-9999999
     - Shows error if invalid

4. **User selects production status** (e.g., "ACTIVE")
   - Dropdown shows two options: ACTIVE, RETIRED
   - Shows error if not selected

5. **User selects completeness** (e.g., "COMPLETE")
   - Dropdown shows two options: COMPLETE, INCOMPLETE
   - Shows error if not selected

6. **User checks attribute checkboxes**
   - has_instructions: checked
   - has_box: checked
   - is_factory_sealed: unchecked
   - Checkboxes are immediately responsive

7. **User optionally enters owner estimate** (e.g., "360")
   - Field validates on blur (must be 1-999999)
   - Shows error if invalid
   - Field can be left empty

8. **User submits the form** by clicking "Dodaj zestaw" or pressing Enter
   - Form validates all required fields
   - If validation fails, errors are displayed next to fields
   - If validation passes, submit button shows loading state
   - API call is made with form data

9. **Success Response (201)**
   - Toast notification shows "Zestaw został dodany"
   - User is redirected to brickset detail view OR list view with newly created set visible
   - Form is cleared

10. **Error Response (400 - Validation)**
    - Error messages appear under respective fields
    - Form remains open for correction
    - Examples:
      - "Ensure this value is less than or equal to 9999999." (number)
      - "Ensure this value is greater than 0." (owner_initial_estimate)
      - "This field may not be blank." (required field)

11. **Error Response (409 - Duplicate)**
    - Modal dialog appears showing: "This brick set already exists"
    - Modal displays the existing set's key attributes
    - Offers button: "Przejdź do istniejącego zestawu"
    - When clicked, navigates to existing brickset's detail view
    - Alternative: Toast notification with link instead of modal

12. **Error Response (401 - Unauthorized)**
    - User is redirected to login page
    - Login page shows message: "Your session expired. Please log in again."

### Secondary Flows

**Cancel/Back Navigation**:
- User clicks back/cancel button
- If form has changes, shows confirmation dialog: "Discard changes?"
- If confirmed, navigates back to previous page (or `/app/bricksets` list)

**Keyboard Shortcuts**:
- Enter in any field triggers form submission
- Escape closes any open modals/dialogs

## 9. Conditions and Validation

### Field-Level Conditions

#### number
- **Frontend validation**:
  - Required: Must not be empty
  - Type: Must be numeric (0-9)
  - Range: Must be >= 0 and <= 9999999
  - Display error on: blur and submit
  - Error message examples:
    - "Zestaw jest wymagany" (if empty)
    - "Numer musi być liczbą" (if non-numeric)
    - "Numer może mieć maksymalnie 7 cyfr" (if > 9999999)

#### production_status
- **Frontend validation**:
  - Required: Must be selected
  - Enum: Must be 'ACTIVE' or 'RETIRED'
  - Display error on: change and submit
  - Error message: "Proszę wybrać status produkcji"

#### completeness
- **Frontend validation**:
  - Required: Must be selected
  - Enum: Must be 'COMPLETE' or 'INCOMPLETE'
  - Display error on: change and submit
  - Error message: "Proszę wybrać kompletność"

#### has_instructions, has_box, is_factory_sealed
- **Frontend validation**: None required (always valid boolean)
- Default value: false

#### owner_initial_estimate
- **Frontend validation**:
  - Optional: Can be null/empty
  - Type: Must be numeric if provided
  - Range: Must be >= 1 and < 1000000 if provided
  - Display error on: blur and submit
  - Error message examples:
    - "Wycena musi być liczbą" (if non-numeric)
    - "Wycena musi być większa niż 0" (if <= 0)
    - "Wycena nie może być większa niż 999999" (if >= 1000000)

### Form-Level Conditions

#### Duplicate Detection (409 Conflict)
- **Condition**: API returns 409 CONFLICT when:
  - A brickset with the same combination of (number, production_status, completeness, has_instructions, has_box, is_factory_sealed) already exists

- **Frontend handling**:
  - Parse 409 response: `{ detail: "BrickSet with this combination already exists.", constraint: "brickset_global_identity" }`
  - Extract existing brickset ID from response (if provided) OR offer search/link option
  - Display modal/toast with option to navigate to existing set
  - Keep form data intact for potential edits

#### Dirty State
- **Condition**: Form is considered "dirty" when:
  - User has modified any field from its initial value
  - At least one field value differs from default/initial state

- **Frontend handling**:
  - Track form dirty state
  - Show unsaved changes warning if user tries to navigate away
  - Used for "Cancel" button confirmation dialog

#### Submit Prevention
- **Conditions**: Form submission is blocked when:
  - Any required field is empty
  - Any field has validation errors
  - Form is already submitting (prevent double-submit)
  - User is not authenticated

- **Frontend handling**:
  - Disable submit button when conditions not met
  - Show validation errors before attempting submission
  - Show loading state during submission to prevent accidental double-click

### API Response Condition Handling

#### 201 Created (Success)
- Response includes full CreateBrickSetResponse object
- Extract `id` from response for potential navigation
- Show success toast and redirect to detail or list view

#### 400 Bad Request (Validation Error)
- Response includes `errors` object: `{ fieldName: ["message"] }`
- Map error messages to corresponding form fields
- Display errors inline under each invalid field
- Keep form open for user to correct

#### 409 Conflict (Duplicate)
- Response includes `detail` and `constraint` fields
- Try to extract existing brickset ID from response (if backend provides it)
- If not available, offer option to search/navigate to list and find it
- Display user-friendly message with navigation option

#### 401 Unauthorized (Authentication Expired)
- User session is invalid or expired
- Clear authentication state from store
- Redirect to login page with return-to URL

#### 500 Internal Server Error
- Show generic error message: "Coś poszło nie tak. Spróbuj ponownie."
- Log error details for debugging
- Offer "Retry" button

## 10. Error Handling

### Frontend Validation Errors

**When validation fails locally** (before API call):
- Show inline errors under each invalid field
- Highlight invalid fields with red border
- Prevent form submission
- Keep form open for correction

**Error display priority**:
1. Required field errors (if field is empty)
2. Type validation errors (if input type is wrong)
3. Range/format validation errors (if value is outside allowed range)

### API Validation Errors (400 Bad Request)

**Structure**:
```json
{
  "errors": {
    "number": ["Ensure this value is less than or equal to 9999999."],
    "owner_initial_estimate": ["Ensure this value is greater than 0."]
  }
}
```

**Frontend handling**:
- Parse error response and map to form fields
- Display server error messages under affected fields
- Replace client-side error messages with server messages (server is source of truth)
- Keep form open for user to fix
- Clear errors when user modifies the field

### Duplicate Set Error (409 Conflict)

**Structure**:
```json
{
  "detail": "BrickSet with this combination already exists.",
  "constraint": "brickset_global_identity"
}
```

**Frontend handling approach 1 - Modal**:
- Show modal dialog: "Zestaw o tej kombinacji już istnieje"
- Display key attributes that caused conflict: number, production_status, completeness, etc.
- Offer button: "Przejdź do istniejącego zestawu"
  - If backend includes existing brickset ID: navigate to `/app/bricksets/{id}`
  - If not: navigate to `/app/bricksets` list
- Keep form data in case user wants to modify and retry

**Frontend handling approach 2 - Toast with Search**:
- Show toast notification: "Zestaw o tej kombinacji już istnieje. Wyświetl podobne zestawy."
- Toast includes quick action link to search results
- Form remains open for modification

**Recommended**: Approach 1 (modal) as it's clearer and follows UX patterns

### Authentication Error (401 Unauthorized)

**When to show**:
- API returns 401 when user token is invalid or expired
- User tries to create brickset without being logged in (should be prevented by router guard)

**Frontend handling**:
- Clear auth state from Pinia store
- Show toast notification: "Twoja sesja wygasła. Zaloguj się ponownie."
- Redirect to `/login` with return-to URL
- Login page can then redirect back to `/app/bricksets/new`

### Generic Server Error (500)

**When to show**:
- API returns 500 or other unexpected status codes

**Frontend handling**:
- Show toast notification: "Coś poszło nie tak. Spróbuj ponownie."
- Log error details to console for debugging
- Show "Retry" button in error message or form level
- Keep form state intact for retry

### Network Error (No Connection)

**When to show**:
- Network request fails (offline, timeout)

**Frontend handling**:
- Show toast notification: "Błąd połączenia. Sprawdź swoją sieć i spróbuj ponownie."
- Show "Retry" button
- Keep form state intact for retry

### Error Dismissal

- User can close/dismiss error messages:
  - By modifying the invalid field (field-level errors disappear when user types)
  - By clicking close button (for general errors)
  - By re-submitting the form

## 11. Implementation Steps

### Step 1: Create Type Definitions

- [ ] Create `src/types/brickset.ts`:
  - `BrickSetFormData`
  - `FieldErrors`
  - `CreateBrickSetRequest`
  - `CreateBrickSetResponse`
  - `TopValuation`
  - `SelectOption`

- [ ] Create `src/types/errors.ts`:
  - `BrickSetValidationError`
  - `BrickSetDuplicateError`

### Step 2: Create API Service

- [ ] Create `src/services/api/bricksetService.ts`:
  - `createBrickSet(data: CreateBrickSetRequest)` function
  - Error handling for 400, 409, 401 responses

- [ ] Create `src/services/errors/BrickSetErrors.ts`:
  - `ValidationError` class
  - `DuplicateError` class
  - `UnauthorizedError` class

### Step 3: Create Custom Composable

- [ ] Create `src/composables/useBrickSetForm.ts`:
  - Initialize form state with default values
  - Field validation logic for each field type
  - Form submission with API integration
  - Error mapping functions
  - Form reset functionality

### Step 4: Create Reusable UI Components

- [ ] Create `src/components/forms/BaseInput.vue`:
  - Number and text input support
  - Label, placeholder, error display
  - Validation feedback

- [ ] Create `src/components/forms/BaseSelect.vue`:
  - Dropdown select with options array
  - Label and error display
  - Default option handling

- [ ] Create `src/components/forms/BaseCheckbox.vue`:
  - Checkbox with label
  - Description/hint text support

- [ ] Create `src/components/forms/InlineError.vue`:
  - Conditional error message display

- [ ] Create `src/components/forms/ValidationErrorList.vue`:
  - Multiple error messages display
  - Optional dismiss functionality

- [ ] Create `src/components/forms/FormActionsBar.vue`:
  - Title, back button, submit button
  - Loading states

### Step 5: Create Main Form Component

- [ ] Create `src/components/forms/BrickSetForm.vue`:
  - Use `useBrickSetForm` composable
  - Compose all BaseInput, BaseSelect, BaseCheckbox components
  - Handle form submission
  - Display validation errors
  - Keyboard support (Enter to submit)
  - Loading state during submission

### Step 6: Create Page Component

- [ ] Create `src/pages/BrickSetCreateView.vue`:
  - Render BrickSetForm component
  - Handle form success → redirect to detail or list view
  - Handle form errors → show toast notifications
  - Handle duplicate (409) → show modal with navigation option
  - Handle authentication (401) → redirect to login
  - Navigate back on cancel
  - Show success toast after creation

### Step 7: Create Router Configuration

- [ ] Add route to `src/router/index.ts`:
  - Path: `/app/bricksets/new`
  - Component: BrickSetCreateView
  - Requires auth: true (router guard)

### Step 8: Create Pinia Store (Optional Enhancement)

- [ ] Create `src/stores/modules/bricksetStore.ts`:
  - Store created brickset data
  - Store creation state
  - Actions for API calls (optional, can use composable directly)

### Step 9: Create i18n Messages

- [ ] Add Polish messages to `src/i18n.ts` or language file:
  - Field labels: "Numer zestawu", "Status produkcji", etc.
  - Placeholders and hints
  - Validation error messages in Polish
  - Success/error toast messages
  - Button labels: "Dodaj zestaw", "Anuluj", etc.

### Step 10: Create Tests

- [ ] Unit tests for `useBrickSetForm` composable:
  - Form initialization
  - Field validation (all field types)
  - Form submission
  - Error handling and mapping

- [ ] Component tests for `BrickSetForm.vue`:
  - Rendering all fields
  - Field input and change events
  - Form submission
  - Error display
  - Loading state

- [ ] Component tests for `BrickSetCreateView.vue`:
  - Form rendering
  - Success navigation
  - Error handling
  - Duplicate set modal

- [ ] Integration tests:
  - Full create flow with API mocking
  - Error scenarios
  - Redirect behavior

### Step 11: Update Navigation

- [ ] Add link to create brickset from list view or main menu
- [ ] Update breadcrumbs if used
- [ ] Ensure navigation guards are properly configured

### Step 12: Testing and QA

- [ ] Manual testing of all user flows:
  - Happy path (successful creation)
  - Field validation errors
  - Duplicate set detection (409)
  - Authentication errors (401)
  - Network errors

- [ ] Keyboard accessibility:
  - Tab through all fields
  - Enter to submit
  - Escape to close modals

- [ ] Visual testing:
  - Error states
  - Loading states
  - Mobile responsive design
  - Focus indicators

### Step 13: Code Review and Documentation

- [ ] Code review with team
- [ ] Update component documentation
- [ ] Update API documentation if needed
- [ ] Add JSDoc comments to functions

### Step 14: Deployment

- [ ] Build and test in development environment
- [ ] Deploy to staging
- [ ] Final QA in staging
- [ ] Deploy to production

---

## Implementation Checklist Summary

- [ ] **Types & DTOs**: 6 main types defined and exported
- [ ] **API Service**: One service function with error handling
- [ ] **Error Classes**: 3 custom error classes
- [ ] **Composable**: Core form logic in `useBrickSetForm`
- [ ] **Base Components**: 6 reusable components (Input, Select, Checkbox, Error, ValidationErrorList, FormActionsBar)
- [ ] **Form Component**: BrickSetForm with full validation and submission
- [ ] **Page Component**: BrickSetCreateView with navigation and error handling
- [ ] **Router**: Route added with auth guard
- [ ] **i18n**: Polish messages added
- [ ] **Tests**: Unit, component, and integration tests
- [ ] **Navigation**: Links and breadcrumbs updated
- [ ] **Documentation**: JSDoc and comments added

---

## Key Design Decisions

1. **Form-first design**: Form state is local to the component, not stored globally, keeping the form self-contained and reusable.

2. **Validation timing**:
   - On blur: Validate individual fields as user moves through form
   - On submit: Validate entire form before API call
   - On input: Clear errors to provide immediate feedback

3. **Error handling hierarchy**:
   - Client validation first (fast feedback)
   - Server validation second (authoritative)
   - Display server errors if they conflict with client validation

4. **409 Conflict handling**: Modal approach provides clear user guidance and option to navigate to existing set without losing form data.

5. **Composable pattern**: `useBrickSetForm` encapsulates all form logic, making it reusable for potential future edit operations without code duplication.

6. **Keyboard accessibility**: Enter key submits form, Escape closes modals, Tab navigates between fields.

7. **Loading state protection**: Submit button disabled during submission to prevent accidental double-submits, visual feedback through button state.

8. **String number binding**: Form data uses string type for `number` and `owner_initial_estimate` to support input binding, converted to number only when submitting to API.

---

## Notes for Implementation

- Ensure all error messages are in Polish per PRD (language: pl)
- Test duplicate detection thoroughly as it's a critical user flow
- Implement proper focus management for accessibility
- Consider debouncing API calls if implementing real-time duplicate checking
- Add analytics/tracking for form completion metrics
- Monitor API response times for timeout handling
- Consider implementing auto-save/draft functionality in future iterations
