# API Endpoint Implementation Plan: GET /api/v1/valuations/{valuation_id}/likes

## 1. Przegląd punktu końcowego

Endpoint umożliwia pobranie listy użytkowników (likes), którzy polubili daną wycenę. Zwraca paginowaną listę z minimalnymi danymi użytkowników (`user_id`, `created_at`). Endpoint wykorzystuje identyczne wzorce implementacyjne co `GET /api/v1/bricksets/{brickset_id}/valuations` - service layer, GenericAPIView z metodą get(), paginacja i obsługa błędów.

**Wzorce implementacyjne**: Endpoint wykorzystuje identyczne wzorce co valuation list endpoint:
- Service layer z metodą `get_queryset(valuation_id: int) -> QuerySet` - zwraca QuerySet Like
- Metoda `map_to_dto(like: Like) -> LikeListItemDTO` - mapowanie na DTO
- Brak Command (GET endpoint nie wymaga command object - tylko path parameter)
- DTO: `LikeListItemDTO` (nowy w `valuation_dto.py`) dla output - minimalne dane like
- GenericAPIView z metodą `get(request, valuation_id)` + paginacja
- IsAuthenticated permission (tylko zalogowani użytkownicy mogą przeglądać likes)
- Custom pagination class: `LikePagination` - dedykowana dla tego endpoint
- Exception: `ValuationNotFoundError` (już istniejący w `valuation/exceptions.py`)
- Pattern: analogiczny do `BrickSetValuationsView.get()` z valuation module

## 2. Szczegóły żądania

- **Metoda HTTP:** GET
- **URL:** /api/v1/valuations/{valuation_id}/likes
- **Parametry:**
  - **Path parameter (wymagany):**
    - `valuation_id` (int) – unikalny identyfikator wyceny (foreign key do Valuation)
  - **Query parameters (opcjonalne - paginacja):**
    - `page` (int) - numer strony (default 1)
    - `page_size` (int) - rozmiar strony (default 20, max 100)
  - **Headers:** 
    - `Authorization: Token <jwt_token>` (wymagany - endpoint wymaga IsAuthenticated)
- **Request Body:** Brak

Przykładowe żądanie:
```bash
GET /api/v1/valuations/77/likes?page=1&page_size=20
Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 3. Wykorzystywane typy

- **Command Model:**
  - Brak - GET endpoint nie wymaga Command object
  - Path parameter `valuation_id` przekazywany bezpośrednio do service layer
  - Pattern: identyczny jak `BrickSetValuationsView` - brak command dla GET

- **DTO Model:**
  - `LikeListItemDTO` - **nowy** w `datastore/domains/valuation_dto.py`
    - Fields: `user_id: int`, `created_at: datetime`
    - Source model: `Like`
    - Pattern: minimalne dane dla list endpoint (bez valuation_id - redundantny w URL context)
    - Analogia do `ValuationListItemDTO` - tylko niezbędne pola dla listy
    - Exclude: `valuation_id` (redundant w context URL), `updated_at` (nie potrzebne w list view)

- **Service Layer:**
  - `LikeListService` - nowa klasa w `valuation/services/like_list_service.py`
  - Metoda `get_queryset(valuation_id: int) -> QuerySet` - zwraca QuerySet Like
  - Metoda `map_to_dto(like: Like) -> LikeListItemDTO` - mapowanie na DTO
  - Wzór: `ValuationListService` z `valuation/services/`
  - Single responsibility: verify valuation exists + filter likes + ordering
  - Ordering: chronologiczne `created_at` (newest first: `-created_at`)
  - Verify valuation exists przed filtrowaniem likes (raise `ValuationNotFoundError`)

- **Serializer:**
  - `LikeListItemSerializer` - nowy w `valuation/serializers/like_list.py`
  - Read-only serializer dla `LikeListItemDTO`
  - Fields: `user_id`, `created_at`
  - Pattern: identyczny jak `ValuationListItemSerializer`

- **Pagination:**
  - `LikePagination` - nowa klasa w view file lub dedykowany plik
  - Extends `PageNumberPagination`
  - Config: `page_size = 20`, `page_size_query_param = "page_size"`, `max_page_size = 100`
  - Pattern: identyczny jak `ValuationPagination` / `BrickSetPagination`

- **View:**
  - `ValuationLikesListView` - nowa klasa w `valuation/views/valuation_likes_list.py`
  - GenericAPIView z metodą `get(request, valuation_id)`
  - Pattern: identyczny jak `BrickSetValuationsView.get()` z valuation
  - Permission: IsAuthenticated (tylko zalogowani mogą przeglądać likes)
  - Pagination: `LikePagination`
  - Serializer: `LikeListItemSerializer`

- **Exceptions:**
  - `ValuationNotFoundError` - już istniejący w `valuation/exceptions.py`
  - Used when Valuation.DoesNotExist (404 NOT_FOUND)
  - Pattern: identyczny jak w `ValuationListService`

- **Models:**
  - `Like` - już istniejący w `valuation/models/like.py`
  - ForeignKey do Valuation i User
  - Indexes na valuation_id i user_id dla wydajności query
  - Query filter: `valuation_id=valuation_id`

## 4. Szczegóły odpowiedzi

- **Sukces (200 OK):**
  Paginowana lista likes dla wyceny. Response zawiera pagination metadata.

  ```json
  {
    "count": 9,
    "next": "http://api.example.com/api/v1/valuations/77/likes?page=2",
    "previous": null,
    "results": [
      {
        "user_id": 42,
        "created_at": "2025-10-25T12:34:56.123456Z"
      },
      {
        "user_id": 55,
        "created_at": "2025-10-24T10:15:30.987654Z"
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
  
  - **404 NOT_FOUND (ValuationNotFoundError):**
    Wycena o podanym valuation_id nie istnieje.
    ```json
    {
      "detail": "Valuation with id 77 not found."
    }
    ```

  - **400 BAD_REQUEST (Invalid pagination params):**
    Automatycznie obsługiwany przez DRF pagination (np. page=-1, page_size=9999).
    ```json
    {
      "detail": "Invalid page."
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

1. **Odbiór żądania:** Klient wysyła GET /api/v1/valuations/{valuation_id}/likes z JWT token + optional pagination params.
2. **Routing:** Django route resolver kieruje do `ValuationLikesListView.get(request, valuation_id)`.
3. **Autentykacja:** DRF middleware sprawdza JWT token (IsAuthenticated) → 401 jeśli brak/invalid.
4. **Walidacja path param:** DRF automatycznie waliduje że valuation_id jest intem (jeśli nie → 404).
5. **Walidacja pagination params:** DRF pagination automatycznie waliduje `page`, `page_size` → 400 jeśli invalid.
6. **Service call:** View wywołuje `LikeListService().get_queryset(valuation_id)`:
   - Service sprawdza czy Valuation exists: `Valuation.valuations.get(pk=valuation_id)`
   - Jeśli `Valuation.DoesNotExist` → rzuca `ValuationNotFoundError` → 404
   - Service filtruje Like: `Like.objects.filter(valuation_id=valuation_id).order_by('-created_at')`
   - Zwraca QuerySet Like
7. **Paginacja:** View paginuje QuerySet przez `self.paginate_queryset(queryset)`.
8. **DTO mapping:** View mapuje każdy Like na `LikeListItemDTO` przez `service.map_to_dto(like)`.
9. **Serializacja:** View serializuje DTOs przez `LikeListItemSerializer(dtos, many=True).data`.
10. **Response:** View zwraca `self.get_paginated_response(serializer.data)` - 200 OK z pagination metadata.
11. **Reakcja na błędy:**
    - `ValuationNotFoundError` → 404 z `{"detail": exc.message}`
    - Authentication errors → 401 automatic (DRF permission)
    - Pagination errors → 400 automatic (DRF pagination)
    - Unexpected errors → 500 (logged with traceback)

## 6. Względy bezpieczeństwa

- **Uwierzytelnienie:** Endpoint wymaga autentykacji (`permission_classes = [IsAuthenticated]`) - tylko zalogowani użytkownicy.
- **Autoryzacja:** Brak dodatkowej autoryzacji - lista likes jest publiczna (w ramach authenticated users). Każdy zalogowany użytkownik może zobaczyć kto polubił wycenę.
- **Primary Key validation:** DRF automatycznie waliduje typ path parametru (int).
- **Pagination limits:** `max_page_size = 100` zapobiega excessive data exposure w pojedynczym request.
- **Ochrona danych:**
  - Parametryzowane zapytania ORM zapobiegają SQL injection
  - Response zawiera tylko `user_id` i `created_at` - minimalne dane użytkownika
  - Nie ujawniamy wrażliwych danych użytkownika (email, username) - tylko ID
  - Można rozszerzyć DTO o username jeśli business requirements tego wymagają
- **Error disclosure:**
  - 404 dla nieistniejącej wyceny jest informacyjny - wycena nie istnieje
  - Nie ujawnia szczegółów systemu w error messages
  - Generic messages dla unexpected errors
- **Performance:**
  - Index na `valuation_id` w Like model zapewnia wydajne query
  - Paginacja zapobiega excessive memory usage
  - QuerySet jest lazy-evaluated - tylko requested page jest fetched

## 7. Obsługa błędów

- **401 UNAUTHORIZED (Not Authenticated):**
  - Automatycznie obsługiwany przez DRF `IsAuthenticated` permission
  - Komunikat: "Authentication credentials were not provided."
  - Nie wymaga custom kodu w view

- **404 NOT_FOUND (ValuationNotFoundError):**
  - Rzucany przez service gdy `Valuation.DoesNotExist` dla `get(pk=valuation_id)`
  - Komunikat: `f"Valuation with id {valuation_id} not found."`
  - Mapowany w view na Response 404 z `{"detail": exc.message}`
  - Scenariusze: wycena o podanym ID nie istnieje
  - Security note: generic message, nie ujawnia szczegółów DB

- **400 BAD_REQUEST (Invalid pagination):**
  - Automatycznie obsługiwany przez DRF pagination
  - Komunikat: "Invalid page." lub podobny
  - Scenariusze: page < 1, page > max_pages, invalid page_size
  - Nie wymaga custom kodu w view

- **500 INTERNAL_SERVER_ERROR:**
  - Dla niespodziewanych błędów (np. database connection issues)
  - Nie powinny wystąpić w normalnych warunkach
  - Logowane z full traceback dla debugging
  - Generic message: "An unexpected error occurred."

## 8. Testy

Pełny zestaw testów w `valuation/services/tests/test_like_list_service.py` i `valuation/views/tests/test_valuation_likes_list.py` zgodnie z patterns z valuation list tests:

### Service Tests (`django.test.TestCase`):
- `test_get_queryset_returns_likes_for_existing_valuation` - happy path, valuation exists
- `test_get_queryset_raises_valuation_not_found_when_valuation_does_not_exist` - Valuation.DoesNotExist
- `test_get_queryset_returns_empty_when_no_likes` - valuation exists ale brak likes
- `test_get_queryset_orders_by_created_at_descending` - newest first ordering
- `test_map_to_dto_creates_correct_like_list_item_dto` - DTO mapping correctness

### View Tests (`APITestCase` z APIRequestFactory):
- `test_get_returns_paginated_likes_when_valuation_exists` - 200 response z pagination
- `test_get_returns_not_found_when_valuation_does_not_exist` - 404 mapping
- `test_get_returns_unauthorized_when_not_authenticated` - 401 permission
- `test_get_returns_empty_results_when_no_likes` - empty list (not 404)
- `test_get_respects_pagination_parameters` - page, page_size query params
- `test_get_returns_bad_request_for_invalid_pagination` - invalid page/page_size

Pattern: identyczna struktura testów jak w `BrickSetValuationsView.get()` i `ValuationListService`

## 9. Etapy implementacji

1. **Stworzenie `LikeListItemDTO` w valuation_dto.py:**
   - Plik: `datastore/domains/valuation_dto.py`
   - Dataclass z `@dataclass(slots=True)`
   - Fields: `user_id: int`, `created_at: datetime`
   - Source model: `Like`
   - Pattern: analogia do `ValuationListItemDTO`

2. **Implementacja `LikeListItemSerializer`:**
   - Plik: `valuation/serializers/like_list.py`
   - Read-only serializer dla `LikeListItemDTO`
   - Fields: `user_id`, `created_at`
   - Pattern: identyczny jak `ValuationListItemSerializer`

3. **Implementacja `LikeListService`:**
   - Plik: `valuation/services/like_list_service.py`
   - Metoda `get_queryset(valuation_id: int) -> QuerySet`:
     - Verify valuation exists (`_verify_valuation_exists`)
     - Filter: `Like.objects.filter(valuation_id=valuation_id)`
     - Order: `.order_by('-created_at')`
   - Metoda `map_to_dto(like: Like) -> LikeListItemDTO`:
     - Extract `user_id`, `created_at`
   - Pattern: identyczny jak `ValuationListService`

4. **Stworzenie `LikePagination` class:**
   - Plik: `valuation/views/valuation_likes_list.py` (lub dedykowany pagination.py)
   - Extends `PageNumberPagination`
   - Config: `page_size=20`, `page_size_query_param="page_size"`, `max_page_size=100`
   - Pattern: identyczny jak `ValuationPagination`

5. **Implementacja `ValuationLikesListView`:**
   - Plik: `valuation/views/valuation_likes_list.py`
   - GenericAPIView z `get(request, valuation_id)` method
   - Permission: `IsAuthenticated`
   - Pagination: `LikePagination`
   - Serializer: `LikeListItemSerializer`
   - Service call: `LikeListService().get_queryset(valuation_id)`
   - Pagination: `self.paginate_queryset(queryset)`
   - DTO mapping: `[service.map_to_dto(like) for like in page]`
   - Error mapping: `ValuationNotFoundError` → 404
   - Success: `self.get_paginated_response(serializer.data)` - 200 OK
   - Pattern: identyczny jak `BrickSetValuationsView.get()`

6. **Dodanie URL routing:**
   - Plik: `valuation/urls.py`
   - Pattern: `valuations/<int:valuation_id>/likes`
   - Name: `valuation-likes-list`
   - View: `ValuationLikesListView.as_view()`
   - Method: GET

7. **Testy service layer:**
   - Plik: `valuation/services/tests/test_like_list_service.py`
   - TestCase dla każdego scenariusza (success, DoesNotExist, ordering, empty list)
   - Pattern: identyczny jak `test_valuation_list_service.py`

8. **Testy view layer:**
   - Plik: `valuation/views/tests/test_valuation_likes_list.py`
   - APITestCase z APIRequestFactory
   - Test all HTTP status codes (200, 401, 404, 400)
   - Test pagination behavior
   - Pattern: identyczny jak valuation list tests

9. **Walidacja:**
   - Run `./bin/lint_backend.sh` - must pass
   - Run `./bin/test_backend.sh` - must pass with 90%+ coverage
   - Manual API testing via curl/Postman

## 10. Rozważania wydajnościowe

- **Database indexing:** Like model ma już indexes na `valuation_id` i `user_id` - query jest wydajny
- **Query optimization:** Filter + order_by na indexed column (`created_at` ma db_index=True)
- **Pagination:** Zapobiega excessive memory usage - tylko requested page fetched
- **No N+1 queries:** Brak related objects do fetch - Like ma tylko FK IDs
- **DTO minimalism:** Response zawiera tylko `user_id`, `created_at` - minimal payload size
- **Potential extensions:**
  - Cache pagination results dla popular valuations (Redis)
  - Add `select_related('user')` jeśli DTO ma zawierać username (wymaga zmiany DTO)
  - Add filtering/sorting query params jeśli wymagane (np. ordering by user_id)
