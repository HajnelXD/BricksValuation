# API Endpoint Implementation Plan: GET /api/v1/valuations/{id}

## 1. Przegląd punktu końcowego

Endpoint umożliwia pobranie szczegółowych informacji o pojedynczej wycenie (Valuation) na podstawie identyfikatora. Zwraca pełne dane wyceny włącznie z timestampami. Endpoint wykorzystuje identyczne wzorce implementacyjne co `GET /api/v1/bricksets/{id}` z katalogu - service layer, DTOs, GenericAPIView i obsługę błędów.

**Wzorce implementacyjne**: Endpoint wykorzystuje identyczne wzorce co catalog detail endpoint:
- Service layer z metodą `execute(valuation_id)` - single responsibility
- Brak Command (GET nie modyfikuje stanu) - tylko DTO dla response
- `ValuationDTO` (już istniejący w `valuation_dto.py`) z pełnym zestawem pól
- Serializer read-only dla `ValuationDTO` 
- GenericAPIView bez paginacji (single object)
- IsAuthenticated permission (tylko zalogowani użytkownicy)
- `ValuationNotFoundError` (nowa custom exception) dla nieistniejącej wyceny
- Pattern: identyczny jak `BrickSetDetailView` z catalog

## 2. Szczegóły żądania

- **Metoda HTTP:** GET
- **URL:** /api/v1/valuations/{id}
- **Parametry:**
  - **Path parameter (wymagany):**
    - `id` (int) – unikalny identyfikator wyceny (primary key)
  - **Query parameters:** Brak
  - **Headers:** 
    - `Authorization: Token <jwt_token>` (wymagany - endpoint wymaga IsAuthenticated)
- **Request Body:** Brak

Przykładowe żądanie:
```bash
GET /api/v1/valuations/77
Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 3. Wykorzystywane typy

- **DTO Models:**
  - `ValuationDTO` - **już istniejący** w `datastore/domains/valuation_dto.py`
    - Response zawiera wszystkie pola: `id`, `brickset_id`, `user_id`, `value`, `currency`, `comment`, `likes_count`, `created_at`, `updated_at`
    - Source model: `Valuation`
    - Pattern: analogia do `BrickSetDetailDTO` (pełny zestaw pól dla detail endpoint)
    - **updated_at** już obecny w DTO (obecnie Optional - wymaga zmiany na required datetime)

- **Service Layer:**
  - `ValuationDetailService` - nowa klasa w `valuation/services/valuation_detail_service.py`
  - Metoda `execute(valuation_id: int) -> ValuationDTO` - zwraca pojedynczą wycenę jako DTO
  - Wzór: `BrickSetDetailService` z `catalog/services/`
  - Single responsibility: fetch + map to DTO + raise exception if not found

- **Serializers:**
  - `ValuationDetailSerializer` - nowy serializer w `valuation/serializers/valuation_detail.py`
    - Read-only serializer dla `ValuationDTO`
    - Wszystkie pola read_only=True (output only)
    - Wzór: `BrickSetDetailSerializer` z catalog

- **Exceptions:**
  - `ValuationNotFoundError` - **nowa** w `valuation/exceptions.py`
    - Pattern identyczny jak `BrickSetNotFoundError`
    - Args: `valuation_id: int`
    - Message: `f"Valuation with id {valuation_id} not found."`
    - Używany gdy Valuation o podanym ID nie istnieje (404)

- **View:**
  - `ValuationDetailView` - nowa klasa w `valuation/views/valuation_detail.py`
  - GenericAPIView bez paginacji (single object)
  - Metoda `get(request, pk)` 
  - Pattern: identyczny jak `BrickSetDetailView.get()` z catalog

- **Models:**
  - `Valuation` - już istniejący w `valuation/models/valuation.py`
  - ForeignKey do BrickSet i User
  - Primary key indexed (automatic)

## 4. Szczegóły odpowiedzi

- **Sukces (200 OK):**
  Pełne szczegóły wyceny z wszystkimi polami.

  ```json
  {
    "id": 77,
    "brickset_id": 10,
    "user_id": 99,
    "value": 400,
    "currency": "PLN",
    "comment": "Looks complete and in great condition",
    "likes_count": 9,
    "created_at": "2025-10-25T11:42:00.000Z",
    "updated_at": "2025-10-25T11:42:00.000Z"
  }
  ```

  **Uwaga**: `comment` może być `null` jeśli nie został podany.

- **Błędy:**
  - **401 UNAUTHORIZED (Not Authenticated):**
    Automatycznie obsługiwany przez DRF `IsAuthenticated` permission.
    ```json
    {
      "detail": "Authentication credentials were not provided."
    }
    ```
  
  - **404 NOT_FOUND (ValuationNotFoundError):**
    Wycena o podanym ID nie istnieje.
    ```json
    {
      "detail": "Valuation with id 999 not found."
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

1. **Odbiór żądania:** Klient wysyła GET /api/v1/valuations/{id} z JWT token.
2. **Routing:** Django route resolver kieruje do `ValuationDetailView.get(request, pk)`.
3. **Autentykacja:** DRF middleware sprawdza JWT token (IsAuthenticated) → 401 jeśli brak/invalid.
4. **Walidacja path param:** DRF automatycznie waliduje że pk jest intem (jeśli nie → 404).
5. **Logika biznesowa:** View wywołuje `ValuationDetailService().execute(pk)`:
   - Service wykonuje: `Valuation.valuations.get(pk=valuation_id)`
   - Jeśli `Valuation.DoesNotExist` → rzuca `ValuationNotFoundError`
   - Mapuje Valuation instance do `ValuationDTO`
   - Zwraca DTO
6. **Serializacja:** View serializuje DTO przez `ValuationDetailSerializer(valuation_dto)`
7. **Response:** View zwraca `Response(serializer.data, status=HTTP_200_OK)`
8. **Reakcja na błędy:**
   - `ValuationNotFoundError` → 404 z `{"detail": exc.message}`
   - Authentication errors → 401 automatic
   - Unexpected errors → 500 (logged with traceback)

## 6. Względy bezpieczeństwa

- **Uwierzytelnienie:** Endpoint wymaga autentykacji (`permission_classes = [IsAuthenticated]`) - tylko zalogowani użytkownicy.
- **Brak autoryzacji per-valuation:** Każdy zalogowany użytkownik może przeglądać szczegóły wyceny (public data w kontekście aplikacji).
- **Primary Key validation:** DRF automatycznie waliduje typ path parametru (int).
- **Ochrona danych:**
  - Parametryzowane zapytania ORM zapobiegają SQL injection
  - Response nie zawiera wrażliwych danych user (tylko user_id)
  - Comment field może zawierać user input - automatycznie escapowany przez DRF JSON serializer
- **Error disclosure:**
  - 404 dla nieistniejącej wyceny nie ujawnia czy ID był kiedykolwiek używany (generic message)
  - Brak ujawniania wewnętrznych szczegółów systemu w error responses
- **Rate limiting:** Rozważyć throttling (np. max 100 requests/hour per user) dla zapobiegania scraping

## 7. Obsługa błędów

- **401 UNAUTHORIZED (Not Authenticated):**
  - Automatycznie obsługiwany przez DRF `IsAuthenticated` permission
  - Komunikat: "Authentication credentials were not provided."
  - Nie wymaga custom kodu

- **404 NOT_FOUND (ValuationNotFoundError):**
  - Rzucany przez service gdy `Valuation.valuations.get(pk=valuation_id)` rzuci `Valuation.DoesNotExist`
  - Komunikat: "Valuation with id {valuation_id} not found."
  - Mapowany w view na Response 404 z `{"detail": exc.message}`
  - Pattern: identyczny jak `BrickSetNotFoundError` w catalog

- **500 INTERNAL_SERVER_ERROR:**
  - Dla niespodziewanych błędów (nie powinny wystąpić w normalnych warunkach)
  - Przykłady:
    - Database connection errors
    - Unexpected exceptions w service
  - Logowanie z traceback dla diagnostyki (Django automatic)
  - Generic error message dla użytkownika (nie ujawniamy szczegółów systemu)
  - DRF exception handler zwraca standardowy format

## 8. Rozważania dotyczące wydajności

- **Query optimization:**
  - Service wykonuje tylko 1 query: `Valuation.valuations.get(pk=valuation_id)`
  - Primary key lookup - najbardziej efektywne zapytanie (indexed)
  - **NIE używamy** `select_related` ani `prefetch_related` - nie potrzebujemy related objects w response (tylko ID fields)
  - Total queries: 1 (optymalne dla detail operation)
  - Pattern: identyczny jak `BrickSetDetailService`

- **Indexes:**
  - Primary key (id) - automatycznie indexed - instant lookup
  - Brak potrzeby dodatkowych indexes dla tego endpoint

- **N+1 prevention:**
  - Response zawiera tylko pola Valuation model - brak nested relations
  - Single query (PK lookup) - brak iteracji po related objects
  - Nie potrzebujemy eager loading

- **Caching considerations:**
  - Valuation detail może być często odczytywany (popularne wyceny)
  - Dla często przeglądanych valuations: rozważyć Redis cache z TTL 5-10 min
  - Cache key: `valuation_detail:{valuation_id}`
  - Cache invalidation: przy edycji/usunięciu valuation lub zmianie likes_count
  - Implementacja: decorator `@cache_page(300)` lub manual cache w service

- **Scaling considerations:**
  - Primary key lookups = O(1) complexity - efektywne pod wysokim obciążeniem
  - Read replicas dla oddzielenia read traffic od write operations

## 9. Etapy implementacji

### 9.1. Dodanie ValuationNotFoundError (valuation/exceptions.py)
- Rozszerzyć istniejący plik `exceptions.py` w `valuation/`
- Klasa `ValuationNotFoundError(Exception)` 
- Wzór: identyczny jak `BrickSetNotFoundError` z catalog
- Args: `valuation_id: int`
- Attributes: `valuation_id`, `message`
- Message: `f"Valuation with id {valuation_id} not found."`

### 9.2. Aktualizacja ValuationDTO (datastore/domains/valuation_dto.py)
- DTO już istnieje ale `updated_at` jest Optional - zmienić na required datetime
- `updated_at: datetime` (bez Optional)
- Wzór: `BrickSetDetailDTO` ma required `updated_at`

### 9.3. Utworzenie serializer (valuation/serializers/valuation_detail.py)
- Nowy plik `valuation_detail.py` w `valuation/serializers/`
- Klasa `ValuationDetailSerializer(serializers.Serializer)`
- Wszystkie pola read_only=True (output only)
- Fields: `id`, `brickset_id`, `user_id`, `value`, `currency`, `comment`, `likes_count`, `created_at`, `updated_at`
- `comment` jako `CharField(read_only=True, allow_null=True)`
- `created_at`, `updated_at` jako `DateTimeField(read_only=True)`
- Wzór: `BrickSetDetailSerializer` z catalog

### 9.4. Implementacja service layer (valuation/services/valuation_detail_service.py)
- Nowy plik `valuation_detail_service.py` w `valuation/services/`
- Klasa `ValuationDetailService` z jedną metodą
- Wzór: `BrickSetDetailService` z catalog

**Metoda `execute(valuation_id: int) -> ValuationDTO`:**
1. Try: `valuation = Valuation.valuations.get(pk=valuation_id)`
2. Except `Valuation.DoesNotExist` → rzuca `ValuationNotFoundError(valuation_id)` (from exc)
3. Mapuje do DTO:
   ```python
   return ValuationDTO(
       id=valuation.id,
       brickset_id=valuation.brickset_id,
       user_id=valuation.user_id,
       value=valuation.value,
       currency=valuation.currency,
       comment=valuation.comment,
       likes_count=valuation.likes_count,
       created_at=valuation.created_at,
       updated_at=valuation.updated_at,
   )
   ```
4. **NIE** używamy select_related - nie potrzeba related objects

### 9.5. Implementacja view (valuation/views/valuation_detail.py)
- Nowy plik `valuation_detail.py` w `valuation/views/`
- Klasa `ValuationDetailView(GenericAPIView)` z metodą `get()`

**Struktura klasy:**
- `permission_classes = [IsAuthenticated]`
- `serializer_class = ValuationDetailSerializer`

**Metoda `get(request, pk)`:**
1. Service call: `service = ValuationDetailService(); valuation_dto = service.execute(pk)`
2. Exception handling: try-except `ValuationNotFoundError` → 404 z `{"detail": exc.message}`
3. Serializacja: `serializer = ValuationDetailSerializer(valuation_dto)`
4. Response: `return Response(serializer.data, status=HTTP_200_OK)`

**Pattern:** Metoda `get()` praktycznie identyczna jak `BrickSetDetailView.get()`:
- Service → DTO
- Catch exception → 404
- Serialize → response 200

**Docstring wzór:**
- Opisać flow, parametry, response format, error codes
- Przykłady response body (success + error)
- Identyczny styl jak w `BrickSetDetailView`

### 9.6. Routing (valuation/urls.py)
- Dodać nowy path w istniejącym pliku `urls.py`
- Pattern: `path("valuations/<int:pk>", ValuationDetailView.as_view(), name="valuation-detail")`
- Import: `from valuation.views.valuation_detail import ValuationDetailView`
- URL musi być included w `config/urls.py` (jeśli valuation app już included - bez zmian)

### 9.7. Testy

**9.7.1. Testy service (valuation/services/tests/test_valuation_detail_service.py)**
- Nowy plik testów
- Używamy `django.test.TestCase` (NIE pytest fixtures)
- Setup: utworzyć test user, BrickSet i Valuation w `setUp()`

**Test cases:**
- Test successful retrieval → zwraca poprawny `ValuationDTO` z wszystkimi polami
- Test non-existent valuation → rzuca `ValuationNotFoundError`
- Test DTO mapping → sprawdzić wszystkie pola (id, brickset_id, user_id, value, currency, comment, likes_count, timestamps)
- Test null comment → sprawdzić że comment=None jest poprawnie zmapowany

**9.7.2. Testy API view (valuation/views/tests/test_valuation_detail_view.py)**
- Nowy plik testów
- Używamy `APITestCase` z DRF
- Setup: utworzyć test user, BrickSet, Valuation, authenticate client

**Test cases:**
- Test GET success → 200 z pełnym JSON, sprawdzić wszystkie pola
- Test GET non-existent valuation → 404 z detail message
- Test GET unauthenticated → 401
- Test GET null comment → sprawdzić że null jest w response
- Test GET verify timestamps → sprawdzić format ISO datetime

### 9.8. Walidacja po implementacji
- Uruchomić `./bin/lint_backend.sh` - zero violations
- Uruchomić `./bin/test_backend.sh` - wszystkie testy pass, coverage ≥90%
- Manualny test przez cURL/Postman:
  - GET z valid valuation_id → 200 z full JSON
  - GET non-existent valuation_id → 404
  - GET bez auth → 401
  - GET valuation z null comment → 200 z "comment": null
- Sprawdzić logs - brak nieobsłużonych exceptions
- Sprawdzić query count (Django Debug Toolbar): powinno być 1 query (PK lookup)
