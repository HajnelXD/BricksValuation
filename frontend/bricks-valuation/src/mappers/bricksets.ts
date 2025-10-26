/**
 * Bricksets Mapper
 * Converts DTO objects to ViewModel objects for UI rendering
 */

import type {
  BrickSetListItemDTO,
  BrickSetCardViewModel,
  BrickSetListItemViewModel,
  TopValuationViewModel,
  ProductionStatus,
  Completeness,
  OrderingOption,
} from '@/types/bricksets';
import { VALID_ORDERING_OPTIONS } from '@/types/bricksets';

/**
 * Format number to PLN currency string
 */
export function formatCurrency(value: number): string {
  return `${value} PLN`;
}

/**
 * Format production status enum to PL label
 */
export function formatProductionStatusLabel(status: ProductionStatus): string {
  const labels: Record<ProductionStatus, string> = {
    ACTIVE: 'Aktywny',
    RETIRED: 'Wycofany',
  };
  return labels[status];
}

/**
 * Format completeness enum to PL label
 */
export function formatCompletenessLabel(completeness: Completeness): string {
  const labels: Record<Completeness, string> = {
    COMPLETE: 'Kompletny',
    INCOMPLETE: 'Niekompletny',
  };
  return labels[completeness];
}

/**
 * Calculate relative time string (e.g., "3 dni temu")
 * Basic implementation - can be enhanced with libraries like date-fns
 */
export function formatRelativeTime(isoDateString: string): string {
  const date = new Date(isoDateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffDays > 0) {
    return diffDays === 1 ? '1 dzień temu' : `${diffDays} dni temu`;
  }
  if (diffHours > 0) {
    return diffHours === 1 ? '1 godzinę temu' : `${diffHours} godzin temu`;
  }
  if (diffMins > 0) {
    return diffMins === 1 ? '1 minutę temu' : `${diffMins} minut temu`;
  }
  return 'przed chwilą';
}

/**
 * Map top valuation from DTO to ViewModel
 */
export function mapTopValuationToViewModel(
  topValuation: BrickSetListItemDTO['top_valuation'],
): TopValuationViewModel | undefined {
  if (!topValuation) {
    return undefined;
  }

  return {
    id: topValuation.id,
    valueFormatted: formatCurrency(topValuation.value),
    likesCount: topValuation.likes_count,
  };
}

/**
 * Map BrickSet DTO to CardViewModel
 * Main mapping function for list items
 */
export function mapBrickSetDtoToViewModel(dto: BrickSetListItemDTO): BrickSetCardViewModel {
  return {
    id: dto.id,
    number: String(dto.number).padStart(5, '0'),
    productionStatusLabel: formatProductionStatusLabel(dto.production_status),
    completenessLabel: formatCompletenessLabel(dto.completeness),
    hasInstructions: dto.has_instructions,
    hasBox: dto.has_box,
    isFactorySealed: dto.is_factory_sealed,
    valuationsCount: dto.valuations_count,
    totalLikes: dto.total_likes,
    topValuation: mapTopValuationToViewModel(dto.top_valuation),
    createdAtRelative: formatRelativeTime(dto.created_at),
  };
}

/**
 * Map BrickSet DTO to ListItemViewModel (extends CardViewModel with createdAt)
 */
export function mapBrickSetDtoToListItemViewModel(dto: BrickSetListItemDTO): BrickSetListItemViewModel {
  return {
    ...mapBrickSetDtoToViewModel(dto),
    createdAt: dto.created_at,
  };
}

/**
 * Validate ordering option against whitelist
 * Returns valid option or default
 */
export function validateOrderingOption(ordering: any): OrderingOption {
  if (VALID_ORDERING_OPTIONS.includes(ordering)) {
    return ordering as OrderingOption;
  }
  return '-created_at';
}

/**
 * Parse boolean from query parameter string
 * Returns null if not valid "true" or "false"
 */
export function parseBooleanQueryParam(value: string | null | undefined): boolean | null {
  if (value === 'true') return true;
  if (value === 'false') return false;
  return null;
}

/**
 * Serialize boolean to query parameter
 * Only include if true (filter is active)
 */
export function serializeBooleanQueryParam(value: boolean | null): string | null {
  return value === true ? 'true' : null;
}
