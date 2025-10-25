# API Endpoint Implementation Plan: PATCH /api/v1/bricksets/{id}

## 1. Przegląd punktu końcowego

Endpoint służy do edycji istniejącego BrickSet. Edycja jest dozwolona tylko dla właściciela rekordu oraz tylko w przypadku, gdy nie istnieją oceny od innych użytkowników, a ocena właściciela (jeśli istnieje) ma 0 like'ów.

**Wzorce implementacyjne**: Endpoint wykorzystuje te same wzorce co `GET /api/v1/bricksets/{id}` oraz `POST /api/v1/bricksets`:
- Service layer z metodą `execute()` dla logiki biznesowej
- Domain exceptions (`BrickSetNotFoundError`, `BrickSetEditForbiddenError`, `BrickSetValidationError`) dla kontrolowanych błędów
- GenericAPIView dla obsługi HTTP (wzór: `BrickSetDetailView`)
- DTO (`BrickSetDetailDTO`) dla strukturyzowanej odpowiedzi (reużycie z GET detail)
- Command (`UpdateBrickSetCommand`) już zdefiniowany w `catalog_dto.py`
- Serializers dla walidacji input + konwersji DTO → JSON
- IsAuthenticated permission (tylko właściciel może edytować)

## 2. Szczegóły żądania

- **Metoda HTTP:** PATCH
- **URL:** /api/v1/bricksets/{id}
- **Parametry:**
  - **Path parameter (wymagany):**
    - `id` (int) – unikalny identyfikator BrickSetu (primary key)
  - **Headers:** 
    - `Authorization: Token <jwt_token>` (wymagany - endpoint wymaga IsAuthenticated)
- **Request Body (JSON):** Wszystkie pola opcjonalne (PATCH = partial update):
  - `has_box` (boolean, opcjonalnie)
  - `owner_initial_estimate` (integer, opcjonalnie, wartość między 1 a 999999 lub null)

**Walidacja body:**
- Co najmniej jedno pole musi być podane (nie można wysłać pustego PATCH)
- `owner_initial_estimate`: jeśli podany, musi być 1-999999 lub null
- `has_box`: jeśli podany, musi być boolean

Przykładowe żądanie:
```bash
PATCH /api/v1/bricksets/42
Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "has_box": false,
  "owner_initial_estimate": 350
}
```

## 3. Wykorzystywane typy

- **Command Model (już istniejący):**
  - `UpdateBrickSetCommand` (zdefiniowany w `datastore/domains/catalog_dto.py`)
    - Pola: `has_box: Optional[bool]`, `owner_initial_estimate: Optional[int]`

- **DTO Models (już istniejące):**
  - `BrickSetDetailDTO` (response, reużycie z GET detail endpoint)

- **Service Layer:**
  - `UpdateBrickSetService` - nowa klasa z metodą `execute(brickset_id: int, command: UpdateBrickSetCommand, requesting_user: User) -> BrickSetDetailDTO`

- **Serializers:**
  - `UpdateBrickSetSerializer` - walidacja partial update input + `to_command()`
  - `BrickSetDetailSerializer` - reużycie dla response (już istniejący)

- **Exceptions:**
  - `BrickSetNotFoundError` - już istniejący
  - `BrickSetEditForbiddenError` - nowy exception dla naruszenia reguł edycji (RB-01)
  - `BrickSetValidationError` - już istniejący

- **View:**
  - `BrickSetUpdateView(GenericAPIView)` - nowy widok z metodą `patch()`

## 4. Szczegóły odpowiedzi

- **Sukces (200 OK):**
  Zwraca zaktualizowany BrickSet zgodnie z `BrickSetDetailDTO` (pełny obiekt jak w GET detail).

  Przykładowa odpowiedź:
  ```json
  {
    "id": 42,
    "number": 12345,
    "production_status": "RETIRED",
    "completeness": "COMPLETE",
    "has_instructions": true,
    "has_box": false,
    "is_factory_sealed": false,
    "owner_initial_estimate": 350,
    "owner_id": 99,
    "valuations": [
      {
        "id": 101,
        "user_id": 25,
        "value": 450,
        "currency": "PLN",
        "comment": "Excellent condition",
        "likes_count": 15,
        "created_at": "2025-10-20T14:23:45.123Z"
      }
    ],
    "valuations_count": 1,
    "total_likes": 15,
    "created_at": "2025-10-10T08:15:30.000Z",
    "updated_at": "2025-10-25T11:42:00.000Z"
  }
  ```

- **Błędy:**
  - **401 UNAUTHORIZED (Not Authenticated):**
    ```json
    {
      "detail": "Authentication credentials were not provided."
    }
    ```
  
  - **403 FORBIDDEN (BrickSetEditForbiddenError - nie właściciel):**
    ```json
    {
      "detail": "Only the owner can edit this BrickSet."
    }
    ```
  
  - **403 FORBIDDEN (BrickSetEditForbiddenError - RB-01 violation):**
    ```json
    {
      "detail": "BrickSet cannot be edited. Valuations from other users exist or owner's valuation has likes.",
      "reason": "other_users_valuations_exist"
    }
    ```
    lub
    ```json
    {
      "detail": "BrickSet cannot be edited. Valuations from other users exist or owner's valuation has likes.",
      "reason": "owner_valuation_has_likes"
    }
    ```

  - **404 NOT_FOUND (BrickSetNotFoundError):**
    ```json
    {
      "detail": "BrickSet with id 999 not found."
    }
    ```

  - **400 BAD_REQUEST (validation errors):**
    ```json
    {
      "has_box": ["This field is required to be a boolean."],
      "owner_initial_estimate": ["Ensure this value is less than or equal to 999999."]
    }
    ```
    lub
    ```json
    {
      "non_field_errors": ["At least one field must be provided for update."]
    }
    ```

## 5. Przepływ danych

1. **Odbiór żądania:** Klient wysyła PATCH /api/v1/bricksets/{id} z JWT token.
2. **Routing:** Django route resolver kieruje do `BrickSetUpdateView.patch()`.
3. **Autentykacja:** DRF middleware sprawdza JWT token (IsAuthenticated) → 401 jeśli brak/invalid.
4. **Walidacja path param:** DRF automatycznie waliduje że id jest intem (jeśli nie → 400).
5. **Walidacja body:** View deserializuje body przez `UpdateBrickSetSerializer`:
   - Sprawdza typy pól (has_box: bool, owner_initial_estimate: int/null)
   - Sprawdza zakresy (owner_initial_estimate: 1-999999 lub null)
   - Sprawdza że co najmniej jedno pole jest podane
   - Konwertuje do `UpdateBrickSetCommand`
6. **Logika biznesowa:** View wywołuje `UpdateBrickSetService.execute(brickset_id, command, request.user)`:
   - Service pobiera BrickSet przez `BrickSet.bricksets.prefetch_related('valuations').get(pk=brickset_id)`
   - Jeśli nie znaleziono → rzuca `BrickSetNotFoundError`
   - Sprawdza autoryzację: `if brickset.owner_id != requesting_user.id` → rzuca `BrickSetEditForbiddenError("not_owner")`
   - Sprawdza reguły RB-01 (czy edycja dozwolona):
     - Pobiera valuations (już prefetched)
     - Sprawdza czy istnieją valuations od innych użytkowników (user_id != owner_id)
     - Sprawdza czy valuation właściciela (jeśli istnieje) ma likes_count > 0
     - Jeśli którykolwiek warunek → rzuca `BrickSetEditForbiddenError("other_users_valuations_exist" lub "owner_valuation_has_likes")`
   - Aktualizuje dozwolone pola w `transaction.atomic()`:
     - `if command.has_box is not None: brickset.has_box = command.has_box`
     - `if command.owner_initial_estimate is not None: brickset.owner_initial_estimate = command.owner_initial_estimate`
     - `brickset.save(update_fields=[...])`
   - Odświeża valuations (już mamy prefetched) i buduje `BrickSetDetailDTO`
7. **Serializacja:** View serializuje DTO przez `BrickSetDetailSerializer` (reużycie).
8. **Response:** Zwraca 200 OK z JSON.
9. **Reakcja na błędy:** 
   - `BrickSetNotFoundError` → 404
   - `BrickSetEditForbiddenError` → 403 z detail + reason
   - `ValidationError` (serializer) → 400 z errors dict
   - `ValueError` (invalid id type) → 400 (DRF automatic)

## 6. Względy bezpieczeństwa

- **Uwierzytelnienie:** Endpoint wymaga autentykacji (`permission_classes = [IsAuthenticated]`) - tylko zalogowani użytkownicy.
- **Autoryzacja na poziomie właściciela:** 
  - Service sprawdza `brickset.owner_id == requesting_user.id`
  - Jeśli nie → 403 FORBIDDEN z komunikatem "Only the owner can edit this BrickSet."
  - Zapobiega edycji BrickSetów innych użytkowników nawet jeśli znają ID
- **Autoryzacja na poziomie reguł biznesowych (RB-01):**
  - Sprawdzenie czy istnieją valuations od innych użytkowników
  - Sprawdzenie czy valuation właściciela ma likes > 0
  - Oba warunki muszą być spełnione (brak valuations innych + (brak valuation właściciela LUB likes=0))
- **Ochrona danych:** 
  - Parametryzowane zapytania ORM zapobiegają SQL injection
  - DRF automatycznie waliduje typy parametrów URL i body
  - Tylko dozwolone pola można edytować (has_box, owner_initial_estimate)
  - Nie można edytować: number, production_status, completeness, has_instructions, is_factory_sealed, owner_id
- **Atomowość:** Update wykonywany w `transaction.atomic()` dla spójności
- **Rate limiting:** Rozważyć throttling (np. max 10 edits/minute per user) w przyszłości
- **Error disclosure:** 
  - 403 dla naruszenia reguł nie ujawnia szczegółów innych użytkowników (tylko reason: "other_users_valuations_exist")
  - 404 dla nieistniejącego BrickSetu nie ujawnia czy ID był kiedykolwiek używany
- **Sprawdzanie reguł biznesowych (RB-01):** 
  - Upewnij się, że nie można edytować BrickSet, jeśli już dokonano oceny przez innych użytkowników
  - Sprawdź czy valuation właściciela (jeśli istnieje) ma więcej niż 0 like'ów
  - Logika w service layer, nie w view
- **Logowanie błędów:** Mechanizm zapisywania prób naruszenia uprawnień (403) w Django logging dla audytu
- **CSRF:** DRF automatycznie obsługuje CSRF dla session-based auth; JWT nie wymaga CSRF token

## 7. Obsługa błędów

- **401 UNAUTHORIZED (Not Authenticated):**
  - Automatycznie obsługiwany przez DRF `IsAuthenticated` permission
  - Komunikat: "Authentication credentials were not provided."
  - Nie wymaga custom kodu

- **403 FORBIDDEN (BrickSetEditForbiddenError - nie właściciel):**
  - Rzucany przez service gdy `brickset.owner_id != requesting_user.id`
  - Komunikat: "Only the owner can edit this BrickSet."
  - Mapowany w view na Response 403

- **403 FORBIDDEN (BrickSetEditForbiddenError - RB-01 violation):**
  - Rzucany przez service gdy:
    - Istnieją valuations od innych użytkowników (`reason="other_users_valuations_exist"`)
    - Lub valuation właściciela ma likes > 0 (`reason="owner_valuation_has_likes"`)
  - Komunikat: "BrickSet cannot be edited. Valuations from other users exist or owner's valuation has likes."
  - Response zawiera `reason` field dla diagnostyki frontend
  - Mapowany w view na Response 403

- **404 NOT_FOUND (BrickSetNotFoundError):**
  - Rzucany przez service gdy `BrickSet.bricksets.get(pk=id)` rzuci `BrickSet.DoesNotExist`
  - Komunikat: "BrickSet with id {id} not found."
  - Mapowany w view na Response 404
  - **NIE** ujawniamy czy ID był kiedykolwiek używany

- **400 BAD_REQUEST (Validation errors):**
  - Automatycznie obsługiwany przez DRF serializer gdy:
    - has_box nie jest boolean
    - owner_initial_estimate nie jest int/null lub poza zakresem 1-999999
    - Pusty body (brak pól do update)
  - Response zawiera dict z errors per field
  - Nie wymaga custom exception handling w view

- **500 INTERNAL_SERVER_ERROR:**
  - Dla niespodziewanych błędów (nie powinny wystąpić w normalnych warunkach)
  - Logowanie z traceback dla diagnostyki
  - Generic error message dla użytkownika (nie ujawniamy szczegółów systemu)

## 8. Rozważania dotyczące wydajności

- **Query optimization:**
  - `prefetch_related('valuations')` dla ForeignKey reverse relation - pobiera wszystkie valuations w 1 dodatkowym query
  - Total queries: 2 (1 dla BrickSet, 1 dla valuations) - identycznie jak GET detail
  - Po update: reużycie już prefetched valuations (bez dodatkowego query)

- **Indexes:**
  - Primary key (id) już indeksowany automatycznie
  - `owner_id` już indeksowany (ForeignKey automatic index)
  - valuations.brickset_id już indeksowany (`valuation_brickset_idx`)
  - valuations.user_id już indeksowany (`valuation_user_idx`)

- **Transaction handling:**
  - Update w `transaction.atomic()` dla atomowości
  - `save(update_fields=['has_box', 'owner_initial_estimate'])` - tylko zmienione pola, nie cały obiekt
  - Minimalizuje lock time na rekordzie

- **Authorization checks:**
  - Sprawdzenie owner_id w memory (już fetched object) - brak dodatkowego query
  - Sprawdzenie RB-01 rules na prefetched valuations - brak dodatkowych queries
  - Total business logic validation: 0 dodatkowych queries

- **Caching:**
  - Po update: invalidacja cache dla GET detail endpoint (jeśli istnieje)
  - Cache key: `brickset_detail:{id}:{updated_at.timestamp()}`
  - Rozważyć Redis cache w przyszłości

- **Memory:**
  - DTOs z `slots=True` minimalizują overhead
  - Prefetch valuations nie stanowi problemu dla rozsądnej liczby (<1000 per set)

## 9. Struktura plików

```
backend/catalog/
├── exceptions.py                              # MODYFIKACJA: dodać BrickSetEditForbiddenError
├── serializers/
│   ├── __init__.py                            # MODYFIKACJA: eksport UpdateBrickSetSerializer
│   ├── brickset_list.py                       # ISTNIEJĄCY
│   ├── brickset_create.py                     # ISTNIEJĄCY
│   ├── brickset_detail.py                     # ISTNIEJĄCY: reużycie BrickSetDetailSerializer
│   ├── brickset_update.py                     # NOWY: UpdateBrickSetSerializer
│   └── tests/
│       ├── test_brickset_list_serializer.py   # ISTNIEJĄCY
│       ├── test_brickset_create_serializer.py # ISTNIEJĄCY
│       ├── test_brickset_detail_serializer.py # ISTNIEJĄCY
│       └── test_brickset_update_serializer.py # NOWY: testy UpdateBrickSetSerializer
├── services/
│   ├── __init__.py                            # MODYFIKACJA: eksport UpdateBrickSetService
│   ├── brickset_list_service.py               # ISTNIEJĄCY
│   ├── brickset_create_service.py             # ISTNIEJĄCY
│   ├── brickset_detail_service.py             # ISTNIEJĄCY
│   ├── brickset_update_service.py             # NOWY: UpdateBrickSetService z execute()
│   └── tests/
│       ├── test_brickset_list_service.py      # ISTNIEJĄCY
│       ├── test_brickset_create_service.py    # ISTNIEJĄCY
│       ├── test_brickset_detail_service.py    # ISTNIEJĄCY
│       └── test_brickset_update_service.py    # NOWY: testy UpdateBrickSetService
├── views/
│   ├── __init__.py                            # MODYFIKACJA: eksport BrickSetUpdateView
│   ├── brickset_list.py                       # ISTNIEJĄCY: BrickSetListView (GET + POST)
│   ├── brickset_detail.py                     # ISTNIEJĄCY: BrickSetDetailView (GET)
│   ├── brickset_update.py                     # NOWY: BrickSetUpdateView (PATCH)
│   └── tests/
│       ├── __init__.py                        # ISTNIEJĄCY
│       ├── test_brickset_list_view.py         # ISTNIEJĄCY
│       ├── test_brickset_create_view.py       # ISTNIEJĄCY
│       ├── test_brickset_detail_view.py       # ISTNIEJĄCY
│       └── test_brickset_update_view.py       # NOWY: testy API PATCH
└── urls.py                                    # MODYFIKACJA: dodać routing PATCH /bricksets/<int:pk>

backend/datastore/domains/
└── catalog_dto.py                             # ISTNIEJĄCY: UpdateBrickSetCommand już zdefiniowany, BrickSetDetailDTO reużycie
```

**Uwaga**: Endpoint wykorzystuje:
- **Istniejące modele i DTO** (BrickSet, Valuation, UpdateBrickSetCommand, BrickSetDetailDTO)
- **Istniejący exception** (BrickSetNotFoundError) + **nowy** (BrickSetEditForbiddenError)
- **Istniejący serializer** (BrickSetDetailSerializer dla response) + **nowy** (UpdateBrickSetSerializer dla input)
- **Nowe komponenty**: update serializer, update service, update view
- **Wzorce z detail/create endpoints**: struktura service/serializer/view/exceptions identyczna

## 10. Etapy wdrożenia

### Krok 1: Domain Exception
- [ ] Zaktualizować `catalog/exceptions.py`:
  ```python
  class BrickSetEditForbiddenError(Exception):
      """Raised when BrickSet edit violates business rules (RB-01) or authorization."""
      
      def __init__(self, reason: str) -> None:
          """Initialize with reason code for diagnostics.
          
          Args:
              reason: One of:
                  - "not_owner": User is not the BrickSet owner
                  - "other_users_valuations_exist": Valuations from other users exist
                  - "owner_valuation_has_likes": Owner's valuation has likes > 0
          """
          messages = {
              "not_owner": "Only the owner can edit this BrickSet.",
              "other_users_valuations_exist": "BrickSet cannot be edited. Valuations from other users exist or owner's valuation has likes.",
              "owner_valuation_has_likes": "BrickSet cannot be edited. Valuations from other users exist or owner's valuation has likes.",
          }
          super().__init__(messages.get(reason, "BrickSet edit forbidden."))
          self.reason = reason
          self.message = messages.get(reason, "BrickSet edit forbidden.")
  ```

### Krok 2: Update Serializer
- [ ] Utworzyć `catalog/serializers/brickset_update.py`:
  - Klasa `UpdateBrickSetSerializer(serializers.Serializer)`:
    - Pola: `has_box` (BooleanField, required=False), `owner_initial_estimate` (IntegerField, required=False, allow_null=True, min_value=1, max_value=999999)
    - Metoda `validate()`: sprawdza czy co najmniej jedno pole podane (jeśli nie → ValidationError)
    - Metoda `to_command() -> UpdateBrickSetCommand`: konwersja validated_data do Command
- [ ] Dodać testy `catalog/serializers/tests/test_brickset_update_serializer.py`:
  - `test_validates_has_box_field`
  - `test_validates_owner_initial_estimate_range`
  - `test_allows_null_owner_initial_estimate`
  - `test_requires_at_least_one_field`
  - `test_rejects_empty_payload`
  - `test_accepts_only_has_box`
  - `test_accepts_only_owner_initial_estimate`
  - `test_accepts_both_fields`
  - `test_to_command_returns_correct_command_object`
  - `test_to_command_raises_if_not_validated`
  - `test_rejects_owner_initial_estimate_below_min`
  - `test_rejects_owner_initial_estimate_above_max`
  - `test_rejects_has_box_non_boolean`

### Krok 3: Update Service
- [ ] Utworzyć `catalog/services/brickset_update_service.py`:
  - Klasa `UpdateBrickSetService`:
    - Metoda `execute(brickset_id: int, command: UpdateBrickSetCommand, requesting_user: User) -> BrickSetDetailDTO`
    - Fetch BrickSet z `prefetch_related('valuations')`
    - Catch `BrickSet.DoesNotExist` → raise `BrickSetNotFoundError`
    - **Authorization check**: `if brickset.owner_id != requesting_user.id` → raise `BrickSetEditForbiddenError("not_owner")`
    - **RB-01 check**:
      - Get all valuations (already prefetched)
      - Check if any valuation where `user_id != brickset.owner_id` → raise `BrickSetEditForbiddenError("other_users_valuations_exist")`
      - Check if owner valuation exists with `likes_count > 0` → raise `BrickSetEditForbiddenError("owner_valuation_has_likes")`
    - **Update in transaction**:
      - `with transaction.atomic():`
      - Update only provided fields: `if command.has_box is not None: brickset.has_box = command.has_box`
      - Update only provided fields: `if command.owner_initial_estimate is not None: brickset.owner_initial_estimate = command.owner_initial_estimate`
      - `brickset.save(update_fields=[list of changed fields])`
    - Reużyć logikę z `BrickSetDetailService._build_dto()` lub bezpośrednio map do `BrickSetDetailDTO`
    - Return DTO
- [ ] Dodać testy `catalog/services/tests/test_brickset_update_service.py`:
  - **Sukces scenarios:**
    - `test_execute_updates_has_box_only`
    - `test_execute_updates_owner_initial_estimate_only`
    - `test_execute_updates_both_fields`
    - `test_execute_sets_owner_initial_estimate_to_null`
    - `test_execute_returns_updated_brickset_dto`
    - `test_execute_updates_updated_at_timestamp`
    - `test_execute_preserves_other_fields`
  - **Authorization errors:**
    - `test_execute_raises_not_found_for_nonexistent_id`
    - `test_execute_raises_forbidden_when_not_owner`
  - **RB-01 errors:**
    - `test_execute_raises_forbidden_when_other_users_valuations_exist`
    - `test_execute_raises_forbidden_when_owner_valuation_has_likes`
    - `test_execute_allows_edit_when_owner_valuation_has_zero_likes`
    - `test_execute_allows_edit_when_only_owner_valuation_exists_no_likes`
    - `test_execute_allows_edit_when_no_valuations_exist`
  - **Edge cases:**
    - `test_execute_correctly_identifies_owner_vs_other_valuations`
    - `test_execute_uses_prefetch_related_efficiently` (query count)

### Krok 4: Update View
- [ ] Utworzyć `catalog/views/brickset_update.py`:
  - `BrickSetUpdateView(GenericAPIView)` z metodą `patch()`:
    - `permission_classes = [IsAuthenticated]`
    - `serializer_class = BrickSetDetailSerializer` (dla response)
    - Get brickset_id z kwargs (`pk`)
    - Deserialize body przez `UpdateBrickSetSerializer`
    - Call `serializer.is_valid(raise_exception=True)`
    - Convert to command: `command = serializer.to_command()`
    - Call `UpdateBrickSetService().execute(pk, command, request.user)`
    - Catch `BrickSetNotFoundError` → Response 404
    - Catch `BrickSetEditForbiddenError` → Response 403 z `detail` + `reason`
    - Serialize updated DTO przez `BrickSetDetailSerializer` i return 200
- [ ] Dodać testy `catalog/views/tests/test_brickset_update_view.py`:
  - **Sukces:**
    - `test_patch_updates_has_box_returns_ok`
    - `test_patch_updates_owner_initial_estimate_returns_ok`
    - `test_patch_updates_both_fields_returns_ok`
    - `test_patch_sets_estimate_to_null_returns_ok`
    - `test_patch_response_structure_matches_detail_dto`
    - `test_patch_response_includes_updated_timestamp`
    - `test_patch_returns_full_brickset_with_valuations`
  - **Authentication:**
    - `test_patch_unauthenticated_returns_unauthorized`
  - **Authorization:**
    - `test_patch_not_owner_returns_forbidden`
    - `test_patch_forbidden_response_includes_reason_not_owner`
  - **RB-01 violations:**
    - `test_patch_with_other_users_valuations_returns_forbidden`
    - `test_patch_with_owner_valuation_likes_returns_forbidden`
    - `test_patch_forbidden_response_includes_reason_field`
    - `test_patch_allowed_when_owner_valuation_zero_likes`
    - `test_patch_allowed_when_no_valuations`
  - **Not found:**
    - `test_patch_nonexistent_id_returns_not_found`
  - **Validation:**
    - `test_patch_empty_body_returns_bad_request`
    - `test_patch_invalid_has_box_type_returns_bad_request`
    - `test_patch_owner_initial_estimate_out_of_range_returns_bad_request`
    - `test_patch_invalid_id_type_returns_not_found`

### Krok 5: URL Routing
- [ ] Zaktualizować `catalog/urls.py`:
  ```python
  from catalog.views.brickset_list import BrickSetListView
  from catalog.views.brickset_detail import BrickSetDetailView
  from catalog.views.brickset_update import BrickSetUpdateView
  
  urlpatterns = [
      path("bricksets", BrickSetListView.as_view(), name="brickset-list"),  # GET list + POST create
      path("bricksets/<int:pk>", BrickSetDetailView.as_view(), name="brickset-detail"),  # GET detail
      path("bricksets/<int:pk>", BrickSetUpdateView.as_view(), name="brickset-update"),  # PATCH update
  ]
  ```
  **Uwaga**: DRF routing pozwala na duplicate paths z różnymi metodami HTTP. Alternatywnie można:
  - Połączyć `BrickSetDetailView` i `BrickSetUpdateView` w jeden widok z metodami `get()` i `patch()`
  - Użyć `ViewSet` (ale dla prostoty pozostajemy przy oddzielnych views jak w istniejącym kodzie)

### Krok 6: Integration i Eksporty
- [ ] Zaktualizować `catalog/exceptions.py` - dodać BrickSetEditForbiddenError
- [ ] Zaktualizować `catalog/serializers/__init__.py` - eksport UpdateBrickSetSerializer
- [ ] Zaktualizować `catalog/services/__init__.py` - eksport UpdateBrickSetService
- [ ] Zaktualizować `catalog/views/__init__.py` - eksport BrickSetUpdateView

### Krok 7: Testy E2E i Walidacja
- [ ] Uruchomić `./bin/test_backend.sh` - coverage min. 90%
- [ ] Uruchomić `./bin/lint_backend.sh` - zero błędów
- [ ] Test ręczny flow:
  - PATCH jako owner bez valuations → 200
  - PATCH jako owner z own valuation (0 likes) → 200
  - PATCH jako owner z own valuation (>0 likes) → 403
  - PATCH jako owner z other users valuations → 403
  - PATCH jako non-owner → 403
  - PATCH unauthenticated → 401
  - PATCH nonexistent id → 404
  - PATCH empty body → 400
  - PATCH invalid field types → 400
- [ ] Sprawdzić liczba zapytań DB (powinno być 2: BrickSet+valuations prefetch)
- [ ] Sprawdzić że updated_at jest aktualizowany

### Krok 8: Dokumentacja i Review
- [ ] Zaktualizować README.md z przykładami curl dla PATCH endpoint
- [ ] Code review
- [ ] Merge do development (branch: BV-12-Remainingcatalog-endpoints lub similar)

## 11. Scenariusze testowe (szczegółowe)

### Serializer Tests (`test_brickset_update_serializer.py`)
- `test_serializer_validates_has_box_true`
- `test_serializer_validates_has_box_false`
- `test_serializer_rejects_has_box_non_boolean`
- `test_serializer_validates_owner_initial_estimate_min_value`
- `test_serializer_validates_owner_initial_estimate_max_value`
- `test_serializer_rejects_owner_initial_estimate_below_min`
- `test_serializer_rejects_owner_initial_estimate_above_max`
- `test_serializer_accepts_null_owner_initial_estimate`
- `test_serializer_requires_at_least_one_field`
- `test_serializer_rejects_empty_data`
- `test_serializer_accepts_only_has_box`
- `test_serializer_accepts_only_owner_initial_estimate`
- `test_serializer_accepts_both_fields`
- `test_to_command_returns_update_brickset_command`
- `test_to_command_includes_provided_fields_only`
- `test_to_command_raises_assertion_error_if_not_validated`
- `test_serializer_ignores_extra_fields` (strict validation)

### Service Tests (`test_brickset_update_service.py`)
- `test_execute_updates_has_box_from_true_to_false`
- `test_execute_updates_has_box_from_false_to_true`
- `test_execute_updates_owner_initial_estimate_to_value`
- `test_execute_updates_owner_initial_estimate_to_null`
- `test_execute_updates_both_fields_simultaneously`
- `test_execute_preserves_unchanged_fields`
- `test_execute_updates_updated_at_timestamp`
- `test_execute_does_not_change_created_at`
- `test_execute_returns_brickset_detail_dto`
- `test_execute_dto_includes_all_required_fields`
- `test_execute_dto_includes_valuations_list`
- `test_execute_dto_aggregates_match_actual_data`
- `test_execute_raises_not_found_for_nonexistent_id`
- `test_execute_raises_forbidden_when_user_not_owner`
- `test_execute_forbidden_reason_is_not_owner`
- `test_execute_raises_forbidden_with_other_users_valuations`
- `test_execute_forbidden_reason_is_other_users_valuations_exist`
- `test_execute_raises_forbidden_when_owner_valuation_has_likes`
- `test_execute_forbidden_reason_is_owner_valuation_has_likes`
- `test_execute_allows_edit_when_no_valuations`
- `test_execute_allows_edit_when_owner_valuation_zero_likes`
- `test_execute_allows_edit_when_only_owner_valuation_no_likes`
- `test_execute_correctly_identifies_owner_valuation`
- `test_execute_correctly_identifies_other_users_valuations`
- `test_execute_uses_transaction_atomic`
- `test_execute_uses_prefetch_related_for_valuations` (query count ≤2)
- `test_execute_uses_save_with_update_fields`

### View Tests (`test_brickset_update_view.py`)
- `test_patch_authenticated_owner_updates_has_box`
- `test_patch_authenticated_owner_updates_estimate`
- `test_patch_authenticated_owner_updates_both_fields`
- `test_patch_authenticated_owner_sets_estimate_to_null`
- `test_patch_returns_status_ok`
- `test_patch_response_content_type_is_json`
- `test_patch_response_structure_matches_detail_dto`
- `test_patch_response_includes_updated_timestamp`
- `test_patch_response_includes_all_brickset_fields`
- `test_patch_response_includes_valuations_array`
- `test_patch_response_includes_aggregates`
- `test_patch_unauthenticated_returns_unauthorized`
- `test_patch_unauthorized_response_has_detail`
- `test_patch_non_owner_returns_forbidden`
- `test_patch_forbidden_not_owner_includes_reason`
- `test_patch_with_other_users_valuations_returns_forbidden`
- `test_patch_forbidden_other_users_includes_reason`
- `test_patch_with_owner_valuation_likes_returns_forbidden`
- `test_patch_forbidden_owner_likes_includes_reason`
- `test_patch_allowed_when_no_valuations`
- `test_patch_allowed_when_owner_valuation_zero_likes`
- `test_patch_nonexistent_id_returns_not_found`
- `test_patch_not_found_response_includes_detail`
- `test_patch_invalid_id_type_returns_not_found_or_bad_request`
- `test_patch_empty_body_returns_bad_request`
- `test_patch_validation_error_includes_field_errors`
- `test_patch_invalid_has_box_type_returns_bad_request`
- `test_patch_owner_initial_estimate_below_min_returns_bad_request`
- `test_patch_owner_initial_estimate_above_max_returns_bad_request`
- `test_patch_query_count_is_optimized` (≤2 queries)

## 12. Przykłady użycia

### Sukces - aktualizacja has_box (200 OK)
```bash
curl -X PATCH https://api.example.com/api/v1/bricksets/1 \
  -H "Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"has_box": false}'

# Response:
# HTTP/1.1 200 OK
# Content-Type: application/json
# {
#   "id": 1,
#   "number": 10001,
#   "production_status": "ACTIVE",
#   "completeness": "COMPLETE",
#   "has_instructions": true,
#   "has_box": false,  # UPDATED
#   "is_factory_sealed": false,
#   "owner_initial_estimate": 250,
#   "owner_id": 15,
#   "valuations": [],
#   "valuations_count": 0,
#   "total_likes": 0,
#   "created_at": "2025-10-15T10:30:00.000Z",
#   "updated_at": "2025-10-25T11:42:00.000Z"  # UPDATED
# }
```

### Sukces - aktualizacja owner_initial_estimate (200 OK)
```bash
curl -X PATCH https://api.example.com/api/v1/bricksets/42 \
  -H "Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"owner_initial_estimate": 450}'

# Response:
# HTTP/1.1 200 OK
# {
#   "id": 42,
#   "owner_initial_estimate": 450,  # UPDATED
#   "updated_at": "2025-10-25T11:45:00.000Z",  # UPDATED
#   ... (rest of fields)
# }
```

### Sukces - aktualizacja obu pól (200 OK)
```bash
curl -X PATCH https://api.example.com/api/v1/bricksets/42 \
  -H "Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "has_box": true,
    "owner_initial_estimate": 500
  }'

# Response: 200 OK with updated BrickSetDetailDTO
```

### Sukces - ustawienie owner_initial_estimate na null (200 OK)
```bash
curl -X PATCH https://api.example.com/api/v1/bricksets/42 \
  -H "Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"owner_initial_estimate": null}'

# Response:
# HTTP/1.1 200 OK
# {
#   "id": 42,
#   "owner_initial_estimate": null,  # CLEARED
#   ... (rest of fields)
# }
```

### Błąd - brak autentykacji (401 Unauthorized)
```bash
curl -X PATCH https://api.example.com/api/v1/bricksets/42 \
  -H "Content-Type: application/json" \
  -d '{"has_box": false}'

# Response:
# HTTP/1.1 401 Unauthorized
# Content-Type: application/json
# {
#   "detail": "Authentication credentials were not provided."
# }
```

### Błąd - nie właściciel (403 Forbidden)
```bash
curl -X PATCH https://api.example.com/api/v1/bricksets/42 \
  -H "Authorization: Token <different_user_token>" \
  -H "Content-Type: application/json" \
  -d '{"has_box": false}'

# Response:
# HTTP/1.1 403 Forbidden
# Content-Type: application/json
# {
#   "detail": "Only the owner can edit this BrickSet.",
#   "reason": "not_owner"
# }
```

### Błąd - valuations od innych użytkowników (403 Forbidden)
```bash
curl -X PATCH https://api.example.com/api/v1/bricksets/42 \
  -H "Authorization: Token <owner_token>" \
  -H "Content-Type: application/json" \
  -d '{"has_box": false}'

# Response (gdy istnieją valuations od innych):
# HTTP/1.1 403 Forbidden
# Content-Type: application/json
# {
#   "detail": "BrickSet cannot be edited. Valuations from other users exist or owner's valuation has likes.",
#   "reason": "other_users_valuations_exist"
# }
```

### Błąd - valuation właściciela ma likes (403 Forbidden)
```bash
curl -X PATCH https://api.example.com/api/v1/bricksets/42 \
  -H "Authorization: Token <owner_token>" \
  -H "Content-Type: application/json" \
  -d '{"has_box": false}'

# Response (gdy owner valuation ma likes > 0):
# HTTP/1.1 403 Forbidden
# Content-Type: application/json
# {
#   "detail": "BrickSet cannot be edited. Valuations from other users exist or owner's valuation has likes.",
#   "reason": "owner_valuation_has_likes"
# }
```

### Błąd - nieistniejący BrickSet (404 Not Found)
```bash
curl -X PATCH https://api.example.com/api/v1/bricksets/999999 \
  -H "Authorization: Token <valid_token>" \
  -H "Content-Type: application/json" \
  -d '{"has_box": false}'

# Response:
# HTTP/1.1 404 Not Found
# Content-Type: application/json
# {
#   "detail": "BrickSet with id 999999 not found."
# }
```

### Błąd - pusty body (400 Bad Request)
```bash
curl -X PATCH https://api.example.com/api/v1/bricksets/42 \
  -H "Authorization: Token <valid_token>" \
  -H "Content-Type: application/json" \
  -d '{}'

# Response:
# HTTP/1.1 400 Bad Request
# Content-Type: application/json
# {
#   "non_field_errors": ["At least one field must be provided for update."]
# }
```

### Błąd - nieprawidłowy typ pola (400 Bad Request)
```bash
curl -X PATCH https://api.example.com/api/v1/bricksets/42 \
  -H "Authorization: Token <valid_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "has_box": "yes",
    "owner_initial_estimate": "expensive"
  }'

# Response:
# HTTP/1.1 400 Bad Request
# Content-Type: application/json
# {
#   "has_box": ["Must be a valid boolean."],
#   "owner_initial_estimate": ["A valid integer is required."]
# }
```

### Błąd - wartość poza zakresem (400 Bad Request)
```bash
curl -X PATCH https://api.example.com/api/v1/bricksets/42 \
  -H "Authorization: Token <valid_token>" \
  -H "Content-Type: application/json" \
  -d '{"owner_initial_estimate": 1000000}'

# Response:
# HTTP/1.1 400 Bad Request
# Content-Type: application/json
# {
#   "owner_initial_estimate": ["Ensure this value is less than or equal to 999999."]
# }
```

---

**KLUCZOWE PUNKTY**:
- Endpoint jest **authenticated** (`IsAuthenticated`) + **owner-only** (service sprawdza owner_id)
- Wykorzystuje **istniejące DTO** (`UpdateBrickSetCommand`, `BrickSetDetailDTO`) + nowy exception (`BrickSetEditForbiddenError`)
- **Service pattern** identyczny jak w `BrickSetDetailService` i `CreateBrickSetService`
- **Serializer pattern** z `to_command()` jak w `CreateBrickSetSerializer`
- **View pattern** identyczny jak w `BrickSetDetailView` (GenericAPIView z metodą HTTP)
- **RB-01 validation** w service layer: sprawdza valuations od innych + owner valuation likes
- **Authorization** na dwóch poziomach: owner check + business rules check
- **Query optimization** przez `prefetch_related('valuations')` - total 2 queries (jak GET detail)
- **Atomowość** przez `transaction.atomic()` + `save(update_fields=[...])`
- **Response** zwraca pełny `BrickSetDetailDTO` (jak GET detail) - frontend ma wszystkie dane po update
- **Error handling** przez domain exceptions + mapowanie w view na HTTP codes + reason field dla diagnostyki
- Pre-commit: `./bin/lint_backend.sh` + `./bin/test_backend.sh` (coverage min. 90%)

Plan wdrożenia zapewnia zgodność ze standardami projektu, wzorcami z istniejących catalog endpoints oraz dobrymi praktykami Django/DRF. Wszystkie komponenty są przetestowane według wzorca unittest.TestCase z descriptive test names (bez numerów w nazwach).
