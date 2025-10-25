# API Endpoint Implementation Plan: GET /api/v1/bricksets/{id}

## 1. Przegląd punktu końcowego

Endpoint GET /api/v1/bricksets/{id} służy do pobierania szczegółowych informacji o zestawie LEGO (BrickSet) wraz z pełną listą ocen (valuations) i podsumowaniem wycen. Ma na celu umożliwienie klientowi uzyskania kompletnych danych o BrickSecie, w tym podstawowych metryki (liczba wycen, suma polubień) oraz szczegółów poszczególnych ocen.

**Wzorce implementacyjne**: Endpoint wykorzystuje te same wzorce co `GET /api/v1/bricksets` oraz `POST /api/v1/bricksets`:
- Service layer z metodą `execute()` dla logiki biznesowej
- Domain exception `BrickSetNotFoundError` dla kontrolowanych błędów
- GenericAPIView dla obsługi HTTP (wzór: `BrickSetListView`)
- DTO (`BrickSetDetailDTO`, `ValuationInlineDTO`) dla strukturyzowanych odpowiedzi
- Serializers dla konwersji DTO → JSON
- AllowAny permission (publiczny odczyt jak w GET list)

## 2. Szczegóły żądania

- **Metoda HTTP:** GET
- **URL:** /api/v1/bricksets/{id}
- **Parametry:**
  - **Path parameter (wymagany):**
    - `id` (int) – unikalny identyfikator BrickSetu (primary key)
  - **Headers:** 
    - Brak wymaganych (endpoint publiczny, AllowAny)
- **Request Body:** Brak (GET nie ma body)

Przykładowe żądanie:
```bash
GET /api/v1/bricksets/42
```

## 3. Wykorzystywane typy

- **DTO Models (odpowiedź):**
  - `BrickSetDetailDTO` (już zdefiniowany w `datastore/domains/catalog_dto.py`)
    - Pola: id, number, production_status, completeness, has_instructions, has_box, is_factory_sealed, owner_initial_estimate, owner_id, valuations (list), valuations_count, total_likes, created_at, updated_at
  - `ValuationInlineDTO` (już zdefiniowany w `datastore/domains/catalog_dto.py`)
    - Pola: id, user_id, value, currency, comment, likes_count, created_at

- **Service Layer:**
  - `BrickSetDetailService` - nowa klasa z metodą `execute(brickset_id: int) -> BrickSetDetailDTO`

- **Serializers:**
  - `ValuationInlineSerializer` - serializacja ValuationInlineDTO do JSON
  - `BrickSetDetailSerializer` - serializacja BrickSetDetailDTO do JSON (nested ValuationInlineSerializer)

- **Exceptions:**
  - `BrickSetNotFoundError` - domain exception dla nieistniejącego BrickSetu (wzór: `BrickSetDuplicateError`)

- **View:**
  - `BrickSetDetailView(GenericAPIView)` - nowy widok z metodą `get()`

## 4. Szczegóły odpowiedzi

- **Sukces (200 OK):**

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
    "valuations": [
      {
        "id": 77,
        "user_id": 99,
        "value": 400,
        "currency": "PLN",
        "comment": "Looks complete and well preserved",
        "likes_count": 9,
        "created_at": "2025-10-20T14:23:45.123Z"
      },
      {
        "id": 78,
        "user_id": 101,
        "value": 380,
        "currency": "PLN",
        "comment": null,
        "likes_count": 3,
        "created_at": "2025-10-21T09:15:22.456Z"
      }
    ],
    "valuations_count": 2,
    "total_likes": 12,
    "created_at": "2025-10-15T10:30:00.000Z",
    "updated_at": "2025-10-15T10:30:00.000Z"
  }
  ```

- **Błędy:**
  - **404 NOT_FOUND (BrickSetNotFoundError):**
    ```json
    {
      "detail": "BrickSet with id 999 not found."
    }
    ```
  - **400 BAD_REQUEST:** Gdy id w URL nie jest liczbą całkowitą (DRF automatycznie)
    ```json
    {
      "detail": "Invalid pk \"abc\" - must be an integer."
    }
    ```

## 5. Przepływ danych

1. **Odbiór żądania:** Klient wysyła GET /api/v1/bricksets/{id} (bez auth, publiczny endpoint).
2. **Routing:** Django route resolver kieruje do `BrickSetDetailView.get()`.
3. **Walidacja id:** DRF automatycznie waliduje że id jest intem (jeśli nie → 400).
4. **Logika biznesowa:** View wywołuje `BrickSetDetailService.execute(brickset_id)`:
   - Service wykonuje `BrickSet.bricksets.get(pk=brickset_id)`
   - Jeśli nie znaleziono → rzuca `BrickSetNotFoundError`
   - Pobiera powiązane valuations przez `prefetch_related('valuations')` 
   - Oblicza agregaty: `valuations_count = valuations.count()`, `total_likes = sum(v.likes_count for v in valuations)`
   - Mapuje valuations do `ValuationInlineDTO`
   - Buduje `BrickSetDetailDTO` z wszystkimi danymi
5. **Serializacja:** View serializuje DTO przez `BrickSetDetailSerializer`.
6. **Response:** Zwraca 200 OK z JSON.
7. **Reakcja na błędy:** 
   - `BrickSetNotFoundError` → 404 z detail message
   - `ValueError` (invalid id type) → 400 (DRF automatic)

## 6. Względy bezpieczeństwa

- **Uwierzytelnienie:** Endpoint publiczny (`permission_classes = [AllowAny]`) - każdy może odczytać szczegóły zestawu (wzór: GET list).
- **Autoryzacja:** Brak - endpoint read-only, publiczny dostęp (zgodnie z GET list pattern).
- **Ochrona danych:** 
  - Parametryzowane zapytania ORM zapobiegają SQL injection
  - DRF automatycznie waliduje typy parametrów URL
  - Nie ujawniamy wrażliwych danych - owner_id jest OK (publiczny), brak hashy/tokenów
- **DoS protection:** 
  - Single object fetch (nie ma N+1 problem jeśli użyjemy prefetch_related)
  - Rozważyć throttling w przyszłości (np. max 100 requests/minute per IP)
- **Error disclosure:** 
  - 404 dla nieistniejącego BrickSetu nie ujawnia informacji systemowych
  - Generic 404 message zamiast szczegółów DB

## 7. Obsługa błędów

- **404 NOT_FOUND (BrickSetNotFoundError):**
  - Rzucany przez service gdy `BrickSet.bricksets.get(pk=id)` rzuci `BrickSet.DoesNotExist`
  - Komunikat: "BrickSet with id {id} not found."
  - Mapowany w view na Response 404
  - **NIE** ujawniamy czy ID był kiedykolwiek używany (bezpieczeństwo)

- **400 BAD_REQUEST:**
  - Automatycznie obsługiwany przez DRF gdy id nie jest intem (np. `/bricksets/abc`)
  - Nie wymaga custom kodu

- **500 INTERNAL_SERVER_ERROR:**
  - Dla niespodziewanych błędów (nie powinny wystąpić w normalnych warunkach)
  - Logowanie z traceback dla diagnostyki
  - Generic error message dla użytkownika

## 8. Rozważania dotyczące wydajności

- **Query optimization:**
  - `select_related('owner')` dla ForeignKey owner (jeśli potrzebny w response - obecnie tylko owner_id)
  - `prefetch_related('valuations')` dla reverse ForeignKey valuations - pobiera wszystkie valuations w 1 dodatkowym query zamiast N queries
  - Total queries: 2 (1 dla BrickSet + owner, 1 dla valuations)

- **Indexes:**
  - Primary key (id) już indeksowany automatycznie
  - valuations.brickset_id już indeksowany (`valuation_brickset_idx`)

- **Aggregations:**
  - `valuations_count` i `total_likes` obliczane in-memory z prefetched valuations (nie dodatkowe query)
  - Dla małej liczby valuations (<100 per set) to jest wydajne
  - Alternatywa: annotate w queryset jak w list endpoint (ale mniej potrzebne dla single object)

- **Caching:**
  - Rozważyć cache per-object (Redis) dla często odczytywanych setów
  - Cache key: `brickset_detail:{id}:{updated_at.timestamp()}`
  - Invalidacja: przy update BrickSetu lub dodaniu/usunięciu valuation

- **Memory:**
  - DTOs z `slots=True` minimalizują overhead
  - Prefetch valuations nie stanowi problemu dla rozsądnej liczby (<1000)

## 9. Struktura plików

```
backend/catalog/
├── exceptions.py                              # MODYFIKACJA: dodać BrickSetNotFoundError
├── serializers/
│   ├── __init__.py                            # MODYFIKACJA: eksport ValuationInlineSerializer, BrickSetDetailSerializer
│   ├── brickset_list.py                       # ISTNIEJĄCY
│   ├── brickset_create.py                     # ISTNIEJĄCY
│   ├── brickset_detail.py                     # NOWY: ValuationInlineSerializer, BrickSetDetailSerializer
│   └── tests/
│       ├── test_brickset_list_serializer.py   # ISTNIEJĄCY
│       ├── test_brickset_create_serializer.py # ISTNIEJĄCY
│       └── test_brickset_detail_serializer.py # NOWY: testy serializerów
├── services/
│   ├── __init__.py                            # MODYFIKACJA: eksport BrickSetDetailService
│   ├── brickset_list_service.py               # ISTNIEJĄCY
│   ├── brickset_create_service.py             # ISTNIEJĄCY
│   ├── brickset_detail_service.py             # NOWY: BrickSetDetailService z execute()
│   └── tests/
│       ├── test_brickset_list_service.py      # ISTNIEJĄCY
│       ├── test_brickset_create_service.py    # ISTNIEJĄCY
│       └── test_brickset_detail_service.py    # NOWY: testy BrickSetDetailService
├── views/
│   ├── __init__.py                            # MODYFIKACJA: eksport BrickSetDetailView
│   ├── brickset_list.py                       # ISTNIEJĄCY: BrickSetListView (GET + POST)
│   ├── brickset_detail.py                     # NOWY: BrickSetDetailView (GET)
│   └── tests/
│       ├── __init__.py                        # ISTNIEJĄCY
│       ├── test_brickset_list_view.py         # ISTNIEJĄCY
│       ├── test_brickset_create_view.py       # ISTNIEJĄCY
│       └── test_brickset_detail_view.py       # NOWY: testy API
└── urls.py                                    # MODYFIKACJA: dodać routing GET /bricksets/<int:pk>

backend/datastore/domains/
└── catalog_dto.py                             # ISTNIEJĄCY: BrickSetDetailDTO, ValuationInlineDTO
```

**Uwaga**: Endpoint wykorzystuje:
- **Istniejące modele i DTO** (BrickSet, Valuation, BrickSetDetailDTO, ValuationInlineDTO)
- **Nowe komponenty**: exception, detail serializers, detail service, detail view
- **Wzorce z list/create endpoints**: struktura service/serializer/view/exceptions identyczna

## 10. Etapy wdrożenia

### Krok 1: Domain Exception
- [ ] Zaktualizować `catalog/exceptions.py`:
  ```python
  class BrickSetNotFoundError(Exception):
      """Raised when BrickSet with given id does not exist."""
      
      def __init__(self, brickset_id: int) -> None:
          super().__init__(f"BrickSet with id {brickset_id} not found.")
          self.brickset_id = brickset_id
  ```

### Krok 2: Detail Serializers
- [ ] Utworzyć `catalog/serializers/brickset_detail.py`:
  - Klasa `ValuationInlineSerializer(serializers.Serializer)`:
    - Pola: id, user_id, value, currency, comment, likes_count, created_at
    - Wszystkie read_only=True
  - Klasa `BrickSetDetailSerializer(serializers.Serializer)`:
    - Pola: id, number, production_status, completeness, has_instructions, has_box, is_factory_sealed, owner_initial_estimate, owner_id, valuations (nested), valuations_count, total_likes, created_at, updated_at
    - valuations = ValuationInlineSerializer(many=True, read_only=True)
    - Wszystkie pola read_only=True
- [ ] Dodać testy `catalog/serializers/tests/test_brickset_detail_serializer.py`:
  - `test_valuation_inline_serializer_with_all_fields`
  - `test_valuation_inline_serializer_with_null_comment`
  - `test_valuation_inline_serializer_formats_datetime_correctly`
  - `test_brickset_detail_serializer_with_no_valuations`
  - `test_brickset_detail_serializer_with_multiple_valuations`
  - `test_brickset_detail_serializer_aggregates_correct_counts`
  - `test_brickset_detail_serializer_with_null_estimate`

### Krok 3: Detail Service
- [ ] Utworzyć `catalog/services/brickset_detail_service.py`:
  - Klasa `BrickSetDetailService`:
    - Metoda `execute(brickset_id: int) -> BrickSetDetailDTO`
    - Fetch BrickSet z `prefetch_related('valuations')`
    - Catch `BrickSet.DoesNotExist` → raise `BrickSetNotFoundError`
    - Map valuations do `ValuationInlineDTO`
    - Oblicz valuations_count i total_likes
    - Return `BrickSetDetailDTO`
- [ ] Dodać testy `catalog/services/tests/test_brickset_detail_service.py`:
  - **Sukces scenarios:**
    - `test_execute_returns_brickset_with_no_valuations`
    - `test_execute_returns_brickset_with_single_valuation`
    - `test_execute_returns_brickset_with_multiple_valuations`
    - `test_execute_aggregates_valuations_count_correctly`
    - `test_execute_aggregates_total_likes_correctly`
    - `test_execute_returns_dto_with_all_brickset_fields`
    - `test_execute_returns_valuations_in_creation_order`
    - `test_execute_maps_valuation_fields_correctly`
  - **Not found error:**
    - `test_execute_raises_not_found_for_nonexistent_id`
    - `test_execute_raises_not_found_includes_id_in_message`
  - **Edge cases:**
    - `test_execute_with_null_owner_initial_estimate`
    - `test_execute_with_valuations_with_null_comments`

### Krok 4: Detail View
- [ ] Utworzyć `catalog/views/brickset_detail.py`:
  - `BrickSetDetailView(GenericAPIView)` z metodą `get()`:
    - `permission_classes = [AllowAny]`
    - `serializer_class = BrickSetDetailSerializer`
    - Get brickset_id z kwargs
    - Call service.execute(brickset_id)
    - Catch `BrickSetNotFoundError` → Response 404
    - Serialize DTO i return 200
- [ ] Dodać testy `catalog/views/tests/test_brickset_detail_view.py`:
  - **Sukces:**
    - `test_get_returns_brickset_with_no_valuations`
    - `test_get_returns_brickset_with_valuations`
    - `test_get_response_has_correct_structure`
    - `test_get_response_includes_all_fields`
    - `test_get_returns_status_ok`
    - `test_get_content_type_is_json`
    - `test_get_aggregates_match_actual_data`
  - **Not found:**
    - `test_get_nonexistent_id_returns_not_found`
    - `test_get_not_found_error_message_includes_id`
  - **Validation:**
    - `test_get_invalid_id_type_returns_bad_request` (DRF auto-handled)
  - **Public access:**
    - `test_get_allows_unauthenticated_access`
    - `test_get_works_for_authenticated_user`

### Krok 5: URL Routing
- [ ] Zaktualizować `catalog/urls.py`:
  ```python
  from catalog.views.brickset_list import BrickSetListView
  from catalog.views.brickset_detail import BrickSetDetailView
  
  urlpatterns = [
      path("bricksets", BrickSetListView.as_view(), name="brickset-list"),  # GET list + POST
      path("bricksets/<int:pk>", BrickSetDetailView.as_view(), name="brickset-detail"),  # GET detail
  ]
  ```

### Krok 6: Integration i Eksporty
- [ ] Zaktualizować `catalog/exceptions.py` - dodać BrickSetNotFoundError
- [ ] Zaktualizować `catalog/serializers/__init__.py` - eksport detail serializers
- [ ] Zaktualizować `catalog/services/__init__.py` - eksport BrickSetDetailService
- [ ] Zaktualizować `catalog/views/__init__.py` - eksport BrickSetDetailView

### Krok 7: Testy E2E i Walidacja
- [ ] Uruchomić `./bin/test_backend.sh` - coverage min. 90%
- [ ] Uruchomić `./bin/lint_backend.sh` - zero błędów
- [ ] Test ręczny flow:
  - GET /api/v1/bricksets/1 → 200 z pełnym DTO
  - GET /api/v1/bricksets/999999 → 404
  - GET /api/v1/bricksets/abc → 400 (DRF auto)
  - Sprawdzić że valuations są w kolejności created_at
  - Sprawdzić że aggregates (count, likes) są poprawne
- [ ] Sprawdzić liczba zapytań DB (powinno być 2: BrickSet + valuations prefetch)

### Krok 8: Dokumentacja i Review
- [ ] Zaktualizować README.md z przykładami curl dla GET detail endpoint
- [ ] Code review
- [ ] Merge do development (branch: BV-13-get-brickset-detail lub similar)

## 11. Scenariusze testowe (szczegółowe)

### Serializer Tests (`test_brickset_detail_serializer.py`)
- `test_valuation_inline_serializer_serializes_all_fields`
- `test_valuation_inline_serializer_handles_null_comment`
- `test_valuation_inline_serializer_formats_datetime_iso8601`
- `test_valuation_inline_serializer_read_only_fields`
- `test_brickset_detail_serializer_serializes_all_fields`
- `test_brickset_detail_serializer_with_empty_valuations_list`
- `test_brickset_detail_serializer_with_single_valuation`
- `test_brickset_detail_serializer_with_multiple_valuations`
- `test_brickset_detail_serializer_valuations_count_matches_list_length`
- `test_brickset_detail_serializer_total_likes_sums_correctly`
- `test_brickset_detail_serializer_handles_null_owner_estimate`
- `test_brickset_detail_serializer_nested_serializer_structure`

### Service Tests (`test_brickset_detail_service.py`)
- `test_execute_returns_dto_for_existing_brickset`
- `test_execute_dto_has_correct_brickset_fields`
- `test_execute_with_no_valuations_returns_empty_list`
- `test_execute_with_no_valuations_has_zero_counts`
- `test_execute_with_single_valuation_returns_list_with_one_item`
- `test_execute_with_multiple_valuations_returns_all_valuations`
- `test_execute_valuations_ordered_by_created_at_ascending`
- `test_execute_aggregates_valuations_count_correctly`
- `test_execute_aggregates_total_likes_correctly`
- `test_execute_valuation_dto_has_all_required_fields`
- `test_execute_handles_null_valuation_comment`
- `test_execute_handles_null_owner_initial_estimate`
- `test_execute_raises_not_found_error_for_nonexistent_id`
- `test_execute_not_found_error_includes_brickset_id`
- `test_execute_uses_prefetch_related_for_valuations` (check query count)

### View Tests (`test_brickset_detail_view.py`)
- `test_get_existing_brickset_returns_ok`
- `test_get_response_has_json_content_type`
- `test_get_response_structure_matches_dto`
- `test_get_response_includes_all_brickset_fields`
- `test_get_response_includes_valuations_list`
- `test_get_response_includes_aggregates`
- `test_get_brickset_without_valuations`
- `test_get_brickset_with_single_valuation`
- `test_get_brickset_with_multiple_valuations`
- `test_get_valuations_count_matches_actual_count`
- `test_get_total_likes_matches_sum`
- `test_get_nonexistent_brickset_returns_not_found`
- `test_get_not_found_response_has_detail_message`
- `test_get_invalid_id_string_returns_bad_request`
- `test_get_negative_id_returns_not_found_not_validation_error`
- `test_get_allows_unauthenticated_user`
- `test_get_works_for_authenticated_user`
- `test_get_query_count_is_optimized` (should be ≤2 queries)

## 12. Przykłady użycia

### Sukces - pobieranie zestawu bez wycen (200 OK)
```bash
curl -X GET https://api.example.com/api/v1/bricksets/1

# Response:
# HTTP/1.1 200 OK
# Content-Type: application/json
# {
#   "id": 1,
#   "number": 10001,
#   "production_status": "ACTIVE",
#   "completeness": "COMPLETE",
#   "has_instructions": true,
#   "has_box": true,
#   "is_factory_sealed": false,
#   "owner_initial_estimate": 250,
#   "owner_id": 15,
#   "valuations": [],
#   "valuations_count": 0,
#   "total_likes": 0,
#   "created_at": "2025-10-15T10:30:00.000Z",
#   "updated_at": "2025-10-15T10:30:00.000Z"
# }
```

### Sukces - pobieranie zestawu z wycenami (200 OK)
```bash
curl -X GET https://api.example.com/api/v1/bricksets/42

# Response:
# HTTP/1.1 200 OK
# Content-Type: application/json
# {
#   "id": 42,
#   "number": 12345,
#   "production_status": "RETIRED",
#   "completeness": "COMPLETE",
#   "has_instructions": true,
#   "has_box": false,
#   "is_factory_sealed": false,
#   "owner_initial_estimate": null,
#   "owner_id": 99,
#   "valuations": [
#     {
#       "id": 101,
#       "user_id": 25,
#       "value": 450,
#       "currency": "PLN",
#       "comment": "Excellent condition, all pieces present",
#       "likes_count": 15,
#       "created_at": "2025-10-20T14:23:45.123Z"
#     },
#     {
#       "id": 102,
#       "user_id": 30,
#       "value": 420,
#       "currency": "PLN",
#       "comment": null,
#       "likes_count": 8,
#       "created_at": "2025-10-21T09:15:22.456Z"
#     },
#     {
#       "id": 103,
#       "user_id": 45,
#       "value": 480,
#       "currency": "PLN",
#       "comment": "Rare find!",
#       "likes_count": 22,
#       "created_at": "2025-10-22T16:42:10.789Z"
#     }
#   ],
#   "valuations_count": 3,
#   "total_likes": 45,
#   "created_at": "2025-10-10T08:15:30.000Z",
#   "updated_at": "2025-10-10T08:15:30.000Z"
# }
```

### Błąd - nieistniejący BrickSet (404 Not Found)
```bash
curl -X GET https://api.example.com/api/v1/bricksets/999999

# Response:
# HTTP/1.1 404 Not Found
# Content-Type: application/json
# {
#   "detail": "BrickSet with id 999999 not found."
# }
```

### Błąd - nieprawidłowy typ id (400 Bad Request)
```bash
curl -X GET https://api.example.com/api/v1/bricksets/abc

# Response:
# HTTP/1.1 404 Not Found (DRF route resolver nie znalazł route)
# lub
# HTTP/1.1 400 Bad Request (jeśli mamy custom converter)
# Content-Type: application/json
# {
#   "detail": "Invalid pk \"abc\" - must be an integer."
# }
```

---

**KLUCZOWE PUNKTY**:
- Endpoint jest **publiczny** (`AllowAny`) - tak jak GET list endpoint
- Wykorzystuje **istniejące DTO** (`BrickSetDetailDTO`, `ValuationInlineDTO`) zdefiniowane w `catalog_dto.py`
- **Service pattern** identyczny jak w `BrickSetListService` i `CreateBrickSetService`
- **Serializer pattern** dla read-only data (wszystkie pola read_only=True)
- **View pattern** identyczny jak w `BrickSetListView` (GenericAPIView)
- **Domain exception** `BrickSetNotFoundError` zamiast generic Django 404
- **Query optimization** przez `prefetch_related('valuations')` - total 2 queries
- **Aggregacje** obliczane in-memory z prefetched data (wydajne dla rozsądnej liczby valuations)
- **Ordering valuations** chronologicznie (created_at ascending) - domyślna kolejność modelu
- Pre-commit: `./bin/lint_backend.sh` + `./bin/test_backend.sh` (coverage min. 90%)

Plan wdrożenia zapewnia zgodność ze standardami projektu, wzorcami z istniejących catalog endpoints oraz dobrymi praktykami Django/DRF.
