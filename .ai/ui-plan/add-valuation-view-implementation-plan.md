# Plan implementacji widoku dodawania wyceny (Add Valuation Inline)

## 1. Przegląd

Widok dodawania wyceny jest inline'owym segmentem formularza wyświetlanym wewnątrz `BrickSet Detail View`. Jego celem jest umożliwienie zalogowanemu użytkownikowi szybkiego dodania wyceny dla zestawu LEGO bez konieczności przeładowania strony. Formularz jest widoczny tylko wtedy, gdy użytkownik nie posiada jeszcze wyceny dla danego zestawu. Po pomyślnym dodaniu wyceny, formularz znika, a nowa wycena pojawia się automatycznie na liście wycen zestawu.

## 2. Routing widoku

Widok nie wymaga osobnego routingu, ponieważ jest segmentem inline wyświetlanym wewnątrz istniejącego widoku szczegółów zestawu:
- **Lokalizacja:** `/bricksets/:id` (wewnątrz `BrickSet Detail View`)
- **Warunek wyświetlenia:** Użytkownik jest zalogowany i nie posiada wyceny dla aktualnie wyświetlanego zestawu

## 3. Struktura komponentów

```
BrickSetDetailView
└── ValuationFormCard (v-if="!userHasValuation && isAuthenticated")
    ├── form
    │   ├── BaseInput (value - pole wartości)
    │   ├── BaseTextarea (comment - pole komentarza)
    │   └── BaseButton (submit - przycisk wysłania)
    └── ErrorAlert (v-if="errors.general" - komunikat błędu ogólnego)
```

## 4. Szczegóły komponentów

### ValuationFormCard

**Opis komponentu:**
Główny kontener formularza dodawania wyceny. Odpowiada za wyświetlenie pól formularza, walidację danych, wysłanie żądania do API oraz obsługę błędów. Komponent zarządza lokalnym stanem formularza i komunikuje się z rodzicem poprzez emitowanie eventów.

**Główne elementy:**
- `<form>` - kontener formularza z obsługą submit
- `<div>` z Tailwind classes - layout i stylowanie
- `BaseInput` - pole do wprowadzania wartości wyceny
- `BaseTextarea` - pole do wprowadzania opcjonalnego komentarza
- `BaseButton` - przycisk wysłania formularza
- `ErrorAlert` - komponent wyświetlający błędy ogólne (np. z API)
- Licznik znaków dla komentarza: `{{ formData.comment.length }}/2000`
- Oznaczenie waluty: "PLN" (stałe, wyświetlane przy polu wartości)

**Obsługiwane zdarzenia:**
- `@submit.prevent` - obsługa wysłania formularza (preventDefault)
- `@valuation-created` - event emitowany do rodzica po pomyślnym dodaniu wyceny (payload: `CreateValuationResponse`)
- `@input` - aktualizacja danych formularza z pól
- `@blur` - walidacja pola po opuszczeniu (first touch)

**Warunki walidacji:**
1. **value (wartość):**
   - Wymagane: wartość nie może być pusta/null
   - Typ: musi być liczbą
   - Minimum: wartość >= 1
   - Maximum: wartość <= 999,999
   - Komunikaty błędów:
     - Puste: "Pole wartość jest wymagane"
     - < 1: "Wartość musi być większa niż 0"
     - > 999,999: "Wartość nie może przekraczać 999 999"
     - Nie jest liczbą: "Wartość musi być liczbą"

2. **comment (komentarz):**
   - Opcjonalne: pole może być puste
   - Maximum: 2000 znaków
   - Komunikat błędu:
     - > 2000: "Komentarz nie może przekraczać 2000 znaków"

3. **Walidacja formularza:**
   - Formularz jest prawidłowy gdy: value jest prawidłowe i comment jest prawidłowy
   - Przycisk submit jest zablokowany gdy: formularz nieprawidłowy lub `isSubmitting === true`

**Typy wymagane przez komponent:**
- `ValuationFormData` (ViewModel - dane formularza)
- `ValidationErrors` (ViewModel - błędy walidacji)
- `CreateValuationRequest` (DTO - request do API)
- `CreateValuationResponse` (DTO - response z API)
- `ApiError` (ViewModel - błąd z API)

**Propsy:**
```typescript
interface ValuationFormCardProps {
  bricksetId: number;  // ID zestawu, do którego dodajemy wycenę
}
```

**Emits:**
```typescript
interface ValuationFormCardEmits {
  (e: 'valuation-created', valuation: CreateValuationResponse): void;
  (e: 'cancel'): void; // opcjonalnie, jeśli dodamy przycisk anulowania
}
```

---

### BaseInput (value)

**Opis komponentu:**
Komponent bazowy do wprowadzania wartości liczbowej wyceny. Jest to wyspecjalizowane pole input z typem `number`, wspierające walidację i wyświetlanie błędów.

**Główne elementy:**
- `<label>` - etykieta pola z atrybutem `for`
- `<input type="number">` - pole wprowadzania wartości
- `<span>` - sufiks "PLN" wyświetlany obok pola
- `<span>` lub `<div>` - komunikat błędu (jeśli istnieje)

**Obsługiwane zdarzenia:**
- `@input` - emitowanie wartości do rodzica przy każdej zmianie
- `@blur` - emitowanie eventu blur do triggera walidacji

**Warunki walidacji:**
- Zakres: 1-999,999
- Typ: tylko liczby całkowite
- Wymagane: pole nie może być puste

**Typy:**
- `modelValue: number | null`
- `error: string | undefined`

**Propsy:**
```typescript
interface BaseInputProps {
  modelValue: number | null;
  label: string;
  error?: string;
  required?: boolean;
  min?: number;
  max?: number;
  placeholder?: string;
  disabled?: boolean;
  id?: string;
}
```

**Emits:**
```typescript
interface BaseInputEmits {
  (e: 'update:modelValue', value: number | null): void;
  (e: 'blur'): void;
}
```

---

### BaseTextarea (comment)

**Opis komponentu:**
Komponent bazowy do wprowadzania opcjonalnego komentarza do wyceny. Pole textarea z ograniczeniem długości do 2000 znaków i licznikiem.

**Główne elementy:**
- `<label>` - etykieta pola z atrybutem `for`
- `<textarea>` - pole wprowadzania komentarza z `maxlength="2000"`
- `<div>` - licznik znaków w formacie "X/2000"
- `<span>` lub `<div>` - komunikat błędu (jeśli istnieje)

**Obsługiwane zdarzenia:**
- `@input` - emitowanie wartości do rodzica przy każdej zmianie

**Warunki walidacji:**
- Maximum: 2000 znaków (wymuszane przez `maxlength`)
- Opcjonalne: pole może być puste

**Typy:**
- `modelValue: string`
- `error: string | undefined`

**Propsy:**
```typescript
interface BaseTextareaProps {
  modelValue: string;
  label: string;
  error?: string;
  maxlength?: number;
  placeholder?: string;
  disabled?: boolean;
  rows?: number;
  id?: string;
}
```

**Emits:**
```typescript
interface BaseTextareaEmits {
  (e: 'update:modelValue', value: string): void;
}
```

---

### BaseButton (submit)

**Opis komponentu:**
Komponent przycisku do wysłania formularza. Obsługuje stan loading i disabled.

**Główne elementy:**
- `<button type="submit">` - przycisk HTML
- Slot dla tekstu/ikony
- Opcjonalny spinner podczas ładowania

**Obsługiwane zdarzenia:**
- `@click` - kliknięcie przycisku (obsługiwane przez formularz jako submit)

**Warunki walidacji:**
- Przycisk zablokowany gdy: `disabled === true` lub `loading === true`

**Typy:**
- Brak specyficznych typów (standardowy przycisk)

**Propsy:**
```typescript
interface BaseButtonProps {
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
}
```

---

### ErrorAlert

**Opis komponentu:**
Komponent wyświetlający komunikaty błędów ogólnych (np. z API) w formacie alertu/bannera.

**Główne elementy:**
- `<div role="alert">` - kontener z rolą alert dla dostępności
- Ikona błędu
- Tekst komunikatu
- Opcjonalny przycisk zamknięcia

**Obsługiwane zdarzenia:**
- `@close` - zamknięcie alertu (opcjonalne)

**Typy:**
- `message: string`

**Propsy:**
```typescript
interface ErrorAlertProps {
  message: string;
  variant?: 'error' | 'warning' | 'info';
  dismissible?: boolean;
}
```

## 5. Typy

### DTO (Data Transfer Objects)

#### CreateValuationRequest
Typ reprezentujący dane wysyłane do API przy tworzeniu wyceny.

```typescript
interface CreateValuationRequest {
  value: number;          // Wartość wyceny (1-999,999)
  currency?: string;      // Waluta (opcjonalne, domyślnie "PLN")
  comment?: string;       // Opcjonalny komentarz do wyceny
}
```

**Pola:**
- `value: number` - wymagane, wartość wyceny w zakresie 1-999,999
- `currency?: string` - opcjonalne, kod waluty (max 3 znaki), domyślnie "PLN"
- `comment?: string` - opcjonalne, komentarz użytkownika do wyceny

---

#### CreateValuationResponse
Typ reprezentujący odpowiedź z API po pomyślnym utworzeniu wyceny.

```typescript
interface CreateValuationResponse {
  id: number;                // Unikalny identyfikator wyceny
  brickset_id: number;       // ID zestawu
  user_id: number;           // ID użytkownika, który dodał wycenę
  value: number;             // Wartość wyceny
  currency: string;          // Waluta wyceny
  comment: string | null;    // Komentarz (może być null)
  likes_count: number;       // Liczba polubień wyceny
  created_at: string;        // Data utworzenia (ISO 8601)
  updated_at: string;        // Data aktualizacji (ISO 8601)
}
```

**Pola:**
- `id: number` - unikalny identyfikator wyceny nadany przez backend
- `brickset_id: number` - identyfikator zestawu, którego dotyczy wycena
- `user_id: number` - identyfikator użytkownika, który utworzył wycenę
- `value: number` - wartość wyceny
- `currency: string` - kod waluty (np. "PLN")
- `comment: string | null` - komentarz użytkownika lub null jeśli nie podano
- `likes_count: number` - liczba polubień (na początku zawsze 0)
- `created_at: string` - timestamp utworzenia w formacie ISO 8601
- `updated_at: string` - timestamp ostatniej aktualizacji w formacie ISO 8601

---

### ViewModel Types

#### ValuationFormData
Typ reprezentujący stan formularza w komponencie.

```typescript
interface ValuationFormData {
  value: number | null;   // Wartość wyceny (null na początku)
  comment: string;        // Komentarz (pusty string na początku)
}
```

**Pola:**
- `value: number | null` - wartość wyceny, null przed pierwszym wprowadzeniem
- `comment: string` - tekst komentarza, pusty string jako wartość początkowa

**Wartości początkowe:**
```typescript
const initialFormData: ValuationFormData = {
  value: null,
  comment: ''
}
```

---

#### ValidationErrors
Typ reprezentujący błędy walidacji w formularzu.

```typescript
interface ValidationErrors {
  value?: string;      // Komunikat błędu dla pola wartości
  comment?: string;    // Komunikat błędu dla pola komentarza
  general?: string;    // Ogólny komunikat błędu (np. z API)
}
```

**Pola:**
- `value?: string` - komunikat błędu związany z polem wartości (undefined gdy brak błędu)
- `comment?: string` - komunikat błędu związany z polem komentarza (undefined gdy brak błędu)
- `general?: string` - ogólny komunikat błędu, typowo z odpowiedzi API (undefined gdy brak błędu)

**Przykładowe wartości:**
```typescript
// Brak błędów
const noErrors: ValidationErrors = {}

// Błąd wartości
const valueError: ValidationErrors = {
  value: "Wartość musi być większa niż 0"
}

// Błąd z API
const apiError: ValidationErrors = {
  general: "Masz już wycenę dla tego zestawu"
}
```

---

#### ApiError
Typ reprezentujący błąd zwrócony z API.

```typescript
interface ApiError {
  code: string;        // Kod błędu (np. "VALUATION_DUPLICATE")
  message: string;     // Komunikat błędu do wyświetlenia
  status: number;      // Kod statusu HTTP (np. 409, 400, 404)
  details?: Record<string, string[]>;  // Opcjonalne szczegóły błędów walidacji
}
```

**Pola:**
- `code: string` - kod błędu zwrócony przez API (np. "VALUATION_DUPLICATE", "VALIDATION_ERROR")
- `message: string` - czytelny komunikat błędu
- `status: number` - kod statusu HTTP (409, 400, 404, 401, 500)
- `details?: Record<string, string[]>` - opcjonalny obiekt ze szczegółami błędów walidacji dla konkretnych pól

**Przykładowe wartości:**
```typescript
// Błąd duplikatu wyceny
const duplicateError: ApiError = {
  code: "VALUATION_DUPLICATE",
  message: "Użytkownik ma już wycenę dla tego zestawu",
  status: 409
}

// Błąd walidacji
const validationError: ApiError = {
  code: "VALIDATION_ERROR",
  message: "Błąd walidacji danych",
  status: 400,
  details: {
    value: ["Wartość musi być w zakresie 1-999999"]
  }
}
```

## 6. Zarządzanie stanem

### Stan lokalny w komponencie ValuationFormCard

Stan formularza będzie zarządzany lokalnie w komponencie `ValuationFormCard` przy użyciu Composition API Vue 3:

```typescript
const formData = ref<ValuationFormData>({
  value: null,
  comment: ''
});

const errors = ref<ValidationErrors>({});
const isSubmitting = ref<boolean>(false);
const touchedFields = ref<Set<string>>(new Set());
```

**Wyjaśnienie zmiennych:**
- `formData` - reaktywny obiekt przechowujący dane wprowadzone w formularzu
- `errors` - reaktywny obiekt przechowujący komunikaty błędów dla pól
- `isSubmitting` - flaga wskazująca czy formularz jest w trakcie wysyłania
- `touchedFields` - zbiór nazw pól, które zostały "dotknięte" przez użytkownika (dla warunkowego wyświetlania błędów)

### Computed properties

```typescript
const isFormValid = computed<boolean>(() => {
  return formData.value.value !== null &&
         formData.value.value >= 1 &&
         formData.value.value <= 999999 &&
         formData.value.comment.length <= 2000;
});

const canSubmit = computed<boolean>(() => {
  return isFormValid.value && !isSubmitting.value;
});
```

**Wyjaśnienie:**
- `isFormValid` - sprawdza czy wszystkie pola spełniają warunki walidacji
- `canSubmit` - sprawdza czy formularz może być wysłany (prawidłowy i nie jest w trakcie wysyłania)

### Custom composable: useValuationForm

Dla lepszej organizacji kodu i możliwości reużycia logiki, zaleca się utworzenie composable:

```typescript
// composables/useValuationForm.ts
export function useValuationForm(bricksetId: Ref<number>) {
  const formData = ref<ValuationFormData>({
    value: null,
    comment: ''
  });

  const errors = ref<ValidationErrors>({});
  const isSubmitting = ref<boolean>(false);
  const touchedFields = ref<Set<string>>(new Set());

  const validateField = (fieldName: keyof ValuationFormData): void => {
    // Logika walidacji pojedynczego pola
  };

  const validateForm = (): boolean => {
    // Logika walidacji całego formularza
  };

  const resetForm = (): void => {
    formData.value = { value: null, comment: '' };
    errors.value = {};
    touchedFields.value.clear();
  };

  const handleSubmit = async (): Promise<CreateValuationResponse | null> => {
    // Logika wysyłania formularza
  };

  const isFormValid = computed<boolean>(() => {
    // Sprawdzenie czy formularz jest prawidłowy
  });

  const canSubmit = computed<boolean>(() => {
    return isFormValid.value && !isSubmitting.value;
  });

  return {
    formData,
    errors,
    isSubmitting,
    touchedFields,
    isFormValid,
    canSubmit,
    validateField,
    validateForm,
    resetForm,
    handleSubmit
  };
}
```

### Pinia Store (opcjonalnie)

Jeśli potrzebujemy globalnego dostępu do informacji o wycenach użytkownika:

```typescript
// stores/valuation.ts
export const useValuationStore = defineStore('valuation', () => {
  const userValuations = ref<Map<number, CreateValuationResponse>>(new Map());

  const addValuation = (valuation: CreateValuationResponse): void => {
    userValuations.value.set(valuation.brickset_id, valuation);
  };

  const hasValuationForBrickset = (bricksetId: number): boolean => {
    return userValuations.value.has(bricksetId);
  };

  const getValuationForBrickset = (bricksetId: number): CreateValuationResponse | undefined => {
    return userValuations.value.get(bricksetId);
  };

  return {
    userValuations,
    addValuation,
    hasValuationForBrickset,
    getValuationForBrickset
  };
});
```

**Uwaga:** Store jest opcjonalny. Jeśli informacja o tym, czy użytkownik ma wycenę jest dostępna w `BrickSetDetailView` (np. z API przy pobieraniu szczegółów zestawu), można pominąć Pinia store i zarządzać tym stanem lokalnie w komponencie rodzica.

## 7. Integracja API

### Endpoint

**POST** `/api/v1/bricksets/{brickset_id}/valuations`

### Request

**Typ:** `CreateValuationRequest`

```typescript
interface CreateValuationRequest {
  value: number;
  currency?: string;  // opcjonalne, domyślnie "PLN"
  comment?: string;   // opcjonalne
}
```

**Przykład:**
```json
{
  "value": 450,
  "currency": "PLN",
  "comment": "Zestaw w dobrym stanie, wszystkie klocki kompletne"
}
```

### Response Success (201 Created)

**Typ:** `CreateValuationResponse`

```typescript
interface CreateValuationResponse {
  id: number;
  brickset_id: number;
  user_id: number;
  value: number;
  currency: string;
  comment: string | null;
  likes_count: number;
  created_at: string;
  updated_at: string;
}
```

**Przykład:**
```json
{
  "id": 77,
  "brickset_id": 10,
  "user_id": 99,
  "value": 450,
  "currency": "PLN",
  "comment": "Zestaw w dobrym stanie, wszystkie klocki kompletne",
  "likes_count": 0,
  "created_at": "2025-11-01T14:30:00Z",
  "updated_at": "2025-11-01T14:30:00Z"
}
```

### Response Errors

#### 409 Conflict - VALUATION_DUPLICATE
Użytkownik posiada już wycenę dla tego zestawu.

```json
{
  "code": "VALUATION_DUPLICATE",
  "message": "Użytkownik ma już wycenę dla tego zestawu"
}
```

**Obsługa:** Wyświetlenie komunikatu "Masz już wycenę dla tego zestawu" w komponencie `ErrorAlert`.

---

#### 400 Bad Request - VALIDATION_ERROR
Błąd walidacji danych (wartość poza zakresem 1-999,999).

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Błąd walidacji danych",
  "details": {
    "value": ["Wartość musi być w zakresie 1-999999"]
  }
}
```

**Obsługa:** Wyświetlenie szczegółowych błędów przy odpowiednich polach formularza.

---

#### 404 Not Found - BRICKSET_NOT_FOUND
Zestaw o podanym ID nie istnieje.

```json
{
  "code": "BRICKSET_NOT_FOUND",
  "message": "Zestaw nie został znaleziony"
}
```

**Obsługa:** Wyświetlenie komunikatu ogólnego i opcjonalnie przekierowanie do listy zestawów.

---

#### 401 Unauthorized - NOT_AUTHENTICATED
Użytkownik nie jest zalogowany.

```json
{
  "code": "NOT_AUTHENTICATED",
  "message": "Wymagane uwierzytelnienie"
}
```

**Obsługa:** Przekierowanie do strony logowania.

---

#### 500 Internal Server Error
Błąd serwera lub problem z siecią.

**Obsługa:** Wyświetlenie komunikatu "Wystąpił błąd. Spróbuj ponownie później".

### Implementacja wywołania API

```typescript
// services/api/valuations.ts
import { apiClient } from './client';

export const valuationsApi = {
  async create(
    bricksetId: number,
    data: CreateValuationRequest
  ): Promise<CreateValuationResponse> {
    const response = await apiClient.post<CreateValuationResponse>(
      `/api/v1/bricksets/${bricksetId}/valuations`,
      data
    );
    return response.data;
  }
};
```

### Obsługa w composable

```typescript
const handleSubmit = async (): Promise<CreateValuationResponse | null> => {
  if (!validateForm()) {
    return null;
  }

  isSubmitting.value = true;
  errors.value = {};

  try {
    const payload: CreateValuationRequest = {
      value: formData.value.value!,
      currency: 'PLN',
      comment: formData.value.comment || undefined
    };

    const response = await valuationsApi.create(bricksetId.value, payload);

    resetForm();
    return response;
  } catch (error) {
    handleApiError(error);
    return null;
  } finally {
    isSubmitting.value = false;
  }
};

const handleApiError = (error: any): void => {
  if (error.response) {
    const apiError: ApiError = error.response.data;

    switch (apiError.status) {
      case 409:
        errors.value.general = 'Masz już wycenę dla tego zestawu';
        break;
      case 400:
        if (apiError.details) {
          Object.entries(apiError.details).forEach(([field, messages]) => {
            errors.value[field as keyof ValidationErrors] = messages[0];
          });
        } else {
          errors.value.general = apiError.message;
        }
        break;
      case 404:
        errors.value.general = 'Zestaw nie został znaleziony';
        break;
      case 401:
        // Przekierowanie do logowania (obsługa przez interceptor lub router)
        break;
      default:
        errors.value.general = 'Wystąpił błąd. Spróbuj ponownie później';
    }
  } else {
    errors.value.general = 'Problem z połączeniem. Sprawdź internet';
  }
};
```

## 8. Interakcje użytkownika

### 1. Wejście na stronę szczegółów zestawu (użytkownik bez wyceny)

**Akcja:** Użytkownik nawiguje do `/bricksets/:id`

**Warunek:** Użytkownik jest zalogowany i nie posiada wyceny dla tego zestawu

**Wynik:**
- Formularz `ValuationFormCard` jest widoczny
- Pole `value` jest puste (placeholder: "np. 450")
- Pole `comment` jest puste (placeholder: "Opcjonalny komentarz...")
- Przycisk "Dodaj wycenę" jest aktywny, ale zablokowany (bo value jest puste)

---

### 2. Wprowadzenie wartości wyceny

**Akcja:** Użytkownik wpisuje wartość w pole `value`

**Scenariusze:**

#### a) Wartość prawidłowa (np. 450)
- Pole zostaje wypełnione
- Brak komunikatu błędu
- Przycisk "Dodaj wycenę" staje się aktywny

#### b) Wartość < 1 (np. 0 lub -5)
- Po opuszczeniu pola (blur) wyświetla się błąd: "Wartość musi być większa niż 0"
- Przycisk pozostaje zablokowany
- Pole ma czerwoną ramkę (error state)

#### c) Wartość > 999,999 (np. 1,000,000)
- Po opuszczeniu pola (blur) wyświetla się błąd: "Wartość nie może przekraczać 999 999"
- Przycisk pozostaje zablokowany
- Pole ma czerwoną ramkę (error state)

#### d) Wartość nieprawidłowa (puste pole po dotknięciu)
- Po opuszczeniu pola (blur) wyświetla się błąd: "Pole wartość jest wymagane"
- Przycisk pozostaje zablokowany

---

### 3. Wprowadzenie komentarza (opcjonalne)

**Akcja:** Użytkownik wpisuje tekst w pole `comment`

**Wynik:**
- Licznik znaków aktualizuje się: "X/2000"
- Jeśli długość przekroczy 2000 znaków, atrybut `maxlength` zapobiega dalszemu wpisywaniu
- Formularz pozostaje prawidłowy (komentarz jest opcjonalny)

---

### 4. Próba wysłania pustego formularza

**Akcja:** Użytkownik klika "Dodaj wycenę" bez wypełnienia pola `value`

**Wynik:**
- Przycisk jest zablokowany, więc kliknięcie nie wywołuje akcji
- Alternatywnie (jeśli przycisk nie jest zablokowany): walidacja formularza przy submit pokazuje błędy przy wszystkich wymaganych polach

---

### 5. Wysłanie prawidłowego formularza

**Akcja:** Użytkownik wypełnia `value` = 450, opcjonalnie `comment` = "Dobry stan", i klika "Dodaj wycenę"

**Proces:**
1. Walidacja formularza przechodzi pomyślnie
2. `isSubmitting` ustawia się na `true`
3. Przycisk wyświetla spinner i tekst zmienia się na "Dodawanie..."
4. Wysłanie żądania POST do API
5. Otrzymanie odpowiedzi 201 Created

**Wynik:**
- Formularz znika (lub jest ukryty)
- Nowa wycena pojawia się na liście wycen zestawu
- Wyświetlenie komunikatu sukcesu (toast/snackbar): "Wycena została dodana"
- Opcjonalnie: scroll do nowo dodanej wyceny

---

### 6. Błąd: Duplikat wyceny (409)

**Akcja:** Użytkownik próbuje dodać wycenę, ale ma już wycenę dla tego zestawu (np. dodał w innej karcie)

**Proces:**
1. Walidacja klienta przechodzi
2. Wysłanie żądania POST do API
3. Otrzymanie odpowiedzi 409 Conflict

**Wynik:**
- `isSubmitting` wraca do `false`
- Wyświetlenie komunikatu w `ErrorAlert`: "Masz już wycenę dla tego zestawu"
- Formularz pozostaje widoczny (użytkownik może zamknąć alert i odświeżyć stronę)

---

### 7. Błąd: Walidacja API (400)

**Akcja:** Backend zwraca błąd walidacji (np. wartość poza zakresem - choć to nie powinno się zdarzyć przy poprawnej walidacji klienta)

**Proces:**
1. Wysłanie żądania POST do API
2. Otrzymanie odpowiedzi 400 Bad Request z szczegółami błędów

**Wynik:**
- Wyświetlenie szczegółowych błędów przy odpowiednich polach
- Przykład: przy polu `value` wyświetla się "Wartość musi być w zakresie 1-999999"
- Przycisk wraca do stanu aktywnego (użytkownik może poprawić i spróbować ponownie)

---

### 8. Błąd: Zestaw nie znaleziony (404)

**Akcja:** Zestaw o podanym ID nie istnieje (np. został usunięty)

**Wynik:**
- Wyświetlenie komunikatu w `ErrorAlert`: "Zestaw nie został znaleziony"
- Opcjonalnie: automatyczne przekierowanie do listy zestawów po 3 sekundach

---

### 9. Błąd: Brak autoryzacji (401)

**Akcja:** Sesja użytkownika wygasła podczas wypełniania formularza

**Wynik:**
- Automatyczne przekierowanie do strony logowania
- Opcjonalnie: zapisanie stanu formularza w sessionStorage i odtworzenie po ponownym zalogowaniu

---

### 10. Błąd: Błąd serwera (500) lub problem z siecią

**Akcja:** Serwer zwraca błąd 500 lub brak połączenia z internetem

**Wynik:**
- Wyświetlenie komunikatu w `ErrorAlert`: "Wystąpił błąd. Spróbuj ponownie później"
- Przycisk wraca do stanu aktywnego (użytkownik może spróbować ponownie)

---

### 11. Anulowanie / Zamknięcie formularza (opcjonalne)

**Akcja:** Użytkownik klika przycisk "Anuluj" lub zamyka formularz

**Wynik:**
- Reset formularza do stanu początkowego
- Wyczyszczenie błędów
- Opcjonalnie: ukrycie formularza (jeśli jest to modal lub rozwijany panel)

## 9. Warunki i walidacja

### Warunki wyświetlania formularza

**Lokalizacja:** `BrickSetDetailView`

**Warunek:**
```typescript
const showValuationForm = computed(() => {
  return isAuthenticated.value && !userHasValuation.value;
});
```

**Komponenty:**
- `BrickSetDetailView` sprawdza czy `showValuationForm === true`
- Jeśli `true`, renderuje `ValuationFormCard`
- Jeśli `false`, formularz nie jest wyświetlany

**Wpływ na UI:**
- Gdy użytkownik nie jest zalogowany: formularz ukryty, opcjonalnie wyświetlany komunikat "Zaloguj się, aby dodać wycenę"
- Gdy użytkownik ma już wycenę: formularz ukryty, wyświetlana jego własna wycena na liście

---

### Walidacja pola `value`

**Lokalizacja:** `ValuationFormCard` lub `useValuationForm` composable

**Warunki:**
1. **Pole wymagane:** `value !== null && value !== undefined`
2. **Typ liczby:** `typeof value === 'number' && !isNaN(value)`
3. **Minimum:** `value >= 1`
4. **Maximum:** `value <= 999999`

**Funkcja walidacji:**
```typescript
const validateValueField = (value: number | null): string | undefined => {
  if (value === null || value === undefined) {
    return 'Pole wartość jest wymagane';
  }
  if (typeof value !== 'number' || isNaN(value)) {
    return 'Wartość musi być liczbą';
  }
  if (value < 1) {
    return 'Wartość musi być większa niż 0';
  }
  if (value > 999999) {
    return 'Wartość nie może przekraczać 999 999';
  }
  return undefined;
};
```

**Moment walidacji:**
- `@blur` - po opuszczeniu pola (first touch)
- `@input` - w czasie rzeczywistym po pierwszym błędzie
- `@submit` - przed wysłaniem formularza

**Wpływ na UI:**
- Komunikat błędu wyświetlany pod polem
- Pole ma czerwoną ramkę (`error` class)
- `aria-invalid="true"` dla dostępności
- Przycisk submit zablokowany gdy błąd istnieje

---

### Walidacja pola `comment`

**Lokalizacja:** `ValuationFormCard` lub `useValuationForm` composable

**Warunki:**
1. **Opcjonalne:** pole może być puste
2. **Maximum długości:** `comment.length <= 2000`

**Funkcja walidacji:**
```typescript
const validateCommentField = (comment: string): string | undefined => {
  if (comment.length > 2000) {
    return 'Komentarz nie może przekraczać 2000 znaków';
  }
  return undefined;
};
```

**Moment walidacji:**
- `@input` - w czasie rzeczywistym (licznik znaków)
- Atrybut `maxlength="2000"` na `<textarea>` zapobiega wpisaniu więcej niż 2000 znaków

**Wpływ na UI:**
- Licznik znaków: "X/2000"
- Licznik zmienia kolor na czerwony gdy zbliża się do limitu (np. > 1900)
- `maxlength` zapobiega wpisaniu więcej znaków (natywna walidacja HTML)

---

### Walidacja całego formularza

**Lokalizacja:** `ValuationFormCard` - funkcja `validateForm()`

**Warunek:**
```typescript
const isFormValid = computed(() => {
  const valueError = validateValueField(formData.value.value);
  const commentError = validateCommentField(formData.value.comment);
  return !valueError && !commentError;
});
```

**Moment walidacji:**
- Przed wysłaniem formularza (w `handleSubmit`)
- Continuous validation dla computed property `canSubmit`

**Wpływ na UI:**
- Przycisk submit: `disabled = !canSubmit`
- Jeśli formularz nieprawidłowy przy próbie submit, wyświetlane są wszystkie błędy

---

### Warunki blokowania przycisku submit

**Lokalizacja:** `BaseButton` w `ValuationFormCard`

**Warunki:**
```typescript
const canSubmit = computed(() => {
  return isFormValid.value && !isSubmitting.value;
});
```

**Wpływ na UI:**
- Przycisk disabled gdy `canSubmit === false`
- Przycisk pokazuje spinner gdy `isSubmitting === true`
- Tekst przycisku zmienia się: "Dodaj wycenę" → "Dodawanie..."

---

### Walidacja po stronie API (fallback)

**Lokalizacja:** Backend + obsługa błędów w `handleApiError`

**Warunki:**
- Backend waliduje te same reguły (1-999,999, max 2000 dla komentarza)
- W przypadku błędu 400, szczegóły są mapowane na pola formularza

**Wpływ na UI:**
- Błędy z API wyświetlane przy odpowiednich polach
- Jeśli brak mapowania, wyświetlany jest ogólny komunikat

## 10. Obsługa błędów

### 1. Błędy walidacji klienta

**Typ:** Błędy formularza przed wysłaniem do API

**Scenariusze:**
- Pusta wartość w polu `value`
- Wartość < 1 lub > 999,999
- Komentarz > 2000 znaków

**Obsługa:**
```typescript
const validateField = (fieldName: keyof ValuationFormData): void => {
  let errorMessage: string | undefined;

  if (fieldName === 'value') {
    errorMessage = validateValueField(formData.value.value);
  } else if (fieldName === 'comment') {
    errorMessage = validateCommentField(formData.value.comment);
  }

  if (errorMessage) {
    errors.value[fieldName] = errorMessage;
  } else {
    delete errors.value[fieldName];
  }
};
```

**UI:**
- Komunikat błędu pod polem
- Czerwona ramka pola
- Przycisk submit zablokowany
- `aria-describedby` łączy pole z komunikatem błędu dla screen readerów

---

### 2. Błąd 409 - VALUATION_DUPLICATE

**Scenariusz:** Użytkownik próbuje dodać drugą wycenę dla tego samego zestawu

**Przyczyna:**
- Użytkownik dodał wycenę w innej karcie/sesji
- Race condition między różnymi klientami
- Nieaktualny stan lokalny (brak synchronizacji)

**Obsługa:**
```typescript
case 409:
  errors.value.general = 'Masz już wycenę dla tego zestawu';
  break;
```

**UI:**
- Wyświetlenie `ErrorAlert` z komunikatem: "Masz już wycenę dla tego zestawu"
- Opcjonalnie: automatyczne odświeżenie listy wycen aby pokazać istniejącą wycenę użytkownika
- Formularz pozostaje widoczny (użytkownik może zamknąć alert)

**Sugerowane działanie użytkownika:**
- Odświeżenie strony aby zobaczyć swoją wycenę
- Alternatywnie: automatyczne ukrycie formularza i scroll do wyceny użytkownika

---

### 3. Błąd 400 - VALIDATION_ERROR

**Scenariusz:** Backend odrzuca dane ze względu na błędy walidacji

**Przyczyny:**
- Wartość poza zakresem 1-999,999 (nie powinno się zdarzyć przy poprawnej walidacji klienta)
- Niespodziewane błędy walidacji po stronie serwera

**Obsługa:**
```typescript
case 400:
  if (apiError.details) {
    // Mapowanie szczegółowych błędów na pola
    Object.entries(apiError.details).forEach(([field, messages]) => {
      errors.value[field as keyof ValidationErrors] = messages[0];
    });
  } else {
    // Ogólny komunikat jeśli brak szczegółów
    errors.value.general = apiError.message || 'Błąd walidacji danych';
  }
  break;
```

**UI:**
- Komunikaty błędów przy konkretnych polach (jeśli `details` zawiera mapowanie)
- Lub ogólny komunikat w `ErrorAlert` (jeśli brak szczegółów)

---

### 4. Błąd 404 - BRICKSET_NOT_FOUND

**Scenariusz:** Zestaw o podanym ID nie istnieje (został usunięty)

**Obsługa:**
```typescript
case 404:
  errors.value.general = 'Zestaw nie został znaleziony';
  // Opcjonalnie: przekierowanie
  setTimeout(() => {
    router.push('/bricksets');
  }, 3000);
  break;
```

**UI:**
- Wyświetlenie `ErrorAlert` z komunikatem: "Zestaw nie został znaleziony"
- Opcjonalnie: automatyczne przekierowanie do listy zestawów po 3 sekundach
- Alternatywnie: przycisk "Wróć do listy zestawów"

---

### 5. Błąd 401 - NOT_AUTHENTICATED

**Scenariusz:** Sesja użytkownika wygasła lub użytkownik nie jest zalogowany

**Obsługa:**
```typescript
case 401:
  // Obsługa w interceptorze Axios lub ręcznie
  const router = useRouter();
  router.push({
    name: 'Login',
    query: { redirect: route.fullPath }
  });
  break;
```

**UI:**
- Automatyczne przekierowanie do strony logowania
- Parametr `redirect` pozwala wrócić do oryginalnej strony po zalogowaniu
- Opcjonalnie: zapisanie stanu formularza w `sessionStorage` i odtworzenie po powrocie

---

### 6. Błąd 500 - Internal Server Error

**Scenariusz:** Błąd serwera lub problem z bazą danych

**Obsługa:**
```typescript
default:
  errors.value.general = 'Wystąpił błąd. Spróbuj ponownie później';
  break;
```

**UI:**
- Wyświetlenie ogólnego komunikatu w `ErrorAlert`
- Przycisk submit wraca do stanu aktywnego (użytkownik może spróbować ponownie)
- Opcjonalnie: logowanie błędu do systemu monitoringu (np. Sentry)

---

### 7. Błąd sieci (Network Error)

**Scenariusz:** Brak połączenia z internetem lub timeout

**Obsługa:**
```typescript
if (!error.response) {
  // Błąd sieci
  errors.value.general = 'Problem z połączeniem. Sprawdź internet i spróbuj ponownie';
}
```

**UI:**
- Wyświetlenie komunikatu: "Problem z połączeniem. Sprawdź internet i spróbuj ponownie"
- Ikona "offline" lub indykator braku połączenia
- Opcjonalnie: automatyczne ponowienie próby (retry) po wykryciu połączenia

---

### 8. Obsługa błędów dostępności (A11y)

**Implementacja:**
- Błędy mają `role="alert"` dla automatycznego ogłoszenia przez screen reader
- Pola z błędami mają `aria-invalid="true"` i `aria-describedby` wskazujący na komunikat błędu
- Focus automatycznie przenoszony na pierwsze pole z błędem po nieudanej walidacji

**Przykład:**
```html
<input
  id="valuation-value"
  v-model="formData.value"
  type="number"
  :aria-invalid="!!errors.value"
  :aria-describedby="errors.value ? 'value-error' : undefined"
/>
<span
  v-if="errors.value"
  id="value-error"
  role="alert"
  class="error-message"
>
  {{ errors.value }}
</span>
```

---

### 9. Przypadki brzegowe

#### a) Użytkownik wprowadza wartość dziesiętną
- HTML `<input type="number">` domyślnie akceptuje dziesiętne
- Backend oczekuje całkowitej liczby
- **Rozwiązanie:** Dodać atrybut `step="1"` i walidację `Number.isInteger(value)`

#### b) Użytkownik kopiuje-wkleja bardzo długi tekst do komentarza
- Atrybut `maxlength="2000"` obcina tekst automatycznie
- **Rozwiązanie:** Dodatkowy komunikat "Tekst został skrócony do 2000 znaków"

#### c) Użytkownik klika submit wielokrotnie
- Flaga `isSubmitting` zapobiega wielokrotnym wysłaniom
- **Rozwiązanie:** Przycisk disabled podczas `isSubmitting === true`

#### d) Formularz jest wypełniony, ale API zwraca 409 (wycena dodana w międzyczasie)
- Wyświetlenie komunikatu o duplikacie
- **Rozwiązanie:** Automatyczne ukrycie formularza i odświeżenie listy wycen

## 11. Kroki implementacji

### Krok 1: Przygotowanie typów TypeScript

**Plik:** `src/types/valuation.ts`

**Zadania:**
1. Utworzenie interfejsów DTO:
   - `CreateValuationRequest`
   - `CreateValuationResponse`
2. Utworzenie interfejsów ViewModel:
   - `ValuationFormData`
   - `ValidationErrors`
   - `ApiError`
3. Eksport wszystkich typów

**Weryfikacja:** Brak błędów TypeScript, wszystkie typy dostępne do importu

---

### Krok 2: Implementacja API service

**Plik:** `src/services/api/valuations.ts`

**Zadania:**
1. Utworzenie funkcji `create(bricksetId, data)` do wysyłania POST request
2. Konfiguracja właściwego URL endpointu
3. Obsługa błędów HTTP (try-catch)
4. Typowanie request i response

**Weryfikacja:** Test manualny lub unit test dla funkcji API

---

### Krok 3: Utworzenie composable `useValuationForm`

**Plik:** `src/composables/useValuationForm.ts`

**Zadania:**
1. Definicja reaktywnych zmiennych: `formData`, `errors`, `isSubmitting`, `touchedFields`
2. Implementacja funkcji `validateValueField`
3. Implementacja funkcji `validateCommentField`
4. Implementacja funkcji `validateForm`
5. Implementacja computed `isFormValid` i `canSubmit`
6. Implementacja funkcji `handleSubmit` z wywołaniem API
7. Implementacja funkcji `handleApiError` do mapowania błędów
8. Implementacja funkcji `resetForm`
9. Return wszystkich potrzebnych wartości i funkcji

**Weryfikacja:** Unit testy dla logiki walidacji i obsługi błędów

---

### Krok 4: Implementacja komponentu `BaseInput`

**Plik:** `src/components/base/BaseInput.vue`

**Zadania:**
1. Utworzenie template z `<label>`, `<input type="number">`, komunikatem błędu
2. Definicja props: `modelValue`, `label`, `error`, `required`, `min`, `max`, `placeholder`, `disabled`, `id`
3. Definicja emits: `update:modelValue`, `blur`
4. Obsługa v-model przez `@input` event
5. Dodanie atrybutów dostępności: `aria-invalid`, `aria-describedby`, `aria-required`
6. Stylowanie z Tailwind (normal state, error state, disabled state)
7. Wyświetlanie sufiksu "PLN" obok pola

**Weryfikacja:** Komponent renderuje się poprawnie, v-model działa, błędy są wyświetlane

---

### Krok 5: Implementacja komponentu `BaseTextarea`

**Plik:** `src/components/base/BaseTextarea.vue`

**Zadania:**
1. Utworzenie template z `<label>`, `<textarea>`, licznikiem znaków, komunikatem błędu
2. Definicja props: `modelValue`, `label`, `error`, `maxlength`, `placeholder`, `disabled`, `rows`, `id`
3. Definicja emits: `update:modelValue`
4. Obsługa v-model przez `@input` event
5. Dodanie atrybutu `maxlength="2000"`
6. Implementacja licznika znaków: `{{ modelValue.length }}/2000`
7. Zmiana koloru licznika na czerwony gdy > 1900 znaków
8. Dodanie atrybutów dostępności
9. Stylowanie z Tailwind

**Weryfikacja:** Komponent renderuje się poprawnie, v-model działa, licznik się aktualizuje

---

### Krok 6: Implementacja komponentu `BaseButton`

**Plik:** `src/components/base/BaseButton.vue` (jeśli nie istnieje)

**Zadania:**
1. Utworzenie template z `<button>`, slotem dla tekstu, opcjonalnym spinnerem
2. Definicja props: `type`, `variant`, `disabled`, `loading`, `fullWidth`
3. Warunkowe wyświetlanie spinnera gdy `loading === true`
4. Stylowanie wariantów: `primary`, `secondary`, `danger`
5. Obsługa stanu disabled (przycisk i wizualnie)
6. Dodanie atrybutów dostępności: `aria-busy` gdy loading

**Weryfikacja:** Przycisk renderuje się w różnych wariantach, loading state działa

---

### Krok 7: Implementacja komponentu `ErrorAlert`

**Plik:** `src/components/base/ErrorAlert.vue`

**Zadania:**
1. Utworzenie template z `<div role="alert">`, ikoną, tekstem, opcjonalnym przyciskiem zamknięcia
2. Definicja props: `message`, `variant`, `dismissible`
3. Definicja emits: `close`
4. Warunkowe wyświetlanie przycisku zamknięcia jeśli `dismissible === true`
5. Stylowanie wariantów: `error` (czerwony), `warning` (żółty), `info` (niebieski)
6. Dodanie ikony odpowiedniej do wariantu
7. Dodanie atrybutów dostępności: `role="alert"`, `aria-live="assertive"`

**Weryfikacja:** Alert renderuje się w różnych wariantach, przycisk zamknięcia działa

---

### Krok 8: Implementacja komponentu `ValuationFormCard`

**Plik:** `src/components/valuation/ValuationFormCard.vue`

**Zadania:**
1. Utworzenie struktury template z formularzem
2. Definicja props: `bricksetId`
3. Definicja emits: `valuation-created`, `cancel`
4. Import i użycie composable `useValuationForm(bricksetId)`
5. Użycie komponentów: `BaseInput`, `BaseTextarea`, `BaseButton`, `ErrorAlert`
6. Bindowanie v-model dla pól formularza
7. Obsługa @submit.prevent z wywołaniem `handleSubmit`
8. Wyświetlanie błędów przy polach: `:error="errors.value"`
9. Warunkowe wyświetlanie `ErrorAlert` gdy `errors.general`
10. Bindowanie `:disabled="!canSubmit"` dla przycisku
11. Bindowanie `:loading="isSubmitting"` dla przycisku
12. Emitowanie eventu `valuation-created` po sukcesie
13. Stylowanie z Tailwind (card layout, spacing, responsive)
14. Dodanie tłumaczeń i18n dla wszystkich tekstów

**Weryfikacja:** Formularz renderuje się, walidacja działa, wysyłanie do API działa, błędy są obsługiwane

---

### Krok 9: Integracja w `BrickSetDetailView`

**Plik:** `src/views/BrickSetDetailView.vue`

**Zadania:**
1. Import komponentu `ValuationFormCard`
2. Dodanie stanu `userHasValuation` (z API lub store)
3. Dodanie stanu `isAuthenticated` (z authStore)
4. Utworzenie computed `showValuationForm`:
   ```typescript
   const showValuationForm = computed(() => {
     return isAuthenticated.value && !userHasValuation.value;
   });
   ```
5. Warunkowe renderowanie `ValuationFormCard` gdy `showValuationForm === true`
6. Obsługa eventu `@valuation-created`:
   - Dodanie nowej wyceny do listy wycen
   - Ustawienie `userHasValuation = true`
   - Wyświetlenie toast/snackbar "Wycena została dodana"
   - Opcjonalnie: scroll do nowej wyceny
7. Przekazanie `bricksetId` jako props do `ValuationFormCard`

**Weryfikacja:** Formularz pojawia się/znika w odpowiednich warunkach, nowa wycena pojawia się na liście

---

### Krok 10: Dodanie tekstów i18n

**Plik:** `src/locales/pl.json`

**Zadania:**
1. Dodanie kluczy dla formularza:
   ```json
   {
     "valuation": {
       "form": {
         "title": "Dodaj wycenę",
         "value": {
           "label": "Wartość (PLN)",
           "placeholder": "np. 450"
         },
         "comment": {
           "label": "Komentarz (opcjonalnie)",
           "placeholder": "Opcjonalny komentarz o stanie zestawu..."
         },
         "submit": "Dodaj wycenę",
         "submitting": "Dodawanie...",
         "cancel": "Anuluj"
       },
       "errors": {
         "required": "Pole wartość jest wymagane",
         "min": "Wartość musi być większa niż 0",
         "max": "Wartość nie może przekraczać 999 999",
         "notNumber": "Wartość musi być liczbą",
         "commentTooLong": "Komentarz nie może przekraczać 2000 znaków",
         "duplicate": "Masz już wycenę dla tego zestawu",
         "notFound": "Zestaw nie został znaleziony",
         "serverError": "Wystąpił błąd. Spróbuj ponownie później",
         "networkError": "Problem z połączeniem. Sprawdź internet i spróbuj ponownie"
       },
       "success": {
         "created": "Wycena została dodana"
       }
     }
   }
   ```
2. Użycie `$t('valuation.form.title')` w komponentach

**Weryfikacja:** Wszystkie teksty są wyświetlane z i18n, łatwo zmienić język

---

### Krok 11: Stylowanie i responsywność

**Zadania:**
1. Stylowanie `ValuationFormCard`:
   - Card z border i shadow
   - Padding i spacing między polami
   - Responsywny layout (mobile-first)
2. Stylowanie stanów błędu:
   - Czerwona ramka dla pól z błędami
   - Czerwony tekst dla komunikatów błędów
   - Ikona błędu obok komunikatu
3. Stylowanie stanu loading:
   - Spinner w przycisku
   - Disabled state dla całego formularza
4. Testowanie na różnych rozdzielczościach (mobile, tablet, desktop)

**Weryfikacja:** UI wygląda dobrze na wszystkich urządzeniach, stany są wyraźnie widoczne

---

### Krok 12: Testowanie dostępności (A11y)

**Zadania:**
1. Sprawdzenie z użyciem narzędzi:
   - Lighthouse (Chrome DevTools)
   - axe DevTools
   - Screen reader (NVDA/JAWS)
2. Weryfikacja:
   - Wszystkie pola mają label
   - Błędy są ogłaszane przez screen reader
   - Nawigacja klawiaturą działa poprawnie
   - Focus jest widoczny i logiczny
   - Kolory mają odpowiedni kontrast
3. Poprawki ewentualnych problemów

**Weryfikacja:** Brak błędów dostępności w narzędziach, screen reader poprawnie ogłasza elementy

---

### Krok 13: Testy jednostkowe

**Zadania:**
1. Testy dla `useValuationForm`:
   - Walidacja pola value (wszystkie scenariusze)
   - Walidacja pola comment
   - handleSubmit success
   - handleSubmit error scenarios (409, 400, 404, 401, 500)
   - resetForm
2. Testy dla komponentów:
   - `BaseInput` - renderowanie, v-model, błędy
   - `BaseTextarea` - renderowanie, v-model, licznik znaków
   - `ValuationFormCard` - renderowanie, walidacja, submit
3. Użycie Vitest i Vue Test Utils

**Weryfikacja:** Wszystkie testy przechodzą, pokrycie kodu > 80%

---

### Krok 14: Testy E2E

**Zadania:**
1. Scenariusze testowe:
   - Dodanie wyceny z poprawnymi danymi
   - Walidacja pustego pola value
   - Walidacja wartości poza zakresem
   - Walidacja długiego komentarza
   - Obsługa błędu 409
   - Obsługa błędu 401 (przekierowanie do logowania)
2. Użycie Cypress lub Playwright

**Weryfikacja:** Wszystkie scenariusze E2E przechodzą

---

### Krok 15: Code review i dokumentacja

**Zadania:**
1. Code review z zespołem
2. Dodanie komentarzy JSDoc dla funkcji publicznych
3. Aktualizacja dokumentacji komponentów (Storybook - opcjonalnie)
4. Utworzenie pull requesta z opisem zmian

**Weryfikacja:** Code review zaakceptowany, dokumentacja aktualna

---

### Krok 16: Deploy i monitoring

**Zadania:**
1. Merge do brancha głównego
2. Deploy na środowisko testowe/produkcyjne
3. Monitoring błędów (np. Sentry)
4. Zbieranie feedbacku od użytkowników

**Weryfikacja:** Funkcjonalność działa na produkcji, brak błędów w monitoringu

---

## Podsumowanie

Plan implementacji widoku dodawania wyceny obejmuje wszystkie aspekty od definicji typów, przez implementację komponentów, walidację, obsługę błędów, do testów i deployment. Kluczowe punkty:

- **Modularność:** Komponenty bazowe (`BaseInput`, `BaseTextarea`, `BaseButton`) są reużywalne
- **Separation of concerns:** Logika biznesowa w composable `useValuationForm`, prezentacja w komponentach
- **Walidacja:** Wielopoziomowa (klient + backend) z czytelnymi komunikatami
- **Obsługa błędów:** Wszystkie scenariusze błędów są obsługiwane i wyświetlane użytkownikowi
- **Dostępność:** Formularz zgodny z WCAG 2.1 AA
- **Testowanie:** Unit testy + E2E testy zapewniają jakość kodu
- **i18n:** Wszystkie teksty zarządzane centralnie, łatwa zmiana języka w przyszłości

Implementacja powinna zająć około 3-5 dni pracy (w zależności od doświadczenia developera), z uwzględnieniem testów i code review.
