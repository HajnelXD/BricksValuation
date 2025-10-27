// @ts-ignore
import { config } from '@vue/test-utils';

// Mock translations dictionary
const translations: Record<string, Record<string, Record<string, string>>> = {
  pl: {
    common: {
      reset: 'Wyczyść filtry',
      retry: 'Spróbuj ponownie',
      previous: 'Poprzednia',
      next: 'Następna',
    },
    bricksets: {
      title: 'Zestawy LEGO',
      subtitle: 'zestawów dostępnych',
      authPrompt: 'Zaloguj się aby dodać własny zestaw lub wycenę',
      search: 'Szukaj',
      productionStatus: 'Status produkcji',
      allStatuses: 'Wszystkie',
      active: 'Aktywny',
      retired: 'Wycofany',
      completeness: 'Kompletność',
      allCompletion: 'Wszystkie',
      complete: 'Kompletny',
      incomplete: 'Niekompletny',
      attributes: 'Atrybuty',
      hasInstructions: 'Ma instrukcje',
      hasBox: 'Ma pudełko',
      sealed: 'Zapieczętowany',
      orderBy: 'Sortuj',
      newest: 'Najnowsze',
      oldest: 'Najstarsze',
      popular: 'Najpopularniejsze',
      mostValuations: 'Najwięcej wycen',
      valuations: 'wycen',
      likes: 'lajków',
      noResults: 'Brak zestawów spełniających kryteria.',
      clearFilters: 'Wyczyść filtry',
    },
  },
};

// Create a mock $t function that resolves translation keys
const mockT = (key: string): string => {
  const parts = key.split('.');
  let value: any = translations.pl;

  for (const part of parts) {
    value = value?.[part];
  }

  return typeof value === 'string' ? value : key;
};

// Configure global mocks and properties
config.global.mocks = {
  $t: mockT,
};

config.global.provide = {
  ...config.global.provide,
};



