# Plan implementacji widoku „Moje wyceny" (My Valuations View)

## 1. Przegląd

Widok "Moje wyceny" (GET /api/v1/users/me/valuations) umożliwia zalogowanemu użytkownikowi przeglądanie listy wszystkich wycen, które dodał do różnych zestawów. Każda wycena pokazywana jest w postaci karty zawierającej referencję do zestawu (numer i ID), wartość wyceny w PLN, liczbę otrzymanych lajków oraz datę utworzenia. Widok obsługuje paginację i umożliwia nawigację do szczegółów zestawu.

**Powiązane wymagania:**
- FR-15: Wyświetlanie własnych wycen
- US-015: Lista moich wycen
- RB-02: Jedna wycena użytkownika na zestaw
- RB-03: Jeden lajk użytkownika na jedną wycenę

## 2. Routing widoku

**Ścieżka:** `/my-valuations`

**Komponenty routingu:**
- Ścieżka dostępna wyłącznie dla zalogowanych użytkowników (guard: `requireAuth`)
- Wymaga aktywnej sesji (sprawdzenie w auth store)
- Redirect na `/login` jeśli użytkownik nie jest zalogowany

## 3. Struktura komponentów

```
MyValuationsView (strona)
├── MyValuationsHeader (nagłówek)
├── LoadingSkeletons (widok ładowania)
├── EmptyState (brak wycen)
├── MyValuationsGrid (główny kontener listy)
│   └── OwnValuationCard (karta pojedynczej wyceny) [powtarzany]
│       ├── ValuationValueDisplay (wartość wyceny)
│       ├── BrickSetReference (link do zestawu)
│       ├── ValuationStats (lajki, data)
│       └── ActionLinks (przejdź do zestawu)
├── PaginationControls (sterowanie stronami)
└── ErrorState (widok błędu)
```

## 4. Szczegóły komponentów

### 4.1 MyValuationsView (Strona)

**Opis:** Główny komponent strony zarządzający stanem widoku, pobieraniem danych i paginacją.

**Główne elementy:**
- Container z padding i maksymalną szerokością
- Nagłówek strony z tytułem
- Sekcja główna z warunkowym renderowaniem:
  - Stan ładowania: wyświetl skeleton loadery
  - Stan błędu: wyświetl komunikat o błędzie
  - Brak danych: wyświetl pusty stan
  - Lista: wyświetl kartę nagłówka i grid wycen
- Paginacja na dole

**Obsługiwane interakcje:**
- Załadowanie danych przy montowaniu komponentu
- Zmiana strony poprzez paginację
- Odświeżenie danych (opcjonalnie)
- Klikniecie na kartę wyceny → przejście do szczegółów zestawu

**Obsługiwana walidacja:**
- Sprawdzenie autentykacji przed renderowaniem (guard)
- Sprawdzenie zwracanego wyniku API (count, results)

**Typy:**
- `OwnedValuationListDTO` (DTO z API)
- `OwnValuationViewModel` (ViewModel do wyświetlania)
- `PaginationState` (stan paginacji)

**Propsy:** Brak (strona root)

**Emits:** Brak

### 4.2 MyValuationsHeader

**Opis:** Nagłówek strony z tytułem i opisem.

**Główne elementy:**
- `<h1>` z tytułem "Moje wyceny"
- `<p>` z opisem: liczba wycen i statystyka lajków
- Opcjonalny przycisk "Dodaj wycenę" (link do listy zestawów)

**Obsługiwane interakcje:**
- Brak

**Typy:**
- `{ totalValuations: number; totalLikes: number }` (props)

**Propsy:**
```typescript
{
  totalValuations: number;
  totalLikes: number;
}
```

### 4.3 OwnValuationCard

**Opis:** Karta pojedynczej wyceny z informacją o zestawie i statystykami.

**Główne elementy:**
- Górna część: numero i nazwa zestawu (link)
- Środkowa część: wartość wyceny w dużym foncie
- Dolna część: data utworzenia i liczba lajków
- Przycisk/link: "Przejdź do zestawu"

**Obsługiwane interakcje:**
- Kliknięcie na numer/nazwę zestawu → nawigacja do detali zestawu
- Kliknięcie na "Przejdź do zestawu" → nawigacja do detali zestawu
- Hover: zmiana koloru tła dla wskazania, że jest klikalne

**Obsługiwana walidacja:**
- Walidacja istnienia ID zestawu
- Walidacja poprawności wartości wyceny

**Typy:**
- `OwnValuationViewModel` (props)

**Propsy:**
```typescript
{
  valuation: OwnValuationViewModel;
}
```

**Emits:**
```typescript
{
  'navigate-to-brickset': [bricksetId: number];
}
```

### 4.4 MyValuationsGrid

**Opis:** Kontener dla karty gridowej wyświetlającej wyceny w układzie responsywnym.

**Główne elementy:**
- CSS Grid z dwoma kolumnami na MD+ breakpoint, jedną na SM
- Sekcja informacyjna: liczba wyników
- Sekcja filtrowania/sortowania (opcjonalnie)

**Obsługiwane interakcje:**
- Klikniecie na kartę → emitowanie zdarzenia do parent

**Typy:**
- Array of `OwnValuationViewModel`

**Propsy:**
```typescript
{
  valuations: OwnValuationViewModel[];
}
```

### 4.5 LoadingSkeletons

**Opis:** Skeleton loaders dla stanu ładowania. Używa istniejącego komponentu `LoadingSkeletons` z bricksets.

**Główne elementy:**
- Wiele placeholderów w kształcie karty
- Animacja shimmer effect

**Obsługiwane interakcje:**
- Brak

### 4.6 EmptyState

**Opis:** Stan wyświetlany gdy użytkownik nie ma żadnych wycen.

**Główne elementy:**
- Ikona (np. emoji 📝)
- Tekst: "Nie dodałeś jeszcze żadnych wycen"
- Podtekst: "Przeglądaj zestawy i dodawaj swoje wyceny"
- Przycisk: "Przejdź do zestawów" (link do `/bricksets`)

**Obsługiwane interakcje:**
- Klikniecie na przycisk → nawigacja do listy zestawów

### 4.7 PaginationControls

**Opis:** Sterowanie stronami dla listy wycen.

**Główne elementy:**
- Informacja: "Strona X z Y"
- Przyciski: Poprzednia, Następna
- Walidacja: disable przycisków na pierwszej/ostatniej stronie

**Obsługiwane interakcje:**
- Kliknięcie "Poprzednia" → zmiana na poprzednią stronę
- Kliknięcie "Następna" → zmiana na następną stronę

**Typy:**
- `PaginationState`

**Propsy:**
```typescript
{
  currentPage: number;
  totalPages: number;
  totalCount: number;
  isLoading: boolean;
}
```

**Emits:**
```typescript
{
  'page-change': [pageNumber: number];
}
```

## 5. Typy

### 5.1 API DTOs

```typescript
/**
 * Pojedyncza wycena użytkownika z referencją do zestawu
 * Odpowiedź z GET /api/v1/users/me/valuations
 */
export interface OwnedValuationListItemDTO {
  id: number;                    // ID wyceny
  brickset: {
    id: number;                  // ID zestawu
    number: number;              // Numer zestawu
  };
  value: number;                 // Wartość wyceny (1-999999)
  currency: 'PLN';               // Kod waluty
  likes_count: number;           // Liczba lajków otrzymanych
  created_at: string;            // ISO 8601 timestamp utworzenia
}

/**
 * Response z listy wycen użytkownika
 */
export interface OwnedValuationListResponseDTO {
  count: number;                 // Całkowita liczba wycen
  results: OwnedValuationListItemDTO[];  // Wyceny na bieżącej stronie
}
```

### 5.2 ViewModels

```typescript
/**
 * Pojedyncza wycena sformatowana do wyświetlenia
 */
export interface OwnValuationViewModel {
  id: number;
  bricksetId: number;
  bricksetNumber: string;        // Sformatowany numer zestawu
  valueFormatted: string;        // np. "450 PLN"
  likesCount: number;
  createdAtRelative: string;     // np. "3 dni temu"
  createdAt: string;             // ISO dla sortowania
}

/**
 * Stan paginacji
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
 * Stan widoku listy wycen
 */
export interface MyValuationsViewState {
  valuations: OwnValuationViewModel[];
  pagination: PaginationState;
  loading: boolean;
  error: string | null;
}
```

## 6. Zarządzanie stanem

### 6.1 State Management Strategy

Widok wymaga prostego zarządzania stanem - głównie pobieranie i wyświetlanie danych. Rekomendacja: **Composable Hook** zamiast Pinia store (ze względu na simplicity i lokalizację stanu).

### 6.2 useMyValuesList Composable (NOWY)

**Przeznaczenie:** Zarządzanie pobieraniem, paginacją i stanem listy wycen użytkownika.

**Reaktywne properties:**
- `valuations: Ref<OwnValuationViewModel[]>` - lista wycen
- `loading: Ref<boolean>` - status ładowania
- `error: Ref<string | null>` - komunikat błędu
- `pagination: Ref<PaginationState>` - informacje o paginacji

**Computed properties:**
- `isEmpty: ComputedRef<boolean>` - czy lista jest pusta
- `totalPages: ComputedRef<number>` - całkowita liczba stron

**Methods:**
- `fetchValuesList(page: number): Promise<void>` - pobranie wycen z API
- `goToPage(pageNumber: number): Promise<void>` - zmiana strony
- `refresh(): Promise<void>` - odświeżenie danych

**Integracja:**
- Korzysta z `apiClient` dla żądań HTTP
- Mapuje DTOs na ViewModels za pomocą mappera
- Obsługuje błędy sieciowe i walidacyjne

## 7. Integracja API

### 7.1 Endpoint: GET /api/v1/users/me/valuations

**URL:** `/api/v1/users/me/valuations`

**Metoda:** GET

**Query Parameters:**
```
page: number (default: 1)
page_size: number (default: 20, max: 100)
```

**Headers:**
```
Authorization: Bearer <token>  (lub HttpOnly cookie)
```

**Response (200 OK):**
```json
{
  "count": 7,
  "results": [
    {
      "id": 77,
      "brickset": {
        "id": 10,
        "number": 12345
      },
      "value": 400,
      "currency": "PLN",
      "likes_count": 9,
      "created_at": "2025-10-21T12:34:56Z"
    },
    // ... więcej wycen
  ]
}
```

**Error Responses:**
- `401 NOT_AUTHENTICATED`: Brak sesji lub token wygasł
- `400 VALIDATION_ERROR`: Niepoprawne parametry paginacji

**Frontend Integration:**
```typescript
// W composable useMyValuesList:
const response = await apiClient.get<OwnedValuationListResponseDTO>(
  `/v${env.api.version}/users/me/valuations`,
  {
    params: {
      page: currentPage.value,
      page_size: pageSize,
    },
    withCredentials: true,
  }
);

// Mapowanie i transformacja
const viewModels = response.data.results.map(mapOwnedValuationDtoToViewModel);
valuations.value = viewModels;
```

## 8. Interakcje użytkownika

### 8.1 Przepływ użytkownika

1. **Zalogowanie i dostęp do widoku:**
   - Użytkownik kliknie na link "Moje wyceny" w menu nawigacji
   - Strona ładuje się, composable automatycznie pobiera dane dla strony 1
   - Wyświetla się lista wycen lub pusty stan

2. **Przeglądanie wycen:**
   - Widzi listę karty wycen w gridzie 2-kolumnowym
   - Każda karta pokazuje:
     - Numer zestawu (jako link)
     - Wartość wyceny w dużym foncie
     - Liczbę lajków
     - Datę utworzenia w formacie względnym (np. "3 dni temu")

3. **Nawigacja do szczegółów zestawu:**
   - Kliknięcie na numer zestawu lub przycisk "Przejdź do zestawu"
   - Router nawiguje do `/bricksets/{id}`

4. **Paginacja:**
   - U dołu strony widzi przyciski "Poprzednia" i "Następna"
   - Klikniecie zmienia stronę, composable pobiera nowe dane

5. **Brak wycen:**
   - Jeśli użytkownik nie ma wycen, widzi pusty stan
   - Przycisk "Dodaj wycenę" linkiem do listy zestawów

6. **Błąd ładowania:**
   - Jeśli API zwróci błąd, wyświetli się komunikat błędu
   - Przycisk "Spróbuj ponownie" do retry

### 8.2 Obsługa błędów

| Scenariusz | Obsługa |
|-----------|---------|
| 401 Unauthorized | Przekierowanie na login, czyszczenie auth store |
| 400 Validation Error | Wyświetlenie komunikatu do użytkownika |
| Network Error | Komunikat "Sprawdź połączenie" z przyciskiem retry |
| 500 Server Error | Komunikat "Błąd serwera" z przyciskiem retry |
| Timeout | Komunikat "Timeout - spróbuj ponownie" |

## 9. Warunki i walidacja

### 9.1 Warunki wymagane przez API

| Warunek | Komponent | Akcja |
|---------|-----------|-------|
| Użytkownik zalogowany | MyValuationsView (guard) | Redirect na `/login` jeśli nie |
| Parametr `page` ≥ 1 | useMyValuesList | Defaulting do 1 |
| Parametr `page_size` 1-100 | useMyValuesList | Defaulting do 20 |
| Poprawny JWT token | Axios client | HttpOnly cookie z żądaniem |

### 9.2 Walidacja na Frontend

| Walidacja | Gdzie | Akcja |
|-----------|-------|-------|
| ID zestawu istnieje | OwnValuationCard | Wyświetlenie warnings jeśli brakuje |
| Wartość wyceny > 0 | OwnValuationViewModel | Transformacja/sformatowanie |
| Timestamp ISO 8601 | useMyValuesList mapper | Konwersja na relative format |
| Paginacja: page ≤ totalPages | PaginationControls | Disable przycisku "Następna" |

## 10. Obsługa błędów

### 10.1 Potencjalne błędy i rozwiązania

| Błąd | Przyczyna | Rozwiązanie |
|-----|----------|------------|
| 401 NOT_AUTHENTICATED | Token wygasł lub brak sesji | Wylogowanie użytkownika, redirect na login |
| 400 VALIDATION_ERROR | Niepoprawne parametry paginacji | Logowanie, reset paginacji do domyślnych |
| Network timeout | Brak połączenia / serwer nieosiągalny | Wyświetlenie "Timeout", przycisk retry |
| 500 Server Error | Błąd serwera | Komunikat o błędzie, przycisk retry |
| Empty response | Nieoczekiwana struktura | Error boundary, logowanie |
| Stale data | Konkurencyjne zmiany wycen | Opcjonalny refresh button |

### 10.2 User-Friendly Komunikaty

Wszystkie komunikaty muszą być w języku polskim:
- "Zaloguj się aby przeglądać wyceny"
- "Błąd połączenia - sprawdź swoją sieć"
- "Błąd serwera - spróbuj później"
- "Nie dodałeś jeszcze żadnych wycen"
- "Wczytywanie wycen..."

## 11. Kroki implementacji

### Faza 1: Setup i Types

1. **Dodaj typy do `src/types/bricksets.ts`:**
   - `OwnedValuationListItemDTO`
   - `OwnedValuationListResponseDTO`
   - `OwnValuationViewModel`
   - `PaginationState`
   - `MyValuationsViewState`

2. **Zaktualizuj enum/const:**
   - Dodaj route type jeśli wymagane

### Faza 2: Composables

3. **Stwórz `src/composables/useMyValuesList.ts`:**
   - Implementuj reactive state (valuations, loading, error, pagination)
   - Implementuj `fetchValuesList(page)` - pobiera dane z API
   - Implementuj `goToPage(pageNumber)` - zmienia stronę i pobiera dane
   - Implementuj `refresh()` - odświeża dane na bieżącej stronie
   - Implementuj error handling (401, 400, network, timeout)
   - Mapowanie DTO na ViewModel

### Faza 3: Mappers

4. **Dodaj mapper w `src/mappers/bricksets.ts` (lub nowy file):**
   - `mapOwnedValuationDtoToViewModel(dto): OwnValuationViewModel`
   - Formatowanie numeru zestawu
   - Formatowanie wartości na "XXX PLN"
   - Konwersja timestamps na relative format (używając i18n)

### Faza 4: Komponenty

5. **Stwórz `src/components/valuations/MyValuationsHeader.vue`:**
   - Props: `{ totalValuations: number; totalLikes: number }`
   - Wyświetl tytuł i statystyki

6. **Stwórz `src/components/valuations/OwnValuationCard.vue`:**
   - Props: `{ valuation: OwnValuationViewModel }`
   - Emit: `navigate-to-brickset`
   - Wyświetl info zestawu, wartość, lajki
   - Linki do `/bricksets/{id}`

7. **Stwórz `src/components/valuations/MyValuationsGrid.vue`:**
   - Props: `{ valuations: OwnValuationViewModel[] }`
   - Emit: `navigate-to-brickset`
   - CSS Grid 2 kolumny na MD+
   - Render `OwnValuationCard` dla każdej wyceny

8. **Stwórz `src/components/valuations/PaginationControls.vue`:**
   - Props: `{ currentPage: number; totalPages: number; totalCount: number; isLoading: boolean }`
   - Emit: `page-change`
   - Przyciski Poprzednia/Następna z disabled state

9. **Stwórz `src/components/valuations/EmptyState.vue`:**
   - Wyświetl komunikat "Brak wycen"
   - Przycisk link do `/bricksets`

10. **Stwórz `src/components/valuations/ErrorState.vue`:**
    - Props: `{ error: string; isLoading: boolean }`
    - Emit: `retry`
    - Wyświetl komunikat błędu i przycisk retry

### Faza 5: Główna strona

11. **Stwórz `src/views/MyValuationsView.vue`:**
    - Używa `useMyValuesList()` composable
    - Rendery warunkowe: loading → skeletons, error → error state, empty → empty state, data → grid
    - Event listeners na `navigate-to-brickset`, `page-change`
    - Route guard dla autentykacji

### Faza 6: Routing

12. **Zaktualizuj `src/router/index.ts`:**
    - Dodaj route: `{ path: '/my-valuations', component: MyValuationsView, requiresAuth: true }`

### Faza 7: i18n

13. **Zaktualizuj pliki tłumaczeń `src/locales/pl.json` (i inne):**
    - Dodaj klucze dla komponentów:
      - `myValuations.title`
      - `myValuations.empty.title`
      - `myValuations.empty.description`
      - `myValuations.goToSets`
      - `myValuations.navigateToBrickset`
      - `pagination.previous`
      - `pagination.next`
      - `errors.timeout`
      - `errors.retry`

### Faza 8: Navigation

14. **Zaktualizuj `src/components/navigation/MainNavigation.vue` (lub gdzie indziej):**
    - Dodaj link "Moje wyceny" w menu (linkiem do `/my-valuations`)
    - Widoczny tylko dla zalogowanych użytkowników

### Faza 9: Testy

15. **Stwórz testy jednostkowe:**
    - `useMyValuesList.spec.ts` - testy composable
    - `OwnValuationCard.spec.ts` - testy komponentu
    - `MyValuationsView.spec.ts` - testy strony
    - Testy mapperów

16. **Testy integracyjne:**
    - `my-valuations.cy.ts` - testy E2E (Cypress)

### Faza 10: Dokumentacja i Polish

17. **Dokumentacja:**
    - Dodaj komentarze JSDoc do composable
    - Dodaj README dla komponentów jeśli wymagane

18. **Code Review:**
    - Verify TypeScript types
    - Verify accessibility (ARIA labels)
    - Verify responsiveness (mobile, tablet, desktop)
    - Verify dark mode (jeśli używany)

---

## Uwagi dodatkowe

- **Sortowanie:** API nie wspiera sortowania dla `/users/me/valuations`. Jeśli wymagane, może być zaimplementowane na frontend przy pobieraniu pełnej listy.
- **Filtrowanie:** Nie przewidziano filtrowania (np. po zakresie wartości). Może być dodane w przyszłości.
- **Real-time updates:** W MVP brak. Paginacja jest statelem - przy dodaniu nowej wyceny użytkownik musi ręcznie odświeżyć.
- **Accessibility:** Wszystkie interaktywne elementy muszą mieć `aria-label` oraz być dostępne z klawiatury (tabindex, ENTER/SPACE).
- **Performance:** Przy dużej ilości wycen (>1000) rozważyć wirtualizację listy (lazy loading).
- **Dark Mode:** Komponenty muszą być stylizowane z obsługą dark mode (klasy Tailwind `dark:`).

