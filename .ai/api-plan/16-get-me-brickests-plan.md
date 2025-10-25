# API Endpoint Implementation Plan: GET /api/v1/users/me/bricksets

## 1. Przegląd punktu końcowego

Endpoint umożliwia pobranie listy zestawów LEGO należących do aktualnie zalogowanego użytkownika. Zestawy są wzbogacone o statystyki (liczba wycen, łączna liczba lajków) oraz flagę `editable` określającą możliwość edycji/usuwania na podstawie reguły RB-01. Endpoint jest zgodny z FR-14.

**Wzorce implementacyjne**: Endpoint wykorzystuje identyczne wzorce co `BrickSetListView`:
- Service layer z metodą `get_queryset(user_id: int) -> QuerySet` - zwraca QuerySet BrickSet
- Metoda `map_to_dto(brickset: BrickSet) -> OwnedBrickSetListItemDTO` - mapowanie na DTO z logiką RB-01
- Brak Command (GET endpoint nie wymaga command object - tylko user z request.user)
- DTO: `OwnedBrickSetListItemDTO` (już istniejący w `catalog_dto.py`) dla output z polem `editable`
- GenericAPIView z metodą `get(request)` + paginacja
- IsAuthenticated permission (tylko zalogowani użytkownicy)
- Custom pagination class: `OwnedBrickSetPagination` - dedykowana dla tego endpoint
- Pattern: analogiczny do `BrickSetListView.get()` z catalog module

## 2. Szczegóły żądania

- **Metoda HTTP:** GET
- **URL:** /api/v1/users/me/bricksets
- **Parametry:**
  - **Query parameters (opcjonalne - paginacja i sortowanie):**
    - `page` (int) - numer strony (default 1)
    - `page_size` (int) - rozmiar strony (default 20, max 100)
    - `ordering` (string) - sortowanie: `-created_at` (default), `created_at`, `-valuations_count`, `valuations_count`, `-total_likes`, `total_likes`
  - **Headers:** 
    - `Authorization: Token <jwt_token>` (wymagany - endpoint wymaga IsAuthenticated)
- **Request Body:** Brak

Przykładowe żądanie:
```bash
GET /api/v1/users/me/bricksets?page=1&page_size=20&ordering=-valuations_count
Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 3. Wykorzystywane typy

- **Command Model:**
  - Brak - GET endpoint nie wymaga Command object
  - User ID pobierany z `request.user.id` (authenticated user)
  - Pattern: identyczny jak `BrickSetListView` - brak command dla GET

- **DTO Model:**
  - `OwnedBrickSetListItemDTO` - **już istniejący** w `datastore/domains/catalog_dto.py`
    - Fields: `id: int`, `number: int`, `production_status: str`, `completeness: str`, `valuations_count: int`, `total_likes: int`, `editable: bool`
    - Source model: `BrickSet`
    - Pattern: minimalne dane dla list endpoint z dodatkowym polem `editable` (RB-01 logic)
    - Analogia do `BrickSetListItemDTO` - ale bez szczegółów (has_instructions, has_box, owner_id, top_valuation)

- **Service Layer:**
  - `OwnedBrickSetListService` - nowa klasa w `catalog/services/owned_brickset_list_service.py`
  - Metoda `get_queryset(user_id: int, ordering: str) -> QuerySet` - zwraca QuerySet BrickSet dla owner
  - Metoda `map_to_dto(brickset: BrickSet) -> OwnedBrickSetListItemDTO` - mapowanie na DTO z RB-01 logic
  - Metoda `_is_editable(brickset: BrickSet) -> bool` - implementacja RB-01 rule validation
  - Wzór: `BrickSetListService` z `catalog/services/`
  - Single responsibility: filter by owner + aggregate stats + ordering + RB-01 evaluation
  - Ordering: `-created_at` (default), `created_at`, `-valuations_count`, `valuations_count`, `-total_likes`, `total_likes`
  - Aggregations: `valuations_count` (Count), `total_likes` (Sum) - identyczne jak w BrickSetListService

- **Serializer:**
  - `OwnedBrickSetListItemSerializer` - nowy w `catalog/serializers/owned_brickset_list.py`
  - Read-only serializer dla `OwnedBrickSetListItemDTO`
  - Fields: `id`, `number`, `production_status`, `completeness`, `valuations_count`, `total_likes`, `editable`
  - Pattern: identyczny jak `BrickSetListItemSerializer` ale bez nested TopValuationSummarySerializer

- **Pagination:**
  - `OwnedBrickSetPagination` - nowa klasa w view file lub dedykowany plik
  - Extends `PageNumberPagination`
  - Config: `page_size = 20`, `page_size_query_param = "page_size"`, `max_page_size = 100`
  - Pattern: identyczny jak `BrickSetPagination` / `ValuationPagination`

- **View:**
  - `OwnedBrickSetListView` - nowa klasa w `catalog/views/owned_brickset_list.py`
  - GenericAPIView z metodą `get(request)`
  - Pattern: identyczny jak `BrickSetListView.get()` z catalog
  - Permission: IsAuthenticated (tylko zalogowani użytkownicy)
  - Pagination: `OwnedBrickSetPagination`
  - Serializer: `OwnedBrickSetListItemSerializer`
  - User ID: `request.user.id` - authenticated user

- **Models:**
  - `BrickSet` - już istniejący w `catalog/models/brickset.py`
  - ForeignKey do User (owner)
  - Indexes na owner_id i created_at dla wydajności query
  - Query filter: `owner_id=request.user.id`
  - Related: Valuation model dla aggregacji

## 4. Szczegóły odpowiedzi

- **Sukces (200 OK):**
  Paginowana lista bricksets należących do authenticated user. Response zawiera pagination metadata.

  ```json
  {
    "count": 15,
    "next": "http://api.example.com/api/v1/users/me/bricksets?page=2",
    "previous": null,
    "results": [
      {
        "id": 42,
        "number": 10001,
        "production_status": "ACTIVE",
        "completeness": "COMPLETE",
        "valuations_count": 5,
        "total_likes": 23,
        "editable": true
      },
      {
        "id": 55,
        "number": 20002,
        "production_status": "RETIRED",
        "completeness": "INCOMPLETE",
        "valuations_count": 3,
        "total_likes": 8,
        "editable": false
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

1. **Odbiór żądania:** Klient wysyła GET /api/v1/users/me/bricksets z JWT token + optional pagination/ordering params.
2. **Routing:** Django route resolver kieruje do `OwnedBrickSetListView.get(request)`.
3. **Autentykacja:** DRF middleware sprawdza JWT token (IsAuthenticated) → 401 jeśli brak/invalid.
4. **Walidacja query params:** Serializer waliduje `page`, `page_size`, `ordering` → 400 jeśli invalid.
5. **Service call:** View wywołuje `OwnedBrickSetListService().get_queryset(request.user.id, ordering)`:
   - Service filtruje BrickSet: `BrickSet.bricksets.filter(owner_id=user_id)`
   - Service dodaje aggregacje: `valuations_count` (Count), `total_likes` (Sum)
   - Service stosuje ordering: `.order_by(ordering)` z validated choice
   - Zwraca QuerySet BrickSet z annotacjami
6. **Paginacja:** View paginuje QuerySet przez `self.paginate_queryset(queryset)`.
7. **DTO mapping:** View mapuje każdy BrickSet na `OwnedBrickSetListItemDTO` przez `service.map_to_dto(brickset)`:
   - Service evaluje RB-01 logic dla pola `editable` przez `_is_editable(brickset)`
   - RB-01: `editable = True` jeśli (no other users' valuations) AND (owner valuation has 0 likes)
8. **Serializacja:** View serializuje DTOs przez `OwnedBrickSetListItemSerializer(dtos, many=True).data`.
9. **Response:** View zwraca `self.get_paginated_response(serializer.data)` - 200 OK z pagination metadata.
10. **Reakcja na błędy:**
    - Authentication errors → 401 automatic (DRF permission)
    - Validation errors → 400 automatic (DRF serializer/pagination)
    - Unexpected errors → 500 (logged with traceback)

## 6. Względy bezpieczeństwa

- **Uwierzytelnienie:** Endpoint wymaga autentykacji (`permission_classes = [IsAuthenticated]`) - tylko zalogowani użytkownicy.
- **Autoryzacja:** Automatyczna autoryzacja przez filter `owner_id=request.user.id` - użytkownik widzi tylko swoje bricksets.
- **Pagination limits:** `max_page_size = 100` zapobiega excessive data exposure w pojedynczym request.
- **Ochrona danych:**
  - Parametryzowane zapytania ORM zapobiegają SQL injection
  - Response zawiera tylko podstawowe dane brickset + agregacje - bez wrażliwych danych
  - Pole `editable` ujawnia tylko możliwość edycji (RB-01) - nie ujawnia szczegółów valuations
- **Error disclosure:**
  - Nie ujawnia szczegółów systemu w error messages
  - Generic messages dla unexpected errors
- **Performance:**
  - Index na `owner_id` w BrickSet model zapewnia wydajne query
  - Aggregacje wykonywane w DB (nie w Python) - optymalne performance
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

Pełny zestaw testów w `catalog/services/tests/test_owned_brickset_list_service.py` i `catalog/views/tests/test_owned_brickset_list_view.py` zgodnie z patterns z BrickSetListView tests:

### Service Tests (`django.test.TestCase`):
- `test_get_queryset_returns_only_owner_bricksets` - filtrowanie po owner_id
- `test_get_queryset_excludes_other_users_bricksets` - security: other users invisible
- `test_get_queryset_returns_empty_when_no_bricksets` - empty list (not error)
- `test_get_queryset_adds_valuations_count_annotation` - aggregacja valuations_count
- `test_get_queryset_adds_total_likes_annotation` - aggregacja total_likes
- `test_get_queryset_applies_ordering_created_at_desc` - default ordering
- `test_get_queryset_applies_custom_ordering` - custom ordering choices
- `test_map_to_dto_creates_correct_owned_brickset_dto` - DTO mapping correctness
- `test_map_to_dto_sets_editable_true_when_rb01_satisfied` - RB-01: no other users, no likes
- `test_map_to_dto_sets_editable_false_when_other_users_valuations_exist` - RB-01 violation
- `test_map_to_dto_sets_editable_false_when_owner_valuation_has_likes` - RB-01 violation
- `test_is_editable_returns_true_when_no_valuations` - edge case: no valuations = editable

### View Tests (`APITestCase` z APIRequestFactory):
- `test_get_returns_paginated_bricksets_when_authenticated` - 200 response z pagination
- `test_get_returns_unauthorized_when_not_authenticated` - 401 permission
- `test_get_returns_only_requesting_user_bricksets` - security: isolation
- `test_get_returns_empty_results_when_user_has_no_bricksets` - empty list (not 404)
- `test_get_respects_pagination_parameters` - page, page_size query params
- `test_get_returns_bad_request_for_invalid_pagination` - invalid page/page_size
- `test_get_respects_ordering_parameter` - ordering query param
- `test_get_returns_bad_request_for_invalid_ordering` - invalid ordering choice
- `test_get_includes_editable_field_in_response` - DTO field presence
- `test_get_sets_editable_correctly_based_on_rb01` - RB-01 logic validation

Pattern: identyczna struktura testów jak w `BrickSetListView` i `BrickSetListService`

## 9. Etapy implementacji

1. **Weryfikacja `OwnedBrickSetListItemDTO` w catalog_dto.py:**
   - Plik: `datastore/domains/catalog_dto.py`
   - DTO już istnieje - sprawdzić czy pola są zgodne z wymaganiami
   - Dataclass z `@dataclass(slots=True)`
   - Fields: `id`, `number`, `production_status`, `completeness`, `valuations_count`, `total_likes`, `editable`
   - Source model: `BrickSet`

2. **Implementacja `OwnedBrickSetListItemSerializer`:**
   - Plik: `catalog/serializers/owned_brickset_list.py`
   - Read-only serializer dla `OwnedBrickSetListItemDTO`
   - Fields: wszystkie pola z DTO
   - Pattern: identyczny jak `BrickSetListItemSerializer` (bez nested serializers)

3. **Implementacja `OwnedBrickSetListService`:**
   - Plik: `catalog/services/owned_brickset_list_service.py`
   - Metoda `get_queryset(user_id: int, ordering: str) -> QuerySet`:
     - Filter: `BrickSet.bricksets.filter(owner_id=user_id)`
     - Annotate: `valuations_count` (Count), `total_likes` (Sum)
     - Order: `.order_by(ordering)` z validated choice
   - Metoda `map_to_dto(brickset: BrickSet) -> OwnedBrickSetListItemDTO`:
     - Extract podstawowe pola + agregacje
     - Evalute `editable = self._is_editable(brickset)`
   - Metoda `_is_editable(brickset: BrickSet) -> bool`:
     - Implementacja RB-01 logic (identyczna jak w UpdateBrickSetService)
     - Check: no other users' valuations AND owner valuation has 0 likes
     - Return: bool
   - Pattern: identyczny jak `BrickSetListService` + RB-01 logic z UpdateBrickSetService

4. **Stworzenie `OwnedBrickSetPagination` class:**
   - Plik: `catalog/views/owned_brickset_list.py` (lub dedykowany pagination.py)
   - Extends `PageNumberPagination`
   - Config: `page_size=20`, `page_size_query_param="page_size"`, `max_page_size=100`
   - Pattern: identyczny jak `BrickSetPagination`

5. **Implementacja `OwnedBrickSetListView`:**
   - Plik: `catalog/views/owned_brickset_list.py`
   - GenericAPIView z `get(request)` method
   - Permission: `IsAuthenticated`
   - Pagination: `OwnedBrickSetPagination`
   - Serializer: `OwnedBrickSetListItemSerializer`
   - Validate query params: ordering choice (can use simple serializer or manual check)
   - Service call: `OwnedBrickSetListService().get_queryset(request.user.id, ordering)`
   - Pagination: `self.paginate_queryset(queryset)`
   - DTO mapping: `[service.map_to_dto(brickset) for brickset in page]`
   - Success: `self.get_paginated_response(serializer.data)` - 200 OK
   - Pattern: identyczny jak `BrickSetListView.get()` ale bez filter serializer (prostsze params)

6. **Dodanie URL routing:**
   - Plik: `catalog/urls.py` (lub dedykowany users app jeśli istnieje)
   - Pattern: `users/me/bricksets`
   - Name: `owned-brickset-list`
   - View: `OwnedBrickSetListView.as_view()`
   - Method: GET

7. **Testy service layer:**
   - Plik: `catalog/services/tests/test_owned_brickset_list_service.py`
   - TestCase dla każdego scenariusza (owner filter, aggregations, ordering, RB-01 logic)
   - Pattern: identyczny jak `test_brickset_list_service.py` + RB-01 tests

8. **Testy view layer:**
   - Plik: `catalog/views/tests/test_owned_brickset_list_view.py`
   - APITestCase z APIRequestFactory
   - Test all HTTP status codes (200, 401, 400)
   - Test pagination, ordering, isolation, RB-01 field
   - Pattern: identyczny jak `test_brickset_list_view.py`

9. **Walidacja:**
   - Run `./bin/lint_backend.sh` - must pass
   - Run `./bin/test_backend.sh` - must pass with 90%+ coverage
   - Manual API testing via curl/Postman

## 10. Rozważania wydajnościowe

- **Database indexing:** BrickSet model ma już indexes na `owner_id` i `created_at` - query jest wydajny
- **Query optimization:** 
  - Filter + annotations + order_by w jednym query - minimalizacja DB roundtrips
  - Aggregacje wykonywane w DB (Count, Sum) - nie w Python
  - Brak N+1 queries - wszystkie agregacje w głównym query
- **Pagination:** Zapobiega excessive memory usage - tylko requested page fetched
- **DTO minimalism:** Response zawiera tylko niezbędne pola - minimal payload size
- **RB-01 evaluation:** 
  - Wykonywana w Python (po pobraniu page) - akceptowalne dla max 100 items
  - Alternative: wykonać jako subquery annotation (bardziej złożone, ale szybsze dla dużych datasets)
- **Potential extensions:**
  - Cache pagination results dla popular users (Redis)
  - Add filtering query params jeśli wymagane (np. production_status, completeness)
  - Pre-compute `editable` jako annotation (subquery) zamiast Python evaluation
