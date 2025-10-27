# Architektura UI dla BricksValuation

## 1. Przegląd struktury UI

Aplikacja BricksValuation (MVP) posiada dwupoziomowy model dostępu: warstwa publiczna (read‑only dla listy i szczegółu zestawu) oraz warstwa uwierzytelniona (pełna funkcjonalność CRUD + wyceny + lajki). Interfejs jest aplikacją SPA (Vue 3 + Composition API + Pinia + Vue Router), z podziałem na dwa główne layouty (`PublicLayout` oraz `AuthenticatedLayout`) przełączane dynamicznie na podstawie stanu sesji. Routing rozdziela ścieżki publiczne (landing/lista, szczegóły zestawu, logowanie, rejestracja) i ścieżki z prefixem /app dla obszaru zalogowanego. 

Architektura kładzie nacisk na:
- Czytelne mapowanie wymagań FR/RB/US -> widoki i komponenty.
- Spójne wzorce walidacji i obsługi błędów (inline, toast, redirect).
- Warunkową interaktywność w zależności od stanu (zalogowany / właściciel / brak uprawnień / brak wyceny).
- Uproszczone ścieżki głównych przepływów (rejestracja → logowanie → dodanie zestawu → wycena → lajk).
- Rozszerzalność (łatwe dodanie np. zdjęć lub rankingów) poprzez separację warstw: layout / widok / komponent domenowy / komponent bazowy.

### Kluczowe założenia
- Brak trybu grid – jedna lista (scroll + paginacja / "Load more").
- i18n w języku polskim (enumy i komunikaty błędów mapowane po stronie klienta; kody błędów -> tłumaczenia).
- Wyceny i lajki aktualizowane optymistycznie, z mechanizmem rollback przy błędach 4xx/5xx.
- Komponenty bazowe zapewniają spójność UX (Input, Select, Checkbox, Button, Badge, Card, Modal, Pagination, ErrorMessage, LoadingSpinner).
- Dostępność (ARIA, focus management, kontrast, klawiaturowa nawigacja) priorytetowo wspierana na poziomie komponentów bazowych.

## 2. Lista widoków

Każdy widok opisany jest przez: nazwa, ścieżka, cel, kluczowe dane, komponenty, aspekty UX/A11y/Security oraz powiązane wymagania (FR, RB, US). Widoki logicznie pogrupowane według layoutu.

### 2.1 Layouty

#### PublicLayout
- Ścieżki: `/`, `/login`, `/register`, `/bricksets`, `/bricksets/:id`
- Cel: Ramy dla publicznego dostępu – prezentacja danych zestawów, zachęta do logowania.
- Kluczowe informacje: Stan sesji (niezalogowany), linki do logowania/rejestracji, lista/szczegóły zestawów bez interakcji mutujących.
- Komponenty: `PublicNav`, `Footer`, `AuthPromptBanner` (kontekstowo), `NotificationToaster`.
- UX/A11y/Security: Minimalne rozpraszanie; wszystkie przyciski wymagające auth ukryte lub zastąpione CTA logowania. Brak ujawniania informacji prywatnych. ARIA landmarki (`<nav>`, `<main>`).
- Powiązane wymagania: FR-08, FR-09 (częściowo read-only), FR-18 (granica), US-012, US-013 (wersja publiczna), decyzje sesyjne 1–2.

#### AuthenticatedLayout
- Ścieżki: `/app/*` (np. `/app/bricksets`, `/app/bricksets/:id`, `/app/bricksets/new`, `/app/bricksets/:id/edit`, `/app/my/bricksets`, `/app/my/valuations`, `/app/profile`)
- Cel: Zapewnienie pełnej funkcjonalności po zalogowaniu z odpowiednią nawigacją i zarządzaniem stanem.
- Kluczowe informacje: Dane użytkownika (username, email), zasoby domenowe, akcje (dodaj, edytuj, usuń, wyceń, lajkuj).
- Komponenty: `AuthenticatedNav`, `UserMenu`, `NotificationToaster`, `GlobalErrorBoundary`.
- UX/A11y/Security: Guard routera (401 redirect), ukrywanie akcji niedozwolonych (RB-01). Silne focus management po nawigacji. Brak przechowywania wrażliwych danych w localStorage – rely na cookie.
- Powiązane wymagania: FR-01..FR-17 (większość), FR-04..FR-15, RB-01..RB-03, US-001..US-017.

### 2.2 Widoki Publiczne

#### Landing / Public BrickSet List View
- Ścieżka: `/` (alias `/bricksets` publiczny)
- Cel: Publiczna lista zestawów (read-only) + zachęta do logowania.
- Kluczowe dane: Paginated `bricksets` (number, atrybuty, valuations_count, total_likes, top_valuation), filtry (nieinteraktywne lub aktywne – decyzja: filtry dostępne, ale próba działań wymagających auth → CTA).
- Komponenty: `BrickSetFiltersPanel` (read-only lub pełny), `BrickSetList`, `BrickSetCard`, `AuthPromptBanner`, `Pagination`.
- UX/A11y/Security: Przy interakcji (np. Dodaj zestaw) – modal/login prompt. Zapewnione sortowanie default `-created_at`. Wersja mobilna – filtry w off-canvas drawer.
- Powiązane wymagania: FR-08 (wyszukiwanie), US-012, US-013 (część listowa), decyzje 1–2–4–7–12.

#### Public BrickSet Detail View
- Ścieżka: `/bricksets/:id`
- Cel: Prezentacja pojedynczego zestawu z listą wycen (read-only) + CTA logowania dla akcji.
- Kluczowe dane: Atrybuty zestawu, `valuations` (posortowane), najwyżej polajkowana (top) wyróżniona, liczby: valuations_count, total_likes.
- Komponenty: `BrickSetHeader`, `BrickSetStats`, `ValuationList`, `ValuationCard` (bez aktywnych przycisków lajku/dodania jeśli brak auth), `AuthPromptBanner`.
- UX/A11y/Security: Interakcyjne elementy (like, dodaj wycenę) zastępowane przyciskiem „Zaloguj się aby…”. Ograniczenie scroll-fatigue: sekcja top valuation pinned / highlight.
- Powiązane wymagania: FR-09 (read-only), US-013 (public część), RB-03 (komunikaty przy próbie like bez auth).

### 2.3 Widoki Uwierzytelnione – Zestawy

#### Auth BrickSet List View
- Ścieżka: `/app/bricksets`
- Cel: Pełna interaktywna lista zestawów (filtry, sortowanie) z możliwością przejścia do tworzenia nowego.
- Kluczowe dane: Kolekcja filtrowana + meta (count, page), parametry filtrów w stanie (q, production_status, completeness, flags, ordering).
- Komponenty: `BrickSetFiltersPanel`, `BrickSetList`, `BrickSetCard` (z top valuation snippet), `AddBrickSetButton`, `Pagination`.
- UX/A11y/Security: Zachowanie filtrów w query param (umożliwia sharowalne linki). Debounce dla wyszukiwania (300 ms). Zarządzanie focus po zmianie strony.
- Powiązane wymagania: FR-08, FR-04 (nawigacja do tworzenia), US-012.

#### BrickSet Create View
- Ścieżka: `/app/bricksets/new`
- Cel: Utworzenie nowego zestawu.
- Kluczowe dane: Formularz pól: number, production_status, completeness, has_instructions, has_box, is_factory_sealed, owner_initial_estimate (opcjonalne).
- Komponenty: `BrickSetForm` (re-używalny), `BaseInput`, `BaseSelect`, `BaseCheckbox`, `FormActionsBar`, `ValidationErrorList`.
- UX/A11y/Security: Natychmiastowa walidacja pól (blur + submit). Błąd 409 -> toast z linkiem „Przejdź do istniejącego zestawu”. Keyboard-friendly (Enter submit). Protection przed wielokrotnym submit (loading state).
- Powiązane wymagania: FR-04, FR-05, FR-20, US-004, US-005.

#### BrickSet Detail View (Auth)
- Ścieżka: `/app/bricksets/:id`
- Cel: Pełny detal z interakcjami (dodanie wyceny jeśli brak, lajkowanie cudzych wycen, ewentualne przejście do edycji/usunięcia jeśli `editable`).
- Kluczowe dane: Atrybuty, valuations (paginated lub chunk load), top valuation, flag `editable` (z API), informacja czy user ma już swoją wycenę.
- Komponenty: `BrickSetHeader`, `BrickSetStats`, `BrickSetActions` (Edit/Delete ukryte gdy editable=false), `ValuationFormCard` (warunkowo), `ValuationList` + `ValuationCard` (z like/unlike), `Pagination` / `LoadMoreButton`, `RuleLockBadge` (gdy zablokowane), `DeleteConfirmModal`.
- UX/A11y/Security: Optimistic update lajków, zabezpieczenie przed lajkowaniem własnej wyceny (UI ukrywa przycisk). W przypadku 403 przy próbie edycji – redirect i toast „Zestaw zablokowany (RB‑01)”.
- Powiązane wymagania: FR-06, FR-09, FR-10, FR-11, FR-12, FR-13, FR-20, RB-01..RB-03, US-006..US-011, US-013.

#### BrickSet Edit View
- Ścieżka: `/app/bricksets/:id/edit`
- Cel: Modyfikacja pól zestawu jeśli dozwolone (RB-01).
- Kluczowe dane: Prefilled formularz (jak create) + informacja `editable`.
- Komponenty: `BrickSetForm`, `RuleLockBadge` (jeśli blokada – wtedy natychmiastowy redirect do detail + toast), `FormActionsBar`.
- UX/A11y/Security: Przy wejściu gdy `editable=false` – natychmiastowe przerwanie i komunikat. Focus na pierwszym polu edytowalnym. Idempotentny PATCH (tylko zmienione pola). 
- Powiązane wymagania: FR-06, FR-20, RB-01, US-006.

#### BrickSet Delete (akcja w detail / edit)
- Ścieżka (akcja): Modal w `/app/bricksets/:id` / `/edit`
- Cel: Usunięcie zestawu jeśli reguła pozwala.
- Kluczowe dane: Nazwa/numer zestawu, confirm pattern np. wpisanie numeru (opcjonalne w MVP – prosty confirm modal).
- Komponenty: `DeleteConfirmModal`, `BaseButton` (danger), `NotificationToaster`.
- UX/A11y/Security: Focus trap w modal, ESC zamyka, 403 -> blokada + badge info. Po sukcesie redirect `/app/bricksets` z toast „Zestaw usunięty”.
- Powiązane wymagania: FR-07, RB-01, US-007.

### 2.4 Widoki Uwierzytelnione – Wyceny i Lajki

#### My BrickSets (Owned) View
- Ścieżka: `/app/my/bricksets`
- Cel: Lista zestawów użytkownika z metrykami (valuations_count, total_likes, editable flag).
- Kluczowe dane: Paginated owned bricksets + sort (opcjonalnie -created_at, -valuations, -likes).
- Komponenty: `OwnedBrickSetList`, `OwnedBrickSetCard` (rozszerzenie `BrickSetCard`), `EditableIndicator`, `Pagination`.
- UX/A11y/Security: Szybkie przejście do edycji (ikonka ołówka gdy editable). Tooltip z uzasadnieniem blokady. Zachowanie filtrów / sort w query.
- Powiązane wymagania: FR-14, RB-01, US-014.

#### My Valuations View
- Ścieżka: `/app/my/valuations`
- Cel: Lista wycen użytkownika (bez owner_initial_estimate) z linkiem do zestawu.
- Kluczowe dane: Paginated valuations (brickset reference minimalna: id + number, value, likes_count, created_at).
- Komponenty: `MyValuationsList`, `MyValuationRow`, `Pagination`.
- UX/A11y/Security: Sort domyślny: -created_at. Kliknięcie przenosi do detail zestawu (kotwiczenie wyceny – scroll do wyceny ID w przyszłości). 
- Powiązane wymagania: FR-15, US-015.

#### Add Valuation (Inline Segment)
- Lokalizacja: Wewnątrz `BrickSet Detail View` jeśli user nie ma wyceny.
- Cel: Szybkie dodanie wyceny bez przeładowania strony.
- Kluczowe dane: value, comment (opcjonalne), waluta stała PLN.
- Komponenty: `ValuationFormCard`, `BaseInput`, `BaseTextarea`, `BaseButton`.
- UX/A11y/Security: Ograniczenie długości komentarza (np. 2000 znaków – klient odcina). Błąd 409 -> komunikat inline „Masz już wycenę”. Value walidacja >0.<1M. 
- Powiązane wymagania: FR-10, FR-11, FR-20, US-008, US-009.

#### Like Valuation (Interakcja w liście)
- Lokalizacja: `ValuationCard` (gdy valuation.user_id != currentUser.id).
- Cel: Dodanie lub zdjęcie lajka (jeśli DELETE endpoint wspierany) / tylko POST jeśli nie.
- Kluczowe dane: likes_count, isLikedByMe (pochodna store / heurystyka po POST 201).
- Komponenty: `LikeButton` (ikonka heart filled/outline), `Tooltip`.
- UX/A11y/Security: Optimistic toggle + rollback przy 409. Aria-label dynamiczny: „Polub wycenę” / „Cofnij polubienie”. Brak przycisku przy własnej wycenie.
- Powiązane wymagania: FR-12, FR-13, FR-20, RB-03, US-010, US-011.

### 2.5 Widoki Uwierzytelnione – Użytkownik

#### Login View
- Ścieżka: `/login`
- Cel: Uwierzytelnienie użytkownika.
- Kluczowe dane: username/email, password.
- Komponenty: `AuthFormLayout`, `BaseInput`, `BaseButton`, `InlineError`, link „Załóż konto”.
- UX/A11y/Security: Po sukcesie redirect do strony docelowej (deep link) lub `/app/bricksets`. Zalecany mechanizm zapamiętania poprzedniej ścieżki (query: redirect). Brak precyzyjnego rozróżnienia błędu: zawsze generuje ogólny komunikat „Nieprawidłowe dane logowania”.
- Powiązane wymagania: FR-02, FR-18, FR-20, US-002.

#### Register View
- Ścieżka: `/register`
- Cel: Rejestracja konta.
- Kluczowe dane: username, email, password, confirm_password.
- Komponenty: `AuthFormLayout`, `BaseInput`, `PasswordStrengthHint` (opcjonalnie), `InlineError`.
- UX/A11y/Security: Walidacja hasła min 8 znaków + zgodność obu pól po stronie klienta. Po sukcesie redirect do `/login` z toast „Konto utworzone”. Brak dodatkowych pól (prostota). 
- Powiązane wymagania: FR-01, FR-16, FR-17 (pośrednio), FR-20, US-001.

#### Profile View
- Ścieżka: `/app/profile`
- Cel: Podgląd podstawowych danych konta (username, email, data utworzenia). (Brak edycji w MVP.)
- Kluczowe dane: user DTO z `/auth/me`.
- Komponenty: `ProfileCard`, `BaseCard`, `AvatarPlaceholder`.
- UX/A11y/Security: Brak edycji (MVP). Ochrona przed pustym user (gdy 401) → redirect login.
- Powiązane wymagania: Pośrednio FR-02, FR-18 (dostęp autoryzowany), US-002.

#### Logout (akcja)
- Ścieżka: (akcja w menu) POST `/auth/logout` → redirect `/`.
- Cel: Zakończenie sesji.
- Kluczowe dane: Brak payload; czyszczenie store, unieważnienie cookie po stronie backendu (lub klient usuwa cookie jeśli samego body brak).
- Komponenty: `UserMenu`, `ConfirmActionModal` (opcjonalnie), `NotificationToaster`.
- UX/A11y/Security: Po kliknięciu natychmiastowa akcja (brak modala w MVP). Toast „Wylogowano pomyślnie”. 
- Powiązane wymagania: FR-03, FR-18, US-003.

### 2.6 Widoki Systemowe / Błędów

#### NotFound View
- Ścieżka: Catch-all (`/:pathMatch(.*)*`)
- Cel: Informacja o nieistniejącej stronie.
- Kluczowe dane: Kod 404, link powrotny.
- Komponenty: `NotFoundIllustration`, `BaseButton`.
- UX/A11y/Security: Przyjazny komunikat PL. Focus na nagłówku po wejściu. 
- Powiązane wymagania: Ogólna jakość UX (niebezpośrednio FR-20).

#### Global Error Boundary View / Fallback
- Ścieżka: (komponent opakowujący) – fallback UI.
- Cel: Bezpieczne przechwycenie nieobsłużonych błędów komponentów.
- Kluczowe dane: Ogólny komunikat + opcja reload.
- Komponenty: `GlobalErrorBoundary`, `ErrorMessage`.
- UX/A11y/Security: Nie wycieka stack trace. Komunikat prosty: „Wystąpił nieoczekiwany błąd”.
- Powiązane wymagania: FR-20 (spójne błędy, user-friendly).

## 3. Mapa podróży użytkownika

### 3.1 Główne przepływy

1. Rejestracja → Logowanie → Lista zestawów (auth) → Dodanie zestawu → Przegląd detalu → Dodanie wyceny → Lajkowanie cudzej wyceny.
2. Publiczny użytkownik → Ogląda listę i detal → Próbuje polubić / dodać wycenę → CTA logowania → Logowanie → Automatyczny redirect do pierwotnej ścieżki → Interakcja dostępna.
3. Właściciel edytuje zestaw: Wejście na detal → (editable true) → Klik „Edytuj” → Zmiana pól → Zapis → Powrót na detal (odświeżone dane). Gdy w międzyczasie inny user doda wycenę → 403 → Toast „Zestaw zablokowany” → Akcje ukryte.
4. Usuwanie zestawu: Detal → Delete (modal) → Potwierdzenie → Redirect lista + toast. Blokada reguły RB‑01 → brak przycisku (nie frustracja 403 po kliknięciu).
5. Lista moich wycen: Nav → „Moje wyceny” → Przegląd rankingowy lajków → Klik wyceny → Detal zestawu (scroll do pozycji w przyszłości / highlight).

### 3.2 Kroki szczegółowe – Przepływ „Dodaj zestaw i uzyskaj wycenę”
1. Użytkownik loguje się (Login View) – FR-02.
2. Przechodzi do `/app/bricksets` – widzi listę (Auth BrickSet List) – FR-08.
3. Klik „Dodaj zestaw” – nawigacja do `/app/bricksets/new` – FR-04.
4. Wypełnia formularz – walidacja lokalna (FR-20); submit.
5. Backend zwraca 201 lub 409:
   - 201 → redirect `/app/bricksets/:id` (Detail) – FR-04.
   - 409 → toast + link „Zobacz istniejący” – FR-05.
6. Na detail (bez własnej wyceny) widoczny `ValuationFormCard` – FR-10.
7. Uzupełnia wartość i komentarz → submit → 201; formularz znika – FR-10, FR-11.
8. Lista wycen aktualizuje się – FR-09.
9. Inny użytkownik lajkuje wycenę właściciela → reguła RB‑01 może zablokować edycję/usuń (przy kolejnym wejściu `editable=false`).

### 3.3 Stany przejściowe i komunikaty
- Loading stany dla fetch (skeleton/placeholder) – uniknięcie skoków layoutu.
- Empty states: brak zestawów, brak wycen – zachęty CTA (np. „Brak wycen – dodaj pierwszą”).
- Error states: 401 (redirect login), 403 (toast + ukrycie akcji), 404 (NotFound), 409 (toast + link), VALIDATION_ERROR (inline form), LIKE_DUPLICATE (revert heart + tooltip).

## 4. Układ i struktura nawigacji

### 4.1 Poziomy nawigacji
- Globalny top bar (PublicNav / AuthenticatedNav) z adaptacyjnym menu.
- Secondary contextual actions (np. przycisk „Dodaj zestaw” w liście / „Edytuj” w detalu) wewnątrz treści.
- Breadcrumbs nie są krytyczne w MVP (płytka hierarchia) – pominięte dla prostoty.

### 4.2 PublicNav
- Elementy: Logo (link `/`), „Zestawy” (`/`), „Zaloguj się” (`/login`), „Zarejestruj się” (`/register`).
- Mobile: Hamburger → panel z tymi samymi linkami.
- Dostępność: ARIA role navigation, focus style widoczny, `aria-current="page"` dla aktywnej sekcji.

### 4.3 AuthenticatedNav
- Elementy: Logo (`/app/bricksets`), „Zestawy”, „Moje zestawy”, „Moje wyceny”, Avatar (menu: „Profil”, „Wyloguj”).
- Desktop: poziomy układ; Mobile: hamburger + panel; Avatar menu jako `menu` + `menuitem` rola.
- Security: Wylogowanie czyści store + navigacja do `/`.

### 4.4 Route Guards
- `beforeEach`: sprawdza meta `requiresAuth`; brak sesji → redirect `/login?redirect=<target>`.
- Po logowaniu: jeśli redirect param jest do ścieżki chronionej – nawiguj tam; fallback `/app/bricksets`.
- Ochrona edycji: guard w komponencie detail i edit – jeśli `editable=false` i ścieżka `edit` → redirect detail.

### 4.5 Deep Linking i odświeżanie
- Bezpośrednie wejście na `/app/bricksets/:id` pobiera profil (jeśli nie w store) + dane zestawu.
- Brak migotania nawigacji: store auth ładowany przed mount layoutu (suspense / initial fetch w router `beforeResolve`).

### 4.6 Responsywność
- Breakpointy: sm, md, lg (Tailwind). Filtry jako panel stały (desktop) i modal/drawer (mobile). Lista wycen – jednokolumnowa na mobile, multi-sekcja (top valuation + reszta) na desktop.

## 5. Kluczowe komponenty

### 5.1 Komponenty Bazowe (Atomic)
- `BaseInput` – tekstowe/pasujące typy, etykieta, błąd, opis pomocniczy; aria-describedBy.
- `BaseSelect` – enumeracje z mapowaniem label (PL), klawiaturowa nawigacja.
- `BaseCheckbox` – stała szerokość, focus ring, etykieta klikalna.
- `BaseButton` – warianty: primary, secondary, danger, subtle; rozmiary; loading state (spinner inline, aria-busy).
- `BaseBadge` – semantyczne oznaczenia statusów (np. „W produkcji”, „Kompletny”).
- `BaseCard` – kontener z nagłówkiem/slotem akcji.
- `BaseModal` – focus trap, aria-modal, zamknięcie ESC.
- `LoadingSpinner` – dostępny tekst alt (sr-only).
- `ErrorMessage` – zunifikowane wyświetlanie błędów globalnych.
- `Pagination` – przyciski poprzednia/następna + numer strony, aria-label.
- `NotificationToaster` – region ARIA live polite.

### 5.2 Komponenty Domenowe
- `BrickSetCard` – skrót atrybutów zestawu + statystyki (valuations_count, total_likes, top valuation snippet).
- `BrickSetFiltersPanel` – wyszukiwanie + filtry + sortowanie + reset.
- `BrickSetForm` – create/edit reuse; przetwarza dane formularza → payload API.
- `BrickSetHeader` – nagłówek detalu (numer zestawu + status + completeness).
- `BrickSetStats` – metryki zestawu (valuations_count, total_likes, owner_initial_estimate).
- `BrickSetActions` – Edit/Delete warunkowo; ukrywa przy `editable=false`.
- `ValuationFormCard` – formularz dodania wyceny (value, comment) – integracja walidacji lokalnej.
- `ValuationList` – stronicowana lista z sortem fixed (likes desc, date asc fallback).
- `ValuationCard` – wycena z przyciskiem serca (like) + licznik; tryb read-only / active.
- `LikeButton` – ikona (outline/filled), aria-pressed.
- `RuleLockBadge` – wyjaśnienie blokady edycji/usuwania (RB‑01) z tooltip.
- `OwnedBrickSetCard` – wariacja z `editable` i szybkim linkiem do edycji.
- `MyValuationRow` – tabela/ lista skrócona z linkiem do zestawu.
- `AuthPromptBanner` – CTA logowania (np. „Zaloguj się aby dodać wycenę i lajkować”).
- `ProfileCard` – dane użytkownika.
- `UserMenu` – rozwijane akcje konta.
- `DeleteConfirmModal` – potwierdzenie usunięcia.

### 5.3 Store / Zarządzanie Stanem (Pinia – kontrakt UI ↔ API)
- `authStore`: user, isAuthenticated, actions: login, logout, register, fetchProfile.
- `bricksetsStore`: items, currentBrickSet, filters, pagination; actions: fetch/list/detail/create/update/delete.
- `valuationsStore`: valuationsByBrickSet, myValuations; actions: fetchForBrickSet, create, fetchMine.
- `likesStore`: likedValuationIds; actions: like, unlike (jeśli DELETE dostępny), hydrateFromValuations.

### 5.4 Wzorce Dostępności
- Każdy formularz: role=form, submit opisany, błędy w aria-live assertive minimalnie.
- Ikony (heart, edit, delete) z `aria-label` i `title`.
- Toastery: aria-live polite, auto dismiss z opcją zamknięcia manualnego.

### 5.5 Bezpieczeństwo na Poziomie UI
- Brak ekspozycji tokena w JS poza dostępnością przez cookie HttpOnly.
- Brak wyświetlania surowego HTML z komentarza (escape / plain text rendering).
- Ukrywanie akcji zamiast disable redukuje enumerację reguł (nieeksponowanie warunków mechaniki niepotrzebnie).
- Centralna obsługa 401 (wipe stores + redirect).

### 5.6 Mapowanie Wymagań (Skrót)
- FR-01/US-001: Register View + `authStore.register` + walidacje.
- FR-02/US-002: Login View + `authStore.login`.
- FR-03/US-003: Logout (UserMenu action).
- FR-04/US-004: BrickSet Create View.
- FR-05/US-005: 409 handling w Create (toast + link).
- FR-06/US-006: Edit View + `editable` gating.
- FR-07/US-007: Delete modal + reguła RB‑01.
- FR-08/US-012: Listy (public + auth) + FiltersPanel.
- FR-09/US-013: Detail View z ValuationList + Top valuation highlight.
- FR-10/US-008: ValuationFormCard.
- FR-11/US-009: Ukrycie formularza po dodaniu / 409 VALUATION_DUPLICATE.
- FR-12/US-010: LikeButton (optimistic) + likesStore.
- FR-13/US-011: Brak LikeButton przy własnej wycenie.
- FR-14/US-014: My BrickSets View.
- FR-15/US-015: My Valuations View.
- FR-16: Register email validation (BaseInput + regex).
- FR-17: (Backend hash) – UI nie wyświetla haseł, maskuje input.
- FR-18/US-017: Route guards + conditional layouts.
- FR-19/US-018: (Wyłączone z UI w MVP – brak metrics view) – decyzja 3.
- FR-20/US-016: Spójne błędy (inline + toast + mapping kodów).
- RB-01: `editable` gating w detail/edit.
- RB-02: Jedna wycena – formularz warunkowy.
- RB-03: LikeButton warunkowy.
- RB-04: (Backend; UI nie eksponuje metryki) – N/A w MVP.
- RB-05: Numer jako liczba – walidacja w BrickSetForm.
- RB-06: Public vs Auth layout separacja.

### 5.7 Przypadki Brzegowe i Strategia Obsługi
- Brak wyników filtrów: Pokaż `EmptyStateCard` z przyciskiem „Wyczyść filtry”.
- Duplikaty (409): Wyróżniony link anchor do istniejącego zestawu (otwórz w bieżącej karcie).
- Utrata sesji (401 w tle podczas akcji): Toaster „Sesja wygasła” + redirect login (z param redirect).
- Lajk wycofany (jeśli DELETE brak): UI prezentuje tylko możliwość like (no unlike) – ikonka pozostaje wypełniona? (Decyzja: jeśli brak DELETE – brak toggle; heart disabled po kliknięciu).
- Opóźnione ładowanie valuations: Pokazuj skeleton karty (3 placeholdery) zanim lista się pojawi.
- Duże komentarze (blisko limitu): UI pokazuje licznik znaków (np. 0/2000).
- Race condition edit vs new external valuation: PATCH → 403; UI refetch detail i pokazuje badge z blokadą.

### 5.8 Potencjalne Punkty Bólu i Mitigacje
- „Czemu nie mogę edytować?” → Badge + tooltip z jasnym powodem (RB‑01).
- „Czemu nie mogę polubić?” (public) → CTA banner / tooltip „Zaloguj się aby lajkować”.
- „Czy moja akcja zadziałała?” → Natychmiastowe optimistic UI + toast sukcesu przy create/delete.
- „Zgubiłem się po logowaniu” → Deep link redirect param & fallback.
- „Filtry niejasne” → Sekcja „Zaawansowane filtry (rozwiń)” + reset jednym kliknięciem.
- „Dużo przewijania w wycenach” → Highlight top valuation + lazy load „Pokaż więcej”.

---
Architektura zapewnia zgodność z zakresem MVP, czytelne mapowanie wymagań na widoki i komponenty oraz przewidywalną ścieżkę rozbudowy (dodanie obrazów, rankingów, metryk) bez naruszania istniejącej struktury.
