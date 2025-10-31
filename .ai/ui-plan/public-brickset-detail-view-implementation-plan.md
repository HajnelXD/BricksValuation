# Plan implementacji widoku Public BrickSet Detail View

## 1. Przegląd
Public BrickSet Detail View to publiczny widok szczegółowy pojedynczego zestawu LEGO, dostępny dla wszystkich użytkowników (zarówno zalogowanych jak i niezalogowanych). Widok prezentuje kompletne informacje o zestawie wraz z listą wszystkich wycen społeczności. Dla użytkowników niezalogowanych interakcyjne elementy (dodawanie wyceny, lajkowanie) są zastąpione bannerem z zachętą do zalogowania. Widok realizuje wymaganie FR-09 oraz publiczną część US-013.

## 2. Routing widoku
- **Ścieżka**: `/bricksets/:id`
- **Nazwa**: `brickset-detail`
- **Komponent**: `src/pages/bricksets/PublicBrickSetDetailView.vue`
- **Meta**: Brak (widok publiczny, dostępny dla wszystkich)

Przykład konfiguracji routingu:
```typescript
{
  path: '/bricksets/:id',
  name: 'brickset-detail',
  component: () => import('../pages/bricksets/PublicBrickSetDetailView.vue'),
}
```

## 3. Struktura komponentów

```
PublicBrickSetDetailView (strona główna)
├── AuthPromptBanner (dla niezalogowanych użytkowników)
├── LoadingSkeletons (stan ładowania)
├── ErrorState (stan błędu)
└── (główna treść - gdy dane załadowane)
    ├── BrickSetHeader (nagłówek z podstawowymi danymi)
    ├── BrickSetStats (statystyki: liczba wycen, lajków)
    ├── TopValuationHighlight (wyróżniona najlepsza wycena)
    └── ValuationList (lista wszystkich wycen)
        └── ValuationCard[] (pojedyncza wycena)
            └── LikeButton | AuthPromptButton (w zależności od stanu auth)
```

## 4. Szczegóły komponentów

### 4.1 PublicBrickSetDetailView (strona główna)
**Opis**: Główny komponent widoku, orkiestruje pobieranie danych z API, zarządza stanem i renderuje odpowiednie komponenty zależnie od stanu ładowania, błędów lub sukcesu.

**Główne elementy**:
- Banner z zachętą do zalogowania (dla niezalogowanych)
- Kontener główny z sekcjami:
  - Nagłówek zestawu (BrickSetHeader)
  - Statystyki (BrickSetStats)
  - Wyróżniona wycena TOP (TopValuationHighlight)
  - Lista wszystkich wycen (ValuationList)
- Komponenty stanów: LoadingSkeletons, ErrorState

**Obsługiwane interakcje**:
- Pobieranie danych przy montowaniu komponentu
- Retry po błędzie
- Nawigacja do logowania/rejestracji
- Scrollowanie do góry przy kliknięciu w top valuation

**Warunki walidacji**: Brak (read-only view)

**Typy**:
- `BrickSetDetailDTO` (DTO z API)
- `BrickSetDetailViewModel` (ViewModel dla UI)
- `ValuationViewModel` (ViewModel dla pojedynczej wyceny)

**Propsy**: Brak (dane pobierane z parametru route `:id`)

### 4.2 AuthPromptBanner
**Opis**: Banner informacyjny dla niezalogowanych użytkowników z wezwaniem do zalogowania i krótkimi korzyściami z rejestracji.

**Główne elementy**:
- `<div>` z tekstem zachęty
- `<router-link>` do `/login`
- `<router-link>` do `/register`

**Obsługiwane interakcje**:
- Kliknięcie w link logowania
- Kliknięcie w link rejestracji

**Warunki walidacji**: Brak

**Typy**: Brak (komponent nie przyjmuje danych)

**Propsy**: Brak

### 4.3 BrickSetHeader
**Opis**: Nagłówek zestawu prezentujący numer, statusy i podstawowe atrybuty.

**Główne elementy**:
- `<h1>` z numerem zestawu (formatowany z zerami wiodącymi)
- Badge statusu produkcji (ACTIVE/RETIRED)
- Badge kompletności (COMPLETE/INCOMPLETE)
- Ikony atrybutów (instrukcje 📘, pudełko 📦, zapieczętowany 🔒)
- Data utworzenia (formatowana relatywnie)

**Obsługiwane interakcje**: Brak (komponent prezentacyjny)

**Warunki walidacji**: Brak

**Typy**:
- `BrickSetHeaderViewModel`

**Propsy**:
```typescript
interface Props {
  number: string;
  productionStatusLabel: string;
  completenessLabel: string;
  hasInstructions: boolean;
  hasBox: boolean;
  isFactorySealed: boolean;
  ownerInitialEstimate: number | null;
  createdAtRelative: string;
}
```

### 4.4 BrickSetStats
**Opis**: Statystyki zestawu prezentowane jako metryki.

**Główne elementy**:
- `<div>` z ikoną 💰 i liczbą wycen
- `<div>` z ikoną ❤️ i sumą lajków

**Obsługiwane interakcje**: Brak

**Warunki walidacji**: Brak

**Typy**:
- `BrickSetStatsViewModel`

**Propsy**:
```typescript
interface Props {
  valuationsCount: number;
  totalLikes: number;
}
```

### 4.5 TopValuationHighlight
**Opis**: Wyróżniona sekcja prezentująca najwyżej polajkowaną wycenę (jeśli istnieje).

**Główne elementy**:
- `<div>` z wyróżnionym tłem (np. żółtym/złotym)
- Ikona 🏆 lub badge "TOP"
- Wartość wyceny z walutą (np. "450 PLN")
- Liczba lajków
- Opcjonalny komentarz (skrócony, z rozwinięciem)
- ID użytkownika lub nazwa (jeśli dostępne)

**Obsługiwane interakcje**:
- Rozwijanie/zwijanie pełnego komentarza (jeśli długi)

**Warunki walidacji**: Brak

**Typy**:
- `TopValuationViewModel`

**Propsy**:
```typescript
interface Props {
  valuation: TopValuationViewModel | null;
}
```

### 4.6 ValuationList
**Opis**: Lista wszystkich wycen zestawu, posortowanych według liczby lajków (malejąco) i daty (rosnąco).

**Główne elementy**:
- `<ul>` z listą wycen
- Nagłówek sekcji ("Wszystkie wyceny")
- Sortowanie domyślne: malejąco po likes_count, rosnąco po created_at

**Obsługiwane interakcje**:
- Scrollowanie listy
- Delegowanie kliknięć w przyciski lajku do komponentu nadrzędnego

**Warunki walidacji**: Brak

**Typy**:
- `ValuationViewModel[]`

**Propsy**:
```typescript
interface Props {
  valuations: ValuationViewModel[];
  isAuthenticated: boolean;
  currentUserId: number | null;
  onLike?: (valuationId: number) => void; // callback dla zalogowanych
}
```

### 4.7 ValuationCard
**Opis**: Pojedyncza karta wyceny prezentująca wartość, komentarz, autora i liczbę lajków.

**Główne elementy**:
- `<li>` z ramką
- Wartość wyceny z walutą (np. "400 PLN")
- Komentarz (opcjonalny, wieloliniowy)
- User ID autora (np. "Użytkownik #99")
- Liczba lajków ❤️
- Przycisk lajku (dla zalogowanych) lub zachęta do logowania (dla niezalogowanych)
- Data dodania (formatowana relatywnie)

**Obsługiwane interakcje**:
- Kliknięcie w przycisk lajku (tylko dla zalogowanych)
- Kliknięcie w przycisk "Zaloguj się" (dla niezalogowanych)

**Warunki walidacji**:
- Użytkownik nie może lajkować własnej wyceny (przycisk disabled)
- Użytkownik nie może lajkować tej samej wyceny wielokrotnie (przycisk disabled po lajku)

**Typy**:
- `ValuationViewModel`

**Propsy**:
```typescript
interface Props {
  valuation: ValuationViewModel;
  isAuthenticated: boolean;
  isOwnValuation: boolean; // czy wycena należy do zalogowanego użytkownika
  hasUserLiked: boolean; // czy użytkownik już polajkował tę wycenę
  onLike?: (valuationId: number) => void;
}
```

### 4.8 LikeButton
**Opis**: Przycisk lajku z licznikiem, disabled jeśli użytkownik jest autorem lub już polajkował.

**Główne elementy**:
- `<button>` z ikoną ❤️
- Licznik lajków
- Stany: aktywny, disabled, załadowany (po kliknięciu)

**Obsługiwane interakcje**:
- Kliknięcie: emituje event `like`

**Warunki walidacji**:
- Disabled jeśli `isOwnValuation === true`
- Disabled jeśli `hasUserLiked === true`

**Typy**: Brak (komponent UI)

**Propsy**:
```typescript
interface Props {
  likesCount: number;
  disabled: boolean;
  loading: boolean;
}
```

### 4.9 AuthPromptButton
**Opis**: Przycisk zastępujący LikeButton dla niezalogowanych użytkowników, prowadzący do strony logowania.

**Główne elementy**:
- `<button>` lub `<router-link>` do `/login`
- Tekst: "Zaloguj się aby polubić"
- Ikona 🔒

**Obsługiwane interakcje**:
- Kliknięcie: przekierowanie do `/login`

**Warunki walidacji**: Brak

**Typy**: Brak

**Propsy**: Brak

## 5. Typy

### 5.1 DTO (Data Transfer Objects - z API)

```typescript
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
```

### 5.2 ViewModel (typy wewnętrzne dla UI)

```typescript
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
```

## 6. Zarządzanie stanem

### 6.1 Stan lokalny w komponencie głównym

Widok zarządza stanem lokalnie przy użyciu Composition API (`ref`, `computed`):

```typescript
const brickSetDetail = ref<BrickSetDetailViewModel | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);
```

### 6.2 Stan uwierzytelniania

Stan użytkownika pobierany z `useAuthStore`:

```typescript
const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);
const currentUserId = computed(() => authStore.user?.id ?? null);
```

### 6.3 Stan lajków

Stan lajków zarządzany lokalnie jako Set dla szybkiego sprawdzania:

```typescript
const userLikes = ref<Set<number>>(new Set()); // Set ID wycen, które użytkownik polajkował
```

### 6.4 Niestandardowy composable (opcjonalny)

W przypadku chęci reużycia logiki można stworzyć `useBrickSetDetail`:

```typescript
/**
 * Composable: useBrickSetDetail
 * Zarządza pobieraniem szczegółów zestawu i lajkowaniem wycen
 */
export function useBrickSetDetail(brickSetId: number) {
  const brickSetDetail = ref<BrickSetDetailViewModel | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const userLikes = ref<Set<number>>(new Set());

  async function fetchBrickSetDetail(): Promise<void> { ... }
  async function likeValuation(valuationId: number): Promise<void> { ... }

  return {
    brickSetDetail,
    loading,
    error,
    userLikes,
    fetchBrickSetDetail,
    likeValuation,
  };
}
```

**Decyzja**: Dla MVP i pojedynczego widoku, zarządzanie stanem lokalnie w komponencie jest wystarczające. Composable można dodać w przyszłości przy rozbudowie.

## 7. Integracja API

### 7.1 Endpoint pobierania szczegółów zestawu

**Żądanie**:
- Metoda: `GET`
- URL: `/api/v1/bricksets/{id}`
- Parametry: `id` z parametru route
- Headers: `withCredentials: true` (dla sesji, jeśli zalogowany)

**Typy żądania**:
```typescript
// Brak body - GET request
interface FetchBrickSetDetailRequest {
  id: number; // z route params
}
```

**Typy odpowiedzi**:
```typescript
// Sukces: 200 OK
type FetchBrickSetDetailSuccessResponse = BrickSetDetailDTO;

// Błąd: 404 Not Found
interface BrickSetNotFoundError {
  detail: string;
  code: 'BRICKSET_NOT_FOUND';
}

// Błąd: 500 Internal Server Error
interface ServerError {
  detail: string;
}
```

**Obsługa błędów**:
- `404`: "Zestaw nie został znaleziony"
- `500`: "Wystąpił błąd serwera. Spróbuj ponownie później"
- Błąd sieci: "Brak połączenia z serwerem. Sprawdź połączenie internetowe"

### 7.2 Endpoint lajkowania wyceny (dla zalogowanych)

**Żądanie**:
- Metoda: `POST`
- URL: `/api/v1/valuations/{valuation_id}/like`
- Body: Brak (lub pusty JSON)
- Headers: `withCredentials: true`

**Typy żądania**:
```typescript
interface LikeValuationRequest {
  valuationId: number;
}
```

**Typy odpowiedzi**:
```typescript
// Sukces: 201 Created
interface LikeValuationSuccessResponse {
  message: string;
  valuation_id: number;
  likes_count: number; // zaktualizowana liczba lajków
}

// Błąd: 400 Bad Request (już polajkowano)
interface AlreadyLikedError {
  detail: string;
  code: 'ALREADY_LIKED';
}

// Błąd: 403 Forbidden (własna wycena)
interface CannotLikeOwnValuationError {
  detail: string;
  code: 'CANNOT_LIKE_OWN_VALUATION';
}

// Błąd: 401 Unauthorized (brak autoryzacji)
interface UnauthorizedError {
  detail: string;
}
```

**Obsługa błędów**:
- `400`: "Już polajkowałeś tę wycenę"
- `403`: "Nie możesz polajkować własnej wyceny"
- `401`: "Zaloguj się aby polubić wycenę"
- `500`: "Błąd serwera. Spróbuj ponownie"

**Uwaga**: Endpoint lajkowania nie jest zdefiniowany w dostarczonym opisie API, zakładam standardową konwencję REST. Należy zweryfikować z backendem i dostosować.

### 7.3 Mapowanie DTO -> ViewModel

Funkcja mapująca `mapBrickSetDetailDtoToViewModel`:

```typescript
export function mapBrickSetDetailDtoToViewModel(
  dto: BrickSetDetailDTO
): BrickSetDetailViewModel {
  // Sortowanie wycen: malejąco po likes_count, następnie rosnąco po created_at
  const sortedValuations = [...dto.valuations].sort((a, b) => {
    if (b.likes_count !== a.likes_count) {
      return b.likes_count - a.likes_count;
    }
    return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
  });

  const topValuation = sortedValuations[0]
    ? mapValuationDtoToTopViewModel(sortedValuations[0])
    : null;

  return {
    id: dto.id,
    number: String(dto.number).padStart(5, '0'),
    productionStatusLabel: formatProductionStatusLabel(dto.production_status),
    completenessLabel: formatCompletenessLabel(dto.completeness),
    hasInstructions: dto.has_instructions,
    hasBox: dto.has_box,
    isFactorySealed: dto.is_factory_sealed,
    ownerInitialEstimate: dto.owner_initial_estimate,
    ownerId: dto.owner_id,
    valuationsCount: dto.valuations_count,
    totalLikes: dto.total_likes,
    topValuation,
    valuations: sortedValuations.map(mapValuationDtoToViewModel),
    createdAtRelative: formatRelativeTime(dto.created_at),
    createdAt: dto.created_at,
  };
}
```

## 8. Interakcje użytkownika

### 8.1 Ładowanie widoku
1. Użytkownik nawiguje do `/bricksets/123`
2. Komponent montuje się i wywołuje `fetchBrickSetDetail()`
3. Wyświetlany jest stan ładowania (LoadingSkeletons)
4. Po otrzymaniu danych: renderowanie pełnego widoku
5. W przypadku błędu: komponent ErrorState z przyciskiem retry

### 8.2 Lajkowanie wyceny (użytkownik zalogowany)
1. Użytkownik klika przycisk "❤️ {liczba}" w ValuationCard
2. Walidacja: czy nie jest to własna wycena, czy użytkownik już nie polajkował
3. Wywołanie `likeValuation(valuationId)`
4. Przycisk zmienia stan na "loading" (disabled, spinner)
5. Po sukcesie:
   - Zwiększenie licznika lajków lokalnie (+1)
   - Dodanie valuationId do `userLikes`
   - Przycisk zmienia stan na disabled z tekstem "Polubiono"
6. W przypadku błędu:
   - Wyświetlenie komunikatu błędu (toast lub inline error)
   - Przywrócenie stanu przycisku

### 8.3 Próba lajkowania (użytkownik niezalogowany)
1. Użytkownik klika przycisk "Zaloguj się aby polubić"
2. Przekierowanie do `/login` z parametrem `redirect=/bricksets/{id}`
3. Po zalogowaniu: automatyczny powrót do widoku zestawu

### 8.4 Kliknięcie w wyróżnioną wycenę TOP
1. Użytkownik klika w sekcję TopValuationHighlight
2. Smooth scroll do odpowiadającej karty ValuationCard w liście (za pomocą `scrollIntoView`)

### 8.5 Retry po błędzie
1. Użytkownik klika przycisk "Spróbuj ponownie" w ErrorState
2. Wywołanie ponowne `fetchBrickSetDetail()`
3. Powrót do stanu ładowania

## 9. Warunki i walidacja

### 9.1 Warunki prezentacji AuthPromptBanner
- **Warunek**: `!authStore.isAuthenticated`
- **Komponent**: `PublicBrickSetDetailView`
- **Wpływ**: Banner wyświetlany tylko dla niezalogowanych użytkowników

### 9.2 Warunki renderowania TopValuationHighlight
- **Warunek**: `brickSetDetail.topValuation !== null`
- **Komponent**: `PublicBrickSetDetailView`
- **Wpływ**: Sekcja TOP wyceny wyświetlana tylko jeśli istnieje przynajmniej jedna wycena

### 9.3 Warunki prezentacji LikeButton vs AuthPromptButton
- **Warunek**: `isAuthenticated`
- **Komponent**: `ValuationCard`
- **Wpływ**:
  - Zalogowany: LikeButton
  - Niezalogowany: AuthPromptButton

### 9.4 Warunki blokady LikeButton
- **Warunek 1**: `isOwnValuation === true` (użytkownik jest autorem wyceny)
  - **Komponent**: `ValuationCard`
  - **Wpływ**: Przycisk disabled z tooltipem "Nie możesz polajkować własnej wyceny"
- **Warunek 2**: `hasUserLiked === true` (użytkownik już polajkował)
  - **Komponent**: `ValuationCard`
  - **Wpływ**: Przycisk disabled z tekstem "Polubiono"

### 9.5 Warunek pustej listy wycen
- **Warunek**: `brickSetDetail.valuations.length === 0`
- **Komponent**: `ValuationList`
- **Wpływ**: Wyświetlenie komunikatu "Brak wycen. Bądź pierwszy!"

### 9.6 Walidacja parametru route
- **Warunek**: Parametr `:id` musi być liczbą całkowitą
- **Komponent**: `PublicBrickSetDetailView` (w `onMounted`)
- **Wpływ**: Jeśli `id` nie jest prawidłowe, wyświetlenie ErrorState z komunikatem "Nieprawidłowy identyfikator zestawu"

## 10. Obsługa błędów

### 10.1 Błąd 404 - Zestaw nie znaleziony
**Scenariusz**: Użytkownik nawiguje do `/bricksets/99999`, a zestaw o tym ID nie istnieje.

**Obsługa**:
1. API zwraca status 404 z kodem `BRICKSET_NOT_FOUND`
2. W `fetchBrickSetDetail()` catch:
   ```typescript
   if (error.response?.status === 404) {
     error.value = 'Zestaw nie został znaleziony';
   }
   ```
3. Renderowanie ErrorState z komunikatem i przyciskiem "Wróć do listy"
4. Przycisk "Wróć do listy" przekierowuje do `/` (public-bricksets)

### 10.2 Błąd 500 - Błąd serwera
**Scenariusz**: Serwer zwraca błąd 500 podczas pobierania szczegółów.

**Obsługa**:
1. API zwraca status 500
2. W catch:
   ```typescript
   if (error.response?.status === 500) {
     error.value = 'Wystąpił błąd serwera. Spróbuj ponownie później';
   }
   ```
3. Renderowanie ErrorState z przyciskiem "Spróbuj ponownie"

### 10.3 Błąd sieci - Brak połączenia
**Scenariusz**: Użytkownik nie ma połączenia z internetem lub serwer jest niedostępny.

**Obsługa**:
1. Axios rzuca błąd sieci (brak `response`)
2. W catch:
   ```typescript
   if (!error.response) {
     error.value = 'Brak połączenia z serwerem. Sprawdź połączenie internetowe';
   }
   ```
3. Renderowanie ErrorState z przyciskiem "Spróbuj ponownie"

### 10.4 Błąd lajkowania - Własna wycena
**Scenariusz**: Użytkownik próbuje polajkować własną wycenę (mimo że przycisk powinien być disabled).

**Obsługa**:
1. API zwraca 403 z kodem `CANNOT_LIKE_OWN_VALUATION`
2. Wyświetlenie toastu błędu: "Nie możesz polajkować własnej wyceny"
3. Użycie `useNotificationStore` do wyświetlenia błędu:
   ```typescript
   notificationStore.showError('Nie możesz polajkować własnej wyceny');
   ```

### 10.5 Błąd lajkowania - Już polajkowano
**Scenariusz**: Użytkownik próbuje ponownie polajkować wycenę (mimo że przycisk powinien być disabled).

**Obsługa**:
1. API zwraca 400 z kodem `ALREADY_LIKED`
2. Wyświetlenie toastu informacyjnego: "Już polajkowałeś tę wycenę"
3. Synchronizacja stanu lokalnego (dodanie do `userLikes`)

### 10.6 Błąd lajkowania - Brak autoryzacji
**Scenariusz**: Sesja użytkownika wygasła podczas przeglądania widoku.

**Obsługa**:
1. API zwraca 401
2. Wyświetlenie toastu błędu: "Sesja wygasła. Zaloguj się ponownie"
3. Odświeżenie stanu auth: `authStore.fetchProfile()`
4. Przekierowanie do `/login` z parametrem `redirect`

### 10.7 Błąd walidacji ID
**Scenariusz**: Parametr `:id` w route nie jest prawidłową liczbą.

**Obsługa**:
1. W `onMounted` walidacja:
   ```typescript
   const id = Number(route.params.id);
   if (isNaN(id) || id <= 0) {
     error.value = 'Nieprawidłowy identyfikator zestawu';
     return;
   }
   ```
2. Renderowanie ErrorState z komunikatem i przyciskiem "Wróć do listy"

## 11. Kroki implementacji

### Krok 1: Rozszerzenie typów
**Plik**: `src/types/bricksets.ts`

1. Dodać nowe interfejsy DTO:
   - `BrickSetDetailDTO`
   - `ValuationDTO`
2. Dodać nowe interfejsy ViewModel:
   - `BrickSetDetailViewModel`
   - `TopValuationDetailViewModel`
   - `ValuationViewModel`
   - `BrickSetHeaderViewModel`
   - `BrickSetStatsViewModel`

### Krok 2: Rozszerzenie mapperów
**Plik**: `src/mappers/bricksets.ts`

1. Dodać funkcję `mapValuationDtoToViewModel(dto: ValuationDTO): ValuationViewModel`
2. Dodać funkcję `mapValuationDtoToTopViewModel(dto: ValuationDTO): TopValuationDetailViewModel`
3. Dodać funkcję `mapBrickSetDetailDtoToViewModel(dto: BrickSetDetailDTO): BrickSetDetailViewModel`

### Krok 3: Utworzenie komponentów pomocniczych
**Pliki**: `src/components/bricksets/`

1. **BrickSetHeader.vue**:
   - Implementacja sekcji nagłówka
   - Props z `BrickSetHeaderViewModel`
   - Stylowanie z Tailwind (ciemny motyw)

2. **BrickSetStats.vue**:
   - Implementacja metryki wycen i lajków
   - Props z `BrickSetStatsViewModel`

3. **TopValuationHighlight.vue**:
   - Rozszerzenie istniejącego `TopValuationSnippet.vue` lub nowy komponent
   - Props z `TopValuationDetailViewModel`
   - Wyróżnione tło (np. gradient żółty/złoty)
   - Obsługa kliknięcia (scroll do karty w liście)

4. **LikeButton.vue**:
   - Przycisk z ikoną ❤️ i licznikiem
   - Props: `likesCount`, `disabled`, `loading`
   - Emituje event `like`
   - Stany: aktywny, disabled, loading

5. **AuthPromptButton.vue**:
   - Przycisk/link do logowania
   - Router-link do `/login`
   - Tekst: "Zaloguj się aby polubić"

### Krok 4: Utworzenie komponentu ValuationCard
**Plik**: `src/components/bricksets/ValuationCard.vue`

1. Struktura karty z danymi wyceny
2. Props:
   - `valuation: ValuationViewModel`
   - `isAuthenticated: boolean`
   - `isOwnValuation: boolean`
   - `hasUserLiked: boolean`
3. Warunkowe renderowanie LikeButton lub AuthPromptButton
4. Obsługa kliknięcia w przycisk lajku (emit `like`)
5. Stylowanie z Tailwind (ciemny motyw, ramka, hover effect)

### Krok 5: Utworzenie komponentu ValuationList
**Plik**: `src/components/bricksets/ValuationList.vue`

1. Nagłówek sekcji "Wszystkie wyceny ({count})"
2. Lista `<ul>` z `ValuationCard` dla każdej wyceny
3. Props:
   - `valuations: ValuationViewModel[]`
   - `isAuthenticated: boolean`
   - `currentUserId: number | null`
   - `userLikes: Set<number>`
4. Obsługa pustej listy (EmptyState)
5. Delegowanie eventów `like` do rodzica

### Krok 6: Utworzenie strony głównej widoku
**Plik**: `src/pages/bricksets/PublicBrickSetDetailView.vue`

1. **Setup script**:
   - Import wszystkich komponentów
   - Dostęp do `route.params.id`
   - Inicjalizacja stanu: `brickSetDetail`, `loading`, `error`, `userLikes`
   - Import `useAuthStore` dla stanu auth
   - Import `useNotificationStore` dla toastów błędów

2. **Funkcja fetchBrickSetDetail()**:
   - Walidacja ID z route
   - Wywołanie API: `GET /api/v1/bricksets/{id}`
   - Mapowanie DTO -> ViewModel
   - Obsługa błędów (404, 500, sieć)
   - Aktualizacja stanu: `brickSetDetail.value`, `error.value`, `loading.value`

3. **Funkcja likeValuation(valuationId)**:
   - Wywołanie API: `POST /api/v1/valuations/{valuationId}/like`
   - Optymistyczne aktualizowanie UI (dodanie do `userLikes`, inkrementacja licznika)
   - Obsługa błędów (400, 403, 401, 500)
   - Rollback w przypadku błędu

4. **onMounted lifecycle**:
   - Wywołanie `fetchBrickSetDetail()`

5. **Template**:
   - AuthPromptBanner (v-if="!isAuthenticated")
   - LoadingSkeletons (v-if="loading && !brickSetDetail")
   - ErrorState (v-else-if="error")
   - Główna treść (v-else):
     - BrickSetHeader
     - BrickSetStats
     - TopValuationHighlight (v-if="brickSetDetail.topValuation")
     - ValuationList

6. **Stylowanie**:
   - Kontener główny: `max-w-7xl mx-auto px-4 py-8`
   - Ciemny motyw zgodny z resztą aplikacji

### Krok 7: Dodanie routingu
**Plik**: `src/router/index.ts`

1. Dodać nową trasę:
   ```typescript
   {
     path: '/bricksets/:id',
     name: 'brickset-detail',
     component: () => import('../pages/bricksets/PublicBrickSetDetailView.vue'),
   }
   ```
2. Zweryfikować brak konfliktów z innymi trasami

### Krok 8: Rozszerzenie i18n
**Plik**: `src/i18n.ts`

1. Dodać tłumaczenia w sekcji `bricksets`:
   ```typescript
   bricksets: {
     // ... istniejące
     detail: {
       title: 'Szczegóły zestawu',
       topValuation: 'Najwyżej oceniana wycena',
       allValuations: 'Wszystkie wyceny',
       noValuations: 'Brak wycen. Bądź pierwszy!',
       addValuation: 'Dodaj wycenę',
       likeButton: 'Polub',
       liked: 'Polubiono',
       loginToLike: 'Zaloguj się aby polubić',
       cannotLikeOwn: 'Nie możesz polajkować własnej wyceny',
       valuation: 'Wycena',
       comment: 'Komentarz',
       by: 'przez użytkownika',
       notFound: 'Zestaw nie został znaleziony',
       backToList: 'Wróć do listy',
     }
   }
   ```

### Krok 9: Testowanie manualne
1. **Scenariusz 1 - Ładowanie szczegółów (niezalogowany)**:
   - Otwórz `/bricksets/1` bez logowania
   - Zweryfikuj wyświetlenie AuthPromptBanner
   - Zweryfikuj poprawne wyświetlenie danych zestawu
   - Zweryfikuj wyświetlenie wszystkich wycen posortowanych poprawnie
   - Zweryfikuj przyciski "Zaloguj się aby polubić"

2. **Scenariusz 2 - Ładowanie szczegółów (zalogowany)**:
   - Zaloguj się
   - Otwórz `/bricksets/1`
   - Zweryfikuj brak AuthPromptBanner
   - Zweryfikuj wyświetlenie przycisków lajku
   - Zweryfikuj disabled dla własnej wyceny (jeśli istnieje)

3. **Scenariusz 3 - Lajkowanie wyceny**:
   - Kliknij przycisk lajku dla cudzej wyceny
   - Zweryfikuj zwiększenie licznika
   - Zweryfikuj zmianę stanu przycisku na disabled "Polubiono"
   - Odśwież stronę i zweryfikuj persystencję lajku

4. **Scenariusz 4 - Błąd 404**:
   - Otwórz `/bricksets/99999`
   - Zweryfikuj wyświetlenie ErrorState z komunikatem "Zestaw nie został znaleziony"
   - Zweryfikuj działanie przycisku "Wróć do listy"

5. **Scenariusz 5 - Brak wycen**:
   - Otwórz zestaw bez wycen
   - Zweryfikuj wyświetlenie komunikatu "Brak wycen. Bądź pierwszy!"
   - Zweryfikuj brak sekcji TopValuationHighlight

6. **Scenariusz 6 - Kliknięcie w TOP wycenę**:
   - Otwórz zestaw z wycenami
   - Kliknij w sekcję TopValuationHighlight
   - Zweryfikuj smooth scroll do odpowiadającej karty w liście

### Krok 10: Optymalizacje i dostępność
1. **A11y - Semantyka HTML**:
   - Użyj `<main>` dla głównej treści
   - Użyj `<article>` dla karty zestawu
   - Użyj `<ul>`/`<li>` dla listy wycen
   - Dodaj `aria-label` dla przycisków bez tekstu
   - Dodaj `role="status"` dla komunikatów błędów

2. **A11y - Nawigacja klawiaturą**:
   - Zweryfikuj możliwość nawigacji Tab przez wszystkie interaktywne elementy
   - Dodaj focus styles dla przycisków
   - Obsługa Enter/Space dla niestandardowych buttonów

3. **A11y - Screen readers**:
   - Dodaj `aria-live="polite"` dla dynamicznie aktualizowanych liczników
   - Dodaj `aria-disabled` dla disabled buttonów z wyjaśnieniem

4. **Performance**:
   - Lazy loading komponentów (już implementowane przez Vue Router)
   - Debouncing dla przycisku retry (zapobieganie spamowi)
   - Optymistyczne aktualizowanie UI przy lajkowaniu (instant feedback)

### Krok 11: Dokumentacja
1. Dodać komentarze JSDoc dla wszystkich funkcji mapujących
2. Dodać komentarze do komponentów opisujące ich przeznaczenie
3. Zaktualizować README projektu o nowy widok
4. Dodać przykładowe screenshoty do dokumentacji

---

## Podsumowanie

Plan implementacji obejmuje kompletny publiczny widok szczegółowy zestawu LEGO z funkcjonalnością przeglądania wycen i lajkowania. Widok jest zaprojektowany zgodnie z istniejącymi wzorcami w projekcie:
- Wykorzystuje Composition API i setup script syntax
- Zarządza stanem lokalnie (bez nadmiarowej złożoności)
- Integruje się z `useAuthStore` dla kontekstu użytkownika
- Używa istniejących komponentów (LoadingSkeletons, ErrorState)
- Stosuje mappers dla transformacji DTO->ViewModel
- Wspiera i18n dla wszystkich tekstów
- Stylowanie z Tailwind w ciemnym motywie

Kluczowe punkty uwagi:
1. **Endpoint lajkowania**: Należy zweryfikować z backendem dokładną ścieżkę i format API dla lajkowania wycen (nie jest zdefiniowany w dostarczonym API plan).
2. **Sortowanie wycen**: Implementacja sortowania malejąco po likes_count, następnie rosnąco po created_at.
3. **Dostępność**: Szczególna uwaga na semantykę HTML, nawigację klawiaturą i wsparcie screen readerów.
4. **Obsługa błędów**: Kompleksowa obsługa wszystkich możliwych scenariuszy błędów z przyjaznymi komunikatami.
