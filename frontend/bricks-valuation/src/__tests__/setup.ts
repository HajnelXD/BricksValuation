// @ts-expect-error Vitest runtime provides this module resolution during tests
import { config } from '@vue/test-utils';
import { beforeEach, afterEach } from 'vitest';

type TranslationNode = {
  [key: string]: string | TranslationNode;
};

// Mock translations dictionary
const translations: Record<string, TranslationNode> = {
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
      sealed: 'Fabrycznie nowy',
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
  let value: string | TranslationNode | undefined = translations.pl;

  for (const part of parts) {
    if (typeof value === 'object' && value !== null && part in value) {
      value = (value as TranslationNode)[part];
    } else {
      value = undefined;
      break;
    }
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

// Setup DOM elements required by components (e.g., for Teleport)
beforeEach(() => {
  // Create #app div for Teleport components
  const app = document.createElement('div');
  app.id = 'app';
  document.body.appendChild(app);
});

afterEach(() => {
  // Clean up #app div
  const app = document.getElementById('app');
  if (app) {
    document.body.removeChild(app);
  }
});
