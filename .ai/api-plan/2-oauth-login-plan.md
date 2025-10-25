# API Endpoint Implementation Plan: POST /api/v1/auth/login

## 1. Przegląd punktu końcowego
Endpoint służy do uwierzytelnienia użytkownika poprzez weryfikację podanych danych logowania. W przypadku poprawnych danych serwer generuje i zwraca token JWT, który jest zapisywany w HttpOnly secure cookie. Token NIE jest dołączany do ciała odpowiedzi JSON ze względów bezpieczeństwa.

## 2. Szczegóły żądania
- **Metoda HTTP:** POST
- **Adres URL:** /api/v1/auth/login
- **Parametry:**
  - **Wymagane:**
    - `username` (string, 3-50 znaków): Nazwa użytkownika (case-sensitive)
    - `password` (string, 8-128 znaków): Hasło użytkownika
  - **Opcjonalne:** Brak
- **Request Body (JSON):**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

## 3. Wykorzystywane typy
- **Command Model:** `LoginCommand` (dataclass z `slots=True`)
- **DTO:** `UserRefDTO`, `LoginSuccessDTO` (bez tokena w ciele odpowiedzi)
- **Exceptions:** `LoginValidationError`, `InvalidCredentialsError`

## 4. Szczegóły odpowiedzi
- **Sukces (200):**
  ```json
  {
    "user": {
      "id": 123,
      "username": "user123",
      "email": "user@example.com"
    }
  }
  ```
  **Headers:**
  ```
  Set-Cookie: jwt_token=<jwt>; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=86400
  ```
  
- **Błędy:**
  - **400 BAD_REQUEST (LoginValidationError):**
    ```json
    {
      "errors": {
        "username": ["This field is required."],
        "password": ["Ensure this field has at least 8 characters."]
      }
    }
    ```
  - **401 UNAUTHORIZED (InvalidCredentialsError):**
    ```json
    {
      "detail": "Invalid username or password."
    }
    ```
  - **429 TOO_MANY_REQUESTS:** Przekroczono limit prób logowania (rate limiting)
  - **500 INTERNAL_SERVER_ERROR:** Błąd po stronie serwera

## 5. Przepływ danych
1. Klient wysyła żądanie POST z danymi `username` i `password` w ciele żądania.
2. **LoginSerializer** waliduje dane wejściowe:
   - Sprawdza obecność wymaganych pól
   - Waliduje długość username (3-50) i password (8-128)
   - Stosuje `trim_whitespace=True` dla username
   - Konwertuje dane do `LoginCommand` przez metodę `to_command()`
3. **LoginService** wykonuje logikę biznesową:
   - Wyszukuje użytkownika po username (case-sensitive)
   - Sprawdza czy konto jest aktywne
   - Weryfikuje hasło używając `user.check_password()`
   - W przypadku błędu rzuca `InvalidCredentialsError` (nigdy nie ujawnia czy problem jest w username czy password)
4. **TokenProvider** generuje JWT:
   - Tworzy token z payload: user_id, username, exp
   - Konfiguracja: HS256, 24h ważności
5. **LoginView** ustawia odpowiedź:
   - Konwertuje `LoginSuccessDTO` do JSON przez `asdict()`
   - Ustawia HttpOnly secure cookie z tokenem
   - Zwraca 200 z danymi użytkownika (bez tokena w body)
6. Odpowiedź jest wysyłana do klienta.

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie/Autoryzacja:** Weryfikacja danych przy użyciu `user.check_password()` z Django.
- **Bezpieczeństwo danych:** 
  - Hasła nigdy nie są logowane ani zwracane w odpowiedziach
  - Porównanie z haszami w bazie danych (PBKDF2 SHA256)
  - Komunikaty błędów są ogólne ("Invalid username or password") aby uniemożliwić enumerację użytkowników
- **Tokeny JWT:** 
  - Token TYLKO w HttpOnly secure cookie (nie w body response)
  - Atrybuty cookie: `HttpOnly`, `Secure` (HTTPS), `SameSite=Strict`
  - Czas życia: 24h (konfigurowalny)
  - Algorytm: HS256
- **Rate Limiting:** WYMAGANE - implementacja throttling dla endpointu:
  - 5 prób / minutę dla pojedynczego IP
  - 10 prób / minutę dla pojedynczego username
  - Użycie DRF throttling classes lub django-ratelimit
- **Timing attacks:** Użycie stałego czasu odpowiedzi niezależnie od powodu błędu
- **HTTPS:** Wymóg w produkcji (Secure cookie flag)

## 7. Obsługa błędów
- **LoginValidationError (400):** 
  - Rzucany przez serializer przy błędach walidacji pól
  - Zawiera dict z errors per field
  - Mapowany w widoku na `Response({"errors": exc.errors}, status=400)`
  
- **InvalidCredentialsError (401):**
  - Rzucany przez LoginService gdy:
    - Użytkownik nie istnieje
    - Hasło jest nieprawidłowe
    - Konto jest nieaktywne
  - Zawsze ten sam komunikat: "Invalid username or password."
  - Mapowany w widoku na `Response({"detail": exc.message}, status=401)`
  
- **IntegrityError / DatabaseError (500):**
  - Nieoczekiwane błędy bazy danych
  - Logowane z pełnym traceback
  - Zwracane jako ogólny 500 bez szczegółów

## 7.1. Dedykowane wyjątki (account/exceptions.py)
```python
class LoginValidationError(Exception):
    """Raised when login data fails validation before authentication."""
    def __init__(self, errors: Mapping[str, list[str]]) -> None:
        super().__init__("Invalid login data.")
        self.errors = errors

class InvalidCredentialsError(Exception):
    """Raised when username/password combination is invalid or account inactive."""
    def __init__(self, message: str = "Invalid username or password.") -> None:
        super().__init__(message)
        self.message = message
```

## 8. Rozważenia dotyczące wydajności
- **Zapytania DB:** Jedno zapytanie `User.objects.filter(username=...).first()` - username ma index
- **Cache:** Rozważyć cache dla nieudanych prób logowania (przeciw brute-force)
- **Token generation:** JWT signing jest szybkie (HS256), ale można cache'ować konfigurację
- **Rate limiting:** Użycie Redis/Memcached dla throttling counters (szybsze niż DB)
- **Monitoring:** Logowanie metryk (czas odpowiedzi, failed login attempts) dla analizy wydajności

## 9. Struktura plików
```
backend/account/
├── exceptions.py                              # +LoginValidationError, +InvalidCredentialsError
├── serializers/
│   ├── login.py                              # NOWY: LoginSerializer z to_command()
│   └── tests/
│       └── test_login_serializer.py          # NOWY: testy serializera
├── services/
│   ├── login_service.py                      # NOWY: LoginService z execute()
│   ├── token_provider.py                     # NOWY: TokenProvider dla JWT
│   └── tests/
│       ├── test_login_service.py             # NOWY: testy serwisu
│       └── test_token_provider.py            # NOWY: testy providera
├── views/
│   ├── login.py                              # NOWY: LoginView (APIView)
│   └── tests/
│       └── test_login_view.py                # NOWY: testy API
└── urls.py                                    # +path('login/', LoginView.as_view())

backend/datastore/domains/
└── account_dto.py                             # LoginCommand, LoginSuccessDTO już istnieją

backend/config/
└── jwt_config.py                              # NOWY: konfiguracja JWT (SECRET_KEY, ALGORITHM, EXP)
```

## 10. Etapy wdrożenia
### Krok 1: Przygotowanie modeli danych i wyjątków
- [ ] Dodać `LoginValidationError` i `InvalidCredentialsError` do `account/exceptions.py`
- [ ] Zweryfikować obecność `LoginCommand` i `LoginSuccessDTO` w `datastore/domains/account_dto.py`
- [ ] Utworzyć `config/jwt_config.py` z konfiguracją (SECRET_KEY, ALGORITHM='HS256', EXPIRATION=86400)

### Krok 2: TokenProvider (infrastruktura)
- [ ] Utworzyć `account/services/token_provider.py`:
  - Metoda `generate_token(user_id: int, username: str) -> str`
  - Użycie biblioteki `PyJWT`
  - Payload: `{"user_id": ..., "username": ..., "exp": ...}`
- [ ] Dodać testy `account/services/tests/test_token_provider.py`:
  - Test generowania tokena
  - Test dekodowania tokena
  - Test wygasłego tokena
  - Test nieprawidłowego tokena

### Krok 3: Serializer
- [ ] Utworzyć `account/serializers/login.py`:
  - `LoginSerializer(serializers.Serializer)`
  - Pola: `username` (CharField, 3-50, trim_whitespace), `password` (CharField, 8-128, write_only)
  - Metoda `to_command() -> LoginCommand`
- [ ] Dodać testy `account/serializers/tests/test_login_serializer.py`:
  - Test poprawnych danych
  - Test brakujących pól (username, password)
  - Test za krótkiego username (<3) i password (<8)
  - Test za długiego username (>50) i password (>128)
  - Test whitespace w username (powinien być trim)
  - Test `to_command()` konwersji

### Krok 4: Service Layer
- [ ] Utworzyć `account/services/login_service.py`:
  - `LoginService.execute(command: LoginCommand) -> UserRefDTO`
  - `_authenticate_user(username, password)` - zwraca User lub rzuca InvalidCredentialsError
  - Sprawdzenie `user.is_active`
  - Użycie `user.check_password()`
  - Zwracanie `UserRefDTO` (bez created_at)
- [ ] Dodać testy `account/services/tests/test_login_service.py`:
  - Test poprawnego logowania
  - Test nieistniejącego użytkownika
  - Test nieprawidłowego hasła
  - Test nieaktywnego użytkownika (is_active=False)
  - Test case-sensitivity username
  - Test whitespace w username

### Krok 5: View Layer
- [ ] Utworzyć `account/views/login.py`:
  - `LoginView(APIView)` z metodą `post()`
  - Walidacja przez LoginSerializer
  - Delegacja do LoginService
  - Generacja tokena przez TokenProvider
  - Ustawienie HttpOnly secure cookie
  - Zwracanie `LoginSuccessDTO` przez `asdict()` (bez tokena w body)
  - Mapowanie wyjątków: LoginValidationError→400, InvalidCredentialsError→401
- [ ] Dodać URL w `account/urls.py`: `path('login/', LoginView.as_view(), name='login')`
- [ ] Dodać testy `account/views/tests/test_login_view.py`:
  - Test poprawnego logowania (200, cookie ustawione, poprawne dane w body)
  - Test błędów walidacji (400)
  - Test nieprawidłowych credentials (401)
  - Test nieaktywnego użytkownika (401)
  - Test cookie attributes (HttpOnly, Secure, SameSite)
  - Test braku tokena w response body

### Krok 6: Rate Limiting
- [ ] Dodać throttling class do `LoginView`:
  - `throttle_classes = [LoginRateThrottle]`
  - Konfiguracja: 5/min per IP, 10/min per username
- [ ] Dodać test przekroczenia limitu (429)

### Krok 7: Testy end-to-end
- [ ] Uruchomić `./bin/test_backend.sh` - coverage min. 90%
- [ ] Uruchomić `./bin/lint_backend.sh` - zero błędów
- [ ] (Opcjonalnie) Testy Cypress dla flow logowania

### Krok 8: Dokumentacja i Review
- [ ] Zaktualizować README.md z opisem endpointu
- [ ] Code review
- [ ] Merge do development

## 11. Scenariusze testowe (szczegółowe)
### Serializer Tests (`test_login_serializer.py`)
- `test_valid_data_creates_command`
- `test_missing_username_raises_validation_error`
- `test_missing_password_raises_validation_error`
- `test_username_too_short_raises_validation_error`
- `test_username_too_long_raises_validation_error`
- `test_password_too_short_raises_validation_error`
- `test_password_too_long_raises_validation_error`
- `test_username_whitespace_is_trimmed`
- `test_to_command_without_validation_raises_assertion_error`

### Service Tests (`test_login_service.py`)
- `test_successful_login_returns_user_ref_dto`
- `test_nonexistent_username_raises_invalid_credentials`
- `test_incorrect_password_raises_invalid_credentials`
- `test_inactive_user_raises_invalid_credentials`
- `test_username_is_case_sensitive`
- `test_username_with_whitespace_fails`
- `test_returned_dto_excludes_sensitive_data`

### View Tests (`test_login_view.py`)
- `test_successful_login_returns_200_with_user_data`
- `test_successful_login_sets_httponly_cookie`
- `test_response_body_excludes_token`
- `test_cookie_has_secure_and_samesite_attributes`
- `test_validation_error_returns_400`
- `test_invalid_credentials_return_401`
- `test_inactive_user_returns_401`
- `test_rate_limit_exceeded_returns_429`
- `test_error_message_does_not_reveal_existence_of_username`

### Token Provider Tests (`test_token_provider.py`)
- `test_generate_valid_token`
- `test_decode_valid_token`
- `test_expired_token_raises_error`
- `test_invalid_signature_raises_error`
- `test_token_contains_required_claims`
