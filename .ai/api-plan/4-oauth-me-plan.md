# API Endpoint Implementation Plan: GET /api/v1/auth/me

## 1. Przegląd punktu końcowego
Endpoint służy do pobrania profilu aktualnie uwierzytelnionego użytkownika. Głównym celem jest umożliwienie klientom aplikacji uzyskania danych swojego konta (id, username, email, created_at). Endpoint wymaga uwierzytelnienia przez JWT token w ciasteczku HttpOnly. Jest to prosty read-only endpoint który wykorzystuje istniejącą infrastrukturę JWT authentication z logout endpoint.

## 2. Szczegóły żądania
- **Metoda HTTP**: GET
- **Adres URL**: /api/v1/auth/me
- **Parametry**:
  - **Wymagane**: Ważny token JWT w ciasteczku `jwt_token` (weryfikowany przez `JWTCookieAuthentication`)
  - **Opcjonalne**: Brak
- **Request Body**: Brak (endpoint GET)
- **Headers**: 
  - `Cookie: jwt_token=<jwt>` (automatycznie wysyłane przez przeglądarkę)

## 3. Wykorzystywane typy
- **Command Models**: Brak - endpoint nie przyjmuje danych wejściowych
- **DTO Models**: 
  - `UserProfileDTO` (dataclass z `slots=True`) - pełny profil użytkownika: id, username, email, created_at
  - Zwracany przez `UserProfileService.get_profile(user_id: int) -> UserProfileDTO`
- **Service Layer**: `UserProfileService` - serwis odpowiedzialny za pobranie danych użytkownika i mapowanie do DTO
- **Serializer**: `UserProfileSerializer` - serializuje `UserProfileDTO` do JSON (read-only, bez walidacji input)
- **Exceptions**: 
  - `rest_framework.exceptions.NotAuthenticated` (wbudowany DRF) - użyty gdy brak tokena
  - Nie wymaga dedykowanych custom exceptions

## 4. Szczegóły odpowiedzi
- **Sukces (200 OK)**:
  ```json
  {
    "id": 123,
    "username": "user123",
    "email": "user@example.com",
    "created_at": "2025-10-21T12:34:56Z"
  }
  ```

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
  - **404 NOT_FOUND**: Użytkownik z tokena nie istnieje w bazie (bardzo rzadki przypadek - token ważny ale user usunięty)
    ```json
    {
      "detail": "User not found."
    }
    ```
  - **500 INTERNAL_SERVER_ERROR**: Nieoczekiwany błąd serwera

## 5. Przepływ danych
1. Klient wysyła żądanie GET do `/api/v1/auth/me` z ciasteczkiem JWT (automatycznie przez przeglądarkę).
2. **JWTCookieAuthentication** (już zaimplementowany dla logout) ekstrahuje token z ciasteczka `jwt_token`.
3. **TokenProvider** dekoduje i waliduje token:
   - Sprawdza sygnaturę (HMAC SHA256)
   - Weryfikuje czy nie wygasł (claim `exp`)
   - Ekstrahuje `user_id` z payload
4. **DRF Permission** (`IsAuthenticated`) sprawdza czy `request.user` jest uwierzytelniony.
5. **UserProfileService** wykonuje logikę biznesową:
   - Pobiera użytkownika z DB: `User.objects.get(id=user_id)`
   - Mapuje do `UserProfileDTO` z polami: id, username, email, created_at
   - Zwraca DTO
6. **UserProfileView** (APIView):
   - Deleguje do `UserProfileService.get_profile(request.user.id)`
   - Serializuje DTO przez `UserProfileSerializer`
   - Zwraca Response 200 z danymi użytkownika
7. Przeglądarka otrzymuje JSON z profilem użytkownika.

**Uwaga**: Endpoint korzysta z infrastruktury JWT authentication zaimplementowanej dla logout endpoint. Nie wymaga nowej infrastruktury.

## 6. Względy bezpieczeństwa
- **Uwierzytelnienie wymagane**: Endpoint wymaga `permission_classes = [IsAuthenticated]` - tylko zalogowani użytkownicy mogą pobrać swój profil.
- **JWT Authentication**: Używa istniejącej `JWTCookieAuthentication` class:
  - Ekstrahuje token z ciasteczka HttpOnly
  - Waliduje token przez `TokenProvider.decode_token()`
  - Ładuje użytkownika z DB
  - Rzuca `AuthenticationFailed` dla nieprawidłowych tokenów
- **Brak wrażliwych danych w odpowiedzi**: 
  - DTO NIE zawiera: password, is_superuser, is_staff, last_login, updated_at
  - Tylko: id, username, email, created_at
- **CORS**: Endpoint musi być dostępny dla frontend aplikacji (konfiguracja CORS w settings.py)
- **Rate Limiting**: Pominięte w MVP - endpoint read-only, niskie ryzyko abuse
- **User może pobrać TYLKO swój profil**: 
  - `request.user` jest ustawiony przez authentication class
  - Service używa `request.user.id` - brak możliwości pobrania cudzych danych
  - Nie ma parametru `user_id` w URL/query - automatyczna izolacja danych

## 7. Obsługa błędów
- **401 UNAUTHORIZED (DRF NotAuthenticated)**:
  - Rzucany automatycznie przez DRF gdy:
    - Brak ciasteczka `jwt_token` w request
    - Token nieprawidłowy (błędna sygnatura)
    - Token wygasły
  - Mapowany przez DRF exception handler na Response 401
  - Komunikat: `{"detail": "Authentication credentials were not provided."}`
  
- **404 NOT_FOUND**:
  - Rzucany przez Service gdy `User.objects.get(id=user_id)` nie znajdzie użytkownika
  - Bardzo rzadki przypadek: token ważny ale user usunięty z DB między login a /me
  - Mapowany w widoku na Response 404
  - Komunikat: `{"detail": "User not found."}`

- **500 INTERNAL_SERVER_ERROR**:
  - Możliwe scenariusze: błąd konfiguracji SECRET_KEY, błąd DB
  - Logowanie z traceback dla diagnostyki

**Nie wymaga custom exceptions** - używamy wbudowanych DRF exceptions (`NotAuthenticated`) i Django `User.DoesNotExist`.

## 8. Rozważania dotyczące wydajności
- **Bardzo lekka operacja**: 
  1. Dekodowanie JWT (crypto operation - ~0.1ms) - już zrobione przez authentication
  2. Lookup użytkownika w DB (1 query z indexem na PK)
  3. Mapowanie do DTO (w pamięci)
  4. Serializacja JSON (w pamięci)
- **Cache możliwy ale niepotrzebny w MVP**: 
  - Profil użytkownika rzadko się zmienia
  - Można cache'ować w przyszłości z TTL 5-15 min
  - Cache key: `user_profile:{user_id}`
- **Select only required fields**: Service używa `.only('id', 'username', 'email', 'created_at')` zamiast `select *`
- **Monitoring**: Service może logować metryki dostępu (timestamp, user_id) dla analytics

## 9. Struktura plików
```
backend/account/
├── authentication.py                          # ISTNIEJĄCY: JWTCookieAuthentication (z logout)
├── serializers/
│   ├── user_profile.py                        # NOWY: UserProfileSerializer (read-only)
│   └── tests/
│       └── test_user_profile_serializer.py    # NOWY: testy serializera
├── services/
│   ├── user_profile_service.py                # NOWY: UserProfileService z get_profile()
│   ├── token_provider.py                      # ISTNIEJĄCY: używany przez authentication
│   └── tests/
│       ├── test_user_profile_service.py       # NOWY: testy serwisu
│       └── test_token_provider.py             # ISTNIEJĄCY
├── views/
│   ├── user_profile.py                        # NOWY: UserProfileView (APIView)
│   └── tests/
│       └── test_user_profile_view.py          # NOWY: testy API
└── urls.py                                    # MODYFIKACJA: +path('auth/me', UserProfileView)

backend/datastore/domains/
└── account_dto.py                             # MODYFIKACJA: +UserProfileDTO

backend/config/
└── jwt_config.py                              # ISTNIEJĄCY: używany przez authentication
```

**Uwaga**: Endpoint wykorzystuje istniejącą infrastrukturę JWT authentication. Wymaga tylko:
- Service layer (UserProfileService) - logika pobrania i mapowania danych
- Serializer (UserProfileSerializer) - serializacja DTO do JSON (read-only)
- View (UserProfileView) - delegacja do service i zwrócenie response
- DTO (UserProfileDTO) - struktura danych wyjściowych

## 10. Etapy wdrożenia

### Krok 1: DTO Model
- [ ] Dodać do `datastore/domains/account_dto.py`:
  ```python
  @dataclass(slots=True)
  class UserProfileDTO:
      """Full user profile data transfer object."""
      source_model = "account.User"
      
      id: int
      username: str
      email: str
      created_at: datetime
  ```
- [ ] Dodać testy typu dla DTO (opcjonalnie - jeśli są testy dla innych DTO)

### Krok 2: Service Layer
- [ ] Utworzyć `account/services/user_profile_service.py`:
  - Klasa `UserProfileService` z metodą `get_profile(user_id: int) -> UserProfileDTO`
  - Logika:
    - Pobiera użytkownika: `User.objects.only('id', 'username', 'email', 'created_at').get(id=user_id)`
    - Mapuje do `UserProfileDTO`
    - Rzuca `User.DoesNotExist` jeśli user nie istnieje
    - Zwraca DTO
- [ ] Dodać testy `account/services/tests/test_user_profile_service.py`:
  - Test poprawnego pobrania profilu (zwraca DTO z poprawnymi polami)
  - Test nieistniejącego user_id (rzuca User.DoesNotExist)
  - Test że DTO nie zawiera wrażliwych pól (password, is_staff, etc.)
  - Test że używa `.only()` dla optymalizacji (mock/spy na ORM)

### Krok 3: Serializer
- [ ] Utworzyć `account/serializers/user_profile.py`:
  - `UserProfileSerializer` - read-only serializer
  - Podejście 1 (prosty dict serializer):
    ```python
    def serialize(dto: UserProfileDTO) -> dict:
        return asdict(dto)
    ```
  - Podejście 2 (DRF Serializer - jeśli potrzebna walidacja formatu):
    ```python
    class UserProfileSerializer(serializers.Serializer):
        id = serializers.IntegerField(read_only=True)
        username = serializers.CharField(read_only=True)
        email = serializers.EmailField(read_only=True)
        created_at = serializers.DateTimeField(read_only=True)
    ```
- [ ] Dodać testy `account/serializers/tests/test_user_profile_serializer.py`:
  - Test serializacji UserProfileDTO do dict/JSON
  - Test że wszystkie pola są read_only
  - Test formatu datetime (ISO 8601)

### Krok 4: View Layer
- [ ] Utworzyć `account/views/user_profile.py`:
  - `UserProfileView(APIView)` z metodą `get()`
  - `permission_classes = [IsAuthenticated]`
  - Deleguje do `UserProfileService.get_profile(request.user.id)`
  - Serializuje DTO przez serializer (lub `asdict()`)
  - Zwraca `Response(data, status=status.HTTP_200_OK)`
  - Obsługa `User.DoesNotExist` → Response 404
- [ ] Dodać URL w `account/urls.py`: 
  ```python
  path('auth/me', UserProfileView.as_view(), name='auth-me'),
  ```
- [ ] Dodać testy `account/views/tests/test_user_profile_view.py`:
  - Test poprawnego pobrania profilu (200, poprawne dane w body)
  - Test dostępu bez uwierzytelnienia (401)
  - Test z wygasłym tokenem (401)
  - Test z nieprawidłowym tokenem (401)
  - Test że zwrócone dane NIE zawierają password/is_staff/etc
  - Test że UserProfileService.get_profile() jest wywołane z request.user.id (mock service)
  - Test obsługi User.DoesNotExist (404)
  - Test że response ma Content-Type: application/json

### Krok 5: Testy end-to-end i integracja
- [ ] Uruchomić `./bin/test_backend.sh` - coverage min. 90%
- [ ] Uruchomić `./bin/lint_backend.sh` - zero błędów
- [ ] Test ręczny flow: register → login → /auth/me (200 z danymi) → logout → /auth/me (401)
- [ ] (Opcjonalnie) Dodać testy Cypress dla flow pobrania profilu

### Krok 6: Dokumentacja i Review
- [ ] Zaktualizować README.md z opisem endpointu /auth/me
- [ ] Dodać przykłady curl/http do dokumentacji
- [ ] Code review
- [ ] Merge do development

## 11. Scenariusze testowe (szczegółowe)

### Service Tests (`test_user_profile_service.py`)
- `test_get_profile_returns_user_profile_dto`
- `test_get_profile_with_valid_user_id`
- `test_get_profile_includes_all_required_fields`
- `test_get_profile_excludes_sensitive_fields`
- `test_get_profile_with_nonexistent_user_raises_does_not_exist`
- `test_get_profile_uses_only_for_query_optimization`
- `test_returned_dto_has_correct_types`

### Serializer Tests (`test_user_profile_serializer.py`)
- `test_serialize_user_profile_dto_to_dict`
- `test_serialized_data_contains_all_fields`
- `test_all_fields_are_read_only`
- `test_datetime_format_is_iso_8601`
- `test_serializer_does_not_modify_dto`

### View Tests (`test_user_profile_view.py`)
- `test_authenticated_user_gets_profile_returns_200`
- `test_response_contains_correct_user_data`
- `test_response_excludes_password_and_sensitive_fields`
- `test_unauthenticated_request_returns_401`
- `test_request_without_cookie_returns_401`
- `test_request_with_expired_token_returns_401`
- `test_request_with_invalid_token_returns_401`
- `test_nonexistent_user_returns_404`
- `test_response_content_type_is_json`
- `test_service_called_with_correct_user_id`
- `test_user_can_only_access_own_profile`

### Integration Tests (opcjonalnie w osobnym pliku)
- `test_full_flow_register_login_get_profile`
- `test_profile_after_logout_returns_401`
- `test_profile_data_matches_registration_data`
- `test_created_at_timestamp_is_accurate`

## 12. Przykłady użycia

### Sukces (200 OK)
```bash
curl -X GET https://api.example.com/api/v1/auth/me \
  -H "Cookie: jwt_token=eyJhbGc..." \
  -v

# Response:
# HTTP/1.1 200 OK
# Content-Type: application/json
# {
#   "id": 123,
#   "username": "user123",
#   "email": "user@example.com",
#   "created_at": "2025-10-21T12:34:56Z"
# }
```

### Błąd - brak uwierzytelnienia (401)
```bash
curl -X GET https://api.example.com/api/v1/auth/me \
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
curl -X GET https://api.example.com/api/v1/auth/me \
  -H "Cookie: jwt_token=expired_token_here" \
  -v

# Response:
# HTTP/1.1 401 Unauthorized
# Content-Type: application/json
# {
#   "detail": "Given token not valid for any token type"
# }
```

### Błąd - użytkownik nie istnieje (404)
```bash
curl -X GET https://api.example.com/api/v1/auth/me \
  -H "Cookie: jwt_token=valid_token_but_user_deleted" \
  -v

# Response:
# HTTP/1.1 404 Not Found
# Content-Type: application/json
# {
#   "detail": "User not found."
# }
```

---

**KLUCZOWE PUNKTY**: 
- Endpoint wykorzystuje istniejącą infrastrukturę JWT authentication z logout endpoint
- NIE wymaga serializera do walidacji input (GET endpoint, brak danych wejściowych)
- WYMAGA service layer (UserProfileService) - zgodność z architekturą projektu, separacja logiki
- WYMAGA serializer do output (UserProfileSerializer) - konwersja DTO do JSON
- WYMAGA nowego DTO (UserProfileDTO) - struktura z pełnym profilem (vs UserRefDTO z login)
- Prostszy niż login/logout - brak złożonej logiki biznesowej, tylko read operacja
- Bezpieczeństwo: user może pobrać TYLKO swój profil (automatyczna izolacja przez `request.user`)
- MVP nie wymaga cache - można dodać w przyszłości przy wysokim obciążeniu

Plan wdrożenia zapewnia zgodność ze standardami API, zasadami bezpieczeństwa oraz dobrymi praktykami implementacyjnymi przy wykorzystaniu Django REST Framework, zgodnie z już zrealizowanymi planami register, login i logout.
