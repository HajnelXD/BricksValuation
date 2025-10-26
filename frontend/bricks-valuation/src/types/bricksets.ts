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
