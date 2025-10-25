# API Endpoint Implementation Plan: GET /api/v1/users/me/valuations

## 1. Przegląd punktu końcowego

Endpoint umożliwia pobranie listy wycen należących do aktualnie zalogowanego użytkownika. Wyceny są wzbogacone o zagnieżdżony obiekt brickset (id, number) dla kontekstu oraz podstawowe metryki (likes_count). Endpoint jest zgodny z FR-14 i chroniony uwierzytelnieniem.

**Wzorce implementacyjne**: Endpoint wykorzystuje identyczne wzorce co `OwnedBrickSetListView` i `BrickSetValuationsView`:
- Service layer z metodą `get_queryset(user_id: int, ordering: str) -> QuerySet` - zwraca QuerySet Valuation
- Metoda `map_to_dto(valuation: Valuation) -> OwnedValuationListItemDTO` - mapowanie na DTO z zagnieżdżonym brickset dict
- Brak Command (GET endpoint nie wymaga command object - tylko user z request.user)
- DTO: `OwnedValuationListItemDTO` (już istniejący w `valuation_dto.py`) dla output z nested brickset
- GenericAPIView z metodą `get(request)` + paginacja
- IsAuthenticated permission (tylko zalogowani użytkownicy)
- Custom pagination class: `OwnedValuationPagination` - dedykowana dla tego endpoint
- Pattern: analogiczny do `OwnedBrickSetListView` i `BrickSetValuationsView.get()`

## 2. Szczegóły żądania

- **Metoda HTTP:** GET
- **URL:** /api/v1/users/me/valuations
- **Parametry:**
  - **Query parameters (opcjonalne - paginacja i sortowanie):**
    - `page` (int) - numer strony (default 1)
    - `page_size` (int) - rozmiar strony (default 20, max 100)
    - `ordering` (string) - sortowanie: `-created_at` (default), `created_at`, `-likes_count`, `likes_count`, `-value`, `value`
  - **Headers:** 
    - `Authorization: Token <jwt_token>` (wymagany - endpoint wymaga IsAuthenticated)
- **Request Body:** Brak

Przykładowe żądanie:
```bash
GET /api/v1/users/me/valuations?page=1&page_size=20&ordering=-likes_count
Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 3. Wykorzystywane typy

- **Command Model:**
  - Brak - GET endpoint nie wymaga Command object
  - User ID pobierany z `request.user.id` (authenticated user)
  - Pattern: identyczny jak `OwnedBrickSetListView` i `BrickSetValuationsView` - brak command dla GET

- **DTO Model:**
  - `OwnedValuationListItemDTO` - **już istniejący** w `datastore/domains/valuation_dto.py`
    - Fields: `id: int`, `brickset: dict`, `value: int`, `currency: str`, `likes_count: int`, `created_at: datetime`
    - Source model: `Valuation`
    - Pattern: minimalne dane dla list endpoint z zagnieżdżonym brickset dict {"id": int, "number": int}
    - Analogia do `ValuationListItemDTO` - ale z nested brickset zamiast user_id i bez comment

- **Service Layer:**
  - `OwnedValuationListService` - nowa klasa w `valuation/services/owned_valuation_list_service.py`
  - Metoda `get_queryset(user_id: int, ordering: str) -> QuerySet` - zwraca QuerySet Valuation dla user
  - Metoda `map_to_dto(valuation: Valuation) -> OwnedValuationListItemDTO` - mapowanie na DTO z nested brickset
  - Wzór: `OwnedBrickSetListService` + `ValuationListService` z `valuation/services/`
  - Single responsibility: filter by user + ordering + select_related optimization
  - Ordering: `-created_at` (default), `created_at`, `-likes_count`, `likes_count`, `-value`, `value`
  - Optimization: `select_related("brickset")` - join z BrickSet dla nested data (uniknięcie N+1 queries)

- **Serializer:**
  - `OwnedValuationListItemSerializer` - nowy w `valuation/serializers/owned_valuation_list.py`
  - Read-only serializer dla `OwnedValuationListItemDTO`
  - Fields: `id`, `brickset` (nested dict), `value`, `currency`, `likes_count`, `created_at`
  - Nested field `brickset`: DictField z structure {"id": int, "number": int}
  - Pattern: identyczny jak `ValuationListItemSerializer` + nested dict handling

- **Pagination:**
  - `OwnedValuationPagination` - nowa klasa w view file lub dedykowany plik
  - Extends `PageNumberPagination`
  - Config: `page_size = 20`, `page_size_query_param = "page_size"`, `max_page_size = 100`
  - Pattern: identyczny jak `OwnedBrickSetPagination` / `ValuationPagination`

- **View:**
  - `OwnedValuationListView` - nowa klasa w `valuation/views/owned_valuation_list.py`
  - GenericAPIView z `get(request)` method
  - Pattern: identyczny jak `OwnedBrickSetListView.get()` i `BrickSetValuationsView.get()`
  - Permission: IsAuthenticated (tylko zalogowani użytkownicy)
  - Pagination: `OwnedValuationPagination`
  - Serializer: `OwnedValuationListItemSerializer`
  - User ID: `request.user.id` - authenticated user

- **Models:**
  - `Valuation` - już istniejący w `valuation/models/valuation.py`
  - ForeignKey do User (user)
  - ForeignKey do BrickSet (brickset)
  - Indexes na user_id i created_at dla wydajności query
  - Query filter: `user_id=request.user.id`
  - select_related("brickset") dla nested data optimization

## 4. Szczegóły odpowiedzi

- **Sukces (200 OK):**
  Paginowana lista valuations należących do authenticated user. Response zawiera pagination metadata.

  ```json
  {
    "count": 7,
    "next": "http://api.example.com/api/v1/users/me/valuations?page=2",
    "previous": null,
    "results": [
      {
        "id": 77,
        "brickset": {
          "id": 10,
          "number": 12345
        },
        "value": 400,
        "currency": "PLN",
        "likes_count": 9,
        "created_at": "2025-10-20T14:30:00Z"
      },
      {
        "id": 55,
        "brickset": {
          "id": 8,
          "number": 10001
        },
        "value": 250,
        "currency": "PLN",
        "likes_count": 3,
        "created_at": "2025-10-15T10:15:00Z"
      }
    ]
  }
  ```

- **Błędy:**
  - **401 UNAUTHORIZED (Not Authenticated):**
    Automatycznie obsługiwany przez DRF `IsAuthenticated` permission.
    ```json
    {
      "detail": "Authentication credentials were not provided."
    }
    ```

  - **400 BAD_REQUEST (Invalid pagination/ordering params):**
    Automatycznie obsługiwany przez DRF pagination i serializer validation.
    ```json
    {
      "detail": "Invalid page."
    }
    ```
    lub
    ```json
    {
      "ordering": ["Select a valid choice. invalid_field is not one of the available choices."]
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

1. **Odbiór żądania:** Klient wysyła GET /api/v1/users/me/valuations z JWT token + optional pagination/ordering params.
2. **Routing:** Django route resolver kieruje do `OwnedValuationListView.get(request)`.
3. **Autentykacja:** DRF middleware sprawdza JWT token (IsAuthenticated) → 401 jeśli brak/invalid.
4. **Walidacja query params:** Serializer waliduje `page`, `page_size`, `ordering` → 400 jeśli invalid.
5. **Service call:** View wywołuje `OwnedValuationListService().get_queryset(request.user.id, ordering)`:
   - Service filtruje Valuation: `Valuation.valuations.filter(user_id=user_id)`
   - Service dodaje `select_related("brickset")` - join dla nested data (uniknięcie N+1)
   - Service stosuje ordering: `.order_by(ordering)` z validated choice
   - Zwraca QuerySet Valuation z optimized joins
6. **Paginacja:** View paginuje QuerySet przez `self.paginate_queryset(queryset)`.
7. **DTO mapping:** View mapuje każdy Valuation na `OwnedValuationListItemDTO` przez `service.map_to_dto(valuation)`:
   - Service ekstrahuje podstawowe pola (id, value, currency, likes_count, created_at)
   - Service konstruuje nested brickset dict: `{"id": valuation.brickset_id, "number": valuation.brickset.number}`
8. **Serializacja:** View serializuje DTOs przez `OwnedValuationListItemSerializer(dtos, many=True).data`.
9. **Response:** View zwraca `self.get_paginated_response(serializer.data)` - 200 OK z pagination metadata.
10. **Reakcja na błędy:**
    - Authentication errors → 401 automatic (DRF permission)
    - Validation errors → 400 automatic (DRF serializer/pagination)
    - Unexpected errors → 500 (logged with traceback)

## 6. Względy bezpieczeństwa

- **Uwierzytelnienie:** Endpoint wymaga autentykacji (`permission_classes = [IsAuthenticated]`) - tylko zalogowani użytkownicy.
- **Autoryzacja:** Automatyczna autoryzacja przez filter `user_id=request.user.id` - użytkownik widzi tylko swoje valuations.
- **Pagination limits:** `max_page_size = 100` zapobiega excessive data exposure w pojedynczym request.
- **Ochrona danych:**
  - Parametryzowane zapytania ORM zapobiegają SQL injection
  - Response zawiera tylko podstawowe dane valuation + nested brickset - bez wrażliwych danych
  - Nested brickset zawiera tylko id i number - nie ujawnia wrażliwych informacji o właścicielu
  - Brak comment field w response - tylko podstawowe metryki
- **Error disclosure:**
  - Nie ujawnia szczegółów systemu w error messages
  - Generic messages dla unexpected errors
- **Performance:**
  - Index na `user_id` w Valuation model zapewnia wydajne query
  - select_related("brickset") zapobiega N+1 queries - jeden JOIN zamiast N oddzielnych query
  - Paginacja zapobiega excessive memory usage
  - QuerySet jest lazy-evaluated - tylko requested page jest fetched

## 7. Obsługa błędów

- **401 UNAUTHORIZED (Not Authenticated):**
  - Automatycznie obsługiwany przez DRF `IsAuthenticated` permission
  - Komunikat: "Authentication credentials were not provided."
  - Nie wymaga custom kodu w view

- **400 BAD_REQUEST (Invalid params):**
  - Automatycznie obsługiwany przez DRF pagination i serializer validation
  - Komunikat: "Invalid page." lub field-specific validation errors
  - Scenariusze: page < 1, page > max_pages, invalid page_size, invalid ordering choice
  - Nie wymaga custom kodu w view

- **500 INTERNAL_SERVER_ERROR:**
  - Dla niespodziewanych błędów (np. database connection issues)
  - Nie powinny wystąpić w normalnych warunkach
  - Logowane z full traceback dla debugging
  - Generic message: "An unexpected error occurred."

## 8. Testy

Pełny zestaw testów w `valuation/services/tests/test_owned_valuation_list_service.py` i `valuation/views/tests/test_owned_valuation_list_view.py` zgodnie z patterns z OwnedBrickSetListView i BrickSetValuationsView tests:

### Service Tests (`django.test.TestCase`):
- `test_get_queryset_returns_only_user_valuations` - filtrowanie po user_id
- `test_get_queryset_excludes_other_users_valuations` - security: other users invisible
- `test_get_queryset_returns_empty_when_no_valuations` - empty list (not error)
- `test_get_queryset_applies_ordering_created_at_desc` - default ordering
- `test_get_queryset_applies_custom_ordering` - custom ordering choices (likes_count, value)
- `test_get_queryset_includes_select_related_brickset` - optimization verification
- `test_map_to_dto_creates_correct_owned_valuation_dto` - DTO mapping correctness
- `test_map_to_dto_includes_nested_brickset_dict` - nested brickset structure
- `test_map_to_dto_extracts_brickset_id_and_number` - brickset data correctness

### View Tests (`APITestCase` z APIRequestFactory):
- `test_get_returns_paginated_valuations_when_authenticated` - 200 response z pagination
- `test_get_returns_unauthorized_when_not_authenticated` - 401 permission
- `test_get_returns_only_requesting_user_valuations` - security: isolation
- `test_get_returns_empty_results_when_user_has_no_valuations` - empty list (not 404)
- `test_get_respects_pagination_parameters` - page, page_size query params
- `test_get_returns_bad_request_for_invalid_pagination` - invalid page/page_size
- `test_get_respects_ordering_parameter` - ordering query param
- `test_get_returns_bad_request_for_invalid_ordering` - invalid ordering choice
- `test_get_includes_nested_brickset_in_response` - nested structure presence
- `test_get_response_structure_matches_dto` - full response validation

Pattern: identyczna struktura testów jak w `OwnedBrickSetListView`, `BrickSetValuationsView` i ich services

## 9. Etapy implementacji

1. **Weryfikacja `OwnedValuationListItemDTO` w valuation_dto.py:**
   - Plik: `datastore/domains/valuation_dto.py`
   - DTO już istnieje (linia ~145) - sprawdzić czy pola są zgodne z wymaganiami
   - Dataclass z `@dataclass(slots=True)`
   - Fields: `id`, `brickset` (dict), `value`, `currency`, `likes_count`, `created_at`
   - Source model: `Valuation`

2. **Implementacja `OwnedValuationListItemSerializer`:**
   - Plik: `valuation/serializers/owned_valuation_list.py`
   - Read-only serializer dla `OwnedValuationListItemDTO`
   - Fields: wszystkie pola z DTO
   - Nested brickset: `DictField()` z proper structure documentation
   - Pattern: identyczny jak `ValuationListItemSerializer` + nested dict field

3. **Implementacja `OwnedValuationListService`:**
   - Plik: `valuation/services/owned_valuation_list_service.py`
   - Metoda `get_queryset(user_id: int, ordering: str) -> QuerySet`:
     - Filter: `Valuation.valuations.filter(user_id=user_id)`
     - Optimization: `.select_related("brickset")` - join dla nested data
     - Order: `.order_by(ordering)` z validated choice
   - Metoda `map_to_dto(valuation: Valuation) -> OwnedValuationListItemDTO`:
     - Extract podstawowe pola (id, value, currency, likes_count, created_at)
     - Construct nested brickset dict: `{"id": valuation.brickset_id, "number": valuation.brickset.number}`
   - Pattern: `OwnedBrickSetListService` + `ValuationListService`
   - ALLOWED_ORDERINGS: `["created_at", "-created_at", "likes_count", "-likes_count", "value", "-value"]`
   - DEFAULT_ORDERING: `"-created_at"`

4. **Stworzenie `OwnedValuationPagination` class:**
   - Plik: `valuation/views/owned_valuation_list.py` (lub dedykowany pagination.py)
   - Extends `PageNumberPagination`
   - Config: `page_size=20`, `page_size_query_param="page_size"`, `max_page_size=100`
   - Pattern: identyczny jak `OwnedBrickSetPagination` / `ValuationPagination`

5. **Implementacja `OwnedValuationListView`:**
   - Plik: `valuation/views/owned_valuation_list.py`
   - GenericAPIView z `get(request)` method
   - Permission: `IsAuthenticated`
   - Pagination: `OwnedValuationPagination`
   - Serializer: `OwnedValuationListItemSerializer`
   - Validate query params: ordering choice (can use simple serializer or manual check)
   - Service call: `OwnedValuationListService().get_queryset(request.user.id, ordering)`
   - Pagination: `self.paginate_queryset(queryset)`
   - DTO mapping: `[service.map_to_dto(valuation) for valuation in page]`
   - Success: `self.get_paginated_response(serializer.data)` - 200 OK
   - Pattern: identyczny jak `OwnedBrickSetListView.get()` i `BrickSetValuationsView.get()`

6. **Dodanie URL routing:**
   - Plik: `valuation/urls.py` (lub dedykowany users app jeśli istnieje)
   - Pattern: `users/me/valuations`
   - Name: `owned-valuation-list`
   - View: `OwnedValuationListView.as_view()`
   - Method: GET

7. **Testy service layer:**
   - Plik: `valuation/services/tests/test_owned_valuation_list_service.py`
   - TestCase dla każdego scenariusza (user filter, ordering, select_related, nested brickset)
   - Pattern: identyczny jak `test_owned_brickset_list_service.py` i `test_valuation_list_service.py`

8. **Testy view layer:**
   - Plik: `valuation/views/tests/test_owned_valuation_list_view.py`
   - APITestCase z APIRequestFactory
   - Test all HTTP status codes (200, 401, 400)
   - Test pagination, ordering, isolation, nested brickset structure
   - Pattern: identyczny jak `test_owned_brickset_list_view.py` i `test_brickset_valuations_view.py`

9. **Walidacja:**
   - Run `./bin/lint_backend.sh` - must pass
   - Run `./bin/test_backend.sh` - must pass with 90%+ coverage
   - Manual API testing via curl/Postman

## 10. Rozważania wydajnościowe

- **Database indexing:** Valuation model ma już indexes na `user_id` i `created_at` - query jest wydajny
- **Query optimization:** 
  - Filter + select_related + order_by w jednym query - minimalizacja DB roundtrips
  - select_related("brickset") wykonuje LEFT JOIN - jeden query zamiast N+1 separate queries
  - Brak N+1 queries - wszystkie dane (valuation + brickset) w głównym query
- **Pagination:** Zapobiega excessive memory usage - tylko requested page fetched
- **DTO minimalism:** Response zawiera tylko niezbędne pola - minimal payload size
- **Nested brickset:** 
  - Tylko 2 pola (id, number) - minimal nested data
  - select_related zapewnia, że nie ma dodatkowych queries
- **Potential extensions:**
  - Cache pagination results dla popular users (Redis)
  - Add filtering query params jeśli wymagane (np. currency, date range)
  - Pre-fetch related data jeśli potrzebne dodatkowe pola w przyszłości
