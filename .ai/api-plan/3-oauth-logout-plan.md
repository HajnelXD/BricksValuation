# API Endpoint Implementation Plan: POST /api/v1/auth/logout

## 1. Przegląd punktu końcowego
Endpoint służy do wylogowania uwierzytelnionego użytkownika poprzez usunięcie ciasteczka JWT. Operacja jest prostsza niż login - nie wymaga walidacji danych wejściowych ani delegacji do service layer. Endpoint wymaga jednak uwierzytelnienia, więc dostęp mają tylko zalogowani użytkownicy.

## 2. Szczegóły żądania
- **Metoda HTTP**: POST
- **Adres URL**: /api/v1/auth/logout
- **Parametry**:
  - **Wymagane**: Ważny token JWT w ciasteczku `jwt_token` (weryfikowany przez DRF authentication class)
  - **Opcjonalne**: Brak
- **Request Body**: Brak (empty body lub `{}`)
- **Headers**: 
  - `Cookie: jwt_token=<jwt>` (automatycznie wysyłane przez przeglądarkę)
  - Opcjonalnie: `Authorization: Bearer <jwt>` (jeśli implementujemy dual auth)

## 3. Wykorzystywane typy
- **Command Models**: Brak - operacja nie przyjmuje danych wejściowych
- **DTO Models**: Brak - odpowiedź 204 nie zawiera body
- **Service Layer**: `LogoutService` - serwis odpowiedzialny za logikę wylogowania (opcjonalna walidacja tokena, logowanie zdarzeń)
- **Exceptions**: 
  - `rest_framework.exceptions.NotAuthenticated` (wbudowany DRF) - użyty gdy brak tokena lub token nieprawidłowy
  - Nie wymaga dedykowanych custom exceptions

## 4. Szczegóły odpowiedzi
- **Sukces (204 No Content)**:
  - Status: 204
  - Body: Brak (empty response)
  - Headers:
    ```
    Set-Cookie: jwt_token=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0
    ```
    (ciasteczko z pustą wartością i natychmiastowym wygaśnięciem)

- **Błędy**:
  - **401 UNAUTHORIZED**: Wywołanie przez niezalogowanego użytkownika (brak tokena, nieprawidłowy token, wygasły token)
    ```json
    {
      "detail": "Authentication credentials were not provided."
    }
    ```
    lub
    ```json
    {
      "detail": "Given token not valid for any token type"
    }
    ```
  - **500 INTERNAL_SERVER_ERROR**: Nieoczekiwany błąd serwera (bardzo rzadki przypadek)

## 5. Przepływ danych
1. Klient wysyła żądanie POST do `/api/v1/auth/logout` z ciasteczkiem JWT (automatycznie przez przeglądarkę).
2. **DRF Authentication Middleware** (nowa klasa `JWTCookieAuthentication`) ekstrahuje token z ciasteczka `jwt_token`.
3. **TokenProvider** dekoduje i waliduje token:
   - Sprawdza sygnaturę (HMAC SHA256)
   - Weryfikuje czy nie wygasł (claim `exp`)
   - Ekstrahuje `user_id` z payload
4. **DRF Permission** (`IsAuthenticated`) sprawdza czy `request.user` jest uwierzytelniony.
5. **LogoutService** wykonuje logikę biznesową:
   - Opcjonalna walidacja tokena (sprawdzenie czy jest w poprawnym formacie)
   - Logowanie zdarzenia wylogowania (dla audytu/analytics)
   - Zwraca potwierdzenie sukcesu
6. **LogoutView** (APIView):
   - Deleguje do `LogoutService.execute(user_id, username)`
   - Tworzy Response z statusem 204
   - Wywołuje `response.delete_cookie()` aby usunąć ciasteczko JWT
   - Zwraca pustą odpowiedź
7. Przeglądarka otrzymuje nagłówek `Set-Cookie` z wygasłym ciasteczkiem i usuwa je ze storage.

**Uwaga**: LogoutService jest cienką warstwą - główna odpowiedzialność to audyt/logging, nie skomplikowana logika biznesowa.

## 6. Względy bezpieczeństwa
- **Uwierzytelnienie wymagane**: Endpoint wymaga `permission_classes = [IsAuthenticated]` - tylko zalogowani użytkownicy mogą się wylogować.
- **JWT Authentication Class**: Wymaga implementacji custom `JWTCookieAuthentication(BaseAuthentication)` która:
  - Ekstrahuje token z ciasteczka (`request.COOKIES.get(jwt_config.COOKIE_NAME)`)
  - Używa `TokenProvider.decode_token()` do walidacji
  - Ładuje użytkownika z DB przez `user_id` z tokena
  - Rzuca `AuthenticationFailed` dla nieprawidłowych tokenów
- **Cookie deletion security**: Ciasteczko jest usuwane z tymi samymi atrybutami bezpieczeństwa co przy ustawianiu:
  - `HttpOnly=True` - brak dostępu z JavaScript
  - `Secure=True` - tylko HTTPS (produkcja)
  - `SameSite=Strict` - ochrona przed CSRF
  - `Path=/` - dostępne dla całej aplikacji
  - `Max-Age=0` - natychmiastowe wygaśnięcie
- **Rate Limiting**: Pominięte w MVP - można dodać w przyszłości jeśli pojawią się problemy z abuse.
- **Token nie jest invalidowany po stronie serwera**: 
  - MVP nie implementuje token blacklist/denylist (stateless JWT)
  - Token pozostaje technicznie ważny do wygaśnięcia (24h)
  - Bezpieczeństwo opiera się na usunięciu cookie z przeglądarki
  - W przyszłości można dodać Redis blacklist dla wylogowanych tokenów
- **Brak CSRF concerns**: POST endpoint, ale ciasteczko jest `SameSite=Strict` więc CSRF jest mało prawdopodobne. DRF CSRF może być wyłączony dla JWT auth.

## 7. Obsługa błędów
- **401 UNAUTHORIZED (DRF NotAuthenticated)**:
  - Rzucany automatycznie przez DRF gdy:
    - Brak ciasteczka `jwt_token` w request
    - Token nieprawidłowy (błędna sygnatura)
    - Token wygasły
    - User z tokena nie istnieje w DB
  - Mapowany przez DRF exception handler na Response 401
  - Komunikat: `{"detail": "Authentication credentials were not provided."}`
  
- **500 INTERNAL_SERVER_ERROR**:
  - W praktyce bardzo rzadki - logout nie ma złożonej logiki
  - Możliwe scenariusze: błąd konfiguracji SECRET_KEY, błąd DB
  - Logowanie z traceback dla diagnostyki

**Nie wymaga custom exceptions** - używamy wbudowanych DRF exceptions (`NotAuthenticated`, `AuthenticationFailed`).

## 8. Rozważania dotyczące wydajności
- **Bardzo lekka operacja**: Logout to tylko:
  1. Dekodowanie JWT (crypto operation - ~0.1ms)
  2. Lookup użytkownika w DB (1 query z indexem na PK)
  3. Opcjonalne logowanie zdarzenia (może być asynchroniczne)
  4. Ustawienie nagłówka Set-Cookie
- **Brak DB writes dla MVP**: Nie zapisujemy faktu wylogowania do bazy (stateless)
- **Cache nie jest potrzebny**: Operacja jest już maksymalnie zoptymalizowana
- **Monitoring**: LogoutService może logować metryki wylogowań (timestamp, user_id) dla analytics używając Python logging

## 9. Struktura plików
```
backend/account/
├── authentication.py                          # NOWY: JWTCookieAuthentication class
├── services/
│   ├── logout_service.py                      # NOWY: LogoutService z execute()
│   ├── token_provider.py                      # ISTNIEJĄCY: używany przez authentication
│   └── tests/
│       ├── test_logout_service.py             # NOWY: testy serwisu
│       └── test_token_provider.py             # ISTNIEJĄCY
├── views/
│   ├── logout.py                              # NOWY: LogoutView (APIView)
│   └── tests/
│       └── test_logout_view.py                # NOWY: testy API
└── urls.py                                    # MODYFIKACJA: +path('auth/logout', LogoutView)

backend/config/
└── jwt_config.py                              # ISTNIEJĄCY: używany przez authentication
```

**Uwaga**: Logout NIE wymaga:
- Serializera (brak danych wejściowych)
- Command/DTO models (brak input/output data)
- Custom exceptions (używamy DRF wbudowanych)

**Logout WYMAGA**:
- Service layer (LogoutService) - zgodność z architekturą projektu, miejsce na audyt/logging

## 10. Etapy wdrożenia

### Krok 1: JWT Authentication Class (infrastruktura)
- [ ] Utworzyć `account/authentication.py`:
  - Klasa `JWTCookieAuthentication(BaseAuthentication)`
  - Metoda `authenticate(request)` zwraca `(user, token)` lub `None`
  - Ekstrahuje token z `request.COOKIES.get(jwt_config.COOKIE_NAME)`
  - Używa `TokenProvider.decode_token()` do walidacji
  - Ładuje użytkownika: `User.objects.get(id=payload['user_id'])`
  - Rzuca `AuthenticationFailed` dla błędów
- [ ] Dodać do `settings.py`:
  ```python
  REST_FRAMEWORK = {
      'DEFAULT_AUTHENTICATION_CLASSES': [
          'account.authentication.JWTCookieAuthentication',
      ],
  }
  ```
- [ ] Dodać testy `account/tests/test_authentication.py`:
  - Test poprawnego tokena w cookie → zwraca (user, token)
  - Test braku cookie → zwraca None
  - Test nieprawidłowego tokena → rzuca AuthenticationFailed
  - Test wygasłego tokena → rzuca AuthenticationFailed
  - Test nieistniejącego user_id → rzuca AuthenticationFailed
  - Test tokena w header `Authorization: Bearer <jwt>` (opcjonalnie)

### Krok 2: Service Layer
- [ ] Utworzyć `account/services/logout_service.py`:
  - Klasa `LogoutService` z metodą `execute(user_id: int, username: str) -> None`
  - Logika:
    - Opcjonalna walidacja (np. sprawdzenie czy user istnieje - już zrobione przez auth)
    - Logowanie zdarzenia: `logger.info(f"User {username} (ID: {user_id}) logged out")`
    - Zwraca None (success)
  - Brak złożonej logiki biznesowej - głównie audyt
- [ ] Dodać testy `account/services/tests/test_logout_service.py`:
  - Test poprawnego wykonania (zwraca None)
  - Test logowania zdarzenia (mock logger, verify call)
  - Test z nieistniejącym user_id (opcjonalnie - może rzucić wyjątek lub ignore)

### Krok 3: View Layer
- [ ] Utworzyć `account/views/logout.py`:
  - `LogoutView(APIView)` z metodą `post()`
  - `permission_classes = [IsAuthenticated]`
  - Deleguje do `LogoutService.execute(request.user.id, request.user.username)`
  - Tworzy `Response(status=status.HTTP_204_NO_CONTENT)`
  - Wywołuje `response.delete_cookie()` z parametrami z `jwt_config`
  - Zwraca response
- [ ] Dodać URL w `account/urls.py`: 
  ```python
  path('auth/logout', LogoutView.as_view(), name='auth-logout'),
  ```
- [ ] Dodać testy `account/views/tests/test_logout_view.py`:
  - Test poprawnego wylogowania (204, cookie usunięte)
  - Test wylogowania bez uwierzytelnienia (401)
  - Test cookie attributes po delete (Max-Age=0, empty value)
  - Test że response nie ma body
  - Test że po wylogowaniu kolejne requesty z tym samym tokenem są odrzucane (token usunięty z cookie)
  - Test że LogoutService.execute() jest wywołane z poprawnymi parametrami (mock service)

### Krok 4: Integracja z istniejącymi endpoints
- [ ] Zweryfikować że `LoginView` nadal działa po dodaniu global authentication class
- [ ] Zweryfikować że `RegisterUserView` działa (powinien mieć `permission_classes = [AllowAny]`)
- [ ] Opcjonalnie dodać `authentication_classes = []` do publicznych endpoints jeśli global auth powoduje problemy

### Krok 5: Testy end-to-end i integracja
- [ ] Uruchomić `./bin/test_backend.sh` - coverage min. 90%
- [ ] Uruchomić `./bin/lint_backend.sh` - zero błędów
- [ ] Test ręczny flow: register → login → logout → próba dostępu do chronionego endpoint (401)
- [ ] (Opcjonalnie) Dodać testy Cypress dla flow wylogowania

### Krok 6: Dokumentacja i Review
- [ ] Zaktualizować README.md z opisem endpointu logout
- [ ] Dodać przykłady curl/http do dokumentacji
- [ ] Code review
- [ ] Merge do development

## 11. Scenariusze testowe (szczegółowe)

### Authentication Class Tests (`test_authentication.py`)
- `test_valid_token_in_cookie_returns_user_and_token`
- `test_missing_cookie_returns_none`
- `test_empty_cookie_returns_none`
- `test_invalid_token_signature_raises_authentication_failed`
- `test_expired_token_raises_authentication_failed`
- `test_malformed_token_raises_authentication_failed`
- `test_user_not_found_raises_authentication_failed`
- `test_inactive_user_raises_authentication_failed`
- `test_token_without_user_id_claim_raises_authentication_failed`

### Service Tests (`test_logout_service.py`)
- `test_execute_completes_successfully`
- `test_execute_logs_logout_event`
- `test_execute_with_valid_user_id_and_username`

### View Tests (`test_logout_view.py`)
- `test_authenticated_logout_returns_204_no_content`
- `test_authenticated_logout_deletes_cookie`
- `test_deleted_cookie_has_max_age_zero`
- `test_deleted_cookie_has_empty_value`
- `test_deleted_cookie_preserves_security_attributes`
- `test_response_body_is_empty`
- `test_unauthenticated_logout_returns_401`
- `test_logout_without_cookie_returns_401`
- `test_logout_with_expired_token_returns_401`
- `test_logout_with_invalid_token_returns_401`
- `test_after_logout_subsequent_requests_fail_authentication`
- `test_logout_calls_service_with_correct_user_data`

### Integration Tests (opcjonalnie w osobnym pliku)
- `test_full_flow_register_login_logout_access_protected_endpoint`
- `test_logout_doesnt_affect_other_users_sessions`
- `test_multiple_logouts_are_idempotent`

## 12. Przykłady użycia

### Sukces (204 No Content)
```bash
curl -X POST https://api.example.com/api/v1/auth/logout \
  -H "Cookie: jwt_token=eyJhbGc..." \
  -v

# Response:
# HTTP/1.1 204 No Content
# Set-Cookie: jwt_token=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0
```

### Błąd - brak uwierzytelnienia (401)
```bash
curl -X POST https://api.example.com/api/v1/auth/logout \
  -v

# Response:
# HTTP/1.1 401 Unauthorized
# Content-Type: application/json
# {
#   "detail": "Authentication credentials were not provided."
# }
```

### Błąd - wygasły token (401)
```bash
curl -X POST https://api.example.com/api/v1/auth/logout \
  -H "Cookie: jwt_token=expired_token_here" \
  -v

# Response:
# HTTP/1.1 401 Unauthorized
# Content-Type: application/json
# {
#   "detail": "Given token not valid for any token type"
# }
```

---

**KLUCZOWE RÓŻNICE vs LOGIN/REGISTER**: 
- Logout MA service layer (LogoutService) - zgodność z architekturą projektu, miejsce na audyt/logging
- Logout NIE ma serializera - brak danych wejściowych do walidacji
- Logout NIE ma Command/DTO - brak strukturyzowanych danych wejściowych/wyjściowych
- Logout WYMAGA nowej infrastruktury (JWT authentication class) której nie miały register/login
- JWT authentication class będzie używany przez WSZYSTKIE przyszłe chronione endpoints (np. `/auth/me`, `/bricksets/*`)
- Jest to jednorazowa inwestycja infrastrukturalna - po implementacji auth class, wszystkie kolejne chronione endpoints będą mogły go używać
- LogoutService jest cienką warstwą - głównie logging/audyt, nie skomplikowana logika biznesowa

Plan wdrożenia zapewnia zgodność ze standardami API, zasadami bezpieczeństwa oraz dobrymi praktykami implementacyjnymi przy wykorzystaniu Django REST Framework, zgodnie z już zrealizowanymi planami login i register.
