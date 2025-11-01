# Plan implementacji funkcjonalności „Like Valuation" w ValuationCard

## 1. Przegląd

Funkcjonalność "Like Valuation" umożliwia zalogowanemu użytkownikowi polajkowanie wycen dodanych przez innych użytkowników. Interakcja zachodzi w komponencie `ValuationCard`, który wyświetla pojedynczą wycenę. Przycisk lajku ma stan `disabled` jeśli użytkownik jest autorem wyceny lub już ją polajkował. Lajk jest wysyłany na API jako żądanie POST, a po sukcesie licznik lajków jest aktualizowany.

**Powiązane wymagania:**
- FR-12: Lajkowanie wycen (FR-13: blokada lajkowania własnej)
- FR-20: Obsługa błędów walidacji
- RB-03: Jeden lajk użytkownika na jedną wycenę; brak lajkowania własnej
- US-010: Lajkowanie wyceny innego użytkownika
- US-011: Blokada lajkowania własnej wyceny

## 2. Routing widoku

Funkcjonalność nie posiada dedykowanej ścieżki routingu - działa w kontekście istniejących widoków:
- Strona detali zestawu: `/bricksets/{id}` - gdzie wyświetlane są wszystkie wyceny
- Lista moich wycen: `/my-valuations` - gdzie wyświetlane są wyceny użytkownika (brak możliwości lajkowania własnych)

## 3. Struktura komponentów

```
ParentComponent (np. BrickSetDetail lub MyValuations)
└── ValuationCard
    ├── ValuationValueDisplay
    ├── ValuationCommentDisplay
    ├── LikeButton (ZMIENIONY)
    │   ├── HeartIcon (filled/outline)
    │   ├── LikeCount
    │   └── LoadingSpinner (opcjonalnie)
    └── ValuationMetadata
```

**Notatka:** Komponent `LikeButton` już istnieje i będzie zmodyfikowany. Funkcjonalność lajkowania będzie obsługiwana w komponencie `ValuationCard` lub w composable.

## 4. Szczegóły komponentów

### 4.1 ValuationCard (ZMIENIONY)

**Opis:** Karta pojedynczej wyceny. Moduł będzie rozszerzony o obsługę lajkowania z optimistic updates i rollback.

**Główne elementy:**
- Wartość wyceny (duży font)
- Komentarz (opcjonalnie z rozszerzeniem)
- Data utworzenia (format względny)
- Przycisk lajku (LikeButton) - **ZMIENIONY**
- Info o autorze (user ID)
- Icona/badge jeśli to wycena użytkownika

**Obsługiwane interakcje:**
- Kliknięcie przycisku LikeButton:
  1. Optimistic toggle: zwiększ likesCount w UI
  2. POST na API
  3. Jeśli sukces (201): zachowaj zmianę, emit event
  4. Jeśli błąd 409 (duplikat): rollback likesCount, pokaż toast error
  5. Jeśli błąd 403 (własna wycena): rollback, pokaż komunikat
  6. Jeśli inne błędy: rollback, pokaż toast

**Obsługiwana walidacja:**
- Walidacja: `currentUserId !== valuation.userId` (nie samego siebie)
- Walidacja: `isLikedByMe` - czy już lajkowane
- Walidacja: user must be authenticated

**Typy:**
- `ValuationViewModel` (props)
- `LikeValuationRequest` (DTO do API)
- `LikeValuationResponse` (DTO z API)

**Propsy:**
```typescript
{
  valuation: ValuationViewModel;
  currentUserId: number | null;      // ID zalogowanego użytkownika (null jeśli niezalogowany)
  isLikedByMe?: boolean;              // Czy bieżący user już polajkował
}
```

**Emits:**
```typescript
{
  'valuation-liked': [valuationId: number, newLikesCount: number];
  'like-error': [error: string];
}
```

### 4.2 LikeButton (ZMIENIONY)

**Opis:** Przycisk lajku z ikoną serca i licznikiem. Będzie zmieniony aby wspierać pełny cykl lajkowania.

**Główne elementy:**
- Ikona serca (filled jeśli lajkowany, outline jeśli nie)
- Licznik lajków
- Spinner podczas ładowania
- Aria-label dynamiczny

**Obsługiwane interakcje:**
- Click: emitowanie zdarzenia `like`
- Hover: zmiana koloru ikonki
- Loading: wyświetlenie spinnera, disable przycisku

**Obsługiwana walidacja:**
- `disabled` prop: prevents click (zarówno jeśli user jest autorem jak i już polajkował)

**Typy:**
- Brak nowych

**Propsy:**
```typescript
{
  likesCount: number;
  disabled: boolean;                  // Jeśli true: button disabled i nieaktywny
  loading: boolean;
  isLiked?: boolean;                  // Jeśli true: serce filled
}
```

**Emits:**
```typescript
{
  like: [];
}
```

### 4.3 useLikeValuation Composable (NOWY)

**Opis:** Composable do obsługi logiki lajkowania wyceny, w tym optimistic updates i rollback.

**Przeznaczenie:**
- Zarządzanie stanem like (isLiking, isLiked)
- API calls (POST /valuations/{id}/likes)
- Error handling
- Optimistic updates

**Reaktywne properties:**
- `isLiking: Ref<boolean>` - czy trwa żądanie
- `isLiked: Ref<boolean>` - czy już lajkowano
- `currentLikesCount: Ref<number>` - licznik (dla rollback)

**Methods:**
- `toggleLike(): Promise<void>` - główna funkcja obsługująca lajk
  - Waliduje czy można lajkować
  - Robi optimistic toggle
  - Wysyła POST na API
  - Obsługuje błędy i rollback
  - Emituje event na sukces

## 5. Typy

### 5.1 API DTOs

```typescript
/**
 * Request dla POST /api/v1/valuations/{valuation_id}/likes
 */
export interface LikeValuationRequest {
  // Body opcjonalny, może być pusty {}
}

/**
 * Response (201 Created) - struktura minimalna
 */
export interface LikeValuationResponse {
  valuation_id: number;
  user_id: number;
  created_at: string; // ISO 8601
}

/**
 * Error Response 403 - nie może lajkować własnej wyceny
 */
export interface LikeForbiddenError {
  detail: string;
  code: 'LIKE_OWN_VALUATION_FORBIDDEN';
}

/**
 * Error Response 409 - już lajkowano tę wycenę
 */
export interface LikeDuplicateError {
  detail: string;
  code: 'LIKE_DUPLICATE';
}
```

### 5.2 ViewModels

```typescript
/**
 * State do śledzenia like interakcji
 */
export interface LikeState {
  isLiking: boolean;
  isLiked: boolean;
  likesCount: number;
  error: string | null;
}

/**
 * Konfiguracja Like Button
 */
export interface LikeButtonConfig {
  disabled: boolean;               // User jest autorem lub nie zalogowany
  loading: boolean;
  liked: boolean;
}
```

## 6. Zarządzanie stanem

### 6.1 State Management Strategy

Lajkowanie jest operacją pojedynczą na daną wycenę w kontekście. Rekomendacja: **Composable + Local Component State** (nie Pinia, bo state jest lokalny do komponentu).

### 6.2 useLikeValuation Composable

**Przeznaczenie:** Zarządzanie logicznym stanów lajkowania i komunikacją z API.

**Reaktywne properties:**
```typescript
{
  isLiking: Ref<boolean>;           // Czy trwa żądanie POST
  isLiked: Ref<boolean>;            // Czy użytkownik już polajkował
  currentLikesCount: Ref<number>;   // Licznik dla optimistic rollback
}
```

**Methods:**
```typescript
{
  toggleLike(valuationId: number): Promise<void>;  // Główna funkcja
  validateCanLike(): boolean;                       // Sprawdzenie warunków
}
```

**Integracja:**
```typescript
// W ValuationCard:
const likeState = useLikeValuation(currentUserId, valuation.userId);

async function handleLike() {
  try {
    await likeState.toggleLike(valuation.id);
    // Optimistic update:
    const oldCount = valuation.likesCount;
    valuation.likesCount += 1;
    likeState.isLiked.value = true;

    // API request
    // Jeśli 409: rollback do oldCount
  } catch (error) {
    // Handle error, rollback
  }
}
```

## 7. Integracja API

### 7.1 Endpoint: POST /api/v1/valuations/{valuation_id}/likes

**URL:** `/api/v1/valuations/{id}/likes`

**Metoda:** POST

**Body:** {} (pusty lub opcjonalnie)

**Headers:**
```
Authorization: Bearer <token>  (lub HttpOnly cookie)
```

**Response (201 Created):**
```json
{
  "valuation_id": 77,
  "user_id": 42,
  "created_at": "2025-10-21T12:34:56Z"
}
```

**Error Responses:**
- `403 LIKE_OWN_VALUATION_FORBIDDEN`: Próba polajkowania własnej wyceny
- `409 LIKE_DUPLICATE`: Już polajkowano tę wycenę
- `404 VALUATION_NOT_FOUND`: Wycena nie istnieje
- `401 NOT_AUTHENTICATED`: Brak sesji

### 7.2 Endpoint: DELETE /api/v1/valuations/{valuation_id}/likes (OPCJONALNY)

**Notatka:** PRD nie wymaga usuwania lajków, ale API plan je wspomina. MVP może **nie implementować**.

Jeśli zaimplementowany:
```
DELETE /api/v1/valuations/{id}/likes
Response: 204 No Content
```

### 7.3 Frontend Integration

```typescript
// useLikeValuation.ts
async function toggleLike(valuationId: number): Promise<void> {
  isLiking.value = true;
  const previousLikeState = isLiked.value;
  const previousCount = currentLikesCount.value;

  try {
    // Optimistic update
    isLiked.value = true;
    currentLikesCount.value += 1;

    // API call
    const response = await apiClient.post(
      `/v${env.api.version}/valuations/${valuationId}/likes`,
      {},
      { withCredentials: true }
    );

    // Success - state remains updated
    // Emit success event
  } catch (err) {
    // Rollback optimistic update
    isLiked.value = previousLikeState;
    currentLikesCount.value = previousCount;

    // Handle specific errors
    if (isAxiosErrorLike(err)) {
      const status = err.response?.status;
      if (status === 403) {
        throw new Error('Nie możesz polajkować własnej wyceny');
      } else if (status === 409) {
        throw new Error('Już polajkowałeś tę wycenę');
      }
    }
    throw err;
  } finally {
    isLiking.value = false;
  }
}
```

## 8. Interakcje użytkownika

### 8.1 Scenariusz 1: Polajkowanie wyceny

1. Użytkownik widzi wycenę innego użytkownika
2. Przycisk lajku jest aktywny (nie disabled)
3. Kliknie na serce
4. **Optimistic:** licznik lajków wzrasta o 1, serce zmienia się na filled
5. **API:** POST /valuations/{id}/likes
6. **Sukces (201):** zmiana pozostaje, toast "Polajkowałeś wycenę" (opcjonalnie)
7. **Błąd 409:** licznik wraca do poprzedniej wartości, toast "Już polajkowałeś tę wycenę"
8. **Błąd 403:** rollback, toast "Nie możesz polajkować własnej wyceny"

### 8.2 Scenariusz 2: Próba polajkowania własnej wyceny

1. Użytkownik ogląda szczegóły zestawu
2. Widzi swoją wycenę
3. Przycisk lajku jest **disabled** (szary, brak kursora)
4. Aria-label: "Nie możesz polajkować własnej wyceny"
5. Brak możliwości klikniecia

### 8.3 Scenariusz 3: Ponowne polajkowanie

1. Użytkownik już polajkował wycenę
2. Przycisk lajku wyświetla filled serce
3. Aria-label: "Usuń polubienie" (jeśli DELETE wspierany)
4. Klikniecie → 409 LIKE_DUPLICATE (jeśli nie wspieramy DELETE)
5. Toast: "Już polajkowałeś tę wycenę"
6. **Alternatywnie:** jeśli DELETE wspierany: klikniecie → DELETE request, zmiana na outline serce

### 8.4 Scenariusz 4: Brak autentykacji

1. Użytkownik niezalogowany przegląda szczegóły zestawu
2. Przycisk lajku jest disabled
3. Aria-label: "Zaloguj się aby lajkować"
4. Klikniecie: wyświetlenie toast "Zaloguj się aby lajkować" + opcjonalny link do loginu

## 9. Warunki i walidacja

### 9.1 Warunki wymagane przez API

| Warunek | Komponenent | Walidacja |
|---------|-----------|-----------|
| `currentUserId !== valuation.userId` | ValuationCard | Disable button jeśli równe |
| Użytkownik zalogowany | ValuationCard | `currentUserId !== null` |
| Valuation ID istnieje | useLikeValuation | Używany z API - zwróci 404 jeśli nie |
| Typ żądania: POST z credentialsami | useLikeValuation | `withCredentials: true` |

### 9.2 Walidacja na Frontend

| Validacja | Gdzie | Akcja |
|-----------|-------|-------|
| `currentUserId !== null` | ValuationCard | Disable button |
| `currentUserId !== valuation.userId` | ValuationCard | Disable button |
| `isLiking === false` | LikeButton | Disable button podczas POST |
| LikesCount > 0 | LikeButton | Display count (może być 0) |
| Valuation ID jest number | useLikeValuation | Typowanie TypeScript |

## 10. Obsługa błędów

### 10.1 Potencjalne błędy i rozwiązania

| Błąd | HTTP | Przyczyna | Rozwiązanie |
|-----|------|----------|------------|
| Własna wycena | 403 LIKE_OWN_VALUATION_FORBIDDEN | User == author | Disable button ex-post (nie powinno się zdarzyć) |
| Już lajkowano | 409 LIKE_DUPLICATE | Duplicate like attempt | Rollback, toast "Już lajkowałeś" |
| Brak wyceny | 404 VALUATION_NOT_FOUND | Valuation deleted | Rollback, toast "Wycena nie istnieje" |
| Brak sesji | 401 NOT_AUTHENTICATED | Token wygasł | Rollback, toast "Zaloguj się", opcjonalnie redirect |
| Network error | - | Brak połączenia | Rollback, toast "Błąd połączenia" |
| Server error | 500+ | Błąd serwera | Rollback, toast "Błąd serwera" |

### 10.2 User-Friendly Komunikaty (i18n)

```typescript
// Errors
'likes.errors.ownValuation': 'Nie możesz polajkować własnej wyceny'
'likes.errors.duplicate': 'Już polajkowałeś tę wycenę'
'likes.errors.notFound': 'Wycena nie istnieje'
'likes.errors.unauthorized': 'Zaloguj się aby lajkować'
'likes.errors.network': 'Błąd połączenia - spróbuj ponownie'
'likes.errors.server': 'Błąd serwera - spróbuj później'

// Success
'likes.success.liked': 'Polajkowałeś wycenę!'

// Button text/labels
'likes.button.like': 'Polub wycenę'
'likes.button.liked': 'Już polajkowałeś'
'likes.button.loginToLike': 'Zaloguj się aby lajkować'
```

## 11. Kroki implementacji

### Faza 1: Types

1. **Zaktualizuj `src/types/bricksets.ts`:**
   - Dodaj `LikeValuationRequest`
   - Dodaj `LikeValuationResponse`
   - Dodaj `LikeState`
   - Dodaj `LikeButtonConfig`

### Faza 2: Composables

2. **Stwórz `src/composables/useLikeValuation.ts`:**
   - Implementuj reactive state: `isLiking`, `isLiked`, `currentLikesCount`
   - Implementuj `toggleLike(valuationId)` method
   - Implementuj optimistic update logic
   - Implementuj error handling + rollback
   - Implementuj walidację (`validateCanLike()`)

### Faza 3: Komponenty - LikeButton

3. **Zmień `src/components/bricksets/LikeButton.vue`:**
   - Dodaj `isLiked` prop
   - Zmień ikonę serca na filled/outline w zależności od `isLiked`
   - Zaktualizuj aria-label aby uwzględniał czy już lajkowano
   - Obsługuj hover state (zmiana koloru)
   - Zachowaj spinner loading state

### Faza 4: Komponenty - ValuationCard

4. **Zmień `src/components/bricksets/ValuationCard.vue`:**
   - Zaimportuj `useLikeValuation` composable
   - Dodaj props: `currentUserId`, `isLikedByMe`
   - Zainicjuj composable
   - Implementuj `handleLike()` handler:
     - Sprawdź czy można lajkować
     - Wołaj composable.toggleLike()
     - Obsługuj błędy z toast messages
   - Aktualizuj local state likesCount
   - Emituj `valuation-liked` event
   - Przekaż `isLiked` i `isLiking` do LikeButton

### Faza 5: Parent Components

5. **Zaktualizuj komponenty używające `ValuationCard`:**
   - `BrickSetDetail.vue`: dodaj `currentUserId` z auth store
   - `MyValuationsView.vue`: opcjonalnie przekaż `currentUserId` (dla consistency)
   - Obsługuj emits z `ValuationCard`
   - Potencjalnie refresh danych po lajku (opcjonalnie)

6. **Zaktualizuj `useBrickSetDetail.ts` composable:**
   - Jeśli stosuje się, dodaj `likeValuation(valuationId)` method
   - Lub pozostaw logikę w komponencie `ValuationCard`

### Faza 6: i18n

7. **Zaktualizuj pliki tłumaczeń `src/locales/pl.json`:**
   - Dodaj klucze dla error komunikatów
   - Dodaj klucze dla button labels
   - Dodaj klucze dla toast notifications

### Faza 7: Notyfikacje

8. **Integracja z notification store:**
   - Przy lajk success: toast success "Polajkowałeś wycenę!"
   - Przy lajk error: toast error z komunikatem

### Faza 8: Testy

9. **Stwórz testy jednostkowe:**
   - `useLikeValuation.spec.ts`:
     - Test toggleLike success
     - Test toggleLike 409 duplicate
     - Test toggleLike 403 forbidden
     - Test rollback na error
   - `LikeButton.spec.ts`:
     - Test rendering filled/outline serce
     - Test disabled state
     - Test emit na click
   - `ValuationCard.spec.ts`:
     - Test handleLike flow
     - Test disable button dla own valuation
     - Test emit `valuation-liked`

10. **Testy integracyjne:**
    - `brickset-detail.cy.ts`:
      - Test like valuation flow
      - Test 409 duplicate error
      - Test 403 forbidden error

### Faza 9: Accessibility & Polish

11. **Accessibility Review:**
    - Verify aria-label dynamiczny
    - Verify focus management
    - Verify keyboard navigation (ENTER/SPACE na button)
    - Verify tabindex

12. **Dark Mode Review:**
    - Verify LikeButton colors na dark mode
    - Verify hover states

13. **Performance Review:**
    - Optimistic update nie blokuje UI
    - Spinner animacja nie jest heavy

### Faza 10: Documentation

14. **Dokumentacja:**
    - JSDoc dla `useLikeValuation`
    - Komentarze w `ValuationCard` wyjaśniające flow
    - README dla komponenty jeśli wymagane

---

## Uwagi dodatkowe

### Optimistic Updates Pattern

Widok powinna implementować optimistic updates, aby U był responsywny:

```typescript
// 1. Immediate UI update
valuation.likesCount++;
isLiked.value = true;

// 2. API call (może się nie powieść)
try {
  await apiClient.post(...)
  // Success - state remains
} catch {
  // 3. Rollback jeśli error
  valuation.likesCount--;
  isLiked.value = false;
}
```

### DELETE Like Support

PRD i API plan wspominają DELETE endpoint dla usuwania lajków, ale MVP nie wymaga. Jeśli zaimplementować, będzie wymagać:
- Toggle zamiast simple "like" - jeśli już lajkowano, DELETE instead
- Zmiana ikony z filled na outline po usunięciu
- Zmniejszenie countera o 1

### Brak isLikedByMe z API

Endpoint `/api/v1/users/me/valuations` nie zwraca `isLikedByMe` dla każdej wyceny. Frontend musi zapamiętać stan lokalnie po lajku lub polegać na heurystyce. Rekomendacja:
- Przechowuj `Set<number>` ID wycen które user polajkował w session
- Po lajku: dodaj do Set
- Przy ładowaniu: inicjuj pusty Set

### Toast Notifications

Wszystkie error/success komunikaty muszą być wyświetlane za pomocą istniejącego notification store (`useNotificationStore`).

### Rate Limiting

Obsługuj gracefully rate limiting (429 Too Many Requests) - wyświetl toast "Zbyt wiele żądań - czekaj przed ponowną próbą".

