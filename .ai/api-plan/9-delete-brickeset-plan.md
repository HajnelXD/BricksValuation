# API Endpoint Implementation Plan: DELETE /api/v1/bricksets/{id}

## 1. Przegląd punktu końcowego

Endpoint służy do usunięcia istniejącego BrickSet. Usunięcie jest dozwolone tylko dla właściciela rekordu oraz tylko w przypadku, gdy nie istnieją oceny od innych użytkowników, a ocena właściciela (jeśli istnieje) ma 0 like'ów (te same reguły RB-01 co przy edycji). W przypadku pomyślnego wykonania, zwracany jest kod 204 bez treści.

**Wzorce implementacyjne**: Endpoint wykorzystuje te same wzorce co `PATCH /api/v1/bricksets/{id}`:
- Service layer z metodą `execute()` dla logiki biznesowej
- Domain exceptions (`BrickSetNotFoundError`, `BrickSetEditForbiddenError`) dla kontrolowanych błędów - **reużycie** exception z PATCH (delete ma te same reguły RB-01)
- GenericAPIView dla obsługi HTTP (wzór: `BrickSetDetailUpdateView`)
- Brak DTO w response (204 No Content)
- Brak Command (DELETE nie wymaga request body)
- IsAuthenticated permission (tylko właściciel może usunąć)

## 2. Szczegóły żądania

- **Metoda HTTP:** DELETE
- **URL:** /api/v1/bricksets/{id}
- **Parametry:**
  - **Path parameter (wymagany):**
    - `id` (int) – unikalny identyfikator BrickSetu (primary key)
  - **Headers:** 
    - `Authorization: Token <jwt_token>` (wymagany - endpoint wymaga IsAuthenticated)
- **Request Body:** Brak (DELETE nie przyjmuje body)

Przykładowe żądanie:
```bash
DELETE /api/v1/bricksets/42
Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 3. Wykorzystywane typy

- **Command Model:** Brak (DELETE nie wymaga command - tylko ID z path)

- **DTO Models:** Brak (response 204 No Content nie zawiera body)

- **Service Layer:**
  - `DeleteBrickSetService` - nowa klasa z metodą `execute(brickset_id: int, requesting_user: User) -> None`

- **Serializers:** Brak (no request/response body)

- **Exceptions (reużycie istniejących):**
  - `BrickSetNotFoundError` - już istniejący
  - `BrickSetEditForbiddenError` - **reużycie** z PATCH (te same reguły RB-01 dla delete)

- **View:**
  - `BrickSetDetailUpdateView` - **modyfikacja** istniejącego widoku z dodaniem metody `delete()`

## 4. Szczegóły odpowiedzi

- **Sukces (204 NO CONTENT):**
  Brak body w odpowiedzi. BrickSet został pomyślnie usunięty wraz z powiązanymi valuations (CASCADE).

  ```http
  HTTP/1.1 204 No Content
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
      "detail": "Only the owner can delete this BrickSet.",
      "reason": "not_owner"
    }
    ```
  
  - **403 FORBIDDEN (BrickSetEditForbiddenError - RB-01 violation):**
    ```json
    {
      "detail": "BrickSet cannot be deleted. Valuations from other users exist or owner's valuation has likes.",
      "reason": "other_users_valuations_exist"
    }
    ```
    lub
    ```json
    {
      "detail": "BrickSet cannot be deleted. Valuations from other users exist or owner's valuation has likes.",
      "reason": "owner_valuation_has_likes"
    }
    ```

  - **404 NOT_FOUND (BrickSetNotFoundError):**
    ```json
    {
      "detail": "BrickSet with id 999 not found."
    }
    ```

## 5. Przepływ danych

1. **Odbiór żądania:** Klient wysyła DELETE /api/v1/bricksets/{id} z JWT token.
2. **Routing:** Django route resolver kieruje do `BrickSetDetailUpdateView.delete()`.
3. **Autentykacja:** DRF middleware sprawdza JWT token (IsAuthenticated) → 401 jeśli brak/invalid.
4. **Walidacja path param:** DRF automatycznie waliduje że id jest intem (jeśli nie → 404).
5. **Logika biznesowa:** View wywołuje `DeleteBrickSetService.execute(brickset_id, request.user)`:
   - Service pobiera BrickSet przez `BrickSet.bricksets.prefetch_related('valuations').get(pk=brickset_id)`
   - Jeśli nie znaleziono → rzuca `BrickSetNotFoundError`
   - Sprawdza autoryzację: `if brickset.owner_id != requesting_user.id` → rzuca `BrickSetEditForbiddenError("not_owner")`
   - Sprawdza reguły RB-01 (identycznie jak w PATCH):
     - Pobiera valuations (już prefetched)
     - Sprawdza czy istnieją valuations od innych użytkowników (user_id != owner_id)
     - Sprawdza czy valuation właściciela (jeśli istnieje) ma likes_count > 0
     - Jeśli którykolwiek warunek → rzuca `BrickSetEditForbiddenError("other_users_valuations_exist" lub "owner_valuation_has_likes")`
   - Usuwa BrickSet w `transaction.atomic()`:
     - `brickset.delete()` - CASCADE automatycznie usuwa powiązane Valuations i Likes (FK on_delete=CASCADE)
6. **Response:** Zwraca 204 No Content (brak body).
7. **Reakcja na błędy:** 
   - `BrickSetNotFoundError` → 404
   - `BrickSetEditForbiddenError` → 403 z detail + reason
   - `ValueError` (invalid id type) → 404 (DRF automatic)

## 6. Względy bezpieczeństwa

- **Uwierzytelnienie:** Endpoint wymaga autentykacji (`permission_classes = [IsAuthenticated]`) - tylko zalogowani użytkownicy.
- **Autoryzacja na poziomie właściciela:** 
  - Service sprawdza `brickset.owner_id == requesting_user.id`
  - Jeśli nie → 403 FORBIDDEN z komunikatem "Only the owner can delete this BrickSet."
  - Zapobiega usuwaniu BrickSetów innych użytkowników nawet jeśli znają ID
- **Autoryzacja na poziomie reguł biznesowych (RB-01):**
  - Identyczne zasady jak PATCH: sprawdzenie czy istnieją valuations od innych użytkowników
  - Sprawdzenie czy valuation właściciela ma likes > 0
  - Oba warunki muszą być spełnione (brak valuations innych + (brak valuation właściciela LUB likes=0))
- **CASCADE deletion:** 
  - Django ORM automatycznie usuwa powiązane Valuations i Likes (FK on_delete=CASCADE)
  - Zachowuje referential integrity bez orphaned records
- **Ochrona danych:** 
  - Parametryzowane zapytania ORM zapobiegają SQL injection
  - DRF automatycznie waliduje typy parametrów URL
  - Nieodwracalna operacja wymaga podwójnej walidacji (auth + RB-01)
- **Atomowość:** Delete wykonywany w `transaction.atomic()` dla spójności
- **Rate limiting:** Rozważyć throttling (np. max 5 deletes/minute per user) w przyszłości
- **Error disclosure:** 
  - 403 dla naruszenia reguł nie ujawnia szczegółów innych użytkowników (tylko reason)
  - 404 dla nieistniejącego BrickSetu nie ujawnia czy ID był kiedykolwiek używany
- **Audit logging:** Mechanizm zapisywania operacji DELETE w Django logging dla audytu (kto, kiedy, co usunął)
- **CSRF:** DRF automatycznie obsługuje CSRF dla session-based auth; JWT nie wymaga CSRF token

## 7. Obsługa błędów

- **401 UNAUTHORIZED (Not Authenticated):**
  - Automatycznie obsługiwany przez DRF `IsAuthenticated` permission
  - Komunikat: "Authentication credentials were not provided."
  - Nie wymaga custom kodu

- **403 FORBIDDEN (BrickSetEditForbiddenError - nie właściciel):**
  - Rzucany przez service gdy `brickset.owner_id != requesting_user.id`
  - Komunikat: "Only the owner can delete this BrickSet."
  - Mapowany w view na Response 403

- **403 FORBIDDEN (BrickSetEditForbiddenError - RB-01 violation):**
  - Rzucany przez service gdy:
    - Istnieją valuations od innych użytkowników (`reason="other_users_valuations_exist"`)
    - Lub valuation właściciela ma likes > 0 (`reason="owner_valuation_has_likes"`)
  - Komunikat: "BrickSet cannot be deleted. Valuations from other users exist or owner's valuation has likes."
  - Response zawiera `reason` field dla diagnostyki frontend
  - Mapowany w view na Response 403

- **404 NOT_FOUND (BrickSetNotFoundError):**
  - Rzucany przez service gdy `BrickSet.bricksets.get(pk=id)` rzuci `BrickSet.DoesNotExist`
  - Komunikat: "BrickSet with id {id} not found."
  - Mapowany w view na Response 404
  - **NIE** ujawniamy czy ID był kiedykolwiek używany

- **500 INTERNAL_SERVER_ERROR:**
  - Dla niespodziewanych błędów (nie powinny wystąpić w normalnych warunkach)
  - Logowanie z traceback dla diagnostyki
  - Generic error message dla użytkownika (nie ujawniamy szczegółów systemu)

## 8. Rozważania dotyczące wydajności

- **Query optimization:**
  - `prefetch_related('valuations')` dla ForeignKey reverse relation - pobiera wszystkie valuations w 1 dodatkowym query
  - Total queries: 2 (1 dla BrickSet, 1 dla valuations) - identycznie jak GET detail i PATCH
  - CASCADE delete: Django wykonuje w ramach tej samej transakcji, efektywnie

- **Indexes:**
  - Primary key (id) już indeksowany automatycznie
  - `owner_id` już indeksowany (ForeignKey automatic index)
  - valuations.brickset_id już indeksowany (`valuation_brickset_idx`)
  - valuations.user_id już indeksowany (`valuation_user_idx`)

- **Transaction handling:**
  - Delete w `transaction.atomic()` dla atomowości
  - CASCADE delete jest optymalne (single transaction)
  - Minimalizuje lock time na rekordach

- **Authorization checks:**
  - Sprawdzenie owner_id w memory (już fetched object) - brak dodatkowego query
  - Sprawdzenie RB-01 rules na prefetched valuations - brak dodatkowych queries
  - Total business logic validation: 0 dodatkowych queries

- **Cascade impact:**
  - Django ORM CASCADE delete jest zoptymalizowane
  - Dla rozsądnej liczby valuations (<1000 per set) nie stanowi problemu
  - W przyszłości: rozważyć soft delete jeśli audit trail wymagany

- **Memory:**
  - Prefetch valuations nie stanowi problemu dla rozsądnej liczby (<1000 per set)
  - Brak DTO = brak alokacji pamięci na response object



