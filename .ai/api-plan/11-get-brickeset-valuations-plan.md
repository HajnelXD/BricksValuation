# API Endpoint Implementation Plan: GET /api/v1/bricksets/{brickset_id}/valuations

## 1. Przegląd punktu końcowego

Endpoint umożliwia pobranie listy wycen powiązanych z określonym zestawem LEGO (BrickSet). Wyniki są sortowane malejąco według liczby polubień (likes_count DESC) oraz rosnąco według daty utworzenia (created_at ASC) dla zachowania stabilnego uporządkowania. Endpoint wykorzystuje te same wzorce implementacyjne co `GET /api/v1/bricksets` - paginację, service layer, DTOs i GenericAPIView.

**Wzorce implementacyjne**: Endpoint wykorzystuje identyczne wzorce co catalog list endpoint:
- Service layer z metodą `get_queryset()` dla optymalizacji zapytań
- Brak Command (GET nie modyfikuje stanu) - tylko DTOs dla response
- Serializer read-only dla `ValuationListItemDTO`
- GenericAPIView z paginacją (wzór: `BrickSetListView.get()`)
- IsAuthenticated permission (tylko zalogowani użytkownicy mogą przeglądać wyceny)
- BrickSetNotFoundError (reużycie z `catalog.exceptions`) dla nieistniejącego BrickSet
- Paginated response w formacie DRF (count, next, previous, results)

## 2. Szczegóły żądania

- **Metoda HTTP:** GET
- **URL:** /api/v1/bricksets/{brickset_id}/valuations
- **Parametry:**
  - **Path parameter (wymagany):**
    - `brickset_id` (int) – unikalny identyfikator BrickSetu
  - **Query parameters (opcjonalne):**
    - `page` (int) – numer strony (default 1, min 1)
    - `page_size` (int) – liczba elementów na stronie (default 20, max 100)
  - **Headers:** 
    - `Authorization: Token <jwt_token>` (wymagany - endpoint wymaga IsAuthenticated)
- **Request Body:** Brak

Przykładowe żądanie:
```bash
GET /api/v1/bricksets/42/valuations?page=1&page_size=20
Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 3. Wykorzystywane typy

- **DTO Models:**
  - `ValuationListItemDTO` - **NOWY** w `datastore/domains/valuation_dto.py`
    - Response zawiera: `id`, `user_id`, `value`, `currency`, `comment`, `likes_count`, `created_at`
    - **NIE zawiera** `brickset_id` (redundant - jest w URL), `updated_at` (nie potrzebny w liście)
    - Source model: `Valuation`
    - Pattern: analogia do `BrickSetListItemDTO` (wybór pól zoptymalizowanych dla list)

- **Service Layer:**
  - `ValuationListService` - nowa klasa w `valuation/services/valuation_list_service.py`
  - Metoda `get_queryset(brickset_id: int) -> QuerySet` - zwraca filtrowany i posortowany QuerySet
  - Metoda `map_to_dto(valuation: Valuation) -> ValuationListItemDTO` - konwersja do DTO
  - Wzór: `BrickSetListService` z `catalog/services/`

- **Serializers:**
  - `ValuationListItemSerializer` - nowy serializer w `valuation/serializers/valuation_list.py`
    - Read-only serializer dla `ValuationListItemDTO`
    - Wszystkie pola read_only=True
    - Wzór: `BrickSetListItemSerializer` z catalog

- **Exceptions:**
  - `BrickSetNotFoundError` - **reużycie** z `catalog.exceptions` (import)
  - Używany gdy BrickSet o podanym ID nie istnieje (404)

- **View:**
  - `BrickSetValuationsView` - rozszerzenie istniejącego widoku w `valuation/views/brickset_valuations.py`
  - Dodanie metody `get(request, brickset_id)` do istniejącej klasy (już ma `post()`)
  - GenericAPIView z custom pagination class
  - Pattern: identyczny jak `BrickSetListView.get()` z catalog

- **Pagination:**
  - `ValuationPagination` - nowa klasa w `valuation/views/brickset_valuations.py`
  - page_size = 20 (default), max_page_size = 100
  - Pattern: identyczny jak `BrickSetPagination` z catalog

- **Models:**
  - `Valuation` - już istniejący w `valuation/models/valuation.py`
  - ForeignKey do BrickSet z CASCADE
  - Index na `brickset` (`valuation_brickset_idx`) dla szybkich filtrów
  - Index na `created_at` dla sortowania

## 4. Szczegóły odpowiedzi

- **Sukces (200 OK):**
  Lista wycen dla BrickSet z paginacją. Sortowanie: `-likes_count, created_at`.

  ```json
  {
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 77,
        "user_id": 99,
        "value": 450,
        "currency": "PLN",
        "comment": "Looks complete and in great condition",
        "likes_count": 9,
        "created_at": "2025-10-25T11:42:00.000Z"
      },
      {
        "id": 78,
        "user_id": 100,
        "value": 400,
        "currency": "PLN",
        "comment": "Good condition",
        "likes_count": 5,
        "created_at": "2025-10-24T10:30:00.000Z"
      }
    ]
  }
  ```

  **Pusta lista** (gdy BrickSet istnieje ale nie ma wycen):
  ```json
  {
    "count": 0,
    "next": null,
    "previous": null,
    "results": []
  }
  ```

- **Błędy:**
  - **400 BAD REQUEST (Validation Error):**
    Błędne parametry paginacji (automatycznie obsługiwane przez DRF).
    ```json
    {
      "page": ["A valid integer is required."]
    }
    ```
    lub
    ```json
    {
      "page_size": ["Ensure this value is less than or equal to 100."]
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

  - **500 INTERNAL_SERVER_ERROR:**
    Dla niespodziewanych błędów (nie powinny wystąpić w normalnych warunkach).
    ```json
    {
      "detail": "An unexpected error occurred."
    }
    ```

## 5. Przepływ danych

1. **Odbiór żądania:** Klient wysyła GET /api/v1/bricksets/{brickset_id}/valuations z JWT token.
2. **Routing:** Django route resolver kieruje do `BrickSetValuationsView.get(request, brickset_id)`.
3. **Autentykacja:** DRF middleware sprawdza JWT token (IsAuthenticated) → 401 jeśli brak/invalid.
4. **Walidacja path param:** DRF automatycznie waliduje że brickset_id jest intem (jeśli nie → 404).
5. **Walidacja query params:** DRF PageNumberPagination waliduje `page` i `page_size` → 400 jeśli błędne.
6. **Logika biznesowa:** View wywołuje `ValuationListService.get_queryset(brickset_id)`:
   - Service najpierw weryfikuje czy BrickSet istnieje: `BrickSet.bricksets.get(pk=brickset_id)`
     - Jeśli nie znaleziono → rzuca `BrickSetNotFoundError`
   - Buduje QuerySet: `Valuation.valuations.filter(brickset_id=brickset_id).order_by('-likes_count', 'created_at')`
   - **NIE** używa `select_related` ani `prefetch_related` - nie potrzebujemy related objects
7. **Paginacja:** View wywołuje `self.paginate_queryset(queryset)` → zwraca page lub None
8. **Mapowanie do DTO:** Service `map_to_dto()` dla każdego Valuation → `ValuationListItemDTO`
9. **Serializacja:** View serializuje DTOs przez `ValuationListItemSerializer(dtos, many=True)`
10. **Response:** View zwraca `self.get_paginated_response(serializer.data)` → 200 OK
11. **Reakcja na błędy:**
    - `BrickSetNotFoundError` → 404 z `{"detail": exc.message}`
    - DRF pagination validation errors → 400 automatic
    - Authentication errors → 401 automatic

## 6. Względy bezpieczeństwa

- **Uwierzytelnienie:** Endpoint wymaga autentykacji (`permission_classes = [IsAuthenticated]`) - tylko zalogowani użytkownicy.
- **Brak autoryzacji per-valuation:** Każdy zalogowany użytkownik może przeglądać wyceny (public data w kontekście aplikacji).
- **ForeignKey validation:** Service weryfikuje istnienie BrickSet przed zapytaniem (404 dla nieistniejącego set).
- **Ochrona danych:**
  - Parametryzowane zapytania ORM zapobiegają SQL injection
  - DRF automatycznie waliduje typy parametrów URL i query params
  - Response nie zawiera wrażliwych danych user (tylko user_id)
- **Rate limiting:** Rozważyć throttling (np. max 100 requests/hour per user) dla zapobiegania scraping
- **Error disclosure:**
  - 404 dla nieistniejącego BrickSetu nie ujawnia czy ID był kiedykolwiek używany
  - Pusta lista vs 404: pusta lista tylko gdy BrickSet istnieje (nie ujawniamy istnienia przez różnicę w response)
- **Pagination abuse:** Max 100 items per page zapobiega przeciążeniu przez duże page_size
- **CSRF:** DRF automatycznie obsługuje CSRF dla session-based auth; JWT nie wymaga CSRF token

## 7. Obsługa błędów

- **400 BAD REQUEST (Validation Error - DRF automatic):**
  - Automatycznie obsługiwany przez DRF PageNumberPagination
  - Przykłady:
    - `page` nie jest liczbą całkowitą
    - `page_size` > 100
    - `page` < 1
  - Format DRF: `{"field_name": ["error message"]}`
  - Nie wymaga custom kodu w view

- **401 UNAUTHORIZED (Not Authenticated):**
  - Automatycznie obsługiwany przez DRF `IsAuthenticated` permission
  - Komunikat: "Authentication credentials were not provided."
  - Nie wymaga custom kodu

- **404 NOT_FOUND (BrickSetNotFoundError):**
  - Rzucany przez service gdy `BrickSet.bricksets.get(pk=brickset_id)` rzuci `BrickSet.DoesNotExist`
  - Komunikat: "BrickSet with id {brickset_id} not found."
  - Mapowany w view na Response 404 z `{"detail": exc.message}`
  - Pattern: identyczny jak w catalog endpoints
  - **Важное**: weryfikacja istnienia BrickSet PRZED filtrowaniem valuations (nie polegamy na pustej liście)

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
  - Service wykonuje tylko 2 queries:
    1. `BrickSet.bricksets.get(pk=brickset_id)` - weryfikacja istnienia (indexed PK)
    2. `Valuation.valuations.filter(brickset_id=brickset_id).order_by(...)` z LIMIT/OFFSET (paginacja)
  - **NIE używamy** `select_related` ani `prefetch_related` - nie potrzebujemy related objects w response
  - Total queries: 2 (optymalne dla list operation)
  - Pattern: identyczny jak `BrickSetListService` (minimize queries)

- **Indexes:**
  - `valuation_brickset_idx` (brickset_id) - już istniejący - szybki filter
  - `created_at` - już indeksowany w modelu - szybki ORDER BY
  - `likes_count` - rozważyć dodanie indexu dla `ORDER BY -likes_count` (composite index: `brickset_id, likes_count DESC, created_at ASC`)
  - Composite index recommendation: `["brickset", "-likes_count", "created_at"]` dla optymalizacji sortowania

- **Pagination:**
  - Default 20 items per page - balance między UX a performance
  - Max 100 items - zapobiega nadmiernemu obciążeniu
  - DRF PageNumberPagination używa LIMIT/OFFSET - efektywne dla małych offset values
  - Dla bardzo dużych datasets: rozważyć CursorPagination (lepsze performance dla dużych offset)

- **Sortowanie:**
  - Primary sort: `-likes_count` (najpopularniejsze najpierw)
  - Secondary sort: `created_at` (stabilny porządek dla równych likes_count)
  - Database wykonuje sort używając indexes - efektywne
  - Composite index znacząco przyspieszy sortowanie (avoid filesort)

- **N+1 prevention:**
  - Response zawiera tylko pola Valuation model - brak nested relations
  - **NIE potrzebujemy** eager loading user ani brickset objects - tylko ID fields
  - Single filter query z paginacją - brak iteracji po related objects

- **Caching considerations:**
  - Endpoint może być często używany (popularne BrickSets)
  - Dla top X popular bricksets: rozważyć Redis cache z TTL 5-10 min
  - Cache key: `valuation_list:{brickset_id}:page:{page}:size:{page_size}`
  - Cache invalidation: przy utworzeniu/edycji/usunięciu valuation lub like
  - Implementacja: decorator `@cache_page(300)` lub manual cache w service

- **Scaling considerations:**
  - Database indexes + pagination = efektywne pod wysokim obciążeniem
  - Dla bardzo popularnych BrickSets (>1000 valuations): rozważyć materialized views
  - Read replicas dla oddzielenia read traffic od write operations

## 9. Etapy implementacji

### 9.1. Utworzenie ValuationListItemDTO (datastore/domains/valuation_dto.py)
- Dodać `ValuationListItemDTO` do istniejącego pliku
- Fields: `id`, `user_id`, `value`, `currency`, `comment`, `likes_count`, `created_at`
- `@dataclass(slots=True)` dla memory efficiency
- `source_model: ClassVar[type[Valuation]] = Valuation`
- **NIE zawiera** `brickset_id` (redundant w URL context) ani `updated_at` (nie potrzebny w liście)
- Wzór: `BrickSetListItemDTO` z `catalog_dto.py`

### 9.2. Utworzenie serializer (valuation/serializers/valuation_list.py)
- Nowy plik `valuation_list.py` w `valuation/serializers/`
- Klasa `ValuationListItemSerializer(serializers.Serializer)`
- Wszystkie pola read_only=True (output only)
- Fields: `id`, `user_id`, `value`, `currency`, `comment`, `likes_count`, `created_at`
- `created_at` jako `DateTimeField(read_only=True)`
- Wzór: `BrickSetListItemSerializer` z catalog

### 9.3. Implementacja service layer (valuation/services/valuation_list_service.py)
- Nowy plik `valuation_list_service.py` w `valuation/services/`
- Klasa `ValuationListService` z dwiema metodami
- Wzór: `BrickSetListService` z catalog

**Metoda `get_queryset(brickset_id: int) -> QuerySet`:**
1. `_verify_brickset_exists(brickset_id)` - helper method
   - `BrickSet.bricksets.get(pk=brickset_id)` 
   - Jeśli `BrickSet.DoesNotExist` → rzuca `BrickSetNotFoundError(brickset_id)` (import z catalog)
2. Return `Valuation.valuations.filter(brickset_id=brickset_id).order_by('-likes_count', 'created_at')`
   - Filter na indexed field (brickset_id)
   - Sortowanie: najpopularniejsze najpierw, potem chronologicznie
   - **NIE** używamy select_related/prefetch_related - nie potrzeba

**Metoda `map_to_dto(valuation: Valuation) -> ValuationListItemDTO`:**
- Mapowanie z Valuation instance do DTO
- Pattern: identyczny jak `BrickSetListService.map_to_dto()`
- Ekstrakcja tylko potrzebnych fields (bez related objects)

### 9.4. Rozszerzenie view (valuation/views/brickset_valuations.py)
- Rozszerzyć istniejącą klasę `BrickSetValuationsView` (już ma POST)
- Dodać custom pagination class na początku pliku
- Dodać metodę `get()` do klasy

**ValuationPagination (przed klasą view):**
```python
class ValuationPagination(PageNumberPagination):
    """Custom pagination for Valuation list endpoint."""
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
```

**Metoda `get(request, brickset_id)`:**
1. Set pagination_class dynamicznie (lub w class attr)
2. Service call: `service = ValuationListService(); queryset = service.get_queryset(brickset_id)`
3. Exception handling: catch `BrickSetNotFoundError` → 404 z `{"detail": exc.message}`
4. Paginacja: `page = self.paginate_queryset(queryset)`
5. Mapping: `dtos = [service.map_to_dto(val) for val in page]`
6. Serializacja: `ValuationListItemSerializer(dtos, many=True).data`
7. Response: `self.get_paginated_response(serializer.data)` → 200 OK
8. Fallback dla no pagination: identyczny jak w `BrickSetListView.get()`

**Pattern:** Metoda `get()` praktycznie identyczna jak `BrickSetListView.get()`:
- Service → QuerySet
- Paginate → page
- Map to DTOs → serializuj → response

### 9.5. Routing
- **NIE wymaga zmian** - URL już zdefiniowany w `valuation/urls.py`:
  - `path("bricksets/<int:brickset_id>/valuations", BrickSetValuationsView.as_view(), name="brickset-valuations")`
- View już obsługuje routing (Django automatycznie dispatchuje do `get()` lub `post()`)
- URL już included w `config/urls.py` (jeśli nie - dodać include)

### 9.6. Testy

**9.6.1. Testy service (valuation/services/tests/test_valuation_list_service.py)**
- Używamy `django.test.TestCase` (NIE pytest fixtures)
- Setup: utworzyć test user, BrickSet i kilka Valuations w `setUp()`
- Test successful list → zwraca QuerySet z poprawnym filtrowaniem
- Test ordering → sprawdzić że sortowanie `-likes_count, created_at` działa
- Test non-existent BrickSet → rzuca `BrickSetNotFoundError`
- Test empty list → zwraca pusty QuerySet (gdy BrickSet istnieje ale brak valuations)
- Test `map_to_dto()` → zwraca poprawny `ValuationListItemDTO` z wszystkimi polami

**9.6.2. Testy API view (valuation/views/tests/test_brickset_valuations_view.py)**
- Rozszerzyć istniejący plik testów (już ma testy POST)
- Używamy `APITestCase` z DRF
- Setup: utworzyć test user, BrickSet, kilka Valuations, authenticate client

**Testy dla metody GET:**
- Test GET success → 200 z paginated response, sprawdzić strukturę i ordering
- Test GET empty list → 200 z count=0, results=[] (gdy BrickSet istnieje bez valuations)
- Test GET non-existent BrickSet → 404 z detail message
- Test GET unauthenticated → 401
- Test GET pagination → sprawdzić page, page_size, count, next, previous
- Test GET ordering → sprawdzić że najpopularniejsze (max likes_count) są pierwsze
- Test GET max page_size → sprawdzić że page_size=100 działa, 101 → 400

### 9.7. Walidacja po implementacji
- Uruchomić `./bin/lint_backend.sh` - zero violations
- Uruchomić `./bin/test_backend.sh` - wszystkie testy pass, coverage ≥90%
- Manualny test przez cURL/Postman:
  - GET z valid brickset_id → 200 z paginated list
  - GET non-existent brickset_id → 404
  - GET bez auth → 401
  - GET z page_size=100 → 200
  - GET z page=2 → 200 z next/previous links
  - GET BrickSet bez valuations → 200 z empty results
- Sprawdzić logs - brak nieobsłużonych exceptions
- Sprawdzić query count (Django Debug Toolbar lub logging): powinno być 2 queries (BrickSet check + Valuation filter)
