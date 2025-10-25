# API Endpoint Implementation Plan: GET /api/v1/bricksets

## 1. Przegląd punktu końcowego
Endpoint służy do pobierania paginowanej listy zestawów LEGO (BrickSets) z możliwością wyszukiwania, filtrowania i sortowania. Zwraca agregowane dane z modeli `BrickSet` i `Valuation` (liczba wycen, suma polubień, top wycena). Endpoint jest **publiczny** (AllowAny) zgodnie z FR-18 – niezalogowani użytkownicy mogą przeglądać katalog, ale nie mogą dodawać własnych zestawów czy wycen.

## 2. Szczegóły żądania
- **Metoda HTTP:** GET
- **Adres URL:** /api/v1/bricksets
- **Parametry zapytania:**
  - **Wymagane:** Brak (paginacja ma domyślne wartości)
  - **Opcjonalne:**
    - `page` (int, ≥1, domyślnie 1) – numer strony
    - `page_size` (int, 1-100, domyślnie 20) – liczba elementów na stronę
    - `q` (string) – wyszukiwanie według numeru zestawu (częściowe dopasowanie, np. `q=12345`)
    - `production_status` (string) – filtrowanie: `ACTIVE` lub `RETIRED`
    - `completeness` (string) – filtrowanie: `COMPLETE` lub `INCOMPLETE`
    - `has_instructions` (boolean) – filtrowanie: `true` lub `false`
    - `has_box` (boolean) – filtrowanie: `true` lub `false`
    - `is_factory_sealed` (boolean) – filtrowanie: `true` lub `false`
    - `ordering` (string) – sortowanie:
      - `created_at` (najstarsze pierwsze)
      - `-created_at` (najnowsze pierwsze, **domyślne**)
      - `valuations_count` (najmniej wycen)
      - `-valuations_count` (najwięcej wycen)
      - `total_likes` (najmniej polubień)
      - `-total_likes` (najwięcej polubień, alias `-popular`)
- **Request Body:** Brak (endpoint GET)
- **Headers:** Brak (endpoint publiczny, JWT authentication opcjonalna)

## 3. Wykorzystywane typy
- **Command Models:** Brak – endpoint nie przyjmuje danych wejściowych w body
- **DTO Models:** 
  - `BrickSetListItemDTO` (dataclass z `slots=True`) – główny typ odpowiedzi:
    - Pola modelu: id, number, production_status, completeness, has_instructions, has_box, is_factory_sealed, owner_id, owner_initial_estimate, created_at, updated_at
    - Pola agregowane: valuations_count (int), total_likes (int)
    - Zagnieżdżone: top_valuation (Optional[TopValuationSummaryDTO])
  - `TopValuationSummaryDTO` (dataclass z `slots=True`) – podsumowanie najpopularniejszej wyceny:
    - Pola: id, value, currency, likes_count, user_id
- **Service Layer:** `BrickSetListService` – serwis odpowiedzialny za:
  - Walidację i parsowanie parametrów filtrowania
  - Budowanie zapytania ORM z annotacjami
  - Optymalizację zapytań (select_related, prefetch_related, subqueries)
  - Mapowanie QuerySet → lista BrickSetListItemDTO
- **Serializers:** 
  - `BrickSetFilterSerializer` – walidacja query params (read-only, nie zapisuje do DB)
  - `BrickSetListItemSerializer` – serializacja DTO do JSON (read-only, wsparcie dla zagnieżdżonych DTO)
- **Exceptions:** 
  - `rest_framework.exceptions.ValidationError` (wbudowany DRF) – błędy walidacji query params
  - Nie wymaga dedykowanych custom exceptions

## 4. Szczegóły odpowiedzi
- **Sukces (200 OK):**
  ```json
  {
    "count": 57,
    "next": "https://api.example.com/api/v1/bricksets?page=2&page_size=20",
    "previous": null,
    "results": [
      {
        "id": 10,
        "number": 12345,
        "production_status": "ACTIVE",
        "completeness": "COMPLETE",
        "has_instructions": true,
        "has_box": false,
        "is_factory_sealed": false,
        "owner_id": 42,
        "owner_initial_estimate": 350,
        "valuations_count": 5,
        "total_likes": 12,
        "top_valuation": {
          "id": 77,
          "value": 400,
          "currency": "PLN",
          "likes_count": 9,
          "user_id": 99
        },
        "created_at": "2025-10-21T12:34:56Z",
        "updated_at": "2025-10-22T09:15:30Z"
      },
      {
        "id": 11,
        "number": 67890,
        "production_status": "RETIRED",
        "completeness": "INCOMPLETE",
        "has_instructions": false,
        "has_box": true,
        "is_factory_sealed": false,
        "owner_id": 43,
        "owner_initial_estimate": null,
        "valuations_count": 0,
        "total_likes": 0,
        "top_valuation": null,
        "created_at": "2025-10-20T08:00:00Z",
        "updated_at": "2025-10-20T08:00:00Z"
      }
    ]
  }
  ```

- **Błędy:**
  - **400 BAD_REQUEST (ValidationError):**
    ```json
    {
      "errors": {
        "page": ["Ensure this value is greater than or equal to 1."],
        "page_size": ["Ensure this value is less than or equal to 100."],
        "production_status": ["Select a valid choice. INVALID is not one of the available choices."],
        "ordering": ["Select a valid choice. -invalid_field is not one of the available choices."]
      }
    }
    ```
  - **500 INTERNAL_SERVER_ERROR:** Nieoczekiwany błąd serwera

## 5. Przepływ danych
1. Klient wysyła żądanie GET do `/api/v1/bricksets` z opcjonalnymi query params.
2. **BrickSetFilterSerializer** waliduje query params:
   - Sprawdza typy (int dla page/page_size, bool dla flags, enum dla production_status/completeness)
   - Waliduje zakresy (page ≥ 1, page_size 1-100)
   - Waliduje dozwolone wartości enum i ordering
3. **DRF Pagination** (`PageNumberPagination`) przejmuje obsługę page/page_size.
4. **BrickSetListService** wykonuje logikę biznesową:
   - Buduje QuerySet z filtrami: `BrickSet.bricksets.all()`
   - Dodaje filtry: `.filter(number__icontains=q)`, `.filter(production_status=...)`, etc.
   - Dodaje annotacje dla agregacji:
     - `valuations_count = Count('valuations')`
     - `total_likes = Coalesce(Sum('valuations__likes_count'), 0)`
   - Dodaje subquery dla `top_valuation` (Valuation z max likes_count dla danego BrickSet)
   - Dodaje sortowanie: `.order_by(ordering_field)`
   - Używa `.select_related('owner')` dla optymalizacji
5. **Pagination** dzieli QuerySet na strony.
6. **Service** mapuje QuerySet → lista `BrickSetListItemDTO`:
   - Iteruje przez QuerySet
   - Dla każdego BrickSet tworzy DTO z polami modelu + pola annotated
   - Jeśli top_valuation_id jest not None, tworzy zagnieżdżony `TopValuationSummaryDTO`
7. **BrickSetListView** (GenericAPIView + ListModelMixin):
   - Deleguje do service dla QuerySet
   - Paginuje wyniki
   - Serializuje przez `BrickSetListItemSerializer`
   - Zwraca Response 200 z paginowanymi danymi
8. Przeglądarka otrzymuje JSON z listą zestawów.

## 6. Względy bezpieczeństwa
- **Uwierzytelnienie NIE wymagane**: Endpoint publiczny (`permission_classes = [AllowAny]`) zgodnie z FR-18.
- **Brak wrażliwych danych w odpowiedzi**: 
  - Zwracane są tylko publiczne dane BrickSet (number, status, flags)
  - Nie zwracamy danych osobowych właściciela (tylko owner_id)
  - Nie zwracamy komentarzy z wycen (tylko summary: id, value, likes_count, user_id)
- **Walidacja query params**: 
  - Serializery DRF zapobiegają SQL injection (ORM używa parametryzowanych zapytań)
  - Walidacja enum zapobiega nieprawidłowym wartościom
  - Walidacja zakresów zapobiega abuse (page_size max 100)
- **Rate Limiting**: Rozważyć w przyszłości (throttling dla search queries)
- **Query optimization**: 
  - Zapobieganie N+1 queries przez select_related/prefetch_related
  - Limit page_size zapobiega DoS przez nadmierne zapytania

## 7. Obsługa błędów
- **400 VALIDATION_ERROR (DRF ValidationError)**:
  - Rzucany przez serializer gdy:
    - `page < 1` lub `page` nie jest int
    - `page_size < 1` lub `page_size > 100`
    - `production_status` nie jest w ["ACTIVE", "RETIRED"]
    - `completeness` nie jest w ["COMPLETE", "INCOMPLETE"]
    - `has_instructions/has_box/is_factory_sealed` nie są bool
    - `ordering` nie jest w dozwolonych wartościach
  - Mapowany przez DRF exception handler na Response 400
  - Komunikat: `{"errors": {"field_name": ["Error message."]}}`
  
- **500 INTERNAL_SERVER_ERROR**:
  - Możliwe scenariusze: błąd konfiguracji DB, błąd w annotacji ORM
  - Logowanie z traceback dla diagnostyki

**Nie wymaga custom exceptions** – używamy wbudowanych DRF exceptions (`ValidationError`).

## 8. Rozważania dotyczące wydajności
- **Agregacje w pojedynczym zapytaniu**: 
  - Użycie `.annotate()` dla `valuations_count` i `total_likes`
  - Subquery dla `top_valuation` zamiast N+1 queries
  - Jedno zapytanie DB na stronę wyników
- **Indeksy DB**: 
  - Index na `BrickSet.number` (już istnieje)
  - Index na `BrickSet.created_at` (już istnieje jako db_index=True)
  - Index na `Valuation.brickset` (już istnieje)
- **Pagination limits**: 
  - Max page_size = 100 zapobiega nadmiernym zapytaniom
  - Default page_size = 20 balansuje UX i wydajność
- **Select related**: 
  - Nie używamy select_related('owner') jeśli zwracamy tylko owner_id
  - Prefetch top_valuation jako subquery annotation
- **Cache możliwy ale niepotrzebny w MVP**: 
  - Lista zestawów zmienia się rzadko (dodawanie nowych zestawów)
  - Można cache'ować w przyszłości z TTL 5-15 min dla popularnych query
  - Cache key: `bricksets_list:{page}:{page_size}:{filters_hash}`
- **Count optymalizacja**: 
  - DRF PageNumberPagination używa `queryset.count()` dla pola `count`
  - Można cache'ować count dla niefiltrowanych list
- **Monitoring**: Service może logować slow queries (>100ms) dla optymalizacji

## 9. Struktura plików
```
backend/catalog/
├── serializers/
│   ├── __init__.py
│   ├── brickset_list.py                       # NOWY: BrickSetFilterSerializer, BrickSetListItemSerializer
│   └── tests/
│       └── test_brickset_list_serializer.py   # NOWY: testy serializerów
├── services/
│   ├── __init__.py
│   ├── brickset_list_service.py               # NOWY: BrickSetListService z get_queryset()
│   └── tests/
│       └── test_brickset_list_service.py      # NOWY: testy serwisu
├── views/
│   ├── __init__.py
│   ├── brickset_list.py                       # NOWY: BrickSetListView (GenericAPIView)
│   └── tests/
│       └── test_brickset_list_view.py         # NOWY: testy API
└── urls.py                                    # NOWY: routing dla catalog app

backend/datastore/domains/
└── catalog_dto.py                             # ISTNIEJĄCY: BrickSetListItemDTO, TopValuationSummaryDTO

backend/config/
└── urls.py                                    # MODYFIKACJA: include catalog.urls

backend/catalog/models/
├── brickset.py                                # ISTNIEJĄCY: model BrickSet
└── __init__.py                                # MODYFIKACJA: eksport modeli

backend/valuation/models/
└── valuation.py                               # ISTNIEJĄCY: model Valuation
```

**Uwaga**: Endpoint wykorzystuje istniejące modele i DTO. Wymaga:
- Service layer (BrickSetListService) – logika filtrowania, agregacji, mapowania
- Serializers (input validation + output serialization)
- View (GenericAPIView + pagination) – delegacja do service i zwrócenie response
- URL routing (nowy plik catalog/urls.py)

## 10. Etapy wdrożenia

### Krok 1: URL Routing (infrastruktura)
- [ ] Utworzyć `catalog/urls.py`:
  ```python
  from django.urls import path
  from catalog.views.brickset_list import BrickSetListView
  
  app_name = 'catalog'
  urlpatterns = [
      path('bricksets', BrickSetListView.as_view(), name='brickset-list'),
  ]
  ```
- [ ] Dodać do `config/urls.py`:
  ```python
  path('api/v1/', include('catalog.urls')),
  ```

### Krok 2: Service Layer
- [ ] Utworzyć `catalog/services/brickset_list_service.py`:
  - Klasa `BrickSetListService` z metodą `get_queryset(filters: dict) -> QuerySet[BrickSet]`
  - Logika:
    - Buduje QuerySet: `BrickSet.bricksets.all()`
    - Dodaje filtry: `q`, `production_status`, `completeness`, `has_*` flags
    - Dodaje annotacje: `valuations_count`, `total_likes`
    - Dodaje subquery dla `top_valuation` (Valuation z max likes_count)
    - Dodaje sortowanie: `ordering` parameter
    - Zwraca QuerySet (bez materializacji - lazy evaluation)
  - Metoda pomocnicza `_get_top_valuation_subquery() -> Subquery`
  - Metoda pomocnicza `_apply_filters(qs, filters) -> QuerySet`
  - Metoda pomocnicza `_apply_ordering(qs, ordering) -> QuerySet`
  - Metoda `map_to_dto(brickset: BrickSet) -> BrickSetListItemDTO` - mapowanie single object
- [ ] Dodać testy `catalog/services/tests/test_brickset_list_service.py`:
  - Test get_queryset bez filtrów (zwraca wszystkie)
  - Test filtrowania po `q` (częściowe dopasowanie number)
  - Test filtrowania po `production_status` (ACTIVE/RETIRED)
  - Test filtrowania po `completeness` (COMPLETE/INCOMPLETE)
  - Test filtrowania po `has_instructions` (true/false)
  - Test filtrowania po `has_box` (true/false)
  - Test filtrowania po `is_factory_sealed` (true/false)
  - Test kombinacji wielu filtrów
  - Test sortowania: `created_at`, `-created_at`
  - Test sortowania: `valuations_count`, `-valuations_count`
  - Test sortowania: `total_likes`, `-total_likes`
  - Test annotacji `valuations_count` (Count)
  - Test annotacji `total_likes` (Sum z Coalesce)
  - Test subquery `top_valuation` (najpopularniejsza wycena)
  - Test że QuerySet jest lazy (nie wykonuje zapytania od razu)
  - Test optymalizacji zapytań (liczba queries = 1 dla listy 10 elementów)
  - Test map_to_dto z top_valuation
  - Test map_to_dto bez top_valuation (valuations_count=0)

### Krok 3: Serializers
- [ ] Utworzyć `catalog/serializers/brickset_list.py`:
  - `BrickSetFilterSerializer(serializers.Serializer)` – walidacja query params:
    - Pola: page (IntegerField, min 1, required=False)
    - page_size (IntegerField, min 1, max 100, default 20, required=False)
    - q (CharField, required=False, allow_blank=True)
    - production_status (ChoiceField, choices=["ACTIVE", "RETIRED"], required=False)
    - completeness (ChoiceField, choices=["COMPLETE", "INCOMPLETE"], required=False)
    - has_instructions (BooleanField, required=False)
    - has_box (BooleanField, required=False)
    - is_factory_sealed (BooleanField, required=False)
    - ordering (ChoiceField, choices=['created_at', '-created_at', 'valuations_count', '-valuations_count', 'total_likes', '-total_likes'], default='-created_at', required=False)
  - `TopValuationSummarySerializer(serializers.Serializer)` – serializacja zagnieżdżonego DTO:
    - Pola: id, value, currency, likes_count, user_id (wszystkie read_only)
  - `BrickSetListItemSerializer(serializers.Serializer)` – serializacja DTO:
    - Pola: id, number, production_status, completeness, has_instructions, has_box, is_factory_sealed, owner_id, owner_initial_estimate, valuations_count, total_likes, created_at, updated_at
    - top_valuation (TopValuationSummarySerializer, allow_null=True, read_only)
    - Wszystkie pola read_only (nie używamy do input)
- [ ] Dodać testy `catalog/serializers/tests/test_brickset_list_serializer.py`:
  - **BrickSetFilterSerializer**:
    - Test poprawnych wartości wszystkich pól
    - Test domyślnych wartości (page=1, page_size=20, ordering='-created_at')
    - Test walidacji page < 1
    - Test walidacji page_size < 1
    - Test walidacji page_size > 100
    - Test walidacji production_status nieprawidłowa wartość
    - Test walidacji completeness nieprawidłowa wartość
    - Test walidacji ordering nieprawidłowa wartość
    - Test walidacji boolean fields z nieprawidłowymi wartościami
    - Test że wszystkie pola są opcjonalne
  - **TopValuationSummarySerializer**:
    - Test serializacji TopValuationSummaryDTO do dict
    - Test że wszystkie pola są read_only
  - **BrickSetListItemSerializer**:
    - Test serializacji BrickSetListItemDTO do dict
    - Test serializacji z top_valuation=None
    - Test serializacji z top_valuation=TopValuationSummaryDTO
    - Test że wszystkie pola są read_only
    - Test formatu datetime (ISO 8601)

### Krok 4: View Layer
- [ ] Utworzyć `catalog/views/brickset_list.py`:
  - `BrickSetListView(GenericAPIView)` z metodą `get()`
  - Konfiguracja:
    - `permission_classes = [AllowAny]` (endpoint publiczny)
    - `pagination_class = PageNumberPagination` (lub custom class z max_page_size=100)
    - `serializer_class = BrickSetListItemSerializer`
  - Logika:
    - Walidacja query params przez `BrickSetFilterSerializer`
    - Delegacja do `BrickSetListService.get_queryset(filters)`
    - Paginacja QuerySet
    - Mapowanie QuerySet → lista DTO przez `service.map_to_dto()`
    - Serializacja przez `BrickSetListItemSerializer(dtos, many=True)`
    - Zwraca Response 200 z paginowanymi danymi
  - Obsługa ValidationError → Response 400
- [ ] Dodać testy `catalog/views/tests/test_brickset_list_view.py`:
  - Test poprawnego pobrania listy (200, paginacja działa)
  - Test pustej listy (200, count=0, results=[])
  - Test filtrowania po `q` (zwraca tylko pasujące numery)
  - Test filtrowania po `production_status`
  - Test filtrowania po `completeness`
  - Test filtrowania po `has_instructions`
  - Test filtrowania po `has_box`
  - Test filtrowania po `is_factory_sealed`
  - Test kombinacji filtrów
  - Test sortowania `-created_at` (domyślne)
  - Test sortowania `created_at`
  - Test sortowania `-valuations_count`
  - Test sortowania `-total_likes`
  - Test paginacji (page=2, page_size=10)
  - Test walidacji błędnych query params (400)
  - Test że endpoint jest publiczny (AllowAny)
  - Test że response zawiera count, next, previous, results
  - Test że top_valuation jest null gdy brak wycen
  - Test że top_valuation jest wypełnione gdy są wyceny
  - Test że valuations_count i total_likes są poprawnie obliczone
  - Test że Content-Type: application/json
  - Test liczby zapytań DB (max 2: count + select z annotacjami)

### Krok 5: Pagination Config
- [ ] Dodać custom pagination class (opcjonalnie) w `catalog/pagination.py`:
  ```python
  from rest_framework.pagination import PageNumberPagination
  
  class BrickSetPagination(PageNumberPagination):
      page_size = 20
      page_size_query_param = 'page_size'
      max_page_size = 100
  ```
- [ ] Użyć w view: `pagination_class = BrickSetPagination`

### Krok 6: Testy end-to-end i integracja
- [ ] Uruchomić `./bin/test_backend.sh` - coverage min. 90%
- [ ] Uruchomić `./bin/lint_backend.sh` - zero błędów
- [ ] Test ręczny flow: 
  - GET /api/v1/bricksets (200 z pełną listą)
  - GET /api/v1/bricksets?q=12345 (200 z filtrowaną listą)
  - GET /api/v1/bricksets?production_status=ACTIVE (200)
  - GET /api/v1/bricksets?ordering=-valuations_count (200, posortowane)
  - GET /api/v1/bricksets?page=2&page_size=10 (200, druga strona)
- [ ] Test wydajności: sprawdzić liczbę zapytań DB (powinno być 2: count + select)
- [ ] (Opcjonalnie) Dodać testy Cypress dla flow przeglądania listy

### Krok 7: Dokumentacja i Review
- [ ] Zaktualizować README.md z opisem endpointu /api/v1/bricksets
- [ ] Dodać przykłady curl/http do dokumentacji
- [ ] Code review
- [ ] Merge do development

## 11. Scenariusze testowe (szczegółowe)

### Service Tests (`test_brickset_list_service.py`)
- `test_get_queryset_without_filters_returns_all_bricksets`
- `test_get_queryset_filters_by_number_query`
- `test_get_queryset_filters_by_production_status_active`
- `test_get_queryset_filters_by_production_status_retired`
- `test_get_queryset_filters_by_completeness_complete`
- `test_get_queryset_filters_by_completeness_incomplete`
- `test_get_queryset_filters_by_has_instructions_true`
- `test_get_queryset_filters_by_has_instructions_false`
- `test_get_queryset_filters_by_has_box_true`
- `test_get_queryset_filters_by_has_box_false`
- `test_get_queryset_filters_by_is_factory_sealed_true`
- `test_get_queryset_filters_by_is_factory_sealed_false`
- `test_get_queryset_filters_by_multiple_criteria`
- `test_get_queryset_orders_by_created_at_ascending`
- `test_get_queryset_orders_by_created_at_descending`
- `test_get_queryset_orders_by_valuations_count_ascending`
- `test_get_queryset_orders_by_valuations_count_descending`
- `test_get_queryset_orders_by_total_likes_ascending`
- `test_get_queryset_orders_by_total_likes_descending`
- `test_get_queryset_annotates_valuations_count_correctly`
- `test_get_queryset_annotates_total_likes_correctly`
- `test_get_queryset_annotates_total_likes_zero_when_no_valuations`
- `test_get_queryset_includes_top_valuation_subquery`
- `test_get_queryset_top_valuation_is_most_liked`
- `test_get_queryset_is_lazy_evaluation`
- `test_get_queryset_optimization_uses_single_query`
- `test_map_to_dto_with_top_valuation`
- `test_map_to_dto_without_top_valuation`
- `test_map_to_dto_includes_all_required_fields`

### Serializer Tests (`test_brickset_list_serializer.py`)
- **BrickSetFilterSerializer:**
  - `test_valid_data_all_fields`
  - `test_default_values_when_fields_omitted`
  - `test_page_validation_minimum_value`
  - `test_page_size_validation_minimum_value`
  - `test_page_size_validation_maximum_value`
  - `test_production_status_validation_invalid_choice`
  - `test_completeness_validation_invalid_choice`
  - `test_ordering_validation_invalid_choice`
  - `test_has_instructions_validation_invalid_type`
  - `test_has_box_validation_invalid_type`
  - `test_is_factory_sealed_validation_invalid_type`
  - `test_all_fields_are_optional`
  - `test_q_allows_empty_string`
- **TopValuationSummarySerializer:**
  - `test_serialize_top_valuation_dto_to_dict`
  - `test_all_fields_are_read_only`
  - `test_serialized_data_contains_all_fields`
- **BrickSetListItemSerializer:**
  - `test_serialize_brickset_dto_to_dict`
  - `test_serialize_with_null_top_valuation`
  - `test_serialize_with_populated_top_valuation`
  - `test_all_fields_are_read_only`
  - `test_datetime_format_is_iso_8601`
  - `test_serialized_data_contains_all_fields`
  - `test_null_owner_initial_estimate_is_serialized_correctly`

### View Tests (`test_brickset_list_view.py`)
- `test_get_bricksets_returns_200_with_paginated_data`
- `test_get_bricksets_empty_list_returns_200_with_zero_count`
- `test_get_bricksets_filters_by_number_query`
- `test_get_bricksets_filters_by_production_status_active`
- `test_get_bricksets_filters_by_production_status_retired`
- `test_get_bricksets_filters_by_completeness_complete`
- `test_get_bricksets_filters_by_completeness_incomplete`
- `test_get_bricksets_filters_by_has_instructions_true`
- `test_get_bricksets_filters_by_has_box_true`
- `test_get_bricksets_filters_by_is_factory_sealed_true`
- `test_get_bricksets_filters_by_multiple_criteria`
- `test_get_bricksets_orders_by_created_at_descending_default`
- `test_get_bricksets_orders_by_created_at_ascending`
- `test_get_bricksets_orders_by_valuations_count_descending`
- `test_get_bricksets_orders_by_total_likes_descending`
- `test_get_bricksets_pagination_page_2`
- `test_get_bricksets_pagination_custom_page_size`
- `test_get_bricksets_validation_error_invalid_page`
- `test_get_bricksets_validation_error_invalid_page_size`
- `test_get_bricksets_validation_error_invalid_production_status`
- `test_get_bricksets_validation_error_invalid_ordering`
- `test_get_bricksets_is_publicly_accessible`
- `test_get_bricksets_response_includes_pagination_fields`
- `test_get_bricksets_top_valuation_null_when_no_valuations`
- `test_get_bricksets_top_valuation_populated_when_valuations_exist`
- `test_get_bricksets_valuations_count_correct`
- `test_get_bricksets_total_likes_correct`
- `test_get_bricksets_content_type_is_json`
- `test_get_bricksets_database_queries_optimized`
- `test_get_bricksets_max_page_size_enforced`

## 12. Przykłady użycia

### Sukces - lista domyślna (200 OK)
```bash
curl -X GET https://api.example.com/api/v1/bricksets

# Response:
# HTTP/1.1 200 OK
# Content-Type: application/json
# {
#   "count": 57,
#   "next": "https://api.example.com/api/v1/bricksets?page=2",
#   "previous": null,
#   "results": [
#     {
#       "id": 10,
#       "number": 12345,
#       "production_status": "ACTIVE",
#       "completeness": "COMPLETE",
#       "has_instructions": true,
#       "has_box": false,
#       "is_factory_sealed": false,
#       "owner_id": 42,
#       "owner_initial_estimate": 350,
#       "valuations_count": 5,
#       "total_likes": 12,
#       "top_valuation": {
#         "id": 77,
#         "value": 400,
#         "currency": "PLN",
#         "likes_count": 9,
#         "user_id": 99
#       },
#       "created_at": "2025-10-21T12:34:56Z",
#       "updated_at": "2025-10-22T09:15:30Z"
#     }
#   ]
# }
```

### Sukces - filtrowanie po numerze (200 OK)
```bash
curl -X GET "https://api.example.com/api/v1/bricksets?q=12345"

# Response: 200 OK
# Zwraca tylko zestawy zawierające "12345" w numerze
```

### Sukces - filtrowanie po statusie produkcji (200 OK)
```bash
curl -X GET "https://api.example.com/api/v1/bricksets?production_status=RETIRED"

# Response: 200 OK
# Zwraca tylko zestawy RETIRED
```

### Sukces - sortowanie po liczbie wycen (200 OK)
```bash
curl -X GET "https://api.example.com/api/v1/bricksets?ordering=-valuations_count"

# Response: 200 OK
# Zwraca zestawy posortowane od największej liczby wycen
```

### Sukces - kombinacja filtrów (200 OK)
```bash
curl -X GET "https://api.example.com/api/v1/bricksets?completeness=COMPLETE&has_box=true&ordering=-total_likes"

# Response: 200 OK
# Zwraca kompletne zestawy z pudełkiem, posortowane po popularności
```

### Sukces - paginacja (200 OK)
```bash
curl -X GET "https://api.example.com/api/v1/bricksets?page=2&page_size=10"

# Response: 200 OK
# {
#   "count": 57,
#   "next": "https://api.example.com/api/v1/bricksets?page=3&page_size=10",
#   "previous": "https://api.example.com/api/v1/bricksets?page=1&page_size=10",
#   "results": [...]
# }
```

### Błąd - nieprawidłowa wartość page (400 Bad Request)
```bash
curl -X GET "https://api.example.com/api/v1/bricksets?page=0"

# Response:
# HTTP/1.1 400 Bad Request
# Content-Type: application/json
# {
#   "errors": {
#     "page": ["Ensure this value is greater than or equal to 1."]
#   }
# }
```

### Błąd - nieprawidłowa wartość page_size (400 Bad Request)
```bash
curl -X GET "https://api.example.com/api/v1/bricksets?page_size=150"

# Response:
# HTTP/1.1 400 Bad Request
# Content-Type: application/json
# {
#   "errors": {
#     "page_size": ["Ensure this value is less than or equal to 100."]
#   }
# }
```

### Błąd - nieprawidłowa wartość enum (400 Bad Request)
```bash
curl -X GET "https://api.example.com/api/v1/bricksets?production_status=INVALID"

# Response:
# HTTP/1.1 400 Bad Request
# Content-Type: application/json
# {
#   "errors": {
#     "production_status": ["Select a valid choice. INVALID is not one of the available choices."]
#   }
# }
```

### Błąd - nieprawidłowe sortowanie (400 Bad Request)
```bash
curl -X GET "https://api.example.com/api/v1/bricksets?ordering=-invalid_field"

# Response:
# HTTP/1.1 400 Bad Request
# Content-Type: application/json
# {
#   "errors": {
#     "ordering": ["Select a valid choice. -invalid_field is not one of the available choices."]
#   }
# }
```

---

**KLUCZOWE PUNKTY**: 
- Endpoint jest **publiczny** (AllowAny) zgodnie z FR-18 - każdy może przeglądać katalog
- Wykorzystuje **istniejące modele** (BrickSet, Valuation) i **istniejące DTO** (już zdefiniowane w catalog_dto.py)
- Wymaga **Service Layer** dla złożonej logiki filtrowania i agregacji
- Wymaga **dwóch serializerów**: input validation (FilterSerializer) + output serialization (ListItemSerializer)
- **Agregacje w single query**: annotate() dla valuations_count/total_likes, subquery dla top_valuation
- **Optymalizacja wydajności**: max 2 zapytania DB (count + select z annotacjami), bez N+1 problem
- **Paginacja**: DRF PageNumberPagination z max_page_size=100
- **Walidacja**: wszystkie query params walidowane przez serializer, zapobieganie SQL injection
- Pre-commit: `./bin/lint_backend.sh` + `./bin/test_backend.sh` (coverage min. 90%)

Plan wdrożenia zapewnia zgodność ze standardami API, zasadami bezpieczeństwa oraz dobrymi praktykami implementacyjnymi przy wykorzystaniu Django REST Framework, zgodnie z już zrealizowanymi planami register, login, logout i me.
