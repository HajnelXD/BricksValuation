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
