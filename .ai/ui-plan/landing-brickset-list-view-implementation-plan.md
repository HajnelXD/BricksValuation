# Plan implementacji widoku Landing / Public BrickSet List View

## 1. Przegląd
Widok publiczny prezentujący listę zestawów LEGO (BrickSet) z podstawowymi statystykami (liczba wycen, suma lajków, wyróżniona top wycena) oraz panelem filtrów i wyszukiwania. Celem jest umożliwienie anonimicznemu użytkownikowi eksploracji zasobu i zachęcenie do zalogowania się (CTA w miejscach akcji wymagających autoryzacji). Widok wspiera stronicowanie, sortowanie oraz filtry domenowe zgodne z FR-08. Wersja mobilna udostępnia filtry w off‑canvas. Brak mutacji danych w trybie niezalogowanym.

## 2. Routing widoku
- Ścieżka główna: `/`
- Alias: `/bricksets`
- Typ dostępu: publiczny (brak wymogu auth) – jeśli backend jednak wymusza auth (FR-18 wariant), UI nadal buduje strukturę i przechodzi do ekranu logowania przy 401.
- Query parametry stosowane do synchronizacji stanu listy:
  - `q`, `production_status`, `completeness`, `has_instructions`, `has_box`, `is_factory_sealed`, `ordering`, `page`.

## 3. Struktura komponentów
```
LandingBrickSetListView (strona)
 ├─ AuthPromptBanner (warunkowo – góra listy lub sticky nad listą)
 ├─ FiltersLayoutWrapper
 │   ├─ BrickSetFiltersPanel
 │   │    ├─ SearchInput
 │   │    ├─ ProductionStatusSelect
 │   │    ├─ CompletenessSelect
 │   │    ├─ AttributeToggles (Instructions / Box / Factory Sealed)
 │   │    └─ OrderingSelect
 │   └─ MobileFiltersToggle / OffCanvasDrawer (<= md breakpoint)
 ├─ BrickSetList
 │   ├─ (n) BrickSetCard
 │   │     ├─ BrickSetMeta (number + badges)
 │   │     ├─ BrickSetStats (valuations_count, total_likes)
 │   │     ├─ TopValuationSnippet (opcjonalnie jeśli istnieje)
 │   │     └─ CTAOverlay (klik → /bricksets/:id, przy akcjach wymagających auth -> login CTA)
 ├─ EmptyState (gdy brak wyników)
 ├─ Pagination (pager lub „Załaduj więcej” – decyzja: klasyczne stronicowanie)
 └─ Global components: NotificationToaster, LoadingOverlay (wewnętrznie w stanie ładowania)
```

## 4. Szczegóły komponentów
### LandingBrickSetListView
- Opis: Komponent widoku routowanego. Orkiestruje pobieranie danych, mapowanie query param → store lokalny, render listy, filtrów i CTA logowania.
- Główne elementy: wrapper `<main>`, panel filtrów, lista kart, paginacja, baner logowania.
- Obsługiwane interakcje: zmiana filtrów, wpisanie wyszukiwania (debounce), zmiana strony, klik karty (nawigacja do detalu), próba akcji „Dodaj zestaw” (jeśli będzie przycisk – otwiera login modal/redirect).
- Walidacja: sanitizacja `page` (min 1), walidacja `ordering` (whitelist), konwersja booleanów z query (`"true"|"false"`).
- Typy: `BrickSetListResponseDTO`, `BrickSetListItemDTO`, lokalny `BrickSetListViewModel`.
- Propsy: brak (root route component).

### AuthPromptBanner
- Opis: Pasek informacyjny zachęcający do logowania (np. „Zaloguj się aby dodać własny zestaw lub wycenę”). Pokazywany jeśli `!isAuthenticated`.
- Elementy: `<div role="note">` z tekstem i przyciskiem „Zaloguj się”.
- Interakcje: klik „Zaloguj się” → redirect `/login?redirect=<current_full_path>`.
- Walidacja: brak domenowej – ochrona przed wielokrotnym renderem (idempotentne).
- Typy: używa globalnego `AuthState` (Pinia store).
- Propsy: `redirectPath?: string` (opcjonalnie ustawiane przez rodzica – fallback `location.fullPath`).

### BrickSetFiltersPanel
- Opis: Panel kontrolny do ustawiania filtrów i parametrów zapytania.
- Elementy: pola wejściowe wyszczególnione w strukturze + przycisk „Wyczyść” (reset do domyślnych) + w mobilnej wersji przycisk zamknięcia.
- Interakcje: onChange każdego pola aktualizuje stan (z debouncingiem dla `q`), onReset czyści filtry i ustawia `page=1`.
- Walidacja: `ordering` ∈ {`-created_at`, `created_at`, `-popular`, `-valuations`} – w przeciwnym razie fallback do `-created_at` i notyfikacja ostrzegawcza (lub ciche zastąpienie). Inne pola booleany: striktne parsowanie.
- Typy: `BrickSetFiltersState`, `OrderingOption`.
- Propsy: `modelValue: BrickSetFiltersState`, `onUpdate:modelValue` (emit), `disabled?: boolean` (gdy loading), `readonlyMode?: boolean` (opcjonalny wariant jeśli w przyszłości public ma ograniczenia).

### SearchInput
- Opis: Pole tekstowe do wyszukiwania częściowego numeru zestawu (FR-08). Debounce 300 ms.
- Elementy: `<input type="search">` + ikona lupy.
- Interakcje: wpisywanie aktualizuje `q` (po debounce); klawisz Enter natychmiast (flush debounce).
- Walidacja: długość maks 20 znaków; stripping whitespace.
- Typy: `string` (value), event `UpdateSearch`.
- Propsy: `value`, `onInput`, `disabled`.

### ProductionStatusSelect
- Opis: Enum filter (`ACTIVE`, `RETIRED`).
- Elementy: `<select>` z placeholderem „Status (wszystkie)”.
- Interakcje: zmiana → aktualizacja `production_status` lub null.
- Walidacja: value in enum lub null.
- Typy: `ProductionStatus = 'ACTIVE' | 'RETIRED'`.
- Propsy: `value`, `onChange`, `disabled`.

### CompletenessSelect
- Opis: Enum filter (`COMPLETE`, `INCOMPLETE`).
- Walidacja analogicznie.
- Typy: `Completeness = 'COMPLETE' | 'INCOMPLETE'`.
- Propsy: analogiczne.

### AttributeToggles
- Opis: Grupowany zestaw trzech przełączników: has_instructions, has_box, is_factory_sealed.
- Elementy: `<fieldset>` z trzema checkboxami.
- Interakcje: toggle → update boolean / unset (strategia UI: checkbox = strict true/false; brak tri-state w MVP). W query brak param=wartosc oznacza filtr nieaktywny; `false` nie wysyłamy (redukcja szumu) – implementacja: store przechowuje `boolean | null`.
- Walidacja: brak (checkbox gwarantuje bool). Serializacja: gdy `true` → `param=true`.
- Typy: część `BrickSetFiltersState`.
- Propsy: `value: {has_instructions: boolean|null, ...}`, `onChange`.

### OrderingSelect
- Opis: Wybór kolejności listy.
- Elementy: `<select>` z labelami: „Najnowsze” (`-created_at`), „Najstarsze” (`created_at`), „Najpopularniejsze” (`-popular`), „Najwięcej wycen” (`-valuations`).
- Walidacja: fallback default.
- Propsy: `value`, `onChange`, `disabled`.

### MobileFiltersToggle / OffCanvasDrawer
- Opis: Mechanizm ukrywania filtrów na małych ekranach. Toggle button + panel wysuwany z lewej/prawej. Focus trap + aria-modal.
- Interakcje: otwarcie, zamknięcie (ESC, backdrop click), zapis zmian (auto – natychmiast). Bez potrzeby dodatkowego przycisku „Zastosuj”.
- Walidacja: brak dodatkowej.
- Propsy: `open`, `onClose`, `filters` (two-way binding z panelem).

### BrickSetList
- Opis: Kontener listy kart. Odpowiada za layout (grid lub responsywny stacked list). Obsługuje skeleton loading.
- Elementy: wrapper `<ul>` lub `<div role="list">` + children.
- Interakcje: brak własnych poza scroll anchor po zmianie strony (ustawia focus na nagłówku listy dla dostępności).
- Walidacja: oczekuje tablicy elementów spełniających `BrickSetListItemViewModel`.
- Propsy: `items: BrickSetListItemViewModel[]`, `loading`, `emptyMessage`.

### BrickSetCard
- Opis: Prezentacja pojedynczego zestawu. Klikalna cała karta → przejście do `/bricksets/:id`.
- Elementy: numer zestawu (duża typografia), badge statusu produkcji i kompletności, ikony: instrukcja, pudełko, sealed; sekcja statystyk (valuations_count, total_likes) + opcjonalny snippet top wyceny (wartość + likes_count). ARIA: `role="article"`.
- Interakcje: onClick navigate; klawiatura (Enter/Space) przy focus. Hover highlight.
- Walidacja: wymaga wszystkich pól view-modelu; jeśli `topValuation` brak – ukrywa snippet.
- Typy: `BrickSetCardViewModel`.
- Propsy: `model: BrickSetCardViewModel`.

### TopValuationSnippet
- Opis: Mini sekcja pokazująca najwyżej polajkowaną wycenę (value + likes_count + opcjonalny user_id placeholder). Mały badge „TOP”.
- Interakcje: klik przenosi do detalu (kontekst ten sam co karta).
- Walidacja: value > 0, likes_count ≥ 0.
- Propsy: `valuation: TopValuationViewModel`.

### Pagination
- Opis: Standardowy pager: poprzednia, numery stron (skrót: aktualna ±2), następna. Dla dostępności aria-label i aria-current.
- Interakcje: klik zmienia `page` i wykonuje scroll/focus top listy; aktualizuje query param.
- Walidacja: blokada kliknięcia poza zakresem. Całkowita liczba stron = `Math.ceil(count / pageSize)`.
- Propsy: `count`, `page`, `pageSize`, `onChange`.

### EmptyState
- Opis: Komunikat gdy brak wyników: „Brak zestawów spełniających kryteria.” + CTA „Wyczyść filtry”.
- Propsy: `onResetFilters`.

### LoadingOverlay / Skeletons
- Opis: Wskaźnik ładowania (ruchome placeholdery kart) – minimalizacja layout shift.
- Propsy: `count` (ile skeletonów).

## 5. Typy
```ts
// DTO z API
interface BrickSetListItemDTO {
  id: number;
  number: number; // lub string jeśli backend dopuści tekst – tu pozostajemy przy number
  production_status: 'ACTIVE' | 'RETIRED';
  completeness: 'COMPLETE' | 'INCOMPLETE';
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
    currency: 'PLN';
    likes_count: number;
    user_id: number;
  } | null;
  created_at: string;
  updated_at: string;
}

interface BrickSetListResponseDTO {
  count: number;
  next: string | null;
  previous: string | null;
  results: BrickSetListItemDTO[];
}

// Filtry (store + query serializacja)
interface BrickSetFiltersState {
  q: string;
  production_status: 'ACTIVE' | 'RETIRED' | null;
  completeness: 'COMPLETE' | 'INCOMPLETE' | null;
  has_instructions: boolean | null;
  has_box: boolean | null;
  is_factory_sealed: boolean | null;
  ordering: '-created_at' | 'created_at' | '-popular' | '-valuations';
  page: number; // >=1
  pageSize: number; // wewnętrzne – synchronizowane z backend default 20
}

// View Models
interface TopValuationViewModel {
  id: number;
  valueFormatted: string; // np. '400 PLN'
  likesCount: number;
}

interface BrickSetCardViewModel {
  id: number;
  number: string; // sformatowany np. z zero padding opcjonalnie
  productionStatusLabel: string; // mapowanie enum -> PL
  completenessLabel: string;
  hasInstructions: boolean;
  hasBox: boolean;
  isFactorySealed: boolean;
  valuationsCount: number;
  totalLikes: number;
  topValuation?: TopValuationViewModel;
  createdAtRelative: string; // np. '3 dni temu'
}

interface BrickSetListItemViewModel extends BrickSetCardViewModel {}

// Błędy (subset)
interface ApiValidationErrors {
  errors?: Record<string, string[]>;
  code?: string; // 'VALIDATION_ERROR'
  detail?: string; // inne przypadki
}
```
Konwersja DTO → ViewModel odbywa się w funkcji czystej `mapBrickSetDtoToViewModel(dto: BrickSetListItemDTO): BrickSetCardViewModel`.

## 6. Zarządzanie stanem
- Lokalny stan filtrów trzymany w komponencie widoku + synchronizacja z query param poprzez `useRoute()` / `useRouter()`.
- Ewentualny globalny store nie jest wymagany (lista publiczna jest niezależna). Można użyć dedykowanego composable `useBrickSetListSearch()` dla enkapsulacji logiki:
  - Dane: `items`, `count`, `loading`, `error`, `filters`.
  - Metody: `setFilters(partial)`, `fetch()`, `resetFilters()`.
  - Reaktywność: watch na `filters` (z debounced `q`) → fetch.
- Cache strategia: Query key (JSON serializacja filtrów bez `pageSize`). Możliwość dołączenia prostego in‑memory cache (Map) aby uniknąć flicker przy nawigacji wstecz (opcjonalne – oznaczyć jako nice-to-have).
- SSR brak w scope – wyłącznie CSR.

## 7. Integracja API
- Endpoint: `GET /api/v1/bricksets`.
- Parametry mapowane 1:1 z `BrickSetFiltersState` (z pominięciem nulli i `pageSize` jeśli default 20; jeśli UI pozwoli zmienić – dodaj `page_size`).
- Serializacja booleanów: tylko gdy `true` (filtr aktywny). Gdy wymagane wymuszenie wartości false (nie w tym MVP) – rozszerzenie w przyszłości.
- Obsługa odpowiedzi: sprawdzenie statusu 200 → parse JSON → mapowanie `results`.
- Błędy 400: walidacja – pokazanie inline toast „Nieprawidłowe parametry filtrów – przywrócono domyślne sortowanie” oraz reset `ordering` jeśli to jego wina.
- Błędy 401: redirect do `/login?redirect=<current>` (warunkowo – jeśli produkt zdecyduje o wymogu auth). W wersji publicznej po prostu CTA w bannerze; jeśli 401 rzucane – fallback analogiczny.
- Timeout / sieć: Retry pasywny przyciskiem „Spróbuj ponownie”.

## 8. Interakcje użytkownika
1. Wpisanie tekstu w wyszukiwaniu → po 300 ms aktualizacja listy (page reset do 1).
2. Zmiana filtra enum → natychmiastowe odświeżenie (reset page).
3. Zaznaczenie przełącznika (instrukcja/pudełko/sealed) → fetch.
4. Zmiana sortowania → fetch.
5. Klik numeru strony → fetch z zachowaniem filtrów.
6. Klik karty zestawu → nawigacja do `/bricksets/:id`.
7. Klik CTA logowania (banner) → redirect login (z param redirect).
8. Reset filtrów → przywraca domyślne (`ordering='-created_at'`, pozostałe null, q='').

## 9. Warunki i walidacja
- `page < 1` → auto-korekta do 1.
- `ordering` spoza whitelist → fallback do `-created_at`.
- `q` trimming + limit znaków (20) → nadmiar obcięty.
- Booleany: jeśli wartość query nie ∈ {"true","false"} → ignoruj.
- Konsekwencja walidacji: UI nie wysyła niepoprawnych parametrów – minimalizacja błędów 400.

## 10. Obsługa błędów
- 400 VALIDATION_ERROR: toast + ewentualny reset tylko tego parametru, który spowodował błąd.
- 401 NOT_AUTHENTICATED (jeśli wystąpi): pokaz banner + opcjonalnie redirect logic (feature flag?).
- 0 / network error: komponent `ErrorStateInline` z przyciskiem Retry (wywołanie `fetch()`).
- Pusty wynik (count=0) ≠ błąd → `EmptyState`.
- Ochrona przed wielokrotnymi fetch: `loading` gate + abort controller (jeśli implementujemy w composable).

## 11. Kroki implementacji
1. Utworzenie folderu `src/views/bricksets` i pliku `LandingBrickSetListView.vue`.
2. Definicja typów DTO i ViewModel w `src/types/bricksets.ts`.
3. Implementacja funkcji mapującej `mapBrickSetDtoToViewModel` w `src/mappers/bricksets.ts`.
4. Stworzenie composable `useBrickSetListSearch.ts` (stan filtrów + fetch + debounce logic dla q).
5. Implementacja komponentu `BrickSetFiltersPanel.vue` (prop modelValue + emit update) + pod-komponenty selektorów/checkboxów jeśli potrzebne lub użycie bazowych Input/Select.
6. Implementacja komponentu `BrickSetCard.vue` (+ snippet top valuation w slocie / sekcji warunkowej).
7. Implementacja `BrickSetList.vue` (iteracja po kartach + skeleton state + empty state / error state placeholdery).
8. Implementacja `Pagination.vue` (dane: count, page, pageSize, emit change). Dodanie aria-labeli.
9. Implementacja `AuthPromptBanner.vue` (sprawdzenie globalnego stanu auth; fallback button redirect login).
10. Połączenie wszystkiego w `LandingBrickSetListView.vue`: inicjalizacja filtrów z query, watch → fetch, render layout.
11. Dodanie route w `router/index.ts`: `{ path: '/', name: 'public-bricksets', component: LandingBrickSetListView }` + alias `/bricksets`.
12. Dodanie mapowania query param <-> filters (useRoute + router.replace w watchEffect by utrzymać synchroniczność bez historii flood – użycie `replace: true`).
13. Implementacja debounce (np. `useDebounceFn` lub ręcznie) dla pola `q` w composable.
14. Dodanie testów jednostkowych: mapper (poprawność mapowania top valuation), walidacji ordering fallback, reset filtrów.
15. Dodanie testu komponentu `BrickSetFiltersPanel` (emit update przy zmianach, reset).
16. Dodanie testu `useBrickSetListSearch` (mock fetch API – sukces, 400, network error, empty).
17. Wdrożenie stylów Tailwind (layout siatki kart, panel filtrów responsywny, off-canvas dla mobile – prosty `v-if` + fixed panel z animacją). 
18. Accessibility pass: role list → `role="list"`, karty `role="listitem"` lub semantyczne `<li>`. Focus outline i skip link (opcjonalny) do listy.
19. Performance: memoization mapowania DTO → VM (cache by id + updated_at) – opcjonalnie na później.
20. Review + integracja z realnym backendem (sprawdzenie parametrów, w razie potrzeby adapter naming np. `page_size`).
21. Dodanie tłumaczeń tekstów stałych do i18n (pliku locale: labels filtrów, komunikaty empty/error, CTA logowania).
22. QA: manualny test scenariuszy (filtry kombinacji, pusta lista, błędny ordering w URL). 
23. Dokumentacja krótkiego usage w `README` sekcja Frontend Views (opcjonalnie) – link do pliku planu.

---
Plan zgodny z PRD (FR-08, elementy FR-14 częściowo: statystyki), user stories US-012/US-013 (część listowa) oraz strategią UI (publiczny dostęp + CTA logowania). Gotowy do realizacji iteracyjnej.
