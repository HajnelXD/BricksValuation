# Plan implementacji widoku Logowania i Wylogowania (Login & Logout View)

## 1. Przegląd

Widok logowania stanowi punkt wejścia dla zarejestrowanych użytkowników, umożliwiając uwierzytelnienie poprzez formularz z polami username/email i password. Po pomyślnym logowaniu użytkownik otrzymuje aktywną sesję (JWT w HttpOnly cookie) i jest przekierowywany do docelowej strony aplikacji. Widok jest dostępny pod publiczną ścieżką `/login` i wykorzystuje wspólny komponent `AuthFormLayout` do zachowania spójności z widokiem rejestracji.

Wylogowanie to akcja dostępna z poziomu zalogowanego użytkownika (menu nawigacji), która unieważnia sesję po stronie serwera i czyści stan klienta, przekierowując użytkownika na stronę publiczną.

### Kluczowe cele:
- **Uwierzytelnienie**: walidacja poprawności pary login/hasło (FR-02)
- **Zarządzanie sesją**: utworzenie aktywnej sesji po zalogowaniu, unieważnienie przy wylogowaniu (FR-02, FR-03)
- **Obsługa błędów**: ogólny komunikat przy błędnych danych (bez ujawniania szczegółów) (FR-20, US-002)
- **Deep linking**: przekierowanie do pierwotnie żądanej ścieżki po zalogowaniu
- **Dostępność**: pełna obsługa klawiatury, ARIA labels, focus management

## 2. Routing widoku

### Login View
- **Ścieżka**: `/login`
- **Nazwa route**: `login`
- **Meta**: `{ requiresGuest: true }` – użytkownik zalogowany powinien być automatycznie przekierowany do `/app/bricksets`
- **Query params (opcjonalne)**: 
  - `redirect` – ścieżka, do której użytkownik ma być przekierowany po zalogowaniu (np. `/app/bricksets/123`)
  - fallback: `/app/bricksets`

### Logout (akcja)
- **Ścieżka**: brak dedykowanego widoku – akcja wywołana z menu nawigacji lub przycisku
- **Endpoint**: `POST /api/v1/auth/logout`
- **Redirect**: po wylogowaniu użytkownik trafia na `/` (strona publiczna)

## 3. Struktura komponentów

```
LoginView.vue (strona)
├── AuthFormLayout (layout)
│   ├── title (slot prop)
│   ├── form (slot default)
│   │   ├── BaseInput (username/email)
│   │   ├── BaseInput (password)
│   │   ├── InlineError (server error)
│   │   ├── BaseButton (submit)
│   └── links (slot)
│       └── RouterLink (do rejestracji)
```

**Logout** (brak dedykowanego komponentu widoku):
- `UserMenu` (komponent nawigacji w `AuthenticatedLayout`)
  - Przycisk "Wyloguj" → wywołanie `authStore.logout()`
  - `NotificationToaster` (toast "Wylogowano pomyślnie")

## 4. Szczegóły komponentów

### LoginView.vue
- **Opis komponentu**: Główny widok strony logowania. Zarządza stanem formularza (username, password), walidacją po stronie klienta, wywołaniem API logowania oraz obsługą błędów i przekierowań. Wykorzystuje Composition API z `<script setup>`.
  
- **Główne elementy**:
  - `AuthFormLayout` – zapewnia spójny układ dla wszystkich formularzy uwierzytelniania
  - Dwa komponenty `BaseInput`:
    - Pole `username` (opcjonalnie email – backend akceptuje oba) – type="text", autocomplete="username"
    - Pole `password` – type="password", autocomplete="current-password"
  - `InlineError` (opcjonalnie `div` z rolą `alert`) – komunikat błędu z API (np. "Nieprawidłowe dane logowania")
  - `BaseButton` typu submit – z loading state (spinner + disabled podczas isSubmitting)
  - Link do rejestracji w sekcji `links` (slot)

- **Obsługiwane interakcje**:
  - **Wypełnienie formularza**: reaktywne pola `username`, `password` (v-model)
  - **Submit formularza** (Enter lub klik przycisku):
    1. Walidacja kliencka (pola niepuste – podstawowa)
    2. Ustawienie `isSubmitting = true` (loading state)
    3. Wywołanie `authStore.login({ username, password })`
    4. Przy sukcesie (200):
       - Zapisanie użytkownika w store (dane z response)
       - Redirect do `redirect` query param lub `/app/bricksets`
    5. Przy błędzie (400/401):
       - Wyświetlenie komunikatu błędu (`serverError = "Nieprawidłowe dane logowania"`)
       - Focus na pierwsze pole (username) dla ponownej próby
    6. Ustawienie `isSubmitting = false`
  - **Nawigacja do rejestracji**: klik linku "Zarejestruj się" → `router.push({ name: 'register' })`

- **Obsługiwana walidacja**:
  - **Klient**:
    - Pola `username` i `password` niepuste (wymagane) – walidacja przy submit
    - Walidacja długości pól (opcjonalnie – min. 1 znak)
  - **Server**:
    - 400 VALIDATION_ERROR – brakujące pola → komunikat "Wypełnij wszystkie pola"
    - 401 INVALID_CREDENTIALS – nieprawidłowe dane → komunikat "Nieprawidłowe dane logowania"
  - **Komunikaty błędów**: wyświetlane w `InlineError` (lub div z role="alert", aria-live="assertive")

- **Typy**:
  - `LoginRequestDTO` – payload żądania
  - `LoginResponseDTO` – odpowiedź z API
  - `UserDTO` – dane użytkownika zwrócone po zalogowaniu
  - `LoginFormData` – lokalny stan formularza (username, password)

- **Propsy**:
  - Brak (widok top-level, dane z routera i store)

### AuthFormLayout (reużywalny)
- **Opis**: Komponent layoutu współdzielony między Login i Register. Zapewnia strukturę (centered container, responsive, dark mode). Opisany szczegółowo w planie Register View.
  
- **Propsy**:
  - `title?: string` – tytuł formularza (np. "Logowanie")

- **Sloty**:
  - `default` – zawartość formularza
  - `links` – sekcja z dodatkowymi linkami (np. do rejestracji)

### BaseInput (reużywalny)
- **Opis**: Komponent input z labelką, walidacją inline i obsługą błędów. Opisany w planie Register View.

- **Propsy**:
  - `modelValue: string`
  - `label: string`
  - `type?: string` (domyślnie "text")
  - `error?: string`
  - `placeholder?: string`
  - `autocomplete?: string`
  - `required?: boolean`
  - `disabled?: boolean`

- **Emity**: `update:modelValue`

### BaseButton (nowy komponent bazowy)
- **Opis**: Reużywalny komponent przycisku z obsługą loading state, wariantów (primary, secondary, danger) i stanów disabled.

- **Główne elementy**:
  - `<button>` z dynamiczną klasą Tailwind (variant-based)
  - Slot dla treści + opcjonalny spinner icon przy `loading=true`

- **Propsy**:
  - `type?: 'button' | 'submit' | 'reset'` (domyślnie "button")
  - `variant?: 'primary' | 'secondary' | 'danger'` (domyślnie "primary")
  - `loading?: boolean` (domyślnie false) – wyświetla spinner i ustawia disabled
  - `disabled?: boolean`
  - `fullWidth?: boolean` – szerokość 100%

- **Interakcje**:
  - `@click` – emit `click` event (jeśli nie disabled/loading)

### InlineError (nowy lub rozszerzenie)
- **Opis**: Komponent wyświetlający komunikat błędu z ikoną ⚠️ i odpowiednią rolą ARIA (`alert`).

- **Główne elementy**:
  - `<div role="alert" aria-live="assertive">` z czerwonym tłem (lub obramowaniem)
  - Ikona + tekst błędu

- **Propsy**:
  - `message: string` – treść błędu
  - `dismissible?: boolean` – opcja zamknięcia (X) – w MVP może być pominięte

### UserMenu (komponent w AuthenticatedLayout)
- **Opis**: Menu dropdown w nawigacji zalogowanego użytkownika. Zawiera opcje "Profil" i "Wyloguj".

- **Główne elementy**:
  - Avatar placeholder (inicjały username lub ikona)
  - Dropdown menu (otwierany po kliknięciu)
  - Lista opcji: 
    - "Profil" → `router.push({ name: 'profile' })`
    - "Wyloguj" → wywołanie `handleLogout()`

- **Obsługiwane interakcje**:
  - **Klik "Wyloguj"**:
    1. Wywołanie `authStore.logout()`
    2. Ustawienie loading state (opcjonalnie)
    3. Czyszczenie store (user, isAuthenticated)
    4. Redirect do `/` (lub `/login`)
    5. Toast "Wylogowano pomyślnie" (z `NotificationToaster`)

- **Typy**: korzysta z `authStore` (Pinia)

- **Propsy**: Brak (dane z store)

## 5. Typy

### DTOs (Request & Response)

```typescript
// Login Request DTO
export interface LoginRequestDTO {
  username: string;  // akceptuje username lub email
  password: string;
}

// Login Response DTO
export interface LoginResponseDTO {
  user: UserDTO;
  token?: string;  // opcjonalnie w body (głównie cookie)
}

// User DTO (zwrócony po logowaniu)
export interface UserDTO {
  id: number;
  username: string;
  email: string;
  created_at?: string;  // ISO 8601 datetime
}

// Logout – brak payload (POST /auth/logout → 204 No Content)
```

### Błędy API

```typescript
// Validation Error (400)
export interface ValidationErrorDTO {
  error_code: 'VALIDATION_ERROR';
  message: string;
  field_errors?: {
    [field: string]: string[];
  };
}

// Invalid Credentials (401)
export interface InvalidCredentialsErrorDTO {
  error_code: 'INVALID_CREDENTIALS';
  message: string;  // "Nieprawidłowe dane logowania"
}

// Not Authenticated (401) – dla logout jeśli sesja już wygasła
export interface NotAuthenticatedErrorDTO {
  error_code: 'NOT_AUTHENTICATED';
  message: string;
}
```

### ViewModels / Stan lokalny

```typescript
// Login Form Data (lokalny stan w LoginView)
export interface LoginFormData {
  username: string;
  password: string;
}

// Server Error State
export interface LoginErrorState {
  message: string | null;
  code?: string;
}
```

### Auth Store State

```typescript
// Auth Store (Pinia)
export interface AuthState {
  user: UserDTO | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
```

## 6. Zarządzanie stanem

### Stan lokalny (LoginView)

Zarządzany w komponencie `LoginView.vue` przy użyciu Composition API (`ref`, `computed`):

```typescript
const formData = ref<LoginFormData>({
  username: '',
  password: '',
});

const isSubmitting = ref(false);
const serverError = ref<string | null>(null);

// Computed dla walidacji
const isFormValid = computed(() => {
  return formData.value.username.trim() !== '' 
      && formData.value.password.trim() !== '';
});
```

### Pinia Store (authStore)

Store `authStore` zarządza globalnym stanem uwierzytelnienia:

```typescript
// stores/auth.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import type { LoginRequestDTO, LoginResponseDTO, UserDTO } from '@/types/auth';

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserDTO | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => user.value !== null);

  async function login(credentials: LoginRequestDTO): Promise<UserDTO> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await axios.post<LoginResponseDTO>(
        '/api/v1/auth/login',
        credentials,
        { withCredentials: true }  // wysyła cookie
      );

      user.value = response.data.user;
      return response.data.user;
    } catch (err: any) {
      // Mapowanie błędów API
      if (err.response?.status === 400) {
        error.value = 'Wypełnij wszystkie pola';
      } else if (err.response?.status === 401) {
        error.value = 'Nieprawidłowe dane logowania';
      } else {
        error.value = 'Wystąpił nieoczekiwany błąd';
      }
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function logout(): Promise<void> {
    isLoading.value = true;

    try {
      await axios.post('/api/v1/auth/logout', {}, { withCredentials: true });
      user.value = null;
      error.value = null;
    } catch (err: any) {
      // Ignorujemy błędy 401 (sesja już wygasła) – czyścimy stan lokalnie
      if (err.response?.status !== 401) {
        console.error('Logout error:', err);
      }
      // Zawsze czyścimy stan użytkownika
      user.value = null;
    } finally {
      isLoading.value = false;
    }
  }

  // Funkcja do pobrania profilu użytkownika (sprawdzenie sesji)
  async function fetchProfile(): Promise<UserDTO | null> {
    isLoading.value = true;
    try {
      const response = await axios.get<UserDTO>('/api/v1/auth/me', {
        withCredentials: true,
      });
      user.value = response.data;
      return response.data;
    } catch (err: any) {
      if (err.response?.status === 401) {
        user.value = null;
      }
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    fetchProfile,
  };
});
```

### Router Guards

Guard dla `/login` zapewniający, że zalogowany użytkownik nie ma dostępu do widoku logowania:

```typescript
// router/index.ts
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // Sprawdzenie sesji przy pierwszym wejściu (jeśli user === null)
  if (authStore.user === null && !authStore.isLoading) {
    await authStore.fetchProfile();
  }

  // Guard dla gości (requiresGuest)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'app-bricksets' });  // redirect zalogowanego użytkownika
    return;
  }

  // Guard dla uwierzytelnionych (requiresAuth)
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } });
    return;
  }

  next();
});
```

## 7. Integracja API

### Login: POST /api/v1/auth/login

**Request**:
```typescript
// Payload
{
  "username": "string",   // akceptuje username lub email
  "password": "string"
}

// Headers (generowane przez axios)
Content-Type: application/json

// Axios config
withCredentials: true  // wysyła i przyjmuje cookies
```

**Response – Success (200)**:
```typescript
{
  "user": {
    "id": 123,
    "username": "user123",
    "email": "user@example.com"
  },
  "token": "<jwt>"  // opcjonalnie (głównie HttpOnly cookie)
}

// Headers
Set-Cookie: jwt=<token>; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=86400
```

**Response – Errors**:
- **400 VALIDATION_ERROR**: brakujące pola (username lub password)
  ```json
  {
    "error_code": "VALIDATION_ERROR",
    "message": "Wszystkie pola są wymagane",
    "field_errors": {
      "username": ["To pole jest wymagane"],
      "password": ["To pole jest wymagane"]
    }
  }
  ```

- **401 INVALID_CREDENTIALS**: nieprawidłowe dane logowania
  ```json
  {
    "error_code": "INVALID_CREDENTIALS",
    "message": "Nieprawidłowe dane logowania"
  }
  ```

**Typy żądania i odpowiedzi**:
```typescript
// Request
const loginPayload: LoginRequestDTO = {
  username: formData.value.username,
  password: formData.value.password,
};

// Response
const response = await axios.post<LoginResponseDTO>(
  '/api/v1/auth/login',
  loginPayload,
  { withCredentials: true }
);

const user: UserDTO = response.data.user;
```

### Logout: POST /api/v1/auth/logout

**Request**:
```typescript
// Payload – brak (pusty body)
{}

// Axios config
withCredentials: true  // wysyła cookie JWT
```

**Response – Success (204)**:
```
No Content

// Headers
Set-Cookie: jwt=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0  // usuwa cookie
```

**Response – Errors**:
- **401 NOT_AUTHENTICATED**: sesja już nieważna (ignorowane – czyścimy stan lokalnie)
  ```json
  {
    "error_code": "NOT_AUTHENTICATED",
    "message": "Nie jesteś zalogowany"
  }
  ```

**Typy żądania i odpowiedzi**:
```typescript
// Request – brak payload
await axios.post<void>('/api/v1/auth/logout', {}, { withCredentials: true });

// Response – 204 No Content (brak body)
```

### Profil użytkownika: GET /api/v1/auth/me

**Request**:
```typescript
// Brak payload

// Axios config
withCredentials: true
```

**Response – Success (200)**:
```typescript
{
  "id": 123,
  "username": "user123",
  "email": "user@example.com",
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Response – Errors**:
- **401 NOT_AUTHENTICATED**: brak sesji lub wygasła
  ```json
  {
    "error_code": "NOT_AUTHENTICATED",
    "message": "Nie jesteś zalogowany"
  }
  ```

## 8. Interakcje użytkownika

### Scenariusz 1: Pomyślne logowanie (Happy Path)

1. **Użytkownik wchodzi na `/login`**:
   - Render `LoginView` z pustym formularzem
   - Focus automatycznie na polu `username` (autofocus)

2. **Użytkownik wypełnia pola**:
   - Wpisuje username (lub email)
   - Wpisuje hasło (type="password", ukryte znaki)

3. **Użytkownik submittuje formularz** (Enter lub klik "Zaloguj się"):
   - Walidacja kliencka: pola niepuste → OK
   - `isSubmitting = true` → przycisk disabled, spinner
   - Wywołanie `authStore.login(credentials)`
   - API zwraca 200 + dane użytkownika
   - Store zapisuje `user`, `isAuthenticated = true`
   - Redirect do `redirect` query param lub `/app/bricksets`
   - Toast (opcjonalnie): "Zalogowano pomyślnie"

4. **Użytkownik widzi główną stronę aplikacji**:
   - Nawigacja `AuthenticatedNav` z menu użytkownika
   - Dostęp do wszystkich chronionych funkcji

### Scenariusz 2: Błędne dane logowania

1. **Użytkownik wypełnia formularz z nieprawidłowymi danymi**:
   - Username: "wronguser"
   - Password: "wrongpassword"

2. **Użytkownik submittuje formularz**:
   - Walidacja kliencka: OK
   - `isSubmitting = true`
   - Wywołanie `authStore.login(credentials)`
   - API zwraca 401 INVALID_CREDENTIALS
   - Store ustawia `error = "Nieprawidłowe dane logowania"`

3. **Komponent wyświetla błąd**:
   - `InlineError` z komunikatem "Nieprawidłowe dane logowania"
   - `isSubmitting = false`
   - Focus powraca na pole `username`

4. **Użytkownik poprawia dane i próbuje ponownie**:
   - Przy zmianie wartości w polach `serverError` jest czyszczony
   - Po ponownym submicie: jeśli dane poprawne → sukces

### Scenariusz 3: Puste pola (walidacja kliencka)

1. **Użytkownik próbuje zasubmitować pusty formularz**:
   - Walidacja kliencka: `isFormValid = false`
   - Prevent submit (opcjonalnie) lub
   - Wyświetlenie komunikatu "Wypełnij wszystkie pola"
   - Focus na pierwszym pustym polu

### Scenariusz 4: Deep linking (przekierowanie po logowaniu)

1. **Niezalogowany użytkownik próbuje wejść na `/app/bricksets/123`**:
   - Router guard: `requiresAuth = true`, `isAuthenticated = false`
   - Redirect do `/login?redirect=/app/bricksets/123`

2. **Użytkownik loguje się**:
   - Po sukcesie: odczyt `redirect` query param
   - Redirect do `/app/bricksets/123`
   - Użytkownik widzi szczegóły zestawu

### Scenariusz 5: Wylogowanie

1. **Zalogowany użytkownik klika "Wyloguj" w menu**:
   - Wywołanie `authStore.logout()`
   - `isLoading = true`
   - Wywołanie `POST /api/v1/auth/logout`
   - API zwraca 204 (sukces)

2. **Store czyści stan**:
   - `user = null`
   - `isAuthenticated = false`

3. **Redirect do `/`**:
   - `router.push({ name: 'public-bricksets' })`
   - Toast "Wylogowano pomyślnie" (z `NotificationToaster`)

4. **Użytkownik widzi stronę publiczną**:
   - Nawigacja `PublicNav` z linkami "Logowanie" i "Rejestracja"

### Scenariusz 6: Wylogowanie z wygasłą sesją

1. **Użytkownik klika "Wyloguj", ale sesja już wygasła**:
   - Wywołanie `POST /api/v1/auth/logout`
   - API zwraca 401 NOT_AUTHENTICATED

2. **Store czyści stan (ignoruje błąd)**:
   - `user = null`
   - Redirect do `/`

3. **Użytkownik widzi stronę publiczną**:
   - Toast (opcjonalnie): "Sesja wygasła, zostałeś wylogowany"

## 9. Warunki i walidacja

### Walidacja kliencka (LoginView)

| Pole | Warunek | Komunikat błędu | Kiedy |
|------|---------|-----------------|-------|
| `username` | Niepuste (trim) | "Nazwa użytkownika jest wymagana" | Submit |
| `password` | Niepuste (trim), min 1 znak | "Hasło jest wymagane" | Submit |
| Formularz | Oba pola wypełnione | "Wypełnij wszystkie pola" | Submit jeśli puste |

**Implementacja**:
```typescript
function validateForm(): boolean {
  let isValid = true;

  if (formData.value.username.trim() === '') {
    fieldErrors.value.username = 'Nazwa użytkownika jest wymagana';
    isValid = false;
  }

  if (formData.value.password.trim() === '') {
    fieldErrors.value.password = 'Hasło jest wymagane';
    isValid = false;
  }

  return isValid;
}
```

### Walidacja serwerowa (API)

| Status | Error Code | Opis | Akcja UI |
|--------|-----------|------|----------|
| 400 | VALIDATION_ERROR | Brakujące lub nieprawidłowe pola | Wyświetl `field_errors` inline dla każdego pola + ogólny komunikat w `InlineError` |
| 401 | INVALID_CREDENTIALS | Nieprawidłowy username/email lub hasło | Wyświetl ogólny komunikat "Nieprawidłowe dane logowania" w `InlineError` |
| 500 | INTERNAL_ERROR | Błąd serwera | Wyświetl "Wystąpił nieoczekiwany błąd. Spróbuj ponownie później" |

**Mapowanie błędów**:
```typescript
catch (err: any) {
  if (err.response?.data?.error_code === 'VALIDATION_ERROR') {
    // Mapowanie field_errors na pola formularza
    const fieldErrors = err.response.data.field_errors || {};
    if (fieldErrors.username) {
      fieldErrors.value.username = fieldErrors.username[0];
    }
    if (fieldErrors.password) {
      fieldErrors.value.password = fieldErrors.password[0];
    }
    serverError.value = err.response.data.message || 'Wypełnij wszystkie pola';
  } else if (err.response?.data?.error_code === 'INVALID_CREDENTIALS') {
    serverError.value = 'Nieprawidłowe dane logowania';
  } else {
    serverError.value = 'Wystąpił nieoczekiwany błąd';
  }
}
```

### Warunki routing guard

| Guard | Warunek | Akcja |
|-------|---------|-------|
| `requiresGuest: true` (route `/login`) | `isAuthenticated = true` | Redirect do `/app/bricksets` |
| `requiresAuth: true` (chronione ścieżki) | `isAuthenticated = false` | Redirect do `/login?redirect=<target>` |

**Implementacja**:
```typescript
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // Inicjalizacja sesji (fetch profile przy pierwszym wejściu)
  if (authStore.user === null && !authStore.isLoading) {
    await authStore.fetchProfile();
  }

  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'app-bricksets' });
    return;
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } });
    return;
  }

  next();
});
```

## 10. Obsługa błędów

### Błędy API

| Typ błędu | Status | Obsługa |
|-----------|--------|---------|
| Walidacja (puste pola) | 400 | Wyświetl komunikaty per pole + ogólny w `InlineError` |
| Nieprawidłowe dane | 401 | Ogólny komunikat "Nieprawidłowe dane logowania" (brak szczegółów) |
| Błąd serwera | 500 | "Wystąpił nieoczekiwany błąd. Spróbuj ponownie później" |
| Błąd sieci (timeout) | N/A | "Sprawdź połączenie z internetem i spróbuj ponownie" |

### Błędy klienta

| Scenariusz | Obsługa |
|------------|---------|
| Puste pola przy submit | Prevent submit + wyświetl komunikaty walidacji klienta |
| Sesja wygasła podczas korzystania | Router guard przekierowuje do `/login` z komunikatem "Sesja wygasła" |
| Utrata połączenia podczas logowania | Wyświetl komunikat błędu sieci + przycisk "Spróbuj ponownie" |

### Przypadki brzegowe

1. **Użytkownik submittuje formularz wielokrotnie (double-click)**:
   - `isSubmitting = true` disabluje przycisk → prevent multiple calls
   - Axios request cancellation (opcjonalnie) przy unmount komponentu

2. **Redirect loop (zalogowany użytkownik na `/login` z `redirect` query)**:
   - Guard sprawdza `isAuthenticated` przed redirect → jeśli true, redirect do docelowej strony (pomijając `/login`)

3. **JWT cookie wygasł, ale klient myśli, że jest zalogowany**:
   - `fetchProfile()` przy inicjalizacji routera sprawdza sesję
   - Jeśli 401 → czyści `user` w store → guard przekierowuje do `/login`

4. **Backend niedostępny (500/503)**:
   - Wyświetl komunikat błędu
   - Przycisk "Spróbuj ponownie" → retry `login()`
   - Opcjonalnie: exponential backoff (w przyszłości)

### Toasty i powiadomienia

| Event | Toast |
|-------|-------|
| Pomyślne logowanie | (Opcjonalnie) "Witaj, [username]!" |
| Pomyślne wylogowanie | "Wylogowano pomyślnie" |
| Sesja wygasła | "Sesja wygasła. Zaloguj się ponownie" |
| Błąd logowania | Brak toasta (komunikat inline) |

## 11. Kroki implementacji

### Faza 1: Przygotowanie typów i store (authStore)

1. **Utworzenie typów DTO** (`src/types/auth.ts`):
   - `LoginRequestDTO`, `LoginResponseDTO`, `UserDTO`
   - `ValidationErrorDTO`, `InvalidCredentialsErrorDTO`
   - `LoginFormData`, `LoginErrorState`

2. **Rozszerzenie `authStore`** (`src/stores/auth.ts`):
   - Dodanie stanu: `user`, `isAuthenticated`, `isLoading`, `error`
   - Implementacja `login(credentials)` – POST `/api/v1/auth/login`
   - Implementacja `logout()` – POST `/api/v1/auth/logout`
   - Implementacja `fetchProfile()` – GET `/api/v1/auth/me`
   - Obsługa błędów: mapowanie 400/401/500 → komunikaty

3. **Konfiguracja Axios** (jeśli jeszcze nie):
   - `withCredentials: true` (globalnie lub per request)
   - Base URL: `/api/v1`
   - Interceptory dla obsługi błędów (opcjonalnie)

### Faza 2: Implementacja komponentów bazowych

4. **Utworzenie `BaseButton.vue`** (`src/components/base/BaseButton.vue`):
   - Propsy: `type`, `variant`, `loading`, `disabled`, `fullWidth`
   - Slot dla treści + spinner przy `loading=true`
   - Style Tailwind dla wariantów (primary, secondary, danger)
   - Emisja `click` event

5. **Utworzenie `InlineError.vue`** (`src/components/base/InlineError.vue`):
   - Props: `message`
   - Struktura: `<div role="alert" aria-live="assertive">` z ikoną ⚠️
   - Style: czerwone tło/obramowanie, transition fade-in
   - Opcjonalnie: props `dismissible` (przycisk X)

### Faza 3: Implementacja widoku logowania (LoginView)

6. **Utworzenie `LoginView.vue`** (`src/pages/auth/LoginView.vue`):
   - Import: `AuthFormLayout`, `BaseInput`, `BaseButton`, `InlineError`
   - Stan lokalny: `formData` (username, password), `isSubmitting`, `serverError`, `fieldErrors`
   - Computed: `isFormValid` (oba pola niepuste)
   - Funkcja `handleSubmit()`:
     - Walidacja kliencka
     - Wywołanie `authStore.login(formData)`
     - Obsługa sukcesu: redirect do `redirect` query lub `/app/bricksets`
     - Obsługa błędów: mapowanie na `serverError` + `fieldErrors`
     - Focus management (powrót na `username` przy błędzie)
   - Funkcja `clearServerError()` – wywołana przy zmianie wartości pól
   - Template:
     - `AuthFormLayout` z title="Logowanie"
     - Slot default: formularz z polami i przyciskiem
     - Slot links: link do rejestracji

7. **Dodanie internacjonalizacji** (`src/i18n.ts`):
   - Dodanie kluczy:
     ```typescript
     login: {
       title: 'Logowanie',
       username: 'Nazwa użytkownika lub email',
       password: 'Hasło',
       submit: 'Zaloguj się',
       hasAccount: 'Nie masz konta?',
       register: 'Zarejestruj się',
     },
     errors: {
       invalidCredentials: 'Nieprawidłowe dane logowania',
       requiredField: 'To pole jest wymagane',
       fillAllFields: 'Wypełnij wszystkie pola',
       unexpectedError: 'Wystąpił nieoczekiwany błąd',
     },
     ```

### Faza 4: Routing i guardy

8. **Aktualizacja routera** (`src/router/index.ts`):
   - Sprawdzenie, czy route `/login` ma `meta: { requiresGuest: true }`
   - Implementacja `beforeEach` guard:
     - Sprawdzenie sesji (`fetchProfile()`) przy pierwszym wejściu
     - Redirect zalogowanego użytkownika z `/login` → `/app/bricksets`
     - Redirect niezalogowanego z chronionych ścieżek → `/login?redirect=<target>`

9. **Dodanie route dla chronionej części** (jeśli jeszcze nie):
   - `/app/bricksets` z `meta: { requiresAuth: true }`
   - Layout: `AuthenticatedLayout` (do utworzenia w przyszłości)

### Faza 5: Implementacja wylogowania (UserMenu)

10. **Utworzenie `UserMenu.vue`** (`src/components/navigation/UserMenu.vue`):
    - Stan lokalny: `isOpen` (dropdown)
    - Dane z `authStore`: `user.username`
    - Avatar placeholder (inicjały lub ikona)
    - Dropdown menu z opcjami:
      - "Profil" → `router.push({ name: 'profile' })`
      - "Wyloguj" → `handleLogout()`
    - Funkcja `handleLogout()`:
      - Wywołanie `authStore.logout()`
      - Redirect do `/`
      - Toast "Wylogowano pomyślnie"
    - Accessibility: role="menu", role="menuitem", focus trap

11. **Dodanie `UserMenu` do nawigacji**:
    - W `AuthenticatedNav.vue` (komponent layoutu zalogowanego) dodać `UserMenu` w sekcji prawej
    - Opcjonalnie: `NotificationToaster` w `AuthenticatedLayout` dla toastów

### Faza 6: Toasty i powiadomienia

12. **Utworzenie `NotificationToaster.vue`** (jeśli jeszcze nie istnieje):
    - Store `notificationStore` (Pinia) z listą toastów
    - Komponent wyświetlający toasty w prawym górnym rogu
    - Funkcja `addToast(message, type, duration)`
    - Auto-dismiss po `duration` ms (domyślnie 5000)

13. **Dodanie toastów w akcjach**:
    - W `authStore.logout()`: po sukcesie wywołaj `notificationStore.addToast('Wylogowano pomyślnie', 'success')`
    - W router guard: przy sesji wygasłej `notificationStore.addToast('Sesja wygasła. Zaloguj się ponownie', 'warning')`

### Faza 7: Testowanie i walidacja

14. **Testy jednostkowe** (`src/__tests__/unit/pages/LoginView.spec.ts`):
    - Render komponentu
    - Walidacja formularza (puste pola)
    - Submit z poprawnymi danymi → wywołanie `authStore.login()`
    - Submit z błędnymi danymi → wyświetlenie komunikatu błędu
    - Redirect po sukcesie
    - Czyszczenie `serverError` przy zmianie wartości pól

15. **Testy integracyjne authStore** (`src/__tests__/unit/stores/auth.spec.ts`):
    - `login()` z poprawnymi danymi → sukces, `user` zapisany
    - `login()` z błędnymi danymi → błąd 401, `error` ustawiony
    - `logout()` → czyszczenie `user`, `isAuthenticated = false`
    - `fetchProfile()` → sprawdzenie sesji

16. **Testy E2E** (Cypress – `cypress/e2e/auth/login.cy.ts`):
    - Pełny przepływ logowania: wejście na `/login` → wypełnienie formularza → submit → redirect
    - Błędne dane → wyświetlenie komunikatu
    - Wylogowanie: klik "Wyloguj" → redirect do `/` → brak dostępu do chronionych ścieżek
    - Deep linking: próba wejścia na `/app/bricksets` → redirect do `/login?redirect=...` → po zalogowaniu redirect do docelowej strony

### Faza 8: Dostępność i responsywność

17. **Audyt dostępności** (axe DevTools):
    - Sprawdzenie kontrastów tekstu i przycisków
    - Sprawdzenie ARIA labels i ról
    - Testowanie nawigacji klawiaturą (Tab, Enter, Esc)
    - Focus management (focus na username przy wejściu, powrót po błędzie)

18. **Testowanie responsywności**:
    - Mobile (375px): formularz full-width, przyciski stacked
    - Tablet (768px): formularz max-width 400px, centrowany
    - Desktop (1280px): formularz max-width 500px

### Faza 9: Integracja z backendem

19. **Testowanie z rzeczywistym API**:
    - Uruchomienie backendu (Django)
    - Testowanie logowania z istniejącym kontem
    - Sprawdzenie, czy JWT cookie jest ustawiany (`HttpOnly`, `Secure`, `SameSite=Strict`)
    - Testowanie wylogowania → sprawdzenie, czy cookie jest usuwany
    - Testowanie `fetchProfile()` → sprawdzenie, czy sesja jest zachowana po odświeżeniu

20. **Debugowanie błędów CORS/cookie** (jeśli występują):
    - Sprawdzenie konfiguracji CORS w Django (`CORS_ALLOW_CREDENTIALS = True`)
    - Sprawdzenie `withCredentials: true` w Axios
    - Sprawdzenie domeny cookie (powinny być ustawione dla tej samej domeny co frontend)

### Faza 10: Dokumentacja i finalizacja

21. **Dodanie dokumentacji** w kodzie:
    - JSDoc dla funkcji `login()`, `logout()`, `fetchProfile()`
    - Komentarze w `LoginView` wyjaśniające flow

22. **Aktualizacja README projektu**:
    - Dodanie sekcji "Uwierzytelnienie" z opisem flow logowania i wylogowania
    - Instrukcje dla deweloperów: jak uruchomić backend, jak testować sesję

23. **Code review i optymalizacja**:
    - Usunięcie nieużywanych importów
    - Sprawdzenie zgodności z linterem (ESLint, Prettier)
    - Refactoring (jeśli potrzebny): wydzielenie logiki walidacji do composable `useLoginForm`

24. **Commit i push**:
    - Commit message: `feat(auth): implement login and logout views with session management`
    - Push do brancha feature: `BV-XX-login-logout-implementation`
    - Utworzenie Pull Request z opisem zmian i screenshotami

---

## Podsumowanie

Plan implementacji widoku logowania i wylogowania obejmuje wszystkie kluczowe elementy zgodne z wymaganiami PRD (FR-02, FR-03, FR-18, FR-20) oraz historyjkami użytkownika (US-002, US-003). Implementacja wykorzystuje najlepsze praktyki Vue 3 (Composition API, TypeScript), zapewnia dostępność (ARIA, focus management), bezpieczeństwo (HttpOnly cookies, ogólne komunikaty błędów) oraz spójność UX (współdzielony `AuthFormLayout`, komponenty bazowe).

Kluczowe punkty:
- **Session management**: JWT w HttpOnly cookie, sprawdzanie sesji w router guard
- **Error handling**: mapowanie błędów API na przyjazne komunikaty, brak ujawniania szczegółów
- **Deep linking**: przekierowanie do pierwotnej ścieżki po zalogowaniu
- **Logout**: czyszczenie stanu klienta, redirect, toast z potwierdzeniem
- **Accessibility**: pełna obsługa klawiatury, ARIA labels, focus management
- **Testing**: testy jednostkowe, integracyjne i E2E dla wszystkich scenariuszy

Implementacja jest gotowa do rozszerzenia w przyszłości (np. "Zapamiętaj mnie", reset hasła, 2FA) bez większych zmian w architekturze.
