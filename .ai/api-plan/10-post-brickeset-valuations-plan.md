# API Endpoint Implementation Plan: POST /api/v1/bricksets/{brickset_id}/valuations

## 1. Przegląd punktu końcowego

Endpoint służy do utworzenia nowej wyceny (Valuation) dla istniejącego BrickSet. Użytkownik może utworzyć tylko jedną wycenę na BrickSet (enforced przez unique constraint). W przypadku pomyślnego wykonania, zwracany jest kod 201 z utworzonym obiektem ValuationDTO.

**Wzorce implementacyjne**: Endpoint wykorzystuje te same wzorce co inne catalog endpoints:
- Service layer z metodą `execute()` dla logiki biznesowej
- Domain exceptions (`ValuationDuplicateError`, `BrickSetNotFoundError`) dla kontrolowanych błędów
- Serializer z `to_command()` dla walidacji i konwersji do Command
- GenericAPIView dla obsługi HTTP (wzór: `BrickSetListView.post()`)
- ValuationDTO w response (201 Created)
- CreateValuationCommand z request body + path parameter
- IsAuthenticated permission (tylko zalogowani użytkownicy)

## 2. Szczegóły żądania

- **Metoda HTTP:** POST
- **URL:** /api/v1/bricksets/{brickset_id}/valuations
- **Parametry:**
  - **Path parameter (wymagany):**
    - `brickset_id` (int) – unikalny identyfikator BrickSetu (foreign key)
  - **Headers:** 
    - `Authorization: Token <jwt_token>` (wymagany - endpoint wymaga IsAuthenticated)
- **Request Body (JSON):**
  - **Wymagane:**
    - `value` (int) – wartość wyceny w zakresie 1..999999
  - **Opcjonalne:**
    - `currency` (string) – kod waluty, domyślnie 'PLN' (3 znaki)
    - `comment` (string) – opcjonalny komentarz do wyceny

Przykładowe żądanie:
```bash
POST /api/v1/bricksets/42/valuations
Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "value": 450,
  "currency": "PLN",
  "comment": "Looks complete and in great condition"
}
```


## 3. Wykorzystywane typy

- **Command Model:** 
  - `CreateValuationCommand` - już istniejący w `datastore/domains/valuation_dto.py`
    - Fields: `brickset_id: int`, `value: int`, `currency: Optional[str]`, `comment: Optional[str]`
    - Source model: `Valuation`

- **DTO Models:** 
  - `ValuationDTO` - już istniejący w `datastore/domains/valuation_dto.py`
    - Response zawiera: `id`, `brickset_id`, `user_id`, `value`, `currency`, `comment`, `likes_count`, `created_at`, `updated_at`
    - Source model: `Valuation`

- **Service Layer:**
  - `CreateValuationService` - nowa klasa z metodą `execute(command: CreateValuationCommand, user: User) -> ValuationDTO`
  - Wzór: `CreateBrickSetService` z `catalog/services/`

- **Serializers:**
  - `CreateValuationSerializer` - nowy serializer w `valuation/serializers/valuation_create.py`
    - Waliduje request body (value, currency, comment)
    - Metoda `to_command(brickset_id: int) -> CreateValuationCommand` - brickset_id z path param
  - `ValuationSerializer` - nowy serializer dla response (read-only) w `valuation/serializers/valuation_detail.py`
    - Serializuje ValuationDTO do JSON response

- **Exceptions (nowe w valuation/exceptions.py):**
  - `ValuationDuplicateError` - gdy użytkownik próbuje utworzyć drugą wycenę tego samego BrickSet
  - `BrickSetNotFoundError` - **reużycie** z `catalog.exceptions` (import)
  - `ValuationValidationError` - dla błędów walidacji modelu (analogia do BrickSetValidationError)

- **View:**
  - `BrickSetValuationsView` - nowy widok w `valuation/views/brickset_valuations.py`
    - GenericAPIView z metodą `post(request, brickset_id)`
    - Pattern: `BrickSetListView` z catalog

- **Models:**
  - `Valuation` - już istniejący w `valuation/models/valuation.py`
    - Unique constraint: `valuation_unique_user_brickset` (user, brickset)
    - ForeignKey do BrickSet z CASCADE
    - Check constraints dla value range i likes_count




## 4. Szczegóły odpowiedzi

- **Sukces (201 CREATED):**
  Valuation została pomyślnie utworzona. Response zawiera pełny obiekt ValuationDTO.

  ```json
  {
    "id": 77,
    "brickset_id": 42,
    "user_id": 99,
    "value": 450,
    "currency": "PLN",
    "comment": "Looks complete and in great condition",
    "likes_count": 0,
    "created_at": "2025-10-25T11:42:00.000Z",
    "updated_at": "2025-10-25T11:42:00.000Z"
  }
  ```

- **Błędy:**
  - **400 BAD REQUEST (Validation Error):**
    Błędy walidacji pól z serializera (DRF format).
    ```json
    {
      "value": ["Ensure this value is less than or equal to 999999."],
      "currency": ["Ensure this field has at most 3 characters."]
    }
    ```
    lub
    ```json
    {
      "value": ["This field is required."]
    }
    ```
  
  - **401 UNAUTHORIZED (Not Authenticated):**
    Automatycznie obsługiwany przez DRF `IsAuthenticated` permission.
    ```json
    {
      "detail": "Authentication credentials were not provided."
    }
    ```
  
  - **404 NOT_FOUND (BrickSetNotFoundError):**
    BrickSet o podanym ID nie istnieje.
    ```json
    {
      "detail": "BrickSet with id 999 not found."
    }
    ```

  - **409 CONFLICT (ValuationDuplicateError):**
    Użytkownik już stworzył wycenę dla tego BrickSet (uniqueness violation).
    ```json
    {
      "detail": "Valuation for this BrickSet already exists.",
      "constraint": "valuation_unique_user_brickset"
    }
    ```

  - **500 INTERNAL_SERVER_ERROR:**
    Dla niespodziewanych błędów (nie powinny wystąpić w normalnych warunkach).
    ```json
    {
      "detail": "An unexpected error occurred."
    }
    ```




## 5. Przepływ danych

1. **Odbiór żądania:** Klient wysyła POST /api/v1/bricksets/{brickset_id}/valuations z JWT token i JSON body.
2. **Routing:** Django route resolver kieruje do `BrickSetValuationsView.post(request, brickset_id)`.
3. **Autentykacja:** DRF middleware sprawdza JWT token (IsAuthenticated) → 401 jeśli brak/invalid.
4. **Walidacja path param:** DRF automatycznie waliduje że brickset_id jest intem (jeśli nie → 404).
5. **Walidacja request body:** View tworzy `CreateValuationSerializer(data=request.data)`:
   - Waliduje `value` (1..999999), `currency` (max 3 chars), `comment` (optional)
   - Jeśli błędy → zwraca 400 BAD REQUEST z DRF error format
6. **Konwersja do Command:** Serializer wywołuje `to_command(brickset_id)` → tworzy `CreateValuationCommand`
   - Command zawiera: `brickset_id` (z path), `value`, `currency` (default='PLN'), `comment`
7. **Logika biznesowa:** View wywołuje `CreateValuationService.execute(command, request.user)`:
   - Service weryfikuje czy BrickSet istnieje: `BrickSet.bricksets.get(pk=brickset_id)`
     - Jeśli nie znaleziono → rzuca `BrickSetNotFoundError`
   - Tworzy instancję Valuation: `Valuation(user=user, brickset=brickset, value=..., currency=..., comment=...)`
   - Zapisuje w `transaction.atomic()`:
     - Jeśli unique constraint violation (user + brickset) → rzuca `ValuationDuplicateError`
     - IntegrityError dla foreign key → re-raise (nie powinno się zdarzyć po weryfikacji)
   - Buduje ValuationDTO z zapisanego obiektu (z `likes_count=0`, timestamps)
8. **Response:** View serializuje ValuationDTO przez `ValuationSerializer` i zwraca 201 CREATED.
9. **Reakcja na błędy:** 
   - `BrickSetNotFoundError` → 404
   - `ValuationDuplicateError` → 409 z detail + constraint
   - `ValueError` (invalid brickset_id type) → 404 (DRF automatic)




## 6. Względy bezpieczeństwa

- **Uwierzytelnienie:** Endpoint wymaga autentykacji (`permission_classes = [IsAuthenticated]`) - tylko zalogowani użytkownicy.
- **Autoryzacja automatyczna:** Valuation automatycznie przypisywana do `request.user` - użytkownik nie może tworzyć wycen dla innych.
- **Uniqueness constraint:** Database-level unique constraint (user, brickset) zapobiega race conditions przy jednoczesnych requestach.
- **ForeignKey validation:** Service weryfikuje istnienie BrickSet przed persystencją (404 dla nieistniejącego set).
- **Ochrona danych:** 
  - Parametryzowane zapytania ORM zapobiegają SQL injection
  - DRF automatycznie waliduje typy parametrów URL i JSON payload
  - Currency validation (max 3 chars) zapobiega injection przez to pole
- **Atomowość:** Create wykonywany w `transaction.atomic()` dla spójności
- **Rate limiting:** Rozważyć throttling (np. max 10 valuations/hour per user) w przyszłości dla zapobiegania spam
- **Error disclosure:** 
  - 404 dla nieistniejącego BrickSetu nie ujawnia czy ID był kiedykolwiek używany
  - 409 dla duplikatu nie ujawnia szczegółów innych wycen
- **Input sanitization:** Comment field (TextField) nie ma length limitu w modelu - rozważyć dodanie MaxLengthValidator (np. 2000 chars) dla zapobiegania abuse
- **CSRF:** DRF automatycznie obsługuje CSRF dla session-based auth; JWT nie wymaga CSRF token
- **Signal handling:** `valuation.signals` automatycznie aktualizuje `likes_count` - nie wymaga akcji w service




## 7. Obsługa błędów

- **400 BAD REQUEST (Validation Error - DRF automatic):**
  - Automatycznie obsługiwany przez DRF serializer validation
  - Przykłady:
    - `value` poza zakresem 1..999999
    - `currency` dłuższy niż 3 znaki
    - Brak wymaganego pola `value`
  - Format DRF: `{"field_name": ["error message"]}`
  - Nie wymaga custom kodu w view

- **401 UNAUTHORIZED (Not Authenticated):**
  - Automatycznie obsługiwany przez DRF `IsAuthenticated` permission
  - Komunikat: "Authentication credentials were not provided."
  - Nie wymaga custom kodu

- **404 NOT_FOUND (BrickSetNotFoundError):**
  - Rzucany przez service gdy `BrickSet.bricksets.get(pk=brickset_id)` rzuci `BrickSet.DoesNotExist`
  - Komunikat: "BrickSet with id {brickset_id} not found."
  - Mapowany w view na Response 404
  - **NIE** ujawniamy czy ID był kiedykolwiek używany

- **409 CONFLICT (ValuationDuplicateError):**
  - Rzucany przez service gdy unique constraint `valuation_unique_user_brickset` jest naruszony
  - Service łapie `IntegrityError` i sprawdza error message dla constraint name
  - Komunikat: "Valuation for this BrickSet already exists."
  - Response zawiera `constraint` field dla diagnostyki
  - Mapowany w view na Response 409
  - Pattern: identyczny jak `BrickSetDuplicateError` w catalog

- **500 INTERNAL_SERVER_ERROR:**
  - Dla niespodziewanych błędów (nie powinny wystąpić w normalnych warunkach)
  - Przykłady:
    - Nieobsłużony IntegrityError (np. check constraint violation - nie powinno się zdarzyć po walidacji)
    - Database connection errors
  - Logowanie z traceback dla diagnostyki (Django automatic)
  - Generic error message dla użytkownika (nie ujawniamy szczegółów systemu)
  - DRF exception handler zwraca standardowy format




## 8. Rozważania dotyczące wydajności

- **Query optimization:**
  - Service wykonuje tylko 2 queries:
    1. `BrickSet.bricksets.get(pk=brickset_id)` - weryfikacja istnienia (indexed PK)
    2. `valuation.save()` - insert z unique constraint check (indexed)
  - **NIE używamy** `select_related` ani `prefetch_related` - nie potrzebujemy related objects w response
  - Total queries: 2 (optymalne dla create operation)

- **Indexes:**
  - Primary key (valuation.id) już indeksowany automatycznie
  - `brickset_id` już indeksowany (`valuation_brickset_idx`) - szybkie foreign key check
  - `user_id` już indeksowany (`valuation_user_idx`) - szybkie user ownership check
  - Unique constraint `valuation_unique_user_brickset` (user, brickset) automatycznie tworzy index - szybkie duplicate check
  - BrickSet.id primary key już indeksowany - szybkie existence check

- **Transaction handling:**
  - Create w `transaction.atomic()` dla atomowości
  - Minimalizuje lock time na rekordach (tylko insert + constraint check)
  - Database-level unique constraint zapobiega race conditions efektywnie

- **Duplicate check optimization:**
  - **NIE** wykonujemy separate SELECT query dla sprawdzenia duplikatu przed insertem
  - Polegamy na database-level unique constraint - try/catch IntegrityError pattern
  - Redukcja z 3 queries do 2 (brak dodatkowego SELECT dla duplicate check)
  - Race condition safe - constraint enforced atomically w database

- **Memory:**
  - Brak dodatkowych queries dla related objects = minimalna alokacja pamięci
  - Single Valuation object w memory (lightweight)
  - ValuationDTO creation - alokacja tylko dla response fields

- **Scaling considerations:**
  - Endpoint może być często używany (każdy user może ocenić wiele sets)
  - Database indexes + atomic constraint check = efektywne pod wysokim obciążeniem
  - Rozważyć rate limiting (throttling) dla zapobiegania spam i database overload
  - Dla bardzo wysokiego trafficu: rozważyć caching dla BrickSet existence checks (Redis)

- **N+1 prevention:**
  - Response zawiera tylko pola Valuation model - brak nested relations
  - **NIE potrzebujemy** eager loading user ani brickset objects - tylko ID fields
  - Single insert operation - brak iteracji po related objects




## 9. Etapy implementacji

### 9.1. Utworzenie exception classes (valuation/exceptions.py)
- Utworzyć nowy plik `valuation/exceptions.py`
- Zaimplementować `ValuationDuplicateError` (wzór: `BrickSetDuplicateError`)
  - `__init__(constraint: str = "valuation_unique_user_brickset")`
  - Przechowuje `constraint` i `message`
- Zaimplementować `ValuationValidationError` (wzór: `BrickSetValidationError`)
  - `__init__(errors: Mapping[str, list[str]])`
  - Dla przyszłych potrzeb walidacji modelu
- **NIE** tworzymy `ValuationNotFoundError` - będzie potrzebny dopiero dla endpointów PATCH/DELETE valuations

### 9.2. Utworzenie serializers
**9.2.1. CreateValuationSerializer (valuation/serializers/valuation_create.py)**
- Wzór: `CreateBrickSetSerializer` z catalog
- Fields: `value` (IntegerField 1..999999), `currency` (CharField max_length=3, default='PLN'), `comment` (CharField optional)
- Metoda `to_command(brickset_id: int) -> CreateValuationCommand`:
  - Przyjmuje `brickset_id` z path parameter (przekazany przez view)
  - Zwraca `CreateValuationCommand(brickset_id=brickset_id, **self.validated_data)`
- Walidacja: `value` required, `currency` i `comment` optional

**9.2.2. ValuationSerializer (valuation/serializers/valuation_detail.py)**
- Read-only serializer dla ValuationDTO
- Wzór: `BrickSetDetailSerializer` z catalog
- Fields: wszystkie z ValuationDTO
- Używany tylko do serializacji response (nie do input validation)

### 9.3. Implementacja service layer (valuation/services/valuation_create_service.py)
- Wzór: `CreateBrickSetService`
- Klasa `CreateValuationService` z metodą `execute(command: CreateValuationCommand, user: User) -> ValuationDTO`
- Przepływ:
  1. `_verify_brickset_exists(brickset_id)` - pobiera BrickSet przez `BrickSet.bricksets.get(pk=brickset_id)`
     - Jeśli `BrickSet.DoesNotExist` → rzuca `BrickSetNotFoundError` (import z catalog)
  2. `_build_valuation(command, user, brickset)` - tworzy instancję Valuation
  3. `_persist_valuation(valuation)` - zapisuje w `transaction.atomic()`
     - Łapie `IntegrityError` i sprawdza constraint name
     - Jeśli `valuation_unique_user_brickset` → rzuca `ValuationDuplicateError`
     - Inne IntegrityError → re-raise
  4. `_build_dto(valuation)` - tworzy ValuationDTO (likes_count=0, timestamps z saved object)

### 9.4. Implementacja view (valuation/views/brickset_valuations.py)
- Wzór: `BrickSetListView.post()` lub `RegisterUserView.post()`
- Klasa `BrickSetValuationsView(GenericAPIView)` z metodą `post(request, brickset_id)`
- `permission_classes = [IsAuthenticated]`
- `serializer_class = CreateValuationSerializer`
- Przepływ:
  1. Walidacja: `serializer = CreateValuationSerializer(data=request.data); serializer.is_valid(raise_exception=True)`
  2. Command: `command = serializer.to_command(brickset_id)` - przekazujemy brickset_id z path
  3. Execute: `service = CreateValuationService(); valuation_dto = service.execute(command, request.user)`
  4. Exception handling:
     - `BrickSetNotFoundError` → 404 z `{"detail": exc.message}`
     - `ValuationDuplicateError` → 409 z `{"detail": exc.message, "constraint": exc.constraint}`
  5. Response: `ValuationSerializer(valuation_dto).data` → 201 CREATED

### 9.5. Routing (valuation/urls.py)
- Dodać `path("bricksets/<int:brickset_id>/valuations", BrickSetValuationsView.as_view(), name="brickset-valuations")`
- app_name = "valuation" (jeśli jeszcze nie ustawiony)
- Include w głównym `config/urls.py`: `path("api/v1/", include("valuation.urls"))`

### 9.6. Testy
**9.6.1. Testy serializer (valuation/serializers/tests/test_valuation_create_serializer.py)**
- Wzór: testy `CreateBrickSetSerializer`
- Test valid payload → `is_valid() == True`
- Test `to_command()` → zwraca poprawny CreateValuationCommand z brickset_id
- Test missing `value` → validation error
- Test invalid `value` (0, negative, > 999999) → validation errors
- Test default currency ('PLN')
- Test optional comment

**9.6.2. Testy service (valuation/services/tests/test_valuation_create_service.py)**
- Używamy `django.test.TestCase` (NIE pytest fixtures)
- Setup: utworzyć test user i BrickSet w `setUp()`
- Test successful creation → zwraca ValuationDTO z poprawnymi polami
- Test duplicate valuation → rzuca `ValuationDuplicateError`
- Test non-existent BrickSet → rzuca `BrickSetNotFoundError`
- Test persistence → sprawdzić że rekord istnieje w DB
- Test default currency → sprawdzić że 'PLN' jest ustawiony
- Test likes_count initialization → sprawdzić że equals 0

**9.6.3. Testy API view (valuation/views/tests/test_brickset_valuations_view.py)**
- Używamy `APITestCase` z DRF
- Setup: utworzyć test user, BrickSet, authenticate client
- Test POST success → 201 z ValuationDTO, sprawdzić persistence
- Test POST duplicate → 409 z constraint info
- Test POST non-existent BrickSet → 404
- Test POST unauthenticated → 401
- Test POST invalid payload → 400 z DRF error format
- Test POST missing value → 400
- Test POST value out of range → 400

### 9.7. Walidacja po implementacji
- Uruchomić `./bin/lint_backend.sh` - zero violations
- Uruchomić `./bin/test_backend.sh` - wszystkie testy pass, coverage ≥90%
- Manualny test przez cURL/Postman:
  - POST z valid payload → 201
  - POST duplicate → 409
  - POST invalid brickset_id → 404
  - POST bez auth → 401
- Sprawdzić logs - brak nieobsłużonych exceptions


