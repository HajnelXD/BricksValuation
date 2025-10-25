# API Endpoint Implementation Plan: DELETE /api/v1/valuations/{valuation_id}/likes

## 1. Przegląd punktu końcowego

Endpoint umożliwia usunięcie polubienia (like) wyceny przez zalogowanego użytkownika. Zwraca status 204 No Content bez body. Endpoint wykorzystuje identyczne wzorce implementacyjne co `DELETE /api/v1/bricksets/{id}` - service layer, Command object, GenericAPIView z metodą delete() i obsługę błędów.

**Wzorce implementacyjne**: Endpoint wykorzystuje identyczne wzorce co catalog delete endpoint:
- Service layer z metodą `execute(command: UnlikeValuationCommand)` - single responsibility
- Command object `UnlikeValuationCommand` (już istniejący w `valuation_dto.py`) dla input (valuation_id z path, user_id z request.user)
- Brak DTO (DELETE zwraca 204 No Content bez body)
- GenericAPIView z custom delete() method
- IsAuthenticated permission (tylko zalogowani użytkownicy)
- Custom exception: `LikeNotFoundError` (nowy w `valuation/exceptions.py`)
- Pattern: analogiczny do `BrickSetDetailUpdateView.delete()` z catalog
- Transaction.atomic() dla atomowości operacji delete

## 2. Szczegóły żądania

- **Metoda HTTP:** DELETE
- **URL:** /api/v1/valuations/{valuation_id}/likes
- **Parametry:**
  - **Path parameter (wymagany):**
    - `valuation_id` (int) – unikalny identyfikator wyceny (foreign key do Valuation)
  - **Query parameters:** Brak
  - **Headers:** 
    - `Authorization: Token <jwt_token>` (wymagany - endpoint wymaga IsAuthenticated)
- **Request Body:** Brak

Przykładowe żądanie:
```bash
DELETE /api/v1/valuations/77/likes
Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 3. Wykorzystywane typy

- **Command Model:**
  - `UnlikeValuationCommand` - **już istniejący** w `datastore/domains/valuation_dto.py`
    - Fields: `valuation_id` (z path parameter)
    - Source model: `Like`
    - Pattern: analogia do delete commands z catalog
    - **Wymaga dodania `user_id: int`** - identycznie jak w `CreateLikeCommand`
    - View przekazuje `valuation_id` z path i `user_id` z `request.user.id`

- **DTO Model:**
  - Brak - DELETE endpoint zwraca 204 No Content bez response body
  - Pattern: identyczny jak `DeleteBrickSetService` - metoda `execute()` zwraca `None`

- **Service Layer:**
  - `UnlikeValuationService` - nowa klasa w `valuation/services/unlike_valuation_service.py`
  - Metoda `execute(command: UnlikeValuationCommand) -> None` - usuwa like, zwraca None
  - Wzór: `DeleteBrickSetService` z `catalog/services/`
  - Single responsibility: validate existence + delete + handle exceptions
  - Transaction.atomic() dla atomowości delete

- **Exceptions:**
  - `LikeNotFoundError` - **nowa** w `valuation/exceptions.py`
    - Args: `valuation_id: int`, `user_id: int`
    - Message: `f"Like for valuation {valuation_id} by user {user_id} not found."`
    - Używany gdy Like.DoesNotExist (404 NOT_FOUND)
    - Pattern: analogia do `BrickSetNotFoundError`, `ValuationNotFoundError`

- **View:**
  - `ValuationUnlikeView` - nowa klasa w `valuation/views/valuation_unlike.py`
  - GenericAPIView z metodą `delete(request, valuation_id)`
  - Pattern: identyczny jak `BrickSetDetailUpdateView.delete()` z catalog
  - Przekazuje `valuation_id` z path i `user_id` z `request.user` do Command
  - Permission: IsAuthenticated (sprawdza auth przed wykonaniem logiki)

- **Models:**
  - `Like` - już istniejący w `valuation/models/like.py`
  - ForeignKey do Valuation i User
  - UniqueConstraint na (user, valuation)
  - Indexes na valuation_id i user_id dla wydajności query

## 4. Szczegóły odpowiedzi

- **Sukces (204 NO_CONTENT):**
  Like został usunięty pomyślnie. Brak response body (zgodnie z REST convention dla DELETE).

  ```
  HTTP/1.1 204 No Content
  ```

- **Błędy:**
  - **401 UNAUTHORIZED (Not Authenticated):**
    Automatycznie obsługiwany przez DRF `IsAuthenticated` permission.
    ```json
    {
      "detail": "Authentication credentials were not provided."
    }
    ```
  
  - **404 NOT_FOUND (LikeNotFoundError):**
    Like dla podanego valuation_id i user_id nie istnieje (użytkownik nie lajkował tej wyceny lub już usunął like).
    ```json
    {
      "detail": "Like for valuation 77 by user 42 not found."
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

1. **Odbiór żądania:** Klient wysyła DELETE /api/v1/valuations/{valuation_id}/likes z JWT token.
2. **Routing:** Django route resolver kieruje do `ValuationUnlikeView.delete(request, valuation_id)`.
3. **Autentykacja:** DRF middleware sprawdza JWT token (IsAuthenticated) → 401 jeśli brak/invalid.
4. **Walidacja path param:** DRF automatycznie waliduje że valuation_id jest intem (jeśli nie → 404).
5. **Command creation:** View tworzy `UnlikeValuationCommand(valuation_id=valuation_id, user_id=request.user.id)`.
6. **Logika biznesowa:** View wywołuje `UnlikeValuationService().execute(command)`:
   - Service próbuje pobrać Like: `Like.objects.get(valuation_id=valuation_id, user_id=user_id)`
   - Jeśli `Like.DoesNotExist` → rzuca `LikeNotFoundError` → 404
   - Service usuwa Like: `like.delete()` w `transaction.atomic()`
   - Zwraca `None`
7. **Response:** View zwraca `Response(status=HTTP_204_NO_CONTENT)` - brak body
8. **Reakcja na błędy:**
   - `LikeNotFoundError` → 404 z `{"detail": exc.message}`
   - Authentication errors → 401 automatic (DRF permission)
   - Unexpected errors → 500 (logged with traceback)

## 6. Względy bezpieczeństwa

- **Uwierzytelnienie:** Endpoint wymaga autentykacji (`permission_classes = [IsAuthenticated]`) - tylko zalogowani użytkownicy.
- **Autoryzacja biznesowa:** Service layer używa filtra `user_id=command.user_id` w query - użytkownik może usunąć tylko własny like. Implicit authorization przez filter.
- **Atomowość:** `transaction.atomic()` zapewnia że delete jest atomowy (rollback w przypadku błędu).
- **Primary Key validation:** DRF automatycznie waliduje typ path parametru (int).
- **Ochrona danych:**
  - Parametryzowane zapytania ORM zapobiegają SQL injection
  - Response nie zawiera wrażliwych danych (204 No Content - brak body)
  - User może usuwać tylko własne likes (implicit przez filter user_id)
- **Error disclosure:**
  - 404 dla nieistniejącego like jest informacyjny - użytkownik nie lajkował tej wyceny
  - Nie ujawnia czy valuation istnieje (generic message)
  - Brak wrażliwych szczegółów systemu w error messages
- **Idempotentność:** DELETE jest idempotentny - wywołanie DELETE na nieistniejącym like zwraca 404 (not 204), co jest zgodne z semantyką REST
- **No race conditions:** Query `get(valuation_id, user_id)` jest deterministyczny dzięki unique constraint - nie może być duplikatów

## 7. Obsługa błędów

- **401 UNAUTHORIZED (Not Authenticated):**
  - Automatycznie obsługiwany przez DRF `IsAuthenticated` permission
  - Komunikat: "Authentication credentials were not provided."
  - Nie wymaga custom kodu w view

- **404 NOT_FOUND (LikeNotFoundError):**
  - Rzucany przez service gdy `Like.DoesNotExist` dla `get(valuation_id, user_id)`
  - Komunikat: `f"Like for valuation {valuation_id} by user {user_id} not found."`
  - Mapowany w view na Response 404 z `{"detail": exc.message}`
  - Scenariusze: użytkownik nie lajkował tej wyceny, już usunął like, lub valuation nie istnieje
  - Security note: nie ujawniamy czy valuation istnieje (generic message)

- **500 INTERNAL_SERVER_ERROR:**
  - Dla niespodziewanych błędów (np. database connection issues)
  - Nie powinny wystąpić w normalnych warunkach
  - Logowane z full traceback dla debugging
  - Generic message: "An unexpected error occurred."

## 8. Testy

Pełny zestaw testów w `valuation/services/tests/test_unlike_valuation_service.py` i `valuation/views/tests/test_valuation_unlike.py` zgodnie z patterns z catalog i existing valuation tests:

### Service Tests (`django.test.TestCase`):
- `test_execute_removes_like_successfully` - happy path, like exists
- `test_execute_raises_like_not_found_when_like_does_not_exist` - Like.DoesNotExist
- `test_execute_raises_like_not_found_when_different_user` - implicit authorization test
- `test_execute_atomic_transaction_rollback` - transaction.atomic() behavior

### View Tests (`APITestCase` z APIRequestFactory):
- `test_delete_returns_no_content_when_like_exists` - 204 response
- `test_delete_returns_not_found_when_like_does_not_exist` - 404 mapping
- `test_delete_returns_unauthorized_when_not_authenticated` - 401 permission
- `test_delete_cannot_remove_other_users_like` - implicit authorization
- `test_delete_idempotent_returns_not_found_on_second_call` - idempotency

Pattern: identyczne struktura testów jak w `BrickSetDetailUpdateView.delete()` i `LikeValuationService`

## 9. Etapy implementacji

1. **Dodanie `user_id` do `UnlikeValuationCommand`:**
   - Plik: `datastore/domains/valuation_dto.py`
   - Dodać pole `user_id: int` do dataclass (analogia do `CreateLikeCommand`)
   - Command zawiera: `valuation_id` (path) + `user_id` (request.user)

2. **Stworzenie `LikeNotFoundError` exception:**
   - Plik: `valuation/exceptions.py`
   - Args: `valuation_id: int`, `user_id: int`
   - Message: `f"Like for valuation {valuation_id} by user {user_id} not found."`
   - Pattern: analogia do `BrickSetNotFoundError`

3. **Implementacja `UnlikeValuationService`:**
   - Plik: `valuation/services/unlike_valuation_service.py`
   - Metoda `execute(command: UnlikeValuationCommand) -> None`
   - Query: `Like.objects.get(valuation_id=..., user_id=...)`
   - Catch `Like.DoesNotExist` → raise `LikeNotFoundError`
   - Delete w `transaction.atomic()`
   - Return `None`
   - Pattern: identyczny jak `DeleteBrickSetService`

4. **Implementacja `ValuationUnlikeView`:**
   - Plik: `valuation/views/valuation_unlike.py`
   - GenericAPIView z `delete(request, valuation_id)` method
   - Permission: `IsAuthenticated`
   - Auth check: `if not request.user or not request.user.is_authenticated`
   - Command creation: `UnlikeValuationCommand(valuation_id, request.user.id)`
   - Service call: `UnlikeValuationService().execute(command)`
   - Error mapping: `LikeNotFoundError` → 404
   - Success: `Response(status=HTTP_204_NO_CONTENT)`
   - Pattern: identyczny jak `BrickSetDetailUpdateView.delete()`

5. **Dodanie URL routing:**
   - Plik: `valuation/urls.py`
   - Pattern: `valuations/<int:valuation_id>/likes`
   - Name: `valuation-unlike` (lub `valuation-like` jeśli shared z POST)
   - View: `ValuationUnlikeView.as_view()`
   - Method: DELETE

6. **Testy service layer:**
   - Plik: `valuation/services/tests/test_unlike_valuation_service.py`
   - TestCase dla każdego scenariusza (success, DoesNotExist, implicit auth)
   - Pattern: identyczny jak `test_like_valuation_service.py`

7. **Testy view layer:**
   - Plik: `valuation/views/tests/test_valuation_unlike.py`
   - APITestCase z APIRequestFactory
   - Test all HTTP status codes (204, 401, 404)
   - Test idempotency
   - Pattern: identyczny jak catalog delete tests

8. **Walidacja:**
   - Run `./bin/lint_backend.sh` - must pass
   - Run `./bin/test_backend.sh` - must pass with 90%+ coverage
   - Manual API testing via curl/Postman
