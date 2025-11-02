# Plan implementacji widoku My BrickSets

## 1. Przegląd

Widok "My BrickSets" (Moje Zestawy) umożliwia zalogowanemu użytkownikowi przeglądanie listy zestawów LEGO, które dodał do systemu. Widok wyświetla podstawowe informacje o każdym zestawie wraz z kluczowymi metrykami: liczbą wycen (valuations_count) oraz sumą polubień (total_likes). Dodatkowo, każdy zestaw posiada wskaźnik edytowalności, który informuje użytkownika, czy może edytować dany zestaw zgodnie z regułą biznesową RB-01 (edycja możliwa tylko gdy brak obcej wyceny i brak lajków wyceny właściciela).

Widok wspiera:
- Paginację wyników
- Sortowanie po dacie utworzenia, liczbie wycen lub liczbie polubień
- Szybkie przejście do szczegółów zestawu
- Szybkie przejście do edycji zestawu (gdy jest edytowalny)
- Wyświetlanie tooltipów z uzasadnieniem blokady edycji

## 2. Routing widoku

**Ścieżka:** `/app/my/bricksets`

**Parametry query:**
- `page` (number, domyślnie 1) - numer aktualnej strony
- `page_size` (number, domyślnie 10) - liczba wyników na stronę
- `ordering` (string, domyślnie '-created_at') - rodzaj sortowania

**Przykład:** `/app/my/bricksets?page=2&page_size=10&ordering=-valuations`

**Konfiguracja routera:**
```typescript
{
  path: '/app/my/bricksets',
  name: 'MyBrickSets',
  component: () => import('@/pages/bricksets/MyBrickSetsView.vue'),
  meta: { requiresAuth: true }
}
```

## 3. Struktura komponentów

```
MyBrickSetsView (strona główna)
├── PageHeader
│   └── h1 (tytuł strony)
├── ViewControls
│   └── SortControl (kontrolka sortowania)
├── OwnedBrickSetList (lista zestawów)
│   ├── OwnedBrickSetCard (pojedyncza karta zestawu) - v-for
│   │   ├── BrickSetBasicInfo (numer, status, kompletność)
│   │   ├── BrickSetMetrics (liczba wycen, suma lajków)
│   │   └── EditableIndicator (ikona edycji z tooltipem)
│   └── EmptyState (komunikat gdy brak zestawów) - v-if
└── PaginationControls (nawigacja między stronami)
```

## 4. Szczegóły komponentów

### MyBrickSetsView (Główny widok)

**Opis komponentu:**
Główny kontener widoku odpowiedzialny za zarządzanie stanem listy zestawów, koordynację wywołań API, obsługę paginacji i sortowania oraz renderowanie podkomponentów.

**Główne elementy:**
- `<div>` - główny kontener z klasami Tailwind
- `PageHeader` - nagłówek strony z tytułem
- `ViewControls` - sekcja kontrolek (sortowanie)
- `OwnedBrickSetList` - lista kart zestawów
- `PaginationControls` - kontrolki paginacji
- Loading spinner (podczas ładowania danych)
- Error message (w przypadku błędu)

**Obsługiwane interakcje:**
- Zmiana sortowania → aktualizacja query params i fetch danych
- Zmiana strony → aktualizacja query params i fetch danych
- Kliknięcie w kartę zestawu → przejście do szczegółów
- Kliknięcie w ikonę edycji → przejście do edycji (jeśli editable)

**Obsługiwana walidacja:**
- Sprawdzenie czy użytkownik jest zalogowany (guard routera)
- Walidacja query params (konwersja do liczb, sprawdzenie zakresu)
- Obsługa błędu 401 → przekierowanie do logowania

**Typy:**
- `OwnedBrickSetDTO[]` - lista zestawów z API
- `PaginatedResponse<OwnedBrickSetDTO>` - odpowiedź API
- `MyBrickSetsFilters` - filtry i sortowanie
- `SortOption` - opcja sortowania

**Propsy:**
Brak (komponent główny widoku)

### OwnedBrickSetList (Lista zestawów)

**Opis komponentu:**
Komponent odpowiedzialny za renderowanie listy kart zestawów lub komunikatu o pustym stanie. Wykorzystuje grid layout do responsywnego wyświetlania kart.

**Główne elementy:**
- `<div>` - kontener grid z klasami Tailwind (grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4)
- `OwnedBrickSetCard` - karta pojedynczego zestawu (v-for)
- `EmptyState` - komunikat o braku zestawów (v-if)

**Obsługiwane interakcje:**
- Propagacja zdarzeń kliknięcia z kart zestawów do rodzica

**Obsługiwana walidacja:**
- Wyświetlanie EmptyState gdy `bricksets.length === 0 && !isLoading`
- Wyświetlanie loading state gdy `isLoading === true`

**Typy:**
- `OwnedBrickSetDTO[]` - lista zestawów
- `boolean` - isLoading

**Propsy:**
```typescript
interface OwnedBrickSetListProps {
  bricksets: OwnedBrickSetDTO[];
  isLoading: boolean;
}
```

**Emitowane zdarzenia:**
```typescript
{
  'card-click': (bricksetId: number) => void;
  'edit-click': (bricksetId: number) => void;
}
```

### OwnedBrickSetCard (Karta zestawu)

**Opis komponentu:**
Rozszerzona wersja BrickSetCard wyświetlająca podstawowe informacje o zestawie wraz z metrykami (liczba wycen, suma lajków) oraz wskaźnikiem edytowalności. Karta jest klikalna i prowadzi do szczegółów zestawu.

**Główne elementy:**
- `<Card>` - główny kontener karty (Shadcn/vue)
- `<CardHeader>` - nagłówek z numerem zestawu
- `<CardContent>` - treść karty:
  - `BrickSetBasicInfo` - numer, status produkcji, kompletność
  - `BrickSetMetrics` - metryki (ikona + liczba wycen, ikona + suma lajków)
- `<CardFooter>` - stopka z EditableIndicator

**Obsługiwane interakcje:**
- Kliknięcie w kartę → emit 'card-click' z brickset.id
- Kliknięcie w EditableIndicator → emit 'edit-click' z brickset.id (tylko gdy editable)
- Hover na EditableIndicator → wyświetlenie tooltipa

**Obsługiwana walidacja:**
- Renderowanie EditableIndicator tylko gdy dane są załadowane
- Przekazanie właściwego stanu editable do EditableIndicator

**Typy:**
- `OwnedBrickSetDTO` - dane zestawu

**Propsy:**
```typescript
interface OwnedBrickSetCardProps {
  brickset: OwnedBrickSetDTO;
}
```

**Emitowane zdarzenia:**
```typescript
{
  'card-click': (bricksetId: number) => void;
  'edit-click': (bricksetId: number) => void;
}
```

### BrickSetBasicInfo (Podstawowe info o zestawie)

**Opis komponentu:**
Komponent wyświetlający podstawowe informacje o zestawie: numer, status produkcji i kompletność. Używa ikon i badge'y do wizualizacji statusów.

**Główne elementy:**
- `<div>` - kontener flex
- `<span>` - numer zestawu (większa czcionka, bold)
- `<Badge>` - status produkcji (ACTIVE/RETIRED) z różnymi kolorami
- `<Badge>` - kompletność (COMPLETE/INCOMPLETE) z różnymi kolorami

**Obsługiwane interakcje:**
Brak (tylko wyświetlanie)

**Obsługiwana walidacja:**
- Mapowanie production_status na odpowiedni tekst i kolor badge'a
- Mapowanie completeness na odpowiedni tekst i kolor badge'a

**Typy:**
- `ProductionStatus` - 'ACTIVE' | 'RETIRED'
- `Completeness` - 'COMPLETE' | 'INCOMPLETE'

**Propsy:**
```typescript
interface BrickSetBasicInfoProps {
  number: number;
  productionStatus: ProductionStatus;
  completeness: Completeness;
}
```

### BrickSetMetrics (Metryki zestawu)

**Opis komponentu:**
Komponent wyświetlający kluczowe metryki zestawu: liczbę wycen i sumę polubień. Używa ikon do wizualizacji.

**Główne elementy:**
- `<div>` - kontener flex z gap
- `<div>` - metryka wycen:
  - Ikona (np. ClipboardList)
  - `<span>` - liczba wycen
  - `<span>` - label z i18n
- `<div>` - metryka lajków:
  - Ikona (np. Heart)
  - `<span>` - suma lajków
  - `<span>` - label z i18n

**Obsługiwane interakcje:**
Brak (tylko wyświetlanie)

**Obsługiwana walidacja:**
- Wyświetlanie 0 gdy brak wycen lub lajków
- Formatowanie liczb (np. separator tysięcy dla dużych wartości)

**Typy:**
- `number` - valuations_count
- `number` - total_likes

**Propsy:**
```typescript
interface BrickSetMetricsProps {
  valuationsCount: number;
  totalLikes: number;
}
```

### EditableIndicator (Wskaźnik edytowalności)

**Opis komponentu:**
Komponent wyświetlający ikonę ołówka z tooltipem wskazującym czy zestaw jest edytowalny. Gdy zestaw jest edytowalny, ikona jest klikalna i prowadzi do edycji. Gdy nie jest edytowalny, tooltip wyjaśnia powód blokady.

**Główne elementy:**
- `<Tooltip>` - kontener tooltipa (Shadcn/vue)
- `<TooltipTrigger>` - trigger:
  - `<Button>` variant="ghost" size="icon" - przycisk z ikoną ołówka (tylko gdy editable)
  - Ikona ołówka z odpowiednią opacity (pełna gdy editable, zmniejszona gdy nie)
- `<TooltipContent>` - treść tooltipa:
  - Gdy editable: "Kliknij aby edytować zestaw"
  - Gdy nie editable: "Nie można edytować zestawu, ponieważ posiada wyceny innych użytkowników lub polubienia"

**Obsługiwane interakcje:**
- Kliknięcie w ikonę (gdy editable) → emit 'edit-click'
- Hover → wyświetlenie tooltipa

**Obsługiwana walidacja:**
- Wyświetlanie aktywnej ikony tylko gdy editable === true
- Blokada kliknięcia gdy editable === false
- Odpowiedni tekst tooltipa w zależności od stanu editable

**Typy:**
- `boolean` - editable

**Propsy:**
```typescript
interface EditableIndicatorProps {
  editable: boolean;
}
```

**Emitowane zdarzenia:**
```typescript
{
  'edit-click': () => void;
}
```

### SortControl (Kontrolka sortowania)

**Opis komponentu:**
Dropdown/select pozwalający użytkownikowi wybrać sposób sortowania listy zestawów. Opcje to: według daty utworzenia, liczby wycen lub sumy polubień.

**Główne elementy:**
- `<Select>` - komponent select (Shadcn/vue)
- `<SelectTrigger>` - trigger
- `<SelectContent>` - lista opcji
- `<SelectItem>` - pojedyncza opcja (v-for)

**Obsługiwane interakcje:**
- Zmiana wartości → emit 'change' z nową wartością sortowania

**Obsługiwana walidacja:**
- Wyświetlanie aktualnie wybranej opcji
- Walidacja dostępnych opcji sortowania

**Typy:**
- `SortOption[]` - lista opcji
- `string` - aktualna wartość sortowania

**Propsy:**
```typescript
interface SortControlProps {
  modelValue: '-created_at' | '-valuations' | '-likes';
  options: SortOption[];
}
```

**Emitowane zdarzenia:**
```typescript
{
  'update:modelValue': (value: string) => void;
}
```

### PaginationControls (Kontrolki paginacji)

**Opis komponentu:**
Komponent renderujący przyciski nawigacji między stronami wyników. Wykorzystuje komponent Pagination z Shadcn/vue.

**Główne elementy:**
- `<Pagination>` - główny kontener (Shadcn/vue)
- `<PaginationPrevious>` - przycisk poprzednia strona
- `<PaginationList>` - lista numerów stron
- `<PaginationNext>` - przycisk następna strona

**Obsługiwane interakcje:**
- Kliknięcie w numer strony → emit 'page-change' z numerem strony
- Kliknięcie Previous → emit 'page-change' z currentPage - 1
- Kliknięcie Next → emit 'page-change' z currentPage + 1

**Obsługiwana walidacja:**
- Disable przycisku Previous gdy currentPage === 1
- Disable przycisku Next gdy currentPage === totalPages
- Wyświetlanie aktywnej strony
- Obliczanie totalPages na podstawie totalCount i pageSize

**Typy:**
- `number` - currentPage
- `number` - totalCount
- `number` - pageSize

**Propsy:**
```typescript
interface PaginationControlsProps {
  currentPage: number;
  totalCount: number;
  pageSize: number;
}
```

**Emitowane zdarzenia:**
```typescript
{
  'page-change': (page: number) => void;
}
```

### EmptyState (Stan pusty)

**Opis komponentu:**
Komponent wyświetlany gdy użytkownik nie posiada jeszcze żadnych zestawów. Zawiera komunikat zachęcający do dodania pierwszego zestawu oraz przycisk akcji.

**Główne elementy:**
- `<div>` - kontener z centrowaną treścią
- Ikona (np. PackageOpen, duży rozmiar, szary kolor)
- `<h3>` - tytuł "Nie masz jeszcze żadnych zestawów"
- `<p>` - opis "Dodaj swój pierwszy zestaw i uzyskaj wycenę od społeczności"
- `<Button>` - przycisk "Dodaj zestaw"

**Obsługiwane interakcje:**
- Kliknięcie w przycisk → emit 'add-brickset' lub bezpośrednie router.push

**Obsługiwana walidacja:**
Brak

**Typy:**
Brak

**Propsy:**
Brak

**Emitowane zdarzenia:**
```typescript
{
  'add-brickset': () => void;
}
```

## 5. Typy

### Typy DTO (z API)

```typescript
/**
 * Reprezentacja zestawu użytkownika zwracanego przez API
 */
interface OwnedBrickSetDTO {
  /** Unikalny identyfikator zestawu */
  id: number;

  /** Numer zestawu LEGO (do 7 cyfr) */
  number: number;

  /** Status produkcji zestawu */
  production_status: ProductionStatus;

  /** Kompletność zestawu */
  completeness: Completeness;

  /** Liczba wycen dodanych do zestawu */
  valuations_count: number;

  /** Suma wszystkich polubień wycen tego zestawu */
  total_likes: number;

  /** Czy zestaw może być edytowany (zgodnie z RB-01) */
  editable: boolean;
}

/**
 * Status produkcji zestawu LEGO
 */
type ProductionStatus = 'ACTIVE' | 'RETIRED';

/**
 * Kompletność zestawu
 */
type Completeness = 'COMPLETE' | 'INCOMPLETE';

/**
 * Generyczna odpowiedź paginowana z API
 */
interface PaginatedResponse<T> {
  /** Całkowita liczba wyników */
  count: number;

  /** Link do następnej strony (jeśli istnieje) */
  next?: string | null;

  /** Link do poprzedniej strony (jeśli istnieje) */
  previous?: string | null;

  /** Tablica wyników dla bieżącej strony */
  results: T[];
}
```

### Typy ViewModel (wewnętrzne)

```typescript
/**
 * Filtry i parametry dla listy moich zestawów
 */
interface MyBrickSetsFilters {
  /** Numer aktualnej strony (od 1) */
  page: number;

  /** Liczba wyników na stronę */
  page_size: number;

  /** Pole i kierunek sortowania (prefix "-" oznacza malejąco) */
  ordering: SortOrderingValue;
}

/**
 * Możliwe wartości sortowania
 */
type SortOrderingValue = '-created_at' | '-valuations' | '-likes';

/**
 * Opcja sortowania w kontrolce
 */
interface SortOption {
  /** Wartość przekazywana do API */
  value: SortOrderingValue;

  /** Wyświetlana etykieta (z i18n) */
  label: string;
}

/**
 * Stan composable do zarządzania listą zestawów
 */
interface MyBrickSetsState {
  /** Lista zestawów */
  bricksets: OwnedBrickSetDTO[];

  /** Całkowita liczba zestawów */
  totalCount: number;

  /** Czy dane są w trakcie ładowania */
  isLoading: boolean;

  /** Obiekt błędu (jeśli wystąpił) */
  error: Error | null;

  /** Aktualne filtry i sortowanie */
  filters: MyBrickSetsFilters;
}
```

### Typy dla mapowania i18n

```typescript
/**
 * Klucze tłumaczeń dla widoku My BrickSets
 */
interface MyBrickSetsTranslations {
  title: string; // "Moje Zestawy"
  sort: {
    label: string; // "Sortuj według"
    createdAt: string; // "Data dodania"
    valuations: string; // "Liczba wycen"
    likes: string; // "Liczba polubień"
  };
  metrics: {
    valuations: string; // "Wyceny"
    likes: string; // "Polubienia"
  };
  editable: {
    tooltipEditable: string; // "Kliknij aby edytować zestaw"
    tooltipNotEditable: string; // "Nie można edytować zestawu..."
  };
  empty: {
    title: string; // "Nie masz jeszcze żadnych zestawów"
    description: string; // "Dodaj swój pierwszy zestaw..."
    action: string; // "Dodaj zestaw"
  };
  productionStatus: {
    active: string; // "Produkowany"
    retired: string; // "Wycofany"
  };
  completeness: {
    complete: string; // "Kompletny"
    incomplete: string; // "Niekompletny"
  };
}
```

## 6. Zarządzanie stanem

### Strategia zarządzania stanem

Widok wykorzystuje kombinację lokalnego stanu Vue oraz custom composable `useMyBrickSetsList` do zarządzania stanem listy zestawów, paginacji i sortowania.

### Custom Composable: useMyBrickSetsList

**Lokalizacja:** `src/composables/useMyBrickSetsList.ts`

**Odpowiedzialności:**
- Zarządzanie stanem listy zestawów
- Wykonywanie zapytań API
- Obsługa paginacji i sortowania
- Synchronizacja z query params routera
- Obsługa błędów i stanu ładowania

**Interfejs:**

```typescript
interface UseMyBrickSetsListReturn {
  // Stan
  bricksets: Ref<OwnedBrickSetDTO[]>;
  totalCount: Ref<number>;
  isLoading: Ref<boolean>;
  error: Ref<Error | null>;
  filters: Ref<MyBrickSetsFilters>;

  // Computed
  totalPages: ComputedRef<number>;
  hasNextPage: ComputedRef<boolean>;
  hasPreviousPage: ComputedRef<boolean>;

  // Metody
  fetchBrickSets: () => Promise<void>;
  changePage: (page: number) => Promise<void>;
  changeSorting: (ordering: SortOrderingValue) => Promise<void>;
  refreshList: () => Promise<void>;
}

function useMyBrickSetsList(): UseMyBrickSetsListReturn
```

**Implementacja logiki:**

1. **Inicjalizacja:**
   - Odczytanie query params z routera
   - Ustawienie domyślnych wartości (page=1, page_size=10, ordering='-created_at')
   - Walidacja i sanitizacja parametrów

2. **Synchronizacja z routerem:**
   - Watcher na `route.query` aktualizujący filters
   - Aktualizacja query params przy zmianie filters
   - Użycie `router.replace` zamiast `router.push` aby uniknąć duplikatów w historii

3. **Pobieranie danych:**
   - Ustawienie `isLoading = true`
   - Wywołanie API `GET /api/v1/users/me/bricksets` z query params
   - Aktualizacja `bricksets` i `totalCount`
   - Obsługa błędów (w tym 401)
   - Ustawienie `isLoading = false`

4. **Zmiana strony:**
   - Aktualizacja `filters.page`
   - Aktualizacja query params routera
   - Automatyczne wywołanie fetchBrickSets (przez watcher)

5. **Zmiana sortowania:**
   - Aktualizacja `filters.ordering`
   - Reset `filters.page` do 1 (powrót na pierwszą stronę)
   - Aktualizacja query params routera
   - Automatyczne wywołanie fetchBrickSets

6. **Odświeżanie:**
   - Ponowne wywołanie fetchBrickSets z aktualnymi filters

### Zarządzanie stanem lokalnym w komponencie

**MyBrickSetsView:**
- Wykorzystuje composable `useMyBrickSetsList`
- Nie zarządza dodatkowym stanem globalnym
- Całość stanu jest lokalna dla widoku

**Brak użycia Pinia Store:**
Ze względu na lokalny charakter danych (specyficzne dla widoku, nieużywane globalnie), nie ma potrzeby wykorzystania Pinia. Composable zapewnia wystarczającą abstrakcję i reużywalność.

## 7. Integracja API

### Endpoint: GET /api/v1/users/me/bricksets

**Typ żądania:**
```typescript
interface GetMyBricksetsRequest {
  page?: number;           // Domyślnie: 1
  page_size?: number;      // Domyślnie: 10
  ordering?: SortOrderingValue; // Domyślnie: '-created_at'
}
```

**Typ odpowiedzi (Success 200):**
```typescript
type GetMyBricksetsResponse = PaginatedResponse<OwnedBrickSetDTO>;

// Przykład:
{
  count: 25,
  next: "/api/v1/users/me/bricksets?page=3&page_size=10&ordering=-valuations",
  previous: "/api/v1/users/me/bricksets?page=1&page_size=10&ordering=-valuations",
  results: [
    {
      id: 10,
      number: 12345,
      production_status: "ACTIVE",
      completeness: "COMPLETE",
      valuations_count: 5,
      total_likes: 12,
      editable: true
    },
    // ... więcej wyników
  ]
}
```

**Typ odpowiedzi (Error 401):**
```typescript
interface UnauthorizedError {
  detail: string; // "NOT_AUTHENTICATED"
}
```

### Implementacja wywołania API

**Lokalizacja:** `src/api/bricksets.ts`

```typescript
import { apiClient } from '@/api/client';

export async function getMyBricksets(
  params: GetMyBricksetsRequest
): Promise<GetMyBricksetsResponse> {
  const response = await apiClient.get<GetMyBricksetsResponse>(
    '/api/v1/users/me/bricksets',
    { params }
  );
  return response.data;
}
```

### Obsługa błędów API

1. **401 NOT_AUTHENTICATED:**
   - Przechwycenie w interceptorze axios
   - Wyczyszczenie sesji użytkownika
   - Przekierowanie do strony logowania
   - Wyświetlenie toast notification: "Sesja wygasła. Zaloguj się ponownie."

2. **Błędy sieciowe (timeout, brak połączenia):**
   - Ustawienie `error` w stanie composable
   - Wyświetlenie komunikatu błędu w widoku
   - Możliwość ponowienia próby (przycisk "Spróbuj ponownie")

3. **Błędy 500:**
   - Wyświetlenie ogólnego komunikatu błędu
   - Logowanie błędu do konsoli (w dev mode)
   - Możliwość ponowienia próby

4. **Błędy walidacji (400):**
   - Wyświetlenie szczegółowego komunikatu błędu
   - Reset do domyślnych parametrów

### Interceptory axios

```typescript
// Request interceptor - dodawanie tokenu
apiClient.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - obsługa 401
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearAuthToken();
      router.push('/login');
      toast.error('Sesja wygasła. Zaloguj się ponownie.');
    }
    return Promise.reject(error);
  }
);
```

## 8. Interakcje użytkownika

### 1. Wejście na stronę

**Akcja użytkownika:** Użytkownik klika link "Moje Zestawy" w nawigacji lub wpisuje URL `/app/my/bricksets`

**Przepływ:**
1. Router weryfikuje czy użytkownik jest zalogowany (meta: requiresAuth)
2. Jeśli niezalogowany → przekierowanie do `/login`
3. Jeśli zalogowany → montowanie komponentu MyBrickSetsView
4. Composable `useMyBrickSetsList` inicjalizuje się:
   - Odczytuje query params lub ustawia domyślne
   - Wywołuje `fetchBrickSets()`
5. Wyświetlenie loading spinner podczas ładowania
6. Po załadowaniu:
   - Jeśli wyniki > 0 → renderowanie listy kart
   - Jeśli wyniki === 0 → renderowanie EmptyState

**Wynik:** Użytkownik widzi listę swoich zestawów lub komunikat o pustym stanie

### 2. Zmiana sortowania

**Akcja użytkownika:** Użytkownik otwiera dropdown sortowania i wybiera opcję (np. "Liczba wycen")

**Przepływ:**
1. Kliknięcie w SortControl
2. Wybór opcji → emit 'update:modelValue' z wartością '-valuations'
3. Obsługa w MyBrickSetsView → wywołanie `changeSorting('-valuations')`
4. Composable:
   - Aktualizuje `filters.ordering = '-valuations'`
   - Resetuje `filters.page = 1`
   - Aktualizuje query params: `?page=1&ordering=-valuations`
5. Watcher na query params wywołuje `fetchBrickSets()`
6. Wyświetlenie loading spinner
7. Aktualizacja listy z nowymi danymi

**Wynik:** Lista zestawów posortowana według liczby wycen (malejąco), użytkownik na pierwszej stronie

### 3. Zmiana strony

**Akcja użytkownika:** Użytkownik klika przycisk "Następna strona" lub konkretny numer strony w paginacji

**Przepływ:**
1. Kliknięcie w PaginationControls
2. Emit 'page-change' z numerem strony (np. 2)
3. Obsługa w MyBrickSetsView → wywołanie `changePage(2)`
4. Composable:
   - Aktualizuje `filters.page = 2`
   - Aktualizuje query params: `?page=2&ordering=-valuations`
5. Watcher wywołuje `fetchBrickSets()`
6. Wyświetlenie loading spinner
7. Aktualizacja listy z danymi ze strony 2

**Wynik:** Użytkownik widzi zestawy ze strony 2, zachowane sortowanie

### 4. Kliknięcie w kartę zestawu

**Akcja użytkownika:** Użytkownik klika w kartę zestawu (poza ikoną edycji)

**Przepływ:**
1. Kliknięcie w OwnedBrickSetCard
2. Emit 'card-click' z brickset.id (np. 10)
3. Obsługa w MyBrickSetsView → `router.push(\`/app/bricksets/\${id}\`)`
4. Przejście do widoku szczegółów zestawu

**Wynik:** Użytkownik widzi szczegóły wybranego zestawu

### 5. Kliknięcie w ikonę edycji (zestaw edytowalny)

**Akcja użytkownika:** Użytkownik klika w ikonę ołówka na zestawie, który jest edytowalny

**Przepływ:**
1. Kliknięcie w EditableIndicator (gdy editable=true)
2. Propagacja zdarzenia przez kartę (emit 'edit-click')
3. Obsługa w MyBrickSetsView → `router.push(\`/app/my/bricksets/\${id}/edit\`)`
4. Przejście do widoku edycji zestawu

**Wynik:** Użytkownik widzi formularz edycji zestawu

### 6. Hover na ikonie edycji (zestaw nieedytowalny)

**Akcja użytkownika:** Użytkownik najeżdża myszą na ikonę ołówka na zestawie, który nie jest edytowalny

**Przepływ:**
1. Hover na EditableIndicator (gdy editable=false)
2. Wyświetlenie Tooltip z treścią:
   "Nie można edytować zestawu, ponieważ posiada wyceny innych użytkowników lub polubienia"

**Wynik:** Użytkownik rozumie dlaczego nie może edytować zestawu

### 7. Kliknięcie "Dodaj zestaw" w EmptyState

**Akcja użytkownika:** Użytkownik klika przycisk "Dodaj zestaw" gdy nie ma jeszcze żadnych zestawów

**Przepływ:**
1. Kliknięcie w Button w EmptyState
2. Przekierowanie: `router.push('/app/bricksets/new')`
3. Przejście do widoku dodawania zestawu

**Wynik:** Użytkownik widzi formularz dodawania nowego zestawu

### 8. Powrót do widoku po edycji

**Akcja użytkownika:** Użytkownik zapisuje zmiany w formularzu edycji i wraca do listy (np. kliknięcie "Anuluj" lub zakończenie edycji)

**Przepływ:**
1. Router push z widoku edycji: `router.push('/app/my/bricksets')`
2. Ponowne montowanie lub reaktywacja MyBrickSetsView
3. Wywołanie `refreshList()` w composable (w onMounted lub onActivated)
4. Aktualizacja danych z API

**Wynik:** Użytkownik widzi zaktualizowaną listę zestawów z naniesionymi zmianami

## 9. Warunki i walidacja

### Warunki weryfikowane przez interfejs

#### 1. Autentykacja użytkownika

**Gdzie:** Route guard w konfiguracji routera

**Warunek:** Użytkownik musi być zalogowany

**Walidacja:**
```typescript
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next('/login');
  } else {
    next();
  }
});
```

**Wpływ na UI:** Przekierowanie do strony logowania jeśli użytkownik niezalogowany

#### 2. Edytowalność zestawu

**Gdzie:** Komponent EditableIndicator

**Warunek:** `brickset.editable === true` (wynikający z RB-01: brak obcej wyceny i brak lajków wyceny właściciela)

**Walidacja:**
```typescript
const isEditable = computed(() => props.editable);
const canEdit = computed(() => isEditable.value);
```

**Wpływ na UI:**
- Gdy `editable=true`: Ikona pełnej opacity, klikalny przycisk, tooltip "Kliknij aby edytować"
- Gdy `editable=false`: Ikona zmniejszonej opacity, nieaktywny przycisk, tooltip z wyjaśnieniem blokady

#### 3. Paginacja - poprzednia strona

**Gdzie:** Komponent PaginationControls

**Warunek:** `currentPage > 1`

**Walidacja:**
```typescript
const hasPreviousPage = computed(() => props.currentPage > 1);
```

**Wpływ na UI:** Przycisk "Poprzednia" disabled gdy currentPage === 1

#### 4. Paginacja - następna strona

**Gdzie:** Komponent PaginationControls

**Warunek:** `currentPage < totalPages`

**Walidacja:**
```typescript
const totalPages = computed(() =>
  Math.ceil(props.totalCount / props.pageSize)
);
const hasNextPage = computed(() =>
  props.currentPage < totalPages.value
);
```

**Wpływ na UI:** Przycisk "Następna" disabled gdy currentPage === totalPages

#### 5. Wyświetlanie pustego stanu

**Gdzie:** Komponent OwnedBrickSetList

**Warunek:** `bricksets.length === 0 && !isLoading && !error`

**Walidacja:**
```typescript
const shouldShowEmpty = computed(() =>
  props.bricksets.length === 0 && !props.isLoading
);
```

**Wpływ na UI:** Wyświetlenie EmptyState zamiast listy kart

#### 6. Walidacja query params

**Gdzie:** Composable useMyBrickSetsList

**Warunki:**
- `page` musi być liczbą całkowitą > 0
- `page_size` musi być liczbą całkowitą z zakresu 1-100
- `ordering` musi być jedną z dozwolonych wartości

**Walidacja:**
```typescript
const sanitizeFilters = (query: LocationQuery): MyBrickSetsFilters => {
  const page = Math.max(1, parseInt(query.page as string) || 1);
  const page_size = Math.min(100, Math.max(1, parseInt(query.page_size as string) || 10));
  const ordering = isValidOrdering(query.ordering)
    ? query.ordering as SortOrderingValue
    : '-created_at';

  return { page, page_size, ordering };
};
```

**Wpływ na UI:** Automatyczna korekta nieprawidłowych parametrów do wartości domyślnych

#### 7. Stan ładowania

**Gdzie:** Komponent MyBrickSetsView

**Warunek:** `isLoading === true`

**Walidacja:**
```typescript
const showLoader = computed(() => isLoading.value);
```

**Wpływ na UI:** Wyświetlenie loading spinner, ukrycie listy i paginacji

#### 8. Stan błędu

**Gdzie:** Komponent MyBrickSetsView

**Warunek:** `error !== null`

**Walidacja:**
```typescript
const hasError = computed(() => error.value !== null);
```

**Wpływ na UI:** Wyświetlenie komunikatu błędu z przyciskiem "Spróbuj ponownie"

### Tabela podsumowująca warunki

| Warunek | Komponent | Wpływ na UI | Typ walidacji |
|---------|-----------|-------------|---------------|
| Autentykacja | Router Guard | Przekierowanie do logowania | Hard (blokada dostępu) |
| Edytowalność | EditableIndicator | Aktywna/nieaktywna ikona, różne tooltips | Soft (informacyjna) |
| Pierwsza strona | PaginationControls | Disabled przycisk "Poprzednia" | Soft (UX) |
| Ostatnia strona | PaginationControls | Disabled przycisk "Następna" | Soft (UX) |
| Pusta lista | OwnedBrickSetList | EmptyState vs lista kart | Prezentacyjna |
| Query params | useMyBrickSetsList | Sanitizacja do poprawnych wartości | Hard (korekta danych) |
| Ładowanie | MyBrickSetsView | Loading spinner | Prezentacyjna |
| Błąd | MyBrickSetsView | Komunikat błędu | Prezentacyjna |

## 10. Obsługa błędów

### 1. Błąd 401 - NOT_AUTHENTICATED

**Scenariusz:** Token wygasł lub użytkownik został wylogowany w innej zakładce

**Obsługa:**
- Przechwycenie w interceptorze axios
- Wyczyszczenie tokenu z localStorage
- Przekierowanie do `/login` z parametrem `redirect`:
  ```typescript
  router.push({
    path: '/login',
    query: { redirect: '/app/my/bricksets' }
  });
  ```
- Wyświetlenie toast notification: "Sesja wygasła. Zaloguj się ponownie."

**Wynik dla użytkownika:** Przekierowanie do logowania, po zalogowaniu powrót do listy zestawów

### 2. Błąd sieciowy (timeout, brak połączenia)

**Scenariusz:** Brak internetu, serwer niedostępny, przekroczenie timeout

**Obsługa:**
- Przechwycenie błędu w composable
- Ustawienie `error.value = new Error('Błąd połączenia')`
- Wyświetlenie w UI:
  ```
  [Ikona ostrzeżenia]
  Nie udało się załadować zestawów
  Sprawdź połączenie z internetem i spróbuj ponownie.
  [Przycisk: Spróbuj ponownie]
  ```
- Kliknięcie "Spróbuj ponownie" → wywołanie `refreshList()`

**Wynik dla użytkownika:** Informacja o problemie i możliwość ponowienia próby

### 3. Błąd 500 - Internal Server Error

**Scenariusz:** Błąd po stronie serwera

**Obsługa:**
- Przechwycenie błędu w composable
- Ustawienie `error.value = new Error('Błąd serwera')`
- Logowanie szczegółów błędu do konsoli (dev mode)
- Wyświetlenie w UI:
  ```
  [Ikona błędu]
  Wystąpił problem po stronie serwera
  Spróbuj ponownie za chwilę.
  [Przycisk: Spróbuj ponownie]
  ```

**Wynik dla użytkownika:** Informacja o tymczasowym problemie, możliwość ponowienia

### 4. Błąd 400 - Bad Request (nieprawidłowe parametry)

**Scenariusz:** Nieprawidłowe query params (teoretycznie nie powinno wystąpić przez sanitizację)

**Obsługa:**
- Przechwycenie błędu w composable
- Reset filtrów do wartości domyślnych
- Wywołanie `fetchBrickSets()` z domyślnymi parametrami
- Wyświetlenie toast notification: "Nieprawidłowe parametry. Zresetowano do domyślnych."

**Wynik dla użytkownika:** Automatyczna korekta, wyświetlenie wyników z domyślnymi parametrami

### 5. Pusta odpowiedź (0 wyników)

**Scenariusz:** Użytkownik nie ma jeszcze żadnych zestawów

**Obsługa:**
- Sprawdzenie `bricksets.length === 0 && !isLoading && !error`
- Renderowanie komponentu EmptyState
- Wyświetlenie zachęty do dodania pierwszego zestawu

**Wynik dla użytkownika:** Komunikat "Nie masz jeszcze żadnych zestawów" z przyciskiem akcji

### 6. Błąd podczas sortowania/paginacji

**Scenariusz:** Błąd API podczas zmiany strony lub sortowania

**Obsługa:**
- Zachowanie poprzedniego stanu (lista nie jest czyszczona)
- Wyświetlenie toast notification: "Nie udało się załadować danych. Spróbuj ponownie."
- Logowanie błędu
- Użytkownik może spróbować ponownie (kliknięcie w tę samą opcję)

**Wynik dla użytkownika:** Brak utraty aktualnie wyświetlanych danych, informacja o błędzie

### 7. Utrata połączenia podczas ładowania

**Scenariusz:** Użytkownik traci internet podczas fetchowania danych

**Obsługa:**
- Timeout po 30 sekundach
- Ustawienie error state
- Wyświetlenie komunikatu jak w punkcie 2
- Zachowanie poprzednich danych (jeśli istniały)

**Wynik dla użytkownika:** Informacja o problemie, poprzednie dane wciąż widoczne

### 8. Nawigacja podczas ładowania

**Scenariusz:** Użytkownik opuszcza stronę przed zakończeniem ładowania

**Obsługa:**
- Anulowanie pending request (axios cancel token)
- Cleanup w `onBeforeUnmount`:
  ```typescript
  onBeforeUnmount(() => {
    abortController.abort();
  });
  ```

**Wynik dla użytkownika:** Brak wycieków pamięci, brak niepotrzebnych requestów

### Centralna obsługa błędów

```typescript
// composables/useMyBrickSetsList.ts
const handleError = (error: unknown) => {
  if (axios.isAxiosError(error)) {
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      error.value = new Error('Przekroczono limit czasu. Sprawdź połączenie.');
    } else if (error.response?.status === 500) {
      error.value = new Error('Błąd serwera. Spróbuj ponownie później.');
    } else if (error.response?.status === 400) {
      // Reset do domyślnych parametrów
      filters.value = getDefaultFilters();
      toast.warning('Nieprawidłowe parametry. Zresetowano do domyślnych.');
      return; // Nie ustawiaj error, bo automatycznie robimy retry
    } else {
      error.value = new Error('Wystąpił nieoczekiwany błąd.');
    }
  } else {
    error.value = error as Error;
  }

  console.error('Error fetching bricksets:', error);
};
```

## 11. Kroki implementacji

### Krok 1: Przygotowanie typów i interfejsów

**Plik:** `src/types/bricksets.ts`

**Zadania:**
1. Zdefiniowanie `OwnedBrickSetDTO`
2. Zdefiniowanie `PaginatedResponse<T>`
3. Zdefiniowanie `ProductionStatus` i `Completeness`
4. Zdefiniowanie `MyBrickSetsFilters`
5. Zdefiniowanie `SortOrderingValue` i `SortOption`

**Rezultat:** Wszystkie typy dostępne do wykorzystania w komponentach i composables

### Krok 2: Implementacja wywołania API

**Plik:** `src/api/bricksets.ts`

**Zadania:**
1. Utworzenie funkcji `getMyBricksets(params: GetMyBricksetsRequest)`
2. Konfiguracja wywołania GET z query params
3. Zwracanie typowanej odpowiedzi

**Rezultat:** Funkcja API gotowa do użycia w composable

### Krok 3: Implementacja composable useMyBrickSetsList

**Plik:** `src/composables/useMyBrickSetsList.ts`

**Zadania:**
1. Zdefiniowanie reactive state (bricksets, totalCount, isLoading, error, filters)
2. Implementacja `fetchBrickSets()`:
   - Ustawienie isLoading
   - Wywołanie API
   - Aktualizacja stanu
   - Obsługa błędów
3. Implementacja `changePage(page)`:
   - Aktualizacja filters.page
   - Aktualizacja router query params
4. Implementacja `changeSorting(ordering)`:
   - Aktualizacja filters.ordering
   - Reset page do 1
   - Aktualizacja router query params
5. Implementacja `refreshList()`:
   - Ponowne wywołanie fetchBrickSets
6. Utworzenie computed properties (totalPages, hasNextPage, hasPreviousPage)
7. Dodanie watchers na route.query
8. Wywołanie fetchBrickSets w onMounted

**Rezultat:** Funkcjonalny composable zarządzający stanem listy

### Krok 4: Dodanie tłumaczeń i18n

**Plik:** `src/locales/pl.json`

**Zadania:**
1. Dodanie sekcji `myBrickSets`:
   ```json
   "myBrickSets": {
     "title": "Moje Zestawy",
     "sort": {
       "label": "Sortuj według",
       "createdAt": "Daty dodania",
       "valuations": "Liczby wycen",
       "likes": "Liczby polubień"
     },
     "metrics": {
       "valuations": "Wyceny",
       "likes": "Polubienia"
     },
     "editable": {
       "tooltipEditable": "Kliknij aby edytować zestaw",
       "tooltipNotEditable": "Nie można edytować zestawu, ponieważ posiada wyceny innych użytkowników lub polubienia"
     },
     "empty": {
       "title": "Nie masz jeszcze żadnych zestawów",
       "description": "Dodaj swój pierwszy zestaw i uzyskaj wycenę od społeczności",
       "action": "Dodaj zestaw"
     },
     "productionStatus": {
       "active": "Produkowany",
       "retired": "Wycofany"
     },
     "completeness": {
       "complete": "Kompletny",
       "incomplete": "Niekompletny"
     }
   }
   ```

**Rezultat:** Wszystkie teksty dostępne przez i18n

### Krok 5: Implementacja komponentu EmptyState

**Plik:** `src/components/bricksets/EmptyState.vue`

**Zadania:**
1. Utworzenie struktury HTML z ikoną, tekstem i przyciskiem
2. Wykorzystanie i18n dla tekstów
3. Obsługa kliknięcia przycisku → router.push('/app/bricksets/new')
4. Stylowanie z Tailwind (centrowanie, spacing)

**Rezultat:** Komponent pustego stanu gotowy do użycia

### Krok 6: Implementacja komponentu BrickSetBasicInfo

**Plik:** `src/components/bricksets/BrickSetBasicInfo.vue`

**Zadania:**
1. Zdefiniowanie props (number, productionStatus, completeness)
2. Utworzenie struktury HTML z numerem i badge'ami
3. Mapowanie statusów na kolory badge'ów
4. Wykorzystanie i18n dla etykiet
5. Stylowanie z Tailwind

**Rezultat:** Komponent wyświetlający podstawowe info o zestawie

### Krok 7: Implementacja komponentu BrickSetMetrics

**Plik:** `src/components/bricksets/BrickSetMetrics.vue`

**Zadania:**
1. Zdefiniowanie props (valuationsCount, totalLikes)
2. Utworzenie struktury HTML z ikonami i liczbami
3. Wykorzystanie ikon z biblioteki (np. lucide-vue-next)
4. Formatowanie liczb (separator tysięcy)
5. Wykorzystanie i18n dla etykiet
6. Stylowanie z Tailwind

**Rezultat:** Komponent wyświetlający metryki zestawu

### Krok 8: Implementacja komponentu EditableIndicator

**Plik:** `src/components/bricksets/EditableIndicator.vue`

**Zadania:**
1. Zdefiniowanie props (editable)
2. Zdefiniowanie emits (edit-click)
3. Utworzenie struktury z Tooltip (Shadcn/vue)
4. Warunkowe renderowanie aktywnej/nieaktywnej ikony
5. Dynamiczny tekst tooltipa w zależności od editable
6. Obsługa kliknięcia (tylko gdy editable)
7. Stylowanie z Tailwind

**Rezultat:** Komponent wskaźnika edytowalności

### Krok 9: Implementacja komponentu OwnedBrickSetCard

**Plik:** `src/components/bricksets/OwnedBrickSetCard.vue`

**Zadania:**
1. Zdefiniowanie props (brickset: OwnedBrickSetDTO)
2. Zdefiniowanie emits (card-click, edit-click)
3. Utworzenie struktury Card (Shadcn/vue)
4. Wykorzystanie podkomponentów (BrickSetBasicInfo, BrickSetMetrics, EditableIndicator)
5. Obsługa kliknięcia w kartę
6. Propagacja zdarzenia edit-click
7. Stylowanie z Tailwind (hover effects, transitions)

**Rezultat:** Komponent karty zestawu

### Krok 10: Implementacja komponentu SortControl

**Plik:** `src/components/bricksets/SortControl.vue`

**Zadania:**
1. Zdefiniowanie props (modelValue, options)
2. Zdefiniowanie emits (update:modelValue)
3. Wykorzystanie Select (Shadcn/vue)
4. Renderowanie opcji z v-for
5. Obsługa zmiany wartości
6. Wykorzystanie i18n dla etykiet
7. Stylowanie z Tailwind

**Rezultat:** Komponent kontrolki sortowania

### Krok 11: Implementacja komponentu PaginationControls

**Plik:** `src/components/bricksets/PaginationControls.vue`

**Zadania:**
1. Zdefiniowanie props (currentPage, totalCount, pageSize)
2. Zdefiniowanie emits (page-change)
3. Obliczenie totalPages
4. Wykorzystanie Pagination (Shadcn/vue)
5. Warunkowe disabled dla przycisków Previous/Next
6. Obsługa kliknięcia w numerację
7. Stylowanie z Tailwind

**Rezultat:** Komponent paginacji

### Krok 12: Implementacja komponentu OwnedBrickSetList

**Plik:** `src/components/bricksets/OwnedBrickSetList.vue`

**Zadania:**
1. Zdefiniowanie props (bricksets, isLoading)
2. Zdefiniowanie emits (card-click, edit-click)
3. Warunkowe renderowanie (loading, empty, list)
4. Renderowanie kart z v-for
5. Propagacja zdarzeń
6. Grid layout z Tailwind (responsywny)

**Rezultat:** Komponent listy zestawów

### Krok 13: Implementacja głównego widoku MyBrickSetsView

**Plik:** `src/pages/bricksets/MyBrickSetsView.vue`

**Zadania:**
1. Wykorzystanie composable `useMyBrickSetsList`
2. Utworzenie struktury widoku:
   - PageHeader z tytułem
   - ViewControls z SortControl
   - OwnedBrickSetList
   - PaginationControls
3. Obsługa zdarzeń (card-click, edit-click, sort-change, page-change)
4. Wyświetlanie stanów (loading, error, empty)
5. Implementacja handleCardClick → router.push
6. Implementacja handleEditClick → router.push
7. Stylowanie z Tailwind (layout, spacing)

**Rezultat:** Kompletny widok My BrickSets

### Krok 14: Konfiguracja routingu

**Plik:** `src/router/index.ts`

**Zadania:**
1. Dodanie route dla `/app/my/bricksets`
2. Ustawienie meta: `{ requiresAuth: true }`
3. Lazy loading komponentu
4. Dodanie do nawigacji (jeśli jeszcze nie istnieje)

**Rezultat:** Widok dostępny pod właściwą ścieżką

### Krok 15: Testy jednostkowe

**Pliki:**
- `src/components/bricksets/__tests__/EmptyState.spec.ts`
- `src/components/bricksets/__tests__/BrickSetBasicInfo.spec.ts`
- `src/components/bricksets/__tests__/BrickSetMetrics.spec.ts`
- `src/components/bricksets/__tests__/EditableIndicator.spec.ts`
- `src/components/bricksets/__tests__/OwnedBrickSetCard.spec.ts`
- `src/components/bricksets/__tests__/SortControl.spec.ts`
- `src/components/bricksets/__tests__/PaginationControls.spec.ts`
- `src/components/bricksets/__tests__/OwnedBrickSetList.spec.ts`
- `src/composables/__tests__/useMyBrickSetsList.spec.ts`
- `src/pages/bricksets/__tests__/MyBrickSetsView.spec.ts`

**Zadania dla każdego testu:**
1. Testowanie renderowania z różnymi propsami
2. Testowanie emitowanych zdarzeń
3. Testowanie warunków wyświetlania
4. Testowanie interakcji użytkownika
5. Testowanie stanów (loading, error, empty)
6. Mockowanie wywołań API (dla composable i widoku)

**Rezultat:** Pełne pokrycie testami jednostkowymi

### Krok 16: Testy integracyjne (E2E opcjonalnie)

**Plik:** `tests/e2e/my-bricksets.spec.ts`

**Zadania:**
1. Test pełnego flow: logowanie → przejście do My BrickSets → wyświetlenie listy
2. Test sortowania i paginacji
3. Test przejścia do szczegółów zestawu
4. Test przejścia do edycji (gdy editable)
5. Test tooltipa dla nieedytowalnego zestawu
6. Test pustego stanu i dodawania pierwszego zestawu

**Rezultat:** Weryfikacja pełnych flow użytkownika

### Krok 17: Stylowanie i responsywność

**Zadania:**
1. Weryfikacja responsywności na różnych rozdzielczościach (mobile, tablet, desktop)
2. Testowanie темной темы (jeśli aplikacja wspiera)
3. Dopracowanie hover effects i transitions
4. Weryfikacja zgodności z design system

**Rezultat:** Widok wygląda dobrze na wszystkich urządzeniach

### Krok 18: Accessibility (A11y)

**Zadania:**
1. Dodanie odpowiednich aria-labels
2. Zapewnienie keyboard navigation (tab, enter, space)
3. Testowanie ze screen readerem
4. Sprawdzenie kontrastu kolorów (WCAG AA)
5. Dodanie focus indicators

**Rezultat:** Widok dostępny dla użytkowników z niepełnosprawnościami

### Krok 19: Code review i optymalizacja

**Zadania:**
1. Review kodu przez zespół
2. Optymalizacja wydajności (lazy loading, memoization)
3. Refactoring duplikatów
4. Aktualizacja dokumentacji

**Rezultat:** Kod wysokiej jakości, zoptymalizowany

### Krok 20: Deployment i monitoring

**Zadania:**
1. Merge do brancha development
2. Deploy na środowisko testowe
3. Weryfikacja działania
4. Monitoring błędów (Sentry?)
5. Analiza użycia (analytics?)

**Rezultat:** Widok dostępny dla użytkowników w środowisku produkcyjnym

---

## Podsumowanie

Plan implementacji widoku "My BrickSets" obejmuje wszystkie aspekty: od definicji typów, przez implementację composables i komponentów, po testy i deployment. Kluczowe elementy to:

- **Modularność**: Każdy komponent ma jasno określoną odpowiedzialność
- **Reużywalność**: Komponenty jak BrickSetBasicInfo czy BrickSetMetrics mogą być użyte w innych widokach
- **Typowanie**: Pełne wykorzystanie TypeScript dla bezpieczeństwa typów
- **Obsługa błędów**: Kompleksowa obsługa wszystkich scenariuszy błędów
- **UX**: Jasne komunikaty, loading states, tooltips wyjaśniające blokady
- **Accessibility**: Wsparcie dla użytkowników z niepełnosprawnościami
- **Testowalność**: Architektura umożliwiająca łatwe testowanie

Implementacja powinna być wykonywana iteracyjnie, zaczynając od core functionality (kroki 1-14), a następnie rozszerzając o testy i optymalizacje (kroki 15-20).
