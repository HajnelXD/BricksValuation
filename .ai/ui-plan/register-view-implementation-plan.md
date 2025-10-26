# Plan implementacji widoku rejestracji (Register View)

## 1. Przegląd
Widok rejestracji umożliwia nowym użytkownikom utworzenie konta w aplikacji BricksValuation. Użytkownik podaje nazwę użytkownika, adres email oraz hasło (dwukrotnie dla potwierdzenia). Po pomyślnej rejestracji użytkownik zostaje przekierowany na stronę logowania z komunikatem potwierdzającym utworzenie konta. Widok implementuje walidację po stronie klienta oraz obsługę błędów walidacji i konfliktów zwracanych przez API.

## 2. Routing widoku
- **Ścieżka**: `/register`
- **Nazwa route**: `register`
- **Dostępność**: publiczna (dla niezalogowanych użytkowników)
- **Meta**: `{ requiresGuest: true }` - aby uniemożliwić dostęp zalogowanym użytkownikom

## 3. Struktura komponentów

```
RegisterView
└── AuthFormLayout
    ├── Nagłówek (tytuł: "Rejestracja")
    └── Formularz
        ├── BaseInput (username)
        │   └── InlineError
        ├── BaseInput (email)
        │   └── InlineError
        ├── BaseInput (password, type="password")
        │   ├── InlineError
        │   └── PasswordStrengthHint (opcjonalnie)
        ├── BaseInput (confirmPassword, type="password")
        │   └── InlineError
        ├── Button (type="submit", "Zarejestruj się")
        └── Link ("Masz już konto? Zaloguj się")
```

## 4. Szczegóły komponentów

### RegisterView (główny komponent widoku)
- **Opis**: Główny komponent zawierający logikę rejestracji użytkownika. Zarządza stanem formularza, walidacją, wywołaniem API oraz obsługą odpowiedzi.
- **Główne elementy**:
  - `AuthFormLayout` jako wrapper zapewniający spójny układ
  - Formularz z czterema polami: username, email, password, confirmPassword
  - Przycisk submit
  - Link do strony logowania
- **Obsługiwane interakcje**:
  - `onSubmit`: walidacja formularza i wywołanie API rejestracji
  - `onInput`: czyszczenie błędu pola przy wprowadzaniu zmian
  - `onBlur`: walidacja pojedynczego pola po utracie fokusu
- **Obsługiwana walidacja**:
  - **username**: 
    - Wymagane (niepuste)
    - Długość: 3-50 znaków
    - Format: alfanumeryczny z kropką, podkreśleniem, myślnikiem (opcjonalnie: `[A-Za-z0-9._-]+`)
  - **email**:
    - Wymagane (niepuste)
    - Poprawny format email (regex: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`)
  - **password**:
    - Wymagane (niepuste)
    - Minimalna długość: 8 znaków
  - **confirmPassword**:
    - Wymagane (niepuste)
    - Musi być identyczne z polem password
- **Typy**: 
  - `RegisterFormData` (ViewModel)
  - `FieldErrors` (ViewModel)
  - `RegisterRequestDTO`
  - `RegisterResponseDTO`
  - `ValidationErrorDTO`
  - `ConflictErrorDTO`
- **Propsy**: Brak (komponent główny widoku)

### AuthFormLayout (komponent układu - istniejący)
- **Opis**: Komponent zapewniający spójny układ dla formularzy uwierzytelniania (rejestracja, logowanie, reset hasła). Dostarcza kontener z odpowiednimi marginesami, centrowaniem i stylowaniem.
- **Główne elementy**:
  - Kontener z max-width i centrowaniem
  - Slot dla nagłówka
  - Slot dla formularza
  - Slot dla linków pomocniczych
- **Obsługiwane interakcje**: Brak (komponent prezentacyjny)
- **Obsługiwana walidacja**: Brak
- **Typy**: Brak specyficznych typów
- **Propsy**:
  - `title?: string` - tytuł formularza

### BaseInput (komponent pola formularza - istniejący)
- **Opis**: Uniwersalny komponent pola wejściowego z obsługą etykiety, walidacji i wyświetlania błędów. Wykorzystywany dla wszystkich pól formularza.
- **Główne elementy**:
  - `<label>` element z tekstem etykiety
  - `<input>` element z bindingiem v-model
  - `InlineError` komponent dla komunikatów błędów
- **Obsługiwane interakcje**:
  - `@input`: emituje zdarzenie `update:modelValue`
  - `@blur`: emituje zdarzenie `blur` dla walidacji
  - `@focus`: emituje zdarzenie `focus`
- **Obsługiwana walidacja**: 
  - Wyświetla komunikat błędu przekazany przez props
  - Wizualna indykacja stanu błędu (czerwona ramka)
- **Typy**:
  - `modelValue: string`
  - `error?: string`
- **Propsy**:
  - `modelValue: string` - wartość pola
  - `label: string` - etykieta pola
  - `type?: string` - typ inputu (domyślnie "text")
  - `error?: string` - komunikat błędu do wyświetlenia
  - `placeholder?: string` - placeholder
  - `disabled?: boolean` - czy pole jest nieaktywne
  - `autocomplete?: string` - atrybut autocomplete

### PasswordStrengthHint (komponent wskazówki siły hasła - opcjonalny, do utworzenia)
- **Opis**: Komponent wyświetlający wizualne wskazówki dotyczące wymagań hasła i ich spełnienia w czasie rzeczywistym.
- **Główne elementy**:
  - Lista wymagań z ikonami (checkmark lub x)
  - Minimalna długość 8 znaków
  - Zawiera literę (opcjonalnie)
  - Zawiera cyfrę (opcjonalnie)
- **Obsługiwane interakcje**: Brak (komponent reaktywnie reaguje na zmiany props)
- **Obsługiwana walidacja**: 
  - Sprawdzenie długości hasła
  - Sprawdzenie obecności litery (opcjonalnie)
  - Sprawdzenie obecności cyfry (opcjonalnie)
- **Typy**:
  - `password: string`
  - `PasswordRequirement` interface (nazwa wymagania, spełnione czy nie)
- **Propsy**:
  - `password: string` - bieżące hasło do analizy

### InlineError (komponent komunikatu błędu - istniejący)
- **Opis**: Komponent wyświetlający komunikat błędu pod polem formularza. Używa stylowania Tailwind do konsystentnego wyglądu.
- **Główne elementy**:
  - `<p>` element ze stylowaniem błędu (czerwony tekst, mała czcionka)
  - Ikona błędu (opcjonalnie)
- **Obsługiwane interakcje**: Brak (komponent prezentacyjny)
- **Obsługiwana walidacja**: Brak
- **Typy**:
  - `message: string`
- **Propsy**:
  - `message: string` - treść komunikatu błędu

## 5. Typy

### RegisterRequestDTO (DTO dla żądania API)
```typescript
interface RegisterRequestDTO {
  username: string;    // 3-50 znaków
  email: string;       // poprawny format email
  password: string;    // minimum 8 znaków
}
```

### RegisterResponseDTO (DTO dla odpowiedzi API - sukces)
```typescript
interface RegisterResponseDTO {
  id: number;
  username: string;
  email: string;
  created_at: string;  // ISO 8601 timestamp
}
```

### ValidationErrorDTO (DTO dla błędu walidacji - 400)
```typescript
interface ValidationErrorDTO {
  errors: {
    [field: string]: string[];  // nazwa pola -> tablica komunikatów błędów
  };
  code: 'VALIDATION_ERROR';
}
```

### ConflictErrorDTO (DTO dla błędu konfliktu - 409)
```typescript
interface ConflictErrorDTO {
  detail: string;
  code: 'USERNAME_TAKEN' | 'EMAIL_TAKEN';
}
```

### RegisterFormData (ViewModel - stan formularza)
```typescript
interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;  // dodatkowe pole nie wysyłane do API
}
```

### FieldErrors (ViewModel - błędy pól)
```typescript
interface FieldErrors {
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
}
```

### PasswordRequirement (dla komponentu PasswordStrengthHint)
```typescript
interface PasswordRequirement {
  label: string;       // etykieta wymagania (np. "Minimum 8 znaków")
  satisfied: boolean;  // czy wymaganie jest spełnione
}
```

## 6. Zarządzanie stanem

### Stan lokalny komponentu (reactive refs)
```typescript
const formData = ref<RegisterFormData>({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
});

const fieldErrors = ref<FieldErrors>({});
const isSubmitting = ref<boolean>(false);
const serverError = ref<string | null>(null);
```

### Custom composable: useRegisterForm (opcjonalnie)
Jeśli logika formularza jest złożona, można wydzielić ją do osobnego composable:

```typescript
export function useRegisterForm() {
  const formData = ref<RegisterFormData>({ ... });
  const fieldErrors = ref<FieldErrors>({});
  const isSubmitting = ref<boolean>(false);
  
  // Walidacja pojedynczego pola
  const validateField = (fieldName: keyof RegisterFormData): boolean => { ... };
  
  // Walidacja całego formularza
  const validateForm = (): boolean => { ... };
  
  // Wysłanie formularza
  const submitForm = async (): Promise<void> => { ... };
  
  // Czyszczenie błędu pola
  const clearFieldError = (fieldName: keyof RegisterFormData): void => { ... };
  
  return {
    formData,
    fieldErrors,
    isSubmitting,
    validateField,
    validateForm,
    submitForm,
    clearFieldError
  };
}
```

### Store Pinia (jeśli potrzebne dla globalnego stanu)
Dla widoku rejestracji prawdopodobnie nie jest potrzebny store Pinia, ponieważ stan jest lokalny dla widoku. Jednak można użyć store'a auth do wywołania API:

```typescript
// stores/auth.ts
export const useAuthStore = defineStore('auth', () => {
  const register = async (data: RegisterRequestDTO): Promise<RegisterResponseDTO> => {
    // Wywołanie API
  };
  
  return { register };
});
```

## 7. Integracja API

### Endpoint
- **Metoda**: POST
- **URL**: `/api/v1/auth/register`
- **Content-Type**: `application/json`

### Typ żądania
```typescript
interface RegisterRequestDTO {
  username: string;
  email: string;
  password: string;
}
```

### Typ odpowiedzi (sukces - 201)
```typescript
interface RegisterResponseDTO {
  id: number;
  username: string;
  email: string;
  created_at: string;
}
```

### Typy odpowiedzi (błędy)
```typescript
// 400 Bad Request
interface ValidationErrorDTO {
  errors: {
    username?: string[];
    email?: string[];
    password?: string[];
  };
  code: 'VALIDATION_ERROR';
}

// 409 Conflict
interface ConflictErrorDTO {
  detail: string;
  code: 'USERNAME_TAKEN' | 'EMAIL_TAKEN';
}
```

### Implementacja wywołania API
```typescript
const submitForm = async () => {
  // Walidacja kliencka
  if (!validateForm()) {
    return;
  }
  
  isSubmitting.value = true;
  serverError.value = null;
  
  try {
    // Przygotowanie danych (bez confirmPassword)
    const requestData: RegisterRequestDTO = {
      username: formData.value.username,
      email: formData.value.email,
      password: formData.value.password
    };
    
    // Wywołanie API
    const response = await authStore.register(requestData);
    
    // Sukces - przekierowanie z toastem
    toast.success(t('register.success')); // "Konto utworzone"
    router.push({ name: 'login' });
    
  } catch (error: any) {
    if (error.response?.status === 400) {
      // Błąd walidacji - mapowanie na pola
      const validationErrors = error.response.data as ValidationErrorDTO;
      mapServerErrorsToFields(validationErrors);
    } else if (error.response?.status === 409) {
      // Konflikt - username lub email zajęte
      const conflictError = error.response.data as ConflictErrorDTO;
      handleConflictError(conflictError);
    } else {
      // Ogólny błąd serwera
      serverError.value = t('errors.serverError');
    }
  } finally {
    isSubmitting.value = false;
  }
};
```

## 8. Interakcje użytkownika

### 1. Nawigacja do strony rejestracji
- **Akcja**: Użytkownik klika link "Zarejestruj się" lub wchodzi na `/register`
- **Rezultat**: Wyświetlenie pustego formularza rejestracji

### 2. Wypełnianie pola username
- **Akcja**: Użytkownik wpisuje tekst w pole username
- **Rezultat**: 
  - Czyszczenie ewentualnego błędu przy wpisywaniu
  - Po utracie focusa (blur): walidacja długości i formatu
  - Wyświetlenie błędu jeśli niepoprawne

### 3. Wypełnianie pola email
- **Akcja**: Użytkownik wpisuje adres email
- **Rezultat**: 
  - Czyszczenie ewentualnego błędu przy wpisywaniu
  - Po blur: walidacja formatu email
  - Wyświetlenie błędu jeśli niepoprawny

### 4. Wypełnianie pola password
- **Akcja**: Użytkownik wpisuje hasło
- **Rezultat**: 
  - Czyszczenie ewentualnego błędu przy wpisywaniu
  - Wyświetlenie komponentu PasswordStrengthHint (jeśli zaimplementowany)
  - Aktualizacja wskaźników spełnienia wymagań w czasie rzeczywistym
  - Po blur: walidacja minimalnej długości

### 5. Wypełnianie pola confirmPassword
- **Akcja**: Użytkownik ponownie wpisuje hasło
- **Rezultat**: 
  - Czyszczenie ewentualnego błędu przy wpisywaniu
  - Po blur lub przy każdej zmianie: walidacja zgodności z password
  - Wyświetlenie błędu jeśli hasła się nie zgadzają

### 6. Próba wysłania formularza z błędami
- **Akcja**: Użytkownik klika "Zarejestruj się" bez poprawnego wypełnienia pól
- **Rezultat**: 
  - Uruchomienie walidacji wszystkich pól
  - Wyświetlenie błędów pod odpowiednimi polami
  - Brak wywołania API
  - Focus na pierwszym polu z błędem

### 7. Wysłanie poprawnie wypełnionego formularza
- **Akcja**: Użytkownik klika "Zarejestruj się" z poprawnymi danymi
- **Rezultat**: 
  - Wyłączenie przycisku submit (stan loading)
  - Wywołanie API POST /api/v1/auth/register
  - Wyświetlenie spinnera lub innej informacji o ładowaniu

### 8. Sukces rejestracji (201)
- **Akcja**: API zwraca status 201 Created
- **Rezultat**: 
  - Wyświetlenie toasta sukcesu "Konto utworzone"
  - Przekierowanie na stronę `/login`

### 9. Błąd walidacji serwera (400)
- **Akcja**: API zwraca status 400 z błędami walidacji
- **Rezultat**: 
  - Mapowanie błędów na odpowiednie pola
  - Wyświetlenie komunikatów błędów pod polami
  - Przywrócenie aktywności przycisku submit

### 10. Konflikt - zajęty username/email (409)
- **Akcja**: API zwraca status 409 z kodem USERNAME_TAKEN lub EMAIL_TAKEN
- **Rezultat**: 
  - Wyświetlenie błędu pod odpowiednim polem (username lub email)
  - Komunikat: "Ta nazwa użytkownika jest już zajęta" lub "Ten adres email jest już zarejestrowany"
  - Przywrócenie aktywności przycisku submit

### 11. Błąd sieciowy lub serwera (5xx, network error)
- **Akcja**: Brak odpowiedzi API lub błąd 500+
- **Rezultat**: 
  - Wyświetlenie ogólnego komunikatu błędu (toast lub banner)
  - Komunikat: "Wystąpił błąd. Spróbuj ponownie później"
  - Przywrócenie aktywności przycisku submit

### 12. Nawigacja do strony logowania
- **Akcja**: Użytkownik klika link "Masz już konto? Zaloguj się"
- **Rezultat**: Przekierowanie na stronę `/login`

## 9. Warunki i walidacja

### Walidacja po stronie klienta (przed wysłaniem API)

#### Pole username
- **Komponent**: BaseInput w RegisterView
- **Warunki**:
  1. Pole nie może być puste
  2. Długość: minimum 3 znaki, maximum 50 znaków
  3. Format: alfanumeryczny z dozwolonymi znakami: `.`, `_`, `-` (regex: `^[A-Za-z0-9._-]+$`)
- **Moment walidacji**: 
  - Przy blur (utrata focusa)
  - Przed submitem formularza
- **Komunikaty błędów**:
  - Puste: "Nazwa użytkownika jest wymagana"
  - Za krótkie: "Nazwa użytkownika musi mieć co najmniej 3 znaki"
  - Za długie: "Nazwa użytkownika może mieć maksymalnie 50 znaków"
  - Niepoprawny format: "Nazwa użytkownika może zawierać tylko litery, cyfry, kropki, podkreślenia i myślniki"
- **Wpływ na UI**: 
  - Czerwona ramka wokół pola
  - Komunikat błędu pod polem
  - Uniemożliwienie wysłania formularza

#### Pole email
- **Komponent**: BaseInput w RegisterView
- **Warunki**:
  1. Pole nie może być puste
  2. Musi spełniać format email (regex: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`)
- **Moment walidacji**: 
  - Przy blur
  - Przed submitem formularza
- **Komunikaty błędów**:
  - Puste: "Adres email jest wymagany"
  - Niepoprawny format: "Wprowadź poprawny adres email"
- **Wpływ na UI**: 
  - Czerwona ramka wokół pola
  - Komunikat błędu pod polem
  - Uniemożliwienie wysłania formularza

#### Pole password
- **Komponent**: BaseInput w RegisterView
- **Warunki**:
  1. Pole nie może być puste
  2. Minimalna długość: 8 znaków
- **Moment walidacji**: 
  - Przy blur
  - Przed submitem formularza
  - W czasie rzeczywistym dla PasswordStrengthHint (jeśli zaimplementowany)
- **Komunikaty błędów**:
  - Puste: "Hasło jest wymagane"
  - Za krótkie: "Hasło musi mieć co najmniej 8 znaków"
- **Wpływ na UI**: 
  - Czerwona ramka wokół pola
  - Komunikat błędu pod polem
  - Uniemożliwienie wysłania formularza
  - PasswordStrengthHint pokazuje status wymagań (czerwony/zielony)

#### Pole confirmPassword
- **Komponent**: BaseInput w RegisterView
- **Warunki**:
  1. Pole nie może być puste
  2. Musi być identyczne z polem password
- **Moment walidacji**: 
  - Przy każdej zmianie (reactive)
  - Przy blur
  - Przed submitem formularza
- **Komunikaty błędów**:
  - Puste: "Potwierdzenie hasła jest wymagane"
  - Niezgodne: "Hasła nie są identyczne"
- **Wpływ na UI**: 
  - Czerwona ramka wokół pola
  - Komunikat błędu pod polem
  - Uniemożliwienie wysłania formularza

### Walidacja po stronie serwera (odpowiedź API)

#### Błąd 400 - VALIDATION_ERROR
- **Warunki**: API wykrywa niepoprawne dane (dubluje walidację kliencką)
- **Obsługa**: 
  - Parsowanie obiektu `errors` z odpowiedzi
  - Mapowanie błędów na pola formularza
  - Wyświetlenie komunikatów błędów pod odpowiednimi polami
- **Komunikaty**: Używane z API lub przetłumaczone przez i18n

#### Błąd 409 - USERNAME_TAKEN
- **Warunki**: Nazwa użytkownika już istnieje w bazie danych
- **Obsługa**: 
  - Wyświetlenie błędu pod polem username
  - Komunikat: "Ta nazwa użytkownika jest już zajęta"
- **Wpływ na UI**: Czerwona ramka i komunikat pod polem username

#### Błąd 409 - EMAIL_TAKEN
- **Warunki**: Adres email już jest zarejestrowany
- **Obsługa**: 
  - Wyświetlenie błędu pod polem email
  - Komunikat: "Ten adres email jest już zarejestrowany"
- **Wpływ na UI**: Czerwona ramka i komunikat pod polem email

### Stan przycisków

#### Przycisk Submit
- **Wyłączony (disabled) gdy**:
  - `isSubmitting === true` (trwa wysyłanie)
  - Istnieją błędy walidacji klienta w `fieldErrors`
- **Aktywny gdy**:
  - Wszystkie pola są wypełnione poprawnie
  - Nie trwa wysyłanie formularza
- **Wizualizacja stanu loading**:
  - Spinner w przycisku
  - Tekst zmieniony na "Rejestrowanie..."
  - Opacity zmniejszona

## 10. Obsługa błędów

### 1. Błędy walidacji klienta
**Scenariusz**: Użytkownik nie wypełnił poprawnie formularza
**Obsługa**:
- Uruchomienie funkcji `validateForm()` przed submitem
- Dla każdego pola sprawdzenie warunków walidacji
- Ustawienie komunikatów w obiekcie `fieldErrors`
- Wyświetlenie błędów pod odpowiednimi polami przez InlineError
- Zapobieżenie wywołaniu API
**Komunikat**: Specyficzne dla każdego pola (patrz sekcja 9)

### 2. Błąd 400 - Walidacja serwera
**Scenariusz**: API zwraca błędy walidacji (duplikacja walidacji klienta)
**Obsługa**:
```typescript
if (error.response?.status === 400) {
  const validationErrors = error.response.data as ValidationErrorDTO;
  // Mapowanie błędów na pola
  Object.keys(validationErrors.errors).forEach(field => {
    fieldErrors.value[field] = validationErrors.errors[field][0];
  });
}
```
**Komunikat**: Z API lub przetłumaczony przez i18n

### 3. Błąd 409 - Konflikt (USERNAME_TAKEN)
**Scenariusz**: Nazwa użytkownika jest już zajęta
**Obsługa**:
```typescript
if (error.response?.status === 409) {
  const conflictError = error.response.data as ConflictErrorDTO;
  if (conflictError.code === 'USERNAME_TAKEN') {
    fieldErrors.value.username = t('register.errors.usernameTaken');
  }
}
```
**Komunikat**: "Ta nazwa użytkownika jest już zajęta"

### 4. Błąd 409 - Konflikt (EMAIL_TAKEN)
**Scenariusz**: Adres email jest już zarejestrowany
**Obsługa**:
```typescript
if (error.response?.status === 409) {
  const conflictError = error.response.data as ConflictErrorDTO;
  if (conflictError.code === 'EMAIL_TAKEN') {
    fieldErrors.value.email = t('register.errors.emailTaken');
  }
}
```
**Komunikat**: "Ten adres email jest już zarejestrowany"

### 5. Błąd 500+ - Błąd serwera
**Scenariusz**: Wewnętrzny błąd serwera
**Obsługa**:
```typescript
if (error.response?.status >= 500) {
  toast.error(t('errors.serverError'));
  // lub
  serverError.value = t('errors.serverError');
}
```
**Komunikat**: "Wystąpił błąd serwera. Spróbuj ponownie później"

### 6. Błąd sieci (Network Error)
**Scenariusz**: Brak połączenia z serwerem
**Obsługa**:
```typescript
catch (error: any) {
  if (!error.response) {
    toast.error(t('errors.networkError'));
  }
}
```
**Komunikat**: "Brak połączenia z serwerem. Sprawdź połączenie internetowe"

### 7. Timeout
**Scenariusz**: Żądanie przekroczyło limit czasu
**Obsługa**:
```typescript
if (error.code === 'ECONNABORTED') {
  toast.error(t('errors.timeout'));
}
```
**Komunikat**: "Żądanie przekroczyło limit czasu. Spróbuj ponownie"

### Strategia obsługi błędów
1. **Walidacja klienta pierwsza**: Zapobieganie niepotrzebnym wywołaniom API
2. **Szczegółowe błędy inline**: Pod każdym polem dla lepszego UX
3. **Toasty dla błędów globalnych**: Błędy serwera, sieci
4. **Czyszczenie błędów**: Przy wprowadzaniu zmian w polach
5. **Zachowanie danych formularza**: Po błędzie użytkownik nie traci wprowadzonych danych
6. **Logowanie błędów**: Wszystkie błędy API logowane do konsoli (development) lub serwisu monitoringu (production)

## 11. Kroki implementacji

### Krok 1: Przygotowanie struktury routing i podstawowego widoku
1. Dodaj route w `router/index.ts`:
```typescript
{
  path: '/register',
  name: 'register',
  component: () => import('@/views/RegisterView.vue'),
  meta: { requiresGuest: true }
}
```
2. Utwórz plik `views/RegisterView.vue` z podstawową strukturą Composition API

### Krok 2: Definicja typów TypeScript
1. Utwórz plik `types/auth.ts` z wszystkimi interfejsami:
   - `RegisterRequestDTO`
   - `RegisterResponseDTO`
   - `ValidationErrorDTO`
   - `ConflictErrorDTO`
   - `RegisterFormData`
   - `FieldErrors`
2. Jeśli tworzysz PasswordStrengthHint, dodaj `PasswordRequirement`

### Krok 3: Implementacja store auth (jeśli nie istnieje)
1. Utwórz `stores/auth.ts` z Pinia
2. Dodaj metodę `register(data: RegisterRequestDTO)`
3. Skonfiguruj axios do wywołań API
4. Obsłuż błędy HTTP i rzuć wyjątki dla łatwiejszej obsługi

### Krok 4: Przygotowanie tłumaczeń i18n
1. Dodaj klucze w `locales/pl.json`:
```json
{
  "register": {
    "title": "Rejestracja",
    "username": "Nazwa użytkownika",
    "email": "Adres email",
    "password": "Hasło",
    "confirmPassword": "Powtórz hasło",
    "submit": "Zarejestruj się",
    "hasAccount": "Masz już konto?",
    "login": "Zaloguj się",
    "success": "Konto utworzone pomyślnie",
    "errors": {
      "usernameRequired": "Nazwa użytkownika jest wymagana",
      "usernameLength": "Nazwa użytkownika musi mieć od 3 do 50 znaków",
      "usernameFormat": "Nazwa użytkownika może zawierać tylko litery, cyfry, kropki, podkreślenia i myślniki",
      "emailRequired": "Adres email jest wymagany",
      "emailFormat": "Wprowadź poprawny adres email",
      "passwordRequired": "Hasło jest wymagane",
      "passwordLength": "Hasło musi mieć co najmniej 8 znaków",
      "confirmPasswordRequired": "Potwierdzenie hasła jest wymagane",
      "passwordsNotMatch": "Hasła nie są identyczne",
      "usernameTaken": "Ta nazwa użytkownika jest już zajęta",
      "emailTaken": "Ten adres email jest już zarejestrowany"
    }
  },
  "errors": {
    "serverError": "Wystąpił błąd serwera. Spróbuj ponownie później",
    "networkError": "Brak połączenia z serwerem. Sprawdź połączenie internetowe",
    "timeout": "Żądanie przekroczyło limit czasu. Spróbuj ponownie"
  }
}
```

### Krok 5: Implementacja komponentu PasswordStrengthHint (opcjonalnie)
1. Utwórz `components/auth/PasswordStrengthHint.vue`
2. Zdefiniuj props `password: string`
3. Utwórz computed property sprawdzające wymagania
4. Zbuduj UI z listą wymagań i ikonami (check/x)

### Krok 6: Implementacja logiki walidacji w RegisterView
1. Utwórz reactive refs dla `formData`, `fieldErrors`, `isSubmitting`
2. Zaimplementuj funkcję `validateField(fieldName)` dla każdego pola:
   - Username: długość 3-50, regex
   - Email: format email
   - Password: min 8 znaków
   - ConfirmPassword: zgodność z password
3. Zaimplementuj funkcję `validateForm()` walidującą wszystkie pola
4. Dodaj funkcję `clearFieldError(fieldName)` czyszczącą błąd przy wpisywaniu

### Krok 7: Budowa struktury HTML formularza
1. Użyj `AuthFormLayout` jako wrappera
2. Dodaj element `<form @submit.prevent="submitForm">`
3. Dla każdego pola użyj `BaseInput`:
```vue
<BaseInput
  v-model="formData.username"
  :label="t('register.username')"
  type="text"
  :error="fieldErrors.username"
  @blur="validateField('username')"
  @input="clearFieldError('username')"
  autocomplete="username"
/>
```
4. Dodaj PasswordStrengthHint pod polem password (jeśli implementujesz)
5. Dodaj przycisk submit z obsługą stanu loading
6. Dodaj link do strony logowania

### Krok 8: Implementacja funkcji submitForm
1. Wywołaj `validateForm()` - jeśli błędy, zatrzymaj
2. Ustaw `isSubmitting.value = true`
3. Przygotuj obiekt `RegisterRequestDTO` (bez confirmPassword)
4. Wywołaj `authStore.register(requestData)` w bloku try-catch
5. Obsłuż sukces:
   - Wyświetl toast sukcesu
   - Przekieruj na `/login`
6. Obsłuż błędy:
   - 400: mapuj błędy na `fieldErrors`
   - 409: sprawdź kod i ustaw błąd pod odpowiednim polem
   - 500+: wyświetl toast z błędem ogólnym
   - Network error: wyświetl toast o braku połączenia
7. W finally: ustaw `isSubmitting.value = false`

### Krok 9: Stylowanie z Tailwind CSS
1. Użyj klas Tailwind dla:
   - Layout: `max-w-md mx-auto p-6`
   - Spacing: `space-y-4`
   - Przycisk submit: `w-full bg-primary text-white disabled:opacity-50`
   - Link: `text-primary hover:underline`
2. Upewnij się, że komponenty BaseInput i InlineError mają odpowiednie style dla stanów błędu

### Krok 10: Obsługa stanów UI
1. Dodaj spinner lub tekst loading w przycisku podczas `isSubmitting`
2. Wyłącz wszystkie pola podczas submitu (opcjonalnie)
3. Dodaj autofocus na pierwszym polu
4. Dodaj focus na pierwszym polu z błędem po nieudanej walidacji

### Krok 11: Testy manualne
1. Test wszystkich warunków walidacji klienta
2. Test submitu z poprawnymi danymi (sprawdź redirect i toast)
3. Test błędu 409 USERNAME_TAKEN (użyj tego samego username dwa razy)
4. Test błędu 409 EMAIL_TAKEN (użyj tego samego email dwa razy)
5. Test błędów sieciowych (wyłącz serwer)
6. Test responsywności na różnych urządzeniach

### Krok 12: Testy jednostkowe (opcjonalnie, ale zalecane)
1. Test walidacji pól (`validateField`)
2. Test walidacji całego formularza (`validateForm`)
3. Test mapowania błędów serwera
4. Test obsługi różnych kodów odpowiedzi API
5. Mock wywołań API i test flow sukcesu/błędu

### Krok 13: Accessibility (A11y)
1. Upewnij się, że wszystkie pola mają odpowiednie `label`
2. Dodaj `aria-invalid="true"` dla pól z błędami
3. Dodaj `aria-describedby` łączące pole z komunikatem błędu
4. Sprawdź nawigację klawiaturą (Tab)
5. Sprawdź z screen readerem

### Krok 14: Optymalizacja i finalizacja
1. Upewnij się, że nie ma console.log w produkcji
2. Dodaj lazy loading dla komponentów, które nie są krytyczne
3. Zoptymalizuj regex i walidacje dla wydajności
4. Dodaj komentarze w kodzie dla skomplikowanych logik
5. Sprawdź zgodność z wytycznymi projektu (lint, prettier)

### Krok 15: Dokumentacja
1. Dodaj komentarze JSDoc dla funkcji publicznych
2. Zaktualizuj dokumentację projektu o nowy widok
3. Dodaj screenshot widoku do dokumentacji (opcjonalnie)

---

## Uwagi końcowe

- **Prostota**: MVP zakłada prostotę - nie dodawaj zbędnych funkcji
- **Spójność**: Użyj istniejących komponentów (AuthFormLayout, BaseInput, InlineError) dla spójności UI
- **Bezpieczeństwo**: Nigdy nie loguj haseł, używaj HTTPS, waliduj po stronie serwera
- **UX**: Wyświetlaj błędy inline, nie blokuj użytkownika długimi komunikatami
- **I18n**: Wszystkie teksty przez system tłumaczeń, gotowe na przyszłą wielojęzyczność
- **Testowanie**: Testuj edge cases (bardzo długie dane, specjalne znaki, etc.)
