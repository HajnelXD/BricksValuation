# API Endpoint Implementation Plan: POST /api/v1/bricksets

## 1. Przegląd punktu końcowego

Endpoint POST /api/v1/bricksets służy do tworzenia nowego rekordu BrickSet. Jego głównym celem jest przyjmowanie danych wejściowych z interfejsu API, walidacja danych oraz zapisanie nowego rekordu w bazie danych, przy jednoczesnym uwzględnieniu reguł biznesowych (np. unikalność kombinacji cech) i zabezpieczeń (uwierzytelnianie użytkownika).

**Wzorce implementacyjne**: Endpoint wykorzystuje te same wzorce co `POST /api/v1/auth/register`:
- Serializer z metodą `to_command()` dla walidacji i konwersji do Command
- Service layer z metodą `execute()` dla logiki biznesowej
- Domain exceptions dla kontrolowanych błędów
- APIView dla obsługi HTTP
- DTO dla strukturyzowanych odpowiedzi

## 2. Szczegóły żądania

- **Metoda HTTP:** POST
- **URL:** /api/v1/bricksets
- **Parametry (w treści żądania JSON):**
  - **Wymagane:**
    - `number` (liczba całkowita, max 7 cyfr, >=0)
    - `production_status` (łańcuch znaków, np. "ACTIVE" lub "RETIRED")
    - `completeness` (łańcuch znaków, np. "COMPLETE" lub "INCOMPLETE")
    - `has_instructions` (boolean)
    - `has_box` (boolean)
    - `is_factory_sealed` (boolean)
  - **Opcjonalne:**
    - `owner_initial_estimate` (liczba całkowita, > 0 i < 1000000)

Przykładowe żądanie:
```json
{
  "number": 12345,
  "production_status": "ACTIVE",
  "completeness": "COMPLETE",
  "has_instructions": true,
  "has_box": true,
  "is_factory_sealed": false,
  "owner_initial_estimate": 360
}
```

## 3. Wykorzystywane typy

- **Command Model:**
  - `CreateBrickSetCommand` (dataclass z `slots=True`, już zdefiniowany w `datastore/domains/catalog_dto.py`)
  - Pola: number, production_status, completeness, has_instructions, has_box, is_factory_sealed, owner_initial_estimate
  - Nie zawiera `owner_id` - właściciel pochodzи z kontekstu uwierzytelnienia (`request.user`)

- **DTO Model (odpowiedź):**
  - `BrickSetListItemDTO` (dataclass z `slots=True`, już zdefiniowany w `datastore/domains/catalog_dto.py`)
  - Używany zarówno w GET list jak i POST create response dla spójności API
  - Pola: id, number, production_status, completeness, has_instructions, has_box, is_factory_sealed, owner_id, owner_initial_estimate, valuations_count, total_likes, top_valuation, created_at, updated_at

- **Service Layer:**
  - `CreateBrickSetService` - nowa klasa z metodą `execute(command: CreateBrickSetCommand, owner: User) -> BrickSetListItemDTO`

- **Serializers:**
  - `CreateBrickSetSerializer` - walidacja input, konwersja do Command przez `to_command()`
  - `BrickSetListItemSerializer` - serializacja DTO do JSON (reużycie z GET endpoint)

- **Exceptions:**
  - `BrickSetDuplicateError` - domain exception dla naruszenia unikalności (wzór: `RegistrationConflictError`)
  - `BrickSetValidationError` - domain exception dla błędów walidacji (wzór: `RegistrationValidationError`)

## 4. Szczegóły odpowiedzi

- **Sukces (201 Created):**

  Przykładowa odpowiedź:
  ```json
  {
    "id": 10,
    "number": 12345,
    "production_status": "ACTIVE",
    "completeness": "COMPLETE",
    "has_instructions": true,
    "has_box": true,
    "is_factory_sealed": false,
    "owner_initial_estimate": 360,
    "owner_id": 42,
    "valuations_count": 0,
    "total_likes": 0,
    "top_valuation": null,
    "created_at": "2025-10-25T12:34:56.789Z",
    "updated_at": "2025-10-25T12:34:56.789Z"
  }
  ```

- **Błędy:**
  - **400 BAD_REQUEST (BrickSetValidationError):**
    ```json
    {
      "errors": {
        "number": ["Ensure this value is less than or equal to 9999999."],
        "owner_initial_estimate": ["Ensure this value is greater than 0."]
      }
    }
    ```
  - **409 CONFLICT (BrickSetDuplicateError):**
    ```json
    {
      "detail": "BrickSet with this combination already exists.",
      "constraint": "brickset_global_identity"
    }
    ```
  - **401 UNAUTHORIZED:** Gdy użytkownik nie jest zalogowany (brak JWT cookie lub token nieprawidłowy)
    ```json
    {
      "detail": "Authentication credentials were not provided."
    }
    ```

## 5. Przepływ danych

1. **Odbiór żądania:** Klient wysyła POST /api/v1/bricksets z JWT cookie authentication.
2. **Uwierzytelnianie:** `JWTCookieAuthentication` + `IsAuthenticated` permission sprawdza dostęp.
3. **Walidacja danych:** `CreateBrickSetSerializer` waliduje payload:
   - Walidacja typów, zakresów (number 0-9999999, owner_initial_estimate 1-999999)
   - Walidacja enum (production_status, completeness)
   - Walidacja boolean flags
4. **Mapowanie:** Serializer konwertuje dane do `CreateBrickSetCommand` przez `to_command()`.
5. **Logika biznesowa:** View wywołuje `CreateBrickSetService.execute(command, request.user)`:
   - Service buduje obiekt BrickSet z command + owner
   - Wywołuje `brickset.full_clean()` dla walidacji modelu (CHECK constraints)
   - Zapisuje w `transaction.atomic()`
   - Łapie `IntegrityError` dla unikalności → `BrickSetDuplicateError`
   - Buduje `BrickSetListItemDTO` z initial values (valuations_count=0, total_likes=0, top_valuation=None)
6. **Budowanie odpowiedzi:** View serializuje DTO przez `BrickSetListItemSerializer` lub `asdict()`.
7. **Reakcja na błędy:** 
   - `BrickSetValidationError` → 400 z errors dict
   - `BrickSetDuplicateError` → 409 z detail message
   - `AuthenticationFailed` → 401 (automatic DRF handling)

## 6. Względy bezpieczeństwa

- **Uwierzytelnianie:** Endpoint wymaga uwierzytelnienia (`permission_classes = [IsAuthenticated]`) - tylko zalogowani użytkownicy mogą tworzyć zestawy.
- **Authentication Method:** JWT z HttpOnly cookie (`JWTCookieAuthentication` jako DEFAULT_AUTHENTICATION_CLASSES).
- **Autoryzacja:** Owner zestawu ustawiany automatycznie na `request.user` - użytkownik nie może tworzyć zestawów dla innych użytkowników.
- **Walidacja:** 
  - Szczegółowa walidacja danych wejściowych na poziomie serializera (typy, zakresy, enum)
  - Model-level validators i CHECK constraints jako dodatkowa warstwa
  - Parametryzowane zapytania ORM zapobiegają SQL injection
- **Kontrola unikalności:** 
  - UniqueConstraint `brickset_global_identity` wymuszana przez DB
  - Service layer łapie `IntegrityError` i mapuje na czytelny komunikat błędu (nie ujawnia szczegółów implementacji DB)
- **Rate Limiting:** Rozważyć throttling dla endpoint (np. max 10 creates/minute per user) w przyszłości.
- **Input Sanitization:** DRF serializers automatycznie sanitize input (trim whitespace, validate types).

## 7. Obsługa błędów

- **400 BAD_REQUEST (BrickSetValidationError):**
  - Rzucany przez service gdy `full_clean()` wykryje błędy walidacji modelu
  - Zawiera dict errors: `{"field_name": ["Error message"]}`
  - Mapowany w view na Response 400
  - Przykładowe scenariusze:
    - number > 9999999 lub < 0
    - owner_initial_estimate <= 0 lub > 999999
    - production_status nie w [ACTIVE, RETIRED]
    - completeness nie w [COMPLETE, INCOMPLETE]

- **409 CONFLICT (BrickSetDuplicateError):**
  - Rzucany przez service gdy `IntegrityError` z constraint `brickset_global_identity`
  - Komunikat: "BrickSet with this combination already exists."
  - Mapowany w view na Response 409
  - Wskazuje duplikat kombinacji: (number, production_status, completeness, has_instructions, has_box, is_factory_sealed)

- **401 UNAUTHORIZED:**
  - Automatycznie rzucany przez DRF gdy brak JWT cookie lub token invalid/expired
  - Obsługiwany przez `JWTCookieAuthentication` + `IsAuthenticated` permission
  - Komunikat: "Authentication credentials were not provided."

- **500 INTERNAL_SERVER_ERROR:**
  - Dla niespodziewanych błędów (nie powinny wystąpić w normalnych warunkach)
  - Logowanie z traceback dla diagnostyki

## 8. Rozważania dotyczące wydajności

- **Single transaction:** Operacja zapisu w `transaction.atomic()` zapewnia atomowość.
- **Model validation:** `full_clean()` wykonywana in-memory przed zapisem - minimalizuje niepotrzebne zapisy do DB.
- **Constraint checking:** DB-level constraints (UniqueConstraint, CheckConstraint) zapewniają spójność nawet przy race conditions.
- **No N+1 problem:** Endpoint tworzy single object - brak potrzeby optymalizacji zapytań.
- **DTO initial values:** Nowo utworzony BrickSet ma `valuations_count=0`, `total_likes=0`, `top_valuation=None` - nie wymaga dodatkowych zapytań agregacyjnych.
- **Index usage:** `brickset_number_idx` przyspiesza sprawdzanie unikalności dla constraint checks.
- **Memory efficiency:** DTOs z `slots=True` redukują overhead pamięciowy.

## 9. Struktura plików

```
backend/catalog/
├── exceptions.py                              # NOWY: BrickSetDuplicateError, BrickSetValidationError
├── serializers/
│   ├── __init__.py                            # MODYFIKACJA: eksport CreateBrickSetSerializer
│   ├── brickset_list.py                       # ISTNIEJĄCY: BrickSetListItemSerializer (reużyty)
│   ├── brickset_create.py                     # NOWY: CreateBrickSetSerializer z to_command()
│   └── tests/
│       ├── test_brickset_list_serializer.py   # ISTNIEJĄCY
│       └── test_brickset_create_serializer.py # NOWY: testy CreateBrickSetSerializer
├── services/
│   ├── __init__.py                            # MODYFIKACJA: eksport CreateBrickSetService
│   ├── brickset_list_service.py               # ISTNIEJĄCY
│   ├── brickset_create_service.py             # NOWY: CreateBrickSetService z execute()
│   └── tests/
│       ├── test_brickset_list_service.py      # ISTNIEJĄCY
│       └── test_brickset_create_service.py    # NOWY: testy CreateBrickSetService
├── views/
│   ├── __init__.py                            # MODYFIKACJA: eksport CreateBrickSetView
│   ├── brickset_list.py                       # ISTNIEJĄCY: BrickSetListView
│   ├── brickset_create.py                     # NOWY: CreateBrickSetView (APIView)
│   └── tests/
│       ├── __init__.py                        # ISTNIEJĄCY
│       ├── test_brickset_list_view.py         # ISTNIEJĄCY
│       └── test_brickset_create_view.py       # NOWY: testy API
└── urls.py                                    # MODYFIKACJA: dodać routing POST

backend/datastore/domains/
└── catalog_dto.py                             # ISTNIEJĄCY: CreateBrickSetCommand, BrickSetListItemDTO

backend/catalog/models/
├── brickset.py                                # ISTNIEJĄCY: model BrickSet z constraints
└── __init__.py                                # ISTNIEJĄCY: eksport modeli
```

**Uwaga**: Endpoint wykorzystuje:
- **Istniejące modele i DTO** (BrickSet, CreateBrickSetCommand, BrickSetListItemDTO)
- **Istniejący serializer** dla response (BrickSetListItemSerializer z GET endpoint)
- **Nowe komponenty**: exceptions, create serializer, create service, create view
- **Wzorce z account app**: struktura service/serializer/view/exceptions identyczna jak w RegisterUserView

## 10. Etapy wdrożenia

### Krok 1: Domain Exceptions (infrastruktura błędów)
- [ ] Utworzyć `catalog/exceptions.py`:
  ```python
  """Domain exceptions for catalog operations."""
  
  class BrickSetValidationError(Exception):
      """Raised when BrickSet validation fails."""
      
      def __init__(self, errors: dict[str, list[str]]):
          self.errors = errors
          super().__init__(f"Validation failed: {errors}")
  
  class BrickSetDuplicateError(Exception):
      """Raised when BrickSet violates uniqueness constraint."""
      
      def __init__(self, constraint: str):
          self.constraint = constraint
          self.message = "BrickSet with this combination already exists."
          super().__init__(self.message)
  ```
- [ ] Dodać eksport w `catalog/__init__.py`

### Krok 2: Create Serializer
- [ ] Utworzyć `catalog/serializers/brickset_create.py`:
  - Klasa `CreateBrickSetSerializer(serializers.Serializer)`:
    - Pola: number, production_status, completeness, has_instructions, has_box, is_factory_sealed, owner_initial_estimate
    - Walidacje: IntegerField z min_value/max_value, ChoiceField dla enum, BooleanField
    - Metoda `to_command() -> CreateBrickSetCommand` (wzór: RegisterUserSerializer)
- [ ] Dodać testy `catalog/serializers/tests/test_brickset_create_serializer.py`:
  - `test_valid_data_all_fields` - wszystkie pola poprawne
  - `test_valid_data_minimal_fields` - tylko required fields
  - `test_invalid_number_too_large` - number > 9999999
  - `test_invalid_number_negative` - number < 0
  - `test_invalid_production_status` - nieprawidłowy enum
  - `test_invalid_completeness` - nieprawidłowy enum
  - `test_invalid_owner_initial_estimate_zero` - estimate = 0
  - `test_invalid_owner_initial_estimate_too_large` - estimate > 999999
  - `test_missing_required_field_number` - brak number
  - `test_missing_required_field_production_status` - brak production_status
  - `test_owner_initial_estimate_optional` - null jest OK
  - `test_to_command_creates_command_object` - sprawdza typ zwracany
  - `test_to_command_raises_without_validation` - AssertionError jeśli nie validated

### Krok 3: Create Service
- [ ] Utworzyć `catalog/services/brickset_create_service.py`:
  - Klasa `CreateBrickSetService`:
    - Metoda `execute(command: CreateBrickSetCommand, owner: User) -> BrickSetListItemDTO`
    - Logika:
      1. `_build_brickset(command, owner)` - tworzenie instance
      2. `_validate_brickset(brickset)` - `full_clean()` + catch DjangoValidationError → BrickSetValidationError
      3. `_persist_brickset(brickset)` - `transaction.atomic()` + catch IntegrityError → BrickSetDuplicateError
      4. `_build_dto(brickset)` - mapowanie do BrickSetListItemDTO z initial values
- [ ] Dodać testy `catalog/services/tests/test_brickset_create_service.py`:
  - **Sukces scenarios:**
    - `test_execute_creates_brickset_with_all_fields` - pełny payload
    - `test_execute_creates_brickset_without_estimate` - owner_initial_estimate=None
    - `test_execute_sets_owner_from_parameter` - sprawdza owner_id
    - `test_execute_returns_dto_with_initial_values` - valuations_count=0, total_likes=0, top_valuation=None
    - `test_execute_persists_to_database` - sprawdza BrickSet.objects.count()
  - **Walidacja errors:**
    - `test_execute_raises_validation_error_for_invalid_number` - number > max
    - `test_execute_raises_validation_error_for_invalid_estimate` - estimate = 0
  - **Duplicate errors:**
    - `test_execute_raises_duplicate_error_for_same_combination` - create 2x identyczne
    - `test_execute_allows_same_number_different_status` - number ten sam ale status inny OK
    - `test_execute_allows_same_number_different_completeness` - number ten sam ale completeness inny OK
  - **Transaction atomicity:**
    - `test_execute_rolls_back_on_integrity_error` - sprawdza że count nie wzrósł

### Krok 4: Create View
- [ ] Utworzyć `catalog/views/brickset_create.py`:
  - `CreateBrickSetView(APIView)` z metodą `post()`:
    - `permission_classes = [IsAuthenticated]`
    - Flow:
      1. Deserializacja i walidacja przez CreateBrickSetSerializer
      2. `serializer.to_command()`
      3. `service.execute(command, request.user)`
      4. Catch exceptions: BrickSetValidationError → 400, BrickSetDuplicateError → 409
      5. Serializacja DTO przez BrickSetListItemSerializer lub asdict()
      6. Return Response 201
- [ ] Dodać testy `catalog/views/tests/test_brickset_create_view.py`:
  - **Sukces:**
    - `test_post_creates_brickset_returns_201` - pełny payload, sprawdza status i response data
    - `test_post_creates_brickset_without_estimate` - owner_initial_estimate=None
    - `test_post_sets_owner_to_authenticated_user` - sprawdza owner_id w response
    - `test_post_persists_to_database` - sprawdza że rekord istnieje
    - `test_post_returns_dto_with_correct_structure` - sprawdza wszystkie pola response
  - **Validation errors:**
    - `test_post_validation_error_returns_400` - invalid number
    - `test_post_validation_error_missing_required_field` - brak number
    - `test_post_validation_error_invalid_enum` - invalid production_status
  - **Duplicate error:**
    - `test_post_duplicate_returns_409` - create 2x to samo
  - **Authentication:**
    - `test_post_requires_authentication` - bez JWT → 401
    - `test_post_with_valid_jwt_succeeds` - z JWT → 201
  - **Response format:**
    - `test_post_response_content_type_is_json` - Content-Type: application/json
    - `test_post_response_includes_all_dto_fields` - sprawdza struktur response

### Krok 5: URL Routing
- [ ] Zmodyfikować `catalog/urls.py`:
  ```python
  from catalog.views.brickset_create import CreateBrickSetView
  
  urlpatterns = [
      path("bricksets", BrickSetListView.as_view(), name="brickset-list"),  # GET
      path("bricksets", CreateBrickSetView.as_view(), name="brickset-create"),  # POST - ten sam URL!
  ]
  ```
  **UWAGA**: DRF automatycznie routuje GET vs POST do odpowiednich views. Alternatywnie użyć ViewSet lub kombinować w jednym view.
  
- [ ] **LEPSZE ROZWIĄZANIE**: Połączyć w jednym view class:
  ```python
  # W brickset_list.py:
  class BrickSetListView(GenericAPIView):
      def get(self, request): ...  # istniejący
      def post(self, request): ...  # nowy
  ```
  Albo utworzyć `BrickSetViewSet` jeśli będzie więcej metod (GET detail, PATCH, DELETE).

### Krok 6: Integration i Eksporty
- [ ] Zaktualizować `catalog/__init__.py` - eksport exceptions
- [ ] Zaktualizować `catalog/serializers/__init__.py` - eksport CreateBrickSetSerializer
- [ ] Zaktualizować `catalog/services/__init__.py` - eksport CreateBrickSetService
- [ ] Zaktualizować `catalog/views/__init__.py` - eksport CreateBrickSetView (jeśli separate view)

### Krok 7: Testy E2E i Walidacja
- [ ] Uruchomić `./bin/test_backend.sh` - coverage min. 90%
- [ ] Uruchomić `./bin/lint_backend.sh` - zero błędów
- [ ] Test ręczny flow:
  - POST /api/v1/bricksets bez auth → 401
  - POST /api/v1/bricksets z JWT, valid payload → 201
  - POST /api/v1/bricksets z invalid number → 400
  - POST /api/v1/bricksets duplicate → 409
  - GET /api/v1/bricksets → nowo utworzony set visible
- [ ] Sprawdzić liczba zapytań DB (powinno być 1-2 INSERT)

### Krok 8: Dokumentacja i Review
- [ ] Zaktualizować README.md z przykładami curl dla POST endpoint
- [ ] Code review
- [ ] Merge do development (branch: BV-12-Add-post-brickset lub similar)

## 11. Scenariusze testowe (szczegółowe)

### Serializer Tests (`test_brickset_create_serializer.py`)
- `test_valid_data_with_all_fields`
- `test_valid_data_with_minimal_required_fields`
- `test_valid_data_without_owner_initial_estimate`
- `test_number_within_valid_range_min`
- `test_number_within_valid_range_max`
- `test_invalid_number_exceeds_maximum`
- `test_invalid_number_negative`
- `test_invalid_production_status_not_in_choices`
- `test_invalid_completeness_not_in_choices`
- `test_owner_initial_estimate_within_valid_range`
- `test_invalid_owner_initial_estimate_zero`
- `test_invalid_owner_initial_estimate_negative`
- `test_invalid_owner_initial_estimate_exceeds_maximum`
- `test_missing_required_field_number`
- `test_missing_required_field_production_status`
- `test_missing_required_field_completeness`
- `test_missing_required_field_has_instructions`
- `test_missing_required_field_has_box`
- `test_missing_required_field_is_factory_sealed`
- `test_to_command_creates_correct_command_object`
- `test_to_command_includes_all_validated_fields`
- `test_to_command_raises_assertion_error_without_validation`

### Service Tests (`test_brickset_create_service.py`)
- `test_execute_successfully_creates_brickset_with_all_fields`
- `test_execute_successfully_creates_brickset_without_estimate`
- `test_execute_sets_correct_owner`
- `test_execute_returns_brickset_list_item_dto`
- `test_execute_dto_has_initial_aggregate_values`
- `test_execute_persists_brickset_to_database`
- `test_execute_raises_validation_error_for_invalid_number_range`
- `test_execute_raises_validation_error_for_invalid_estimate_range`
- `test_execute_raises_duplicate_error_for_identical_combination`
- `test_execute_allows_same_number_with_different_production_status`
- `test_execute_allows_same_number_with_different_completeness`
- `test_execute_allows_same_number_with_different_has_instructions`
- `test_execute_allows_same_number_with_different_has_box`
- `test_execute_allows_same_number_with_different_is_factory_sealed`
- `test_execute_transaction_rollback_on_integrity_error`
- `test_execute_formats_validation_errors_correctly`
- `test_execute_duplicate_error_includes_constraint_name`

### View Tests (`test_brickset_create_view.py`)
- `test_post_successfully_creates_brickset_returns_201`
- `test_post_creates_brickset_without_owner_initial_estimate`
- `test_post_sets_owner_to_authenticated_user`
- `test_post_response_includes_all_dto_fields`
- `test_post_persists_brickset_to_database`
- `test_post_validation_error_invalid_number_returns_400`
- `test_post_validation_error_missing_number_returns_400`
- `test_post_validation_error_invalid_production_status_returns_400`
- `test_post_validation_error_invalid_completeness_returns_400`
- `test_post_validation_error_invalid_estimate_returns_400`
- `test_post_duplicate_brickset_returns_409`
- `test_post_requires_authentication_returns_401_without_jwt`
- `test_post_with_valid_jwt_succeeds`
- `test_post_with_expired_jwt_returns_401`
- `test_post_response_content_type_is_json`
- `test_post_response_has_correct_structure`
- `test_post_new_brickset_visible_in_list_endpoint`

## 12. Przykłady użycia

### Sukces - utworzenie zestawu (201 Created)
```bash
# Najpierw login aby uzyskać JWT cookie
curl -X POST https://api.example.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user123", "password": "pass"}' \
  -c cookies.txt

# Następnie create brickset z JWT cookie
curl -X POST https://api.example.com/api/v1/bricksets \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "number": 12345,
    "production_status": "ACTIVE",
    "completeness": "COMPLETE",
    "has_instructions": true,
    "has_box": true,
    "is_factory_sealed": false,
    "owner_initial_estimate": 360
  }'

# Response:
# HTTP/1.1 201 Created
# Content-Type: application/json
# {
#   "id": 10,
#   "number": 12345,
#   "production_status": "ACTIVE",
#   "completeness": "COMPLETE",
#   "has_instructions": true,
#   "has_box": true,
#   "is_factory_sealed": false,
#   "owner_initial_estimate": 360,
#   "owner_id": 42,
#   "valuations_count": 0,
#   "total_likes": 0,
#   "top_valuation": null,
#   "created_at": "2025-10-25T12:34:56.789Z",
#   "updated_at": "2025-10-25T12:34:56.789Z"
# }
```

### Sukces - bez owner_initial_estimate (201 Created)
```bash
curl -X POST https://api.example.com/api/v1/bricksets \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "number": 67890,
    "production_status": "RETIRED",
    "completeness": "INCOMPLETE",
    "has_instructions": false,
    "has_box": false,
    "is_factory_sealed": false
  }'

# Response: 201 Created
# owner_initial_estimate: null w response
```

### Błąd - walidacja number (400 Bad Request)
```bash
curl -X POST https://api.example.com/api/v1/bricksets \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "number": 99999999,
    "production_status": "ACTIVE",
    "completeness": "COMPLETE",
    "has_instructions": true,
    "has_box": true,
    "is_factory_sealed": false
  }'

# Response:
# HTTP/1.1 400 Bad Request
# Content-Type: application/json
# {
#   "errors": {
#     "number": ["Ensure this value is less than or equal to 9999999."]
#   }
# }
```

### Błąd - walidacja estimate (400 Bad Request)
```bash
curl -X POST https://api.example.com/api/v1/bricksets \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "number": 12345,
    "production_status": "ACTIVE",
    "completeness": "COMPLETE",
    "has_instructions": true,
    "has_box": true,
    "is_factory_sealed": false,
    "owner_initial_estimate": 0
  }'

# Response:
# HTTP/1.1 400 Bad Request
# {
#   "errors": {
#     "owner_initial_estimate": ["Ensure this value is greater than or equal to 1."]
#   }
# }
```

### Błąd - duplikat (409 Conflict)
```bash
# Najpierw create
curl -X POST https://api.example.com/api/v1/bricksets \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "number": 12345,
    "production_status": "ACTIVE",
    "completeness": "COMPLETE",
    "has_instructions": true,
    "has_box": true,
    "is_factory_sealed": false
  }'
# Response: 201 Created

# Potem spróbuj create identical
curl -X POST https://api.example.com/api/v1/bricksets \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "number": 12345,
    "production_status": "ACTIVE",
    "completeness": "COMPLETE",
    "has_instructions": true,
    "has_box": true,
    "is_factory_sealed": false
  }'

# Response:
# HTTP/1.1 409 Conflict
# {
#   "detail": "BrickSet with this combination already exists.",
#   "constraint": "brickset_global_identity"
# }
```

### Błąd - brak uwierzytelnienia (401 Unauthorized)
```bash
curl -X POST https://api.example.com/api/v1/bricksets \
  -H "Content-Type: application/json" \
  -d '{
    "number": 12345,
    "production_status": "ACTIVE",
    "completeness": "COMPLETE",
    "has_instructions": true,
    "has_box": true,
    "is_factory_sealed": false
  }'

# Response:
# HTTP/1.1 401 Unauthorized
# {
#   "detail": "Authentication credentials were not provided."
# }
```

---

**KLUCZOWE PUNKTY**:
- Endpoint jest **authenticated only** (`IsAuthenticated`) - w przeciwieństwie do GET który jest `AllowAny`
- Wykorzystuje **istniejące DTO** (`BrickSetListItemDTO`) dla spójności z GET endpoint
- **Command object** (`CreateBrickSetCommand`) już zdefiniowany w `catalog_dto.py`
- **Service pattern** identyczny jak w `RegistrationService` (execute, domain exceptions, transaction.atomic)
- **Serializer pattern** identyczny jak w `RegisterUserSerializer` (to_command method)
- **View pattern** identyczny jak w `RegisterUserView` (APIView, catch exceptions, map to HTTP codes)
- **Domain exceptions** zamiast generic DRF exceptions dla kontrolowanych błędów
- **Transaction atomicity** zapewnia consistency przy race conditions
- **Initial DTO values**: nowo utworzony set ma valuations_count=0, total_likes=0, top_valuation=None
- Pre-commit: `./bin/lint_backend.sh` + `./bin/test_backend.sh` (coverage min. 90%)

Plan wdrożenia zapewnia zgodność ze standardami projektu, wzorcami z account app oraz dobrymi praktykami Django/DRF.