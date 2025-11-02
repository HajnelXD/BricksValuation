/**
 * Bricksets Domain Types
 * DTO types from API and internal ViewModel types for UI layer
 */

import type { Ref, ComputedRef } from 'vue';

// Enums for type safety
export type ProductionStatus = 'ACTIVE' | 'RETIRED';
export type Completeness = 'COMPLETE' | 'INCOMPLETE';
export type OrderingOption = '-created_at' | 'created_at' | '-popular' | '-valuations';
export type Currency = 'PLN';

/**
 * DTO - Data Transfer Object from API
 * Represents raw data received from backend
 */
export interface BrickSetListItemDTO {
  id: number;
  number: number;
  production_status: ProductionStatus;
  completeness: Completeness;
  has_instructions: boolean;
  has_box: boolean;
  is_factory_sealed: boolean;
  owner_id: number;
  owner_initial_estimate: number | null;
  valuations_count: number;
  total_likes: number;
  top_valuation?: {
    id: number;
    value: number;
    currency: Currency;
    likes_count: number;
    user_id: number;
  } | null;
  created_at: string;
  updated_at: string;
}

export interface BrickSetListResponseDTO {
  count: number;
  next: string | null;
  previous: string | null;
  results: BrickSetListItemDTO[];
}

/**
 * ViewModel - Internal representation for UI layer
 * Contains formatted and computed values for display
 */
export interface TopValuationViewModel {
  id: number;
  valueFormatted: string; // e.g., '400 PLN'
  likesCount: number;
}

export interface BrickSetCardViewModel {
  id: number;
  number: string; // formatted
  productionStatusLabel: string; // e.g., 'Aktywny' in PL
  completenessLabel: string; // e.g., 'Kompletny' in PL
  hasInstructions: boolean;
  hasBox: boolean;
  isFactorySealed: boolean;
  valuationsCount: number;
  totalLikes: number;
  topValuation?: TopValuationViewModel;
  createdAtRelative: string; // e.g., '3 dni temu'
}

export interface BrickSetListItemViewModel extends BrickSetCardViewModel {
  createdAt: string; // ISO for internal use
}

/**
 * Filter State - Local component/composable state
 * Synchronized with query parameters
 */
export interface BrickSetFiltersState {
  q: string;
  production_status: ProductionStatus | null;
  completeness: Completeness | null;
  has_instructions: boolean | null;
  has_box: boolean | null;
  is_factory_sealed: boolean | null;
  ordering: OrderingOption;
  page: number; // >= 1
  pageSize: number; // internal, default 20
}

export const DEFAULT_FILTERS_STATE: BrickSetFiltersState = {
  q: '',
  production_status: null,
  completeness: null,
  has_instructions: null,
  has_box: null,
  is_factory_sealed: null,
  ordering: '-created_at',
  page: 1,
  pageSize: 20,
};

export const VALID_ORDERING_OPTIONS: OrderingOption[] = [
  '-created_at',
  'created_at',
  '-popular',
  '-valuations',
];

/**
 * API Response wrapper for composition
 */
export interface UseBrickSetListSearchResult {
  items: Readonly<Ref<BrickSetListItemViewModel[]>>;
  count: Readonly<Ref<number>>;
  loading: Readonly<Ref<boolean>>;
  error: Readonly<Ref<string | null>>;
  filters: ComputedRef<BrickSetFiltersState>;
  setFilters: (partial: Partial<BrickSetFiltersState>) => void;
  resetFilters: () => void;
  fetch: () => Promise<void>;
}

/**
 * BrickSet Create/Edit Form Types
 */

/**
 * Form data ViewModel - String representation for input binding
 */
export interface BrickSetFormData {
  number: string; // String for input binding, converted to number on submit
  productionStatus: ProductionStatus;
  completeness: Completeness;
  hasInstructions: boolean;
  hasBox: boolean;
  isFactorySealed: boolean;
  ownerInitialEstimate: string | null; // String for input binding, null when empty
  isDirty: boolean; // Tracks if form has been modified
}

/**
 * Field-level validation errors
 */
export interface FieldErrors {
  number?: string;
  productionStatus?: string;
  completeness?: string;
  hasInstructions?: string;
  hasBox?: string;
  isFactorySealed?: string;
  ownerInitialEstimate?: string;
  general?: string[];
}

/**
 * DTO - Request payload for API
 */
export interface CreateBrickSetRequest {
  number: number;
  production_status: ProductionStatus;
  completeness: Completeness;
  has_instructions: boolean;
  has_box: boolean;
  is_factory_sealed: boolean;
  owner_initial_estimate?: number | null;
}

/**
 * DTO - Response from API after successful creation
 */
export interface CreateBrickSetResponse {
  id: number;
  number: number;
  production_status: ProductionStatus;
  completeness: Completeness;
  has_instructions: boolean;
  has_box: boolean;
  is_factory_sealed: boolean;
  owner_initial_estimate: number | null;
  owner_id: number;
  valuations_count: number;
  total_likes: number;
  top_valuation: {
    id: number;
    value: number;
    user_id: number;
    likes_count: number;
    created_at: string;
  } | null;
  created_at: string; // ISO 8601 timestamp
  updated_at: string; // ISO 8601 timestamp
}

/**
 * DTO - Validation error response from API (400 Bad Request)
 */
export interface BrickSetValidationError {
  errors: {
    [fieldName: string]: string[];
  };
}

/**
 * DTO - Duplicate error response from API (409 Conflict)
 */
export interface BrickSetDuplicateError {
  detail: string;
  constraint: string;
}

/**
 * ViewModel - Info about duplicate set for modal display
 */
export interface DuplicateSetInfo {
  setId: number;
  setNumber: number;
  productionStatus: ProductionStatus;
  completeness: Completeness;
  hasInstructions: boolean;
  hasBox: boolean;
  isFactorySealed: boolean;
  ownerName: string;
}

/**
 * Select option for dropdowns
 */
export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

/**
 * Default form data for initialization
 */
export const DEFAULT_BRICKSET_FORM_DATA: BrickSetFormData = {
  number: '',
  productionStatus: 'ACTIVE',
  completeness: 'COMPLETE',
  hasInstructions: false,
  hasBox: false,
  isFactorySealed: false,
  ownerInitialEstimate: null,
  isDirty: false,
};

/**
 * DTO - Szczegóły zestawu z API
 * Endpoint: GET /api/v1/bricksets/{id}
 */
export interface BrickSetDetailDTO {
  id: number;
  number: number;
  production_status: ProductionStatus;
  completeness: Completeness;
  has_instructions: boolean;
  has_box: boolean;
  is_factory_sealed: boolean;
  owner_initial_estimate: number | null;
  owner_id: number;
  valuations: ValuationDTO[];
  valuations_count: number;
  total_likes: number;
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}

/**
 * DTO - Pojedyncza wycena w odpowiedzi z API
 */
export interface ValuationDTO {
  id: number;
  user_id: number;
  value: number;
  currency: Currency; // "PLN"
  comment: string;
  likes_count: number;
  created_at: string; // ISO 8601
}

/**
 * ViewModel - Szczegóły zestawu dla UI
 */
export interface BrickSetDetailViewModel {
  id: number;
  number: string; // formatowany z zerami wiodącymi
  productionStatusLabel: string;
  completenessLabel: string;
  hasInstructions: boolean;
  hasBox: boolean;
  isFactorySealed: boolean;
  ownerInitialEstimate: number | null;
  ownerId: number;
  valuationsCount: number;
  totalLikes: number;
  topValuation: TopValuationDetailViewModel | null;
  valuations: ValuationViewModel[];
  createdAtRelative: string;
  createdAt: string; // ISO dla potrzeb wewnętrznych
}

/**
 * ViewModel - Wyróżniona TOP wycena
 */
export interface TopValuationDetailViewModel {
  id: number;
  userId: number;
  valueFormatted: string; // "450 PLN"
  comment: string;
  likesCount: number;
  createdAtRelative: string;
}

/**
 * ViewModel - Pojedyncza wycena w liście
 */
export interface ValuationViewModel {
  id: number;
  userId: number;
  valueFormatted: string; // "400 PLN"
  comment: string;
  likesCount: number;
  createdAtRelative: string;
  createdAt: string; // ISO dla sortowania
}

/**
 * ViewModel - Nagłówek zestawu
 */
export interface BrickSetHeaderViewModel {
  number: string;
  productionStatusLabel: string;
  completenessLabel: string;
  hasInstructions: boolean;
  hasBox: boolean;
  isFactorySealed: boolean;
  ownerInitialEstimate: number | null;
  createdAtRelative: string;
}

/**
 * ViewModel - Statystyki zestawu
 */
export interface BrickSetStatsViewModel {
  valuationsCount: number;
  totalLikes: number;
}

/**
 * Edit/Delete Feature Types
 */

/**
 * DTO - BrickSet Detail with editable/deletable flags
 * Extended detail response for edit view with client-side calculated flags
 *
 * Flags are calculated on frontend based on RB-01 business rule:
 * - editable = (total_likes === 0)
 * - deletable = (total_likes === 0)
 */
export interface BrickSetEditDetailDTO extends BrickSetDetailDTO {
  editable: boolean; // Calculated client-side based on valuations/likes
  deletable: boolean; // Calculated client-side based on valuations/likes
}

/**
 * DTO - Partial update request for PATCH
 */
export interface BrickSetUpdateDTO {
  number?: number;
  production_status?: ProductionStatus;
  completeness?: Completeness;
  has_instructions?: boolean;
  has_box?: boolean;
  is_factory_sealed?: boolean;
  owner_initial_estimate?: number | null;
}

/**
 * Form mode type
 */
export type FormMode = 'create' | 'edit';

/**
 * Form actions configuration
 */
export interface FormActionsConfig {
  canSave: boolean;
  canDelete: boolean;
  isSaving: boolean;
  isDeleting: boolean;
}

/**
 * Delete confirmation data
 */
export interface DeleteConfirmData {
  brickSetNumber: string;
  brickSetId: number;
}

/**
 * Rule lock badge type
 */
export type RuleLockType = 'edit' | 'delete' | 'both';

/**
 * Valuation Creation Types
 */

/**
 * DTO - Request payload for creating a valuation
 * Endpoint: POST /api/v1/bricksets/{brickset_id}/valuations
 */
export interface CreateValuationRequest {
  value: number; // 1-999,999
  currency?: string; // Optional, defaults to "PLN"
  comment?: string; // Optional, max 2000 characters
}

/**
 * DTO - Response from API after successful valuation creation
 */
export interface CreateValuationResponse {
  id: number;
  brickset_id: number;
  user_id: number;
  value: number;
  currency: string; // e.g., "PLN"
  comment: string | null;
  likes_count: number;
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}

/**
 * Form data ViewModel - String representation for input binding
 * Used in ValuationFormCard for v-model binding
 */
export interface ValuationFormData {
  value: number | null; // null initially, number after input
  comment: string; // Empty string initially
}

/**
 * Field-level validation errors for valuation form
 */
export interface ValuationValidationErrors {
  value?: string; // Error message for value field
  comment?: string; // Error message for comment field
  general?: string; // General API error message
}

/**
 * API Error response wrapper
 * Handles various error scenarios (validation, duplicate, server error, etc.)
 */
export interface ApiErrorResponse {
  code: string; // e.g., "VALUATION_DUPLICATE", "VALIDATION_ERROR", "BRICKSET_NOT_FOUND"
  message: string; // User-friendly error message
  status: number; // HTTP status code
  details?: Record<string, string[]>; // Optional validation error details per field
}

/**
 * Default valuation form data for initialization
 */
export const DEFAULT_VALUATION_FORM_DATA: ValuationFormData = {
  value: null,
  comment: '',
};

/**
 * API Response wrapper for valuation form composable
 */
export interface UseValuationFormResult {
  formData: Readonly<Ref<ValuationFormData>>;
  errors: Readonly<Ref<ValuationValidationErrors>>;
  isSubmitting: Readonly<Ref<boolean>>;
  touchedFields: Readonly<Ref<Set<string>>>;
  isFormValid: ComputedRef<boolean>;
  canSubmit: ComputedRef<boolean>;
  validateField: (fieldName: keyof ValuationFormData) => void;
  validateForm: () => boolean;
  resetForm: () => void;
  handleSubmit: () => Promise<CreateValuationResponse | null>;
  markFieldTouched: (fieldName: string) => void;
}

/**
 * Valuation Like Types
 */

/**
 * DTO - Request payload for liking a valuation
 * Endpoint: POST /api/v1/valuations/{valuation_id}/likes
 * Empty object - body is optional, POST requires no payload
 */
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface LikeValuationRequest {}

/**
 * DTO - Response from API after successful like
 * Status code: 201 Created
 */
export interface LikeValuationResponse {
  valuation_id: number;
  user_id: number;
  created_at: string; // ISO 8601
}

/**
 * DTO - Error response when trying to like own valuation
 * Status code: 403 Forbidden
 */
export interface LikeForbiddenError {
  detail: string;
  code: 'LIKE_OWN_VALUATION_FORBIDDEN';
}

/**
 * DTO - Error response when trying to like already liked valuation
 * Status code: 409 Conflict
 */
export interface LikeDuplicateError {
  detail: string;
  code: 'LIKE_DUPLICATE';
}

/**
 * ViewModel - State for tracking like interaction
 */
export interface LikeState {
  isLiking: boolean; // Whether API request is in progress
  isLiked: boolean; // Whether current user has liked this valuation
  likesCount: number; // Current number of likes
  error: string | null; // Error message if like failed
}

/**
 * ViewModel - Configuration for LikeButton display
 */
export interface LikeButtonConfig {
  disabled: boolean; // User is author or not authenticated
  loading: boolean; // API request in progress
  liked: boolean; // Whether user has liked
}

/**
 * API Response wrapper for like composable
 */
export interface UseLikeValuationResult {
  isLiking: Readonly<Ref<boolean>>;
  isLiked: Readonly<Ref<boolean>>;
  currentLikesCount: Readonly<Ref<number>>;
  toggleLike: (valuationId: number) => Promise<void>;
  validateCanLike: () => boolean;
}

/**
 * My BrickSets View Types
 * FR-14: Widok "Moje Zestawy" - lista zestawów użytkownika z wycenami i polubienia
 */

/**
 * DTO - Pojedynczy zestaw użytkownika z metrykami
 * Odpowiedź z GET /api/v1/users/me/bricksets
 */
export interface OwnedBrickSetDTO {
  id: number; // Unikalny identyfikator zestawu
  number: number; // Numer zestawu LEGO
  production_status: ProductionStatus; // Status produkcji (ACTIVE|RETIRED)
  completeness: Completeness; // Kompletność (COMPLETE|INCOMPLETE)
  valuations_count: number; // Liczba wycen dodanych do zestawu
  total_likes: number; // Suma wszystkich polubień wycen tego zestawu
  editable: boolean; // Czy zestaw może być edytowany (RB-01)
}

/**
 * DTO - Response z listy moich zestawów
 */
export interface OwnedBrickSetListResponseDTO {
  count: number; // Całkowita liczba zestawów
  next: string | null; // Link do następnej strony
  previous: string | null; // Link do poprzedniej strony
  results: OwnedBrickSetDTO[]; // Zestawy na bieżącej stronie
}

/**
 * ViewModel - Sformatowany zestaw do wyświetlenia w liście
 */
export interface OwnedBrickSetViewModel {
  id: number;
  number: string; // Sformatowany numer zestawu
  productionStatusLabel: string; // Etykieta statusu produkcji
  completenessLabel: string; // Etykieta kompletności
  valuationsCount: number;
  totalLikes: number;
  editable: boolean;
}

/**
 * ViewModel - Filtry i parametry paginacji dla listy moich zestawów
 */
export interface MyBrickSetsFilters {
  page: number; // Numer aktualnej strony (od 1)
  page_size: number; // Liczba wyników na stronę (domyślnie 10)
  ordering: SortOrderingValue; // Sortowanie
}

/**
 * ViewModel - Możliwe wartości sortowania
 */
export type SortOrderingValue = '-created_at' | '-valuations' | '-likes';

/**
 * ViewModel - Opcja sortowania w kontrolce
 */
export interface SortOption {
  value: SortOrderingValue;
  label: string;
}

/**
 * ViewModel - Stan composable do zarządzania listą zestawów użytkownika
 */
export interface UseMyBrickSetsListReturn {
  bricksets: Ref<OwnedBrickSetViewModel[]>;
  totalCount: Ref<number>;
  isLoading: Ref<boolean>;
  error: Ref<Error | null>;
  filters: ComputedRef<MyBrickSetsFilters>;
  totalPages: ComputedRef<number>;
  hasNextPage: ComputedRef<boolean>;
  hasPreviousPage: ComputedRef<boolean>;
  fetchBrickSets: () => Promise<void>;
  changePage: (page: number) => Promise<void>;
  changeSorting: (ordering: SortOrderingValue) => Promise<void>;
  refreshList: () => Promise<void>;
}

const VALID_MY_BRICKSETS_ORDERING: SortOrderingValue[] = [
  '-created_at',
  '-valuations',
  '-likes',
];

export const isValidMyBrickSetsOrdering = (value: unknown): value is SortOrderingValue => {
  return typeof value === 'string' && VALID_MY_BRICKSETS_ORDERING.includes(value as SortOrderingValue);
};

/**
 * My Valuations View Types
 */

/**
 * DTO - Pojedyncza wycena użytkownika z referencją do zestawu
 * Odpowiedź z GET /api/v1/users/me/valuations
 */
export interface OwnedValuationListItemDTO {
  id: number; // ID wyceny
  brickset: {
    id: number; // ID zestawu
    number: number; // Numer zestawu
  };
  value: number; // Wartość wyceny (1-999999)
  currency: 'PLN'; // Kod waluty
  likes_count: number; // Liczba lajków otrzymanych
  created_at: string; // ISO 8601 timestamp utworzenia
}

/**
 * DTO - Response z listy wycen użytkownika
 */
export interface OwnedValuationListResponseDTO {
  count: number; // Całkowita liczba wycen
  results: OwnedValuationListItemDTO[]; // Wyceny na bieżącej stronie
}

/**
 * ViewModel - Pojedyncza wycena sformatowana do wyświetlenia
 */
export interface OwnValuationViewModel {
  id: number;
  bricksetId: number;
  bricksetNumber: string; // Sformatowany numer zestawu
  valueFormatted: string; // np. "450 PLN"
  likesCount: number;
  createdAtRelative: string; // np. "3 dni temu"
  createdAt: string; // ISO dla sortowania
}

/**
 * ViewModel - Stan paginacji
 */
export interface PaginationState {
  currentPage: number;
  pageSize: number;
  totalCount: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}

/**
 * ViewModel - Stan widoku listy wycen
 */
export interface MyValuationsViewState {
  valuations: OwnValuationViewModel[];
  pagination: PaginationState;
  loading: boolean;
  error: string | null;
}
