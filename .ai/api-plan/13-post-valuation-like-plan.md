# API Endpoint Implementation Plan: POST /api/v1/valuations/{valuation_id}/likes

## 1. Przegląd punktu końcowego

Endpoint umożliwia dodanie polubienia (like) do wyceny przez zalogowanego użytkownika. Zwraca obiekt z identyfikatorem wyceny, identyfikatorem użytkownika oraz datą utworzenia polubienia. Endpoint wykorzystuje identyczne wzorce implementacyjne co `POST /api/v1/bricksets/{brickset_id}/valuations` - service layer, DTOs, Command objects, GenericAPIView i obsługę błędów.

**Wzorce implementacyjne**: Endpoint wykorzystuje identyczne wzorce co valuation create endpoint:
- Service layer z metodą `execute(command: LikeValuationCommand)` - single responsibility
- Command object `LikeValuationCommand` dla input (valuation_id z path, user_id z request.user)
- `LikeDTO` (już istniejący w `valuation_dto.py`) dla response
- Serializer write-only dla Command, read-only dla DTO
- GenericAPIView z custom post() method (nie CreateAPIView - potrzebujemy path param)
- IsAuthenticated permission (tylko zalogowani użytkownicy)
- Custom exceptions: `LikeOwnValuationError`, `LikeDuplicateError`, `ValuationNotFoundError` (już istniejący)
- Pattern: analogiczny do `BrickSetValuationsView.post()` z catalog

## 2. Szczegóły żądania

- **Metoda HTTP:** POST
- **URL:** /api/v1/valuations/{valuation_id}/likes
- **Parametry:**
  - **Path parameter (wymagany):**
    - `valuation_id` (int) – unikalny identyfikator wyceny (foreign key do Valuation)
  - **Query parameters:** Brak
  - **Headers:** 
    - `Authorization: Token <jwt_token>` (wymagany - endpoint wymaga IsAuthenticated)
- **Request Body:** Pusty JSON object `{}` lub brak body

Przykładowe żądanie:
```bash
POST /api/v1/valuations/77/likes
Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{}
```

## 3. Wykorzystywane typy

- **Command Model:**
  - `LikeValuationCommand` - **już istniejący** w `datastore/domains/valuation_dto.py`
    - Fields: `valuation_id` (z path parameter), `user_id` (z request.user - dodane w view)
    - Source model: `Like`
    - Pattern: analogia do `CreateValuationCommand` (input dla service layer)
    - **user_id nie jest w obecnej wersji - wymaga dodania**

- **DTO Model:**
  - `LikeDTO` - **już istniejący** w `datastore/domains/valuation_dto.py`
    - Response zawiera: `valuation_id`, `user_id`, `created_at`
    - Source model: `Like`
    - Pattern: output z service layer, serializowany w response


- **Service Layer:**
  - `LikeValuationService` - nowa klasa w `valuation/services/like_valuation_service.py`
  - Metoda `execute(command: LikeValuationCommand) -> LikeDTO` - tworzy like i zwraca DTO
  - Wzór: `CreateValuationService` z `valuation/services/`
  - Single responsibility: validate + create + map to DTO + handle exceptions

- **Serializers:**
  - `LikeValuationSerializer` - nowy serializer w `valuation/serializers/like_valuation.py`
    - Empty serializer (brak pól) - body jest pusty
    - Metoda `to_command(valuation_id, user_id)` tworzy `LikeValuationCommand`
  - `LikeSerializer` - nowy serializer w `valuation/serializers/like.py`
    - Read-only serializer dla `LikeDTO` (output only)
    - Fields: `valuation_id`, `user_id`, `created_at` (wszystkie read_only=True)
    - Wzór: `ValuationSerializer` z catalog

- **Exceptions:**
  - `LikeOwnValuationError` - **nowa** w `valuation/exceptions.py`
    - Args: `valuation_id: int`
    - Message: `"Cannot like your own valuation."`
    - Używany gdy user_id == valuation.user_id (403 FORBIDDEN)
  - `LikeDuplicateError` - **nowa** w `valuation/exceptions.py`
    - Args: `valuation_id: int`, `user_id: int`
    - Message: `f"Like for valuation {valuation_id} by user {user_id} already exists."`
    - Używany przy IntegrityError na unique constraint (409 CONFLICT)
  - `ValuationNotFoundError` - **już istniejący** w `valuation/exceptions.py`
    - Używany gdy Valuation o podanym valuation_id nie istnieje (404)

- **View:**
  - `ValuationLikeView` - nowa klasa w `valuation/views/valuation_like.py`
  - GenericAPIView z metodą `post(request, valuation_id)`
  - Pattern: identyczny jak `BrickSetValuationsView.post()` z catalog
  - Przekazuje `valuation_id` z path i `user_id` z `request.user` do Command

- **Models:**
  - `Like` - już istniejący w `valuation/models/like.py`
  - ForeignKey do Valuation i User
  - UniqueConstraint na (user, valuation) - zapobiega duplikatom
  - Indexes na valuation_id i user_id dla wydajności

## 4. Szczegóły odpowiedzi

- **Sukces (201 CREATED):**
  Like został utworzony pomyślnie.

  ```json
  {
    "valuation_id": 77,
    "user_id": 42,
    "created_at": "2025-10-25T12:30:00.000Z"
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
  
  - **403 FORBIDDEN (LikeOwnValuationError):**
    Użytkownik próbuje polubić własną wycenę.
    ```json
    {
      "detail": "Cannot like your own valuation."
    }
    ```

  - **404 NOT_FOUND (ValuationNotFoundError):**
    Wycena o podanym valuation_id nie istnieje.
    ```json
    {
      "detail": "Valuation with id 999 not found."
    }
    ```

  - **409 CONFLICT (LikeDuplicateError):**
    Użytkownik już polubił tę wycenę (unique constraint violation).
    ```json
    {
      "detail": "Like for valuation 77 by user 42 already exists."
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

1. **Odbiór żądania:** Klient wysyła POST /api/v1/valuations/{valuation_id}/likes z JWT token.
2. **Routing:** Django route resolver kieruje do `ValuationLikeView.post(request, valuation_id)`.
3. **Autentykacja:** DRF middleware sprawdza JWT token (IsAuthenticated) → 401 jeśli brak/invalid.
4. **Walidacja path param:** DRF automatycznie waliduje że valuation_id jest intem (jeśli nie → 404).
5. **Command creation:** View tworzy `LikeValuationCommand(valuation_id=valuation_id, user_id=request.user.id)`.
6. **Logika biznesowa:** View wywołuje `LikeValuationService().execute(command)`:
   - Service weryfikuje czy Valuation istnieje (query: `Valuation.valuations.get(pk=valuation_id)`)
   - Jeśli `Valuation.DoesNotExist` → rzuca `ValuationNotFoundError` → 404
   - Service sprawdza czy `valuation.user_id == command.user_id` → rzuca `LikeOwnValuationError` → 403
   - Service tworzy Like: `Like.objects.create(user_id=user_id, valuation_id=valuation_id)`
   - Catch `IntegrityError` (unique constraint) → rzuca `LikeDuplicateError` → 409
   - Mapuje Like instance do `LikeDTO`
   - Zwraca DTO
7. **Serializacja:** View serializuje DTO przez `LikeSerializer(like_dto)`
8. **Response:** View zwraca `Response(serializer.data, status=HTTP_201_CREATED)`
9. **Reakcja na błędy:**
   - `LikeOwnValuationError` → 403 z `{"detail": exc.message}`
   - `LikeDuplicateError` → 409 z `{"detail": exc.message}`
   - `ValuationNotFoundError` → 404 z `{"detail": exc.message}`
   - Authentication errors → 401 automatic
   - Unexpected errors → 500 (logged with traceback)

## 6. Względy bezpieczeństwa

- **Uwierzytelnienie:** Endpoint wymaga autentykacji (`permission_classes = [IsAuthenticated]`) - tylko zalogowani użytkownicy.
- **Autoryzacja biznesowa:** Service layer sprawdza czy user nie lajkuje własnej wyceny (403 FORBIDDEN).
- **Unique constraint:** Database-level constraint zapobiega race conditions przy duplikatach (user + valuation unique).
- **Primary Key validation:** DRF automatycznie waliduje typ path parametru (int).
- **Ochrona danych:**
  - Parametryzowane zapytania ORM zapobiegają SQL injection
  - Response nie zawiera wrażliwych danych (tylko ID i timestamp)
  - User może lajkować tylko istniejące wyceny (walidacja w service)
- **Error disclosure:**
  - 404 dla nieistniejącej wyceny nie ujawnia szczegółów systemu (generic message)
  - 403 dla własnej wyceny ujawnia business rule ale nie jest to wrażliwe
  - 409 dla duplikatu jest informacyjny dla użytkownika (już polubił)
- **Rate limiting:** Rozważyć throttling (np. max 100 likes/hour per user) dla zapobiegania spam/abuse
- **Transaction handling:** Service używa `transaction.atomic()` dla atomowości operacji create + validate

## 7. Obsługa błędów

- **401 UNAUTHORIZED (Not Authenticated):**
  - Automatycznie obsługiwany przez DRF `IsAuthenticated` permission
  - Komunikat: "Authentication credentials were not provided."
  - Nie wymaga custom kodu

- **403 FORBIDDEN (LikeOwnValuationError):**
  - Rzucany przez service gdy `valuation.user_id == command.user_id`
  - Komunikat: "Cannot like your own valuation."
  - Mapowany w view na Response 403 z `{"detail": exc.message}`
  - Business logic validation - użytkownik nie może polubić własnej wyceny

- **404 NOT_FOUND (ValuationNotFoundError):**
  - Rzucany przez service gdy `Valuation.valuations.get(pk=valuation_id)` rzuci `Valuation.DoesNotExist`
  - Komunikat: "Valuation with id {valuation_id} not found."
  - Mapowany w view na Response 404 z `{"detail": exc.message}`
  - Pattern: identyczny jak w `ValuationDetailView`

- **409 CONFLICT (LikeDuplicateError):**
  - Rzucany przez service gdy catch `IntegrityError` podczas `Like.objects.create()`
  - IntegrityError spowodowany unique constraint `like_unique_user_valuation`
  - Komunikat: "Like for valuation {valuation_id} by user {user_id} already exists."
  - Mapowany w view na Response 409 z `{"detail": exc.message}`
  - Pattern: identyczny jak `ValuationDuplicateError` w CreateValuationService

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
  - Service wykonuje 2 queries:
    1. `Valuation.valuations.get(pk=valuation_id)` - validation + ownership check
    2. `Like.objects.create(user_id=user_id, valuation_id=valuation_id)` - insert
  - Total queries: 2 (optymalne dla create operation z validation)
  - **NIE używamy** `select_related` - nie potrzebujemy related objects, tylko validation
  - Pattern: identyczny jak `CreateValuationService`

- **Indexes:**
  - Primary key (valuation_id) - automatycznie indexed - instant lookup
  - Unique constraint (user, valuation) - automatycznie indexed - instant duplicate check
  - Index na valuation_id - już istniejący w Like model - przyspieszenie lookup
  - Index na user_id - już istniejący w Like model - przyspieszenie filtrowania

- **Unique constraint prevention:**
  - Database-level UniqueConstraint `like_unique_user_valuation` zapobiega duplikatom
  - Catch `IntegrityError` w service → map to `LikeDuplicateError` → 409 response
  - Race condition safe - atomic database operation

- **Transaction handling:**
  - Service używa `transaction.atomic()` dla atomowości:
    1. Validation (Valuation exists + not own)
    2. Like creation
  - Rollback jeśli walidacja fail lub IntegrityError
  - Pattern: identyczny jak `CreateValuationService`

- **N+1 prevention:**
  - Tylko 2 queries - brak iteracji po related objects
  - Single insert operation (Like.objects.create)
  - Nie potrzebujemy eager loading

- **Caching considerations:**
  - Like creation nie wymaga cache - write operation
  - Rozważyć invalidację cache dla:
    - Valuation detail (likes_count się zmienia - update valuation)
    - Valuation list (jeśli pokazujemy likes_count)
  - Cache key: `valuation_detail:{valuation_id}` - invalidate po create like

- **Scaling considerations:**
  - Write operations = O(1) complexity z unique constraint check
  - Unique constraint index = O(log n) lookup przed insert
  - Database handles constraint validation atomically (no race conditions)
  - For high write volume: consider database write replicas/sharding by valuation_id

## 9. Etapy implementacji

### 9.1. Dodanie custom exceptions (valuation/exceptions.py)
- Rozszerzyć istniejący plik `exceptions.py` w `valuation/`
- Klasa `LikeOwnValuationError(Exception)`
  - Args: `valuation_id: int`
  - Attributes: `valuation_id`, `message`
  - Message: `"Cannot like your own valuation."`
- Klasa `LikeDuplicateError(Exception)`
  - Args: `valuation_id: int`, `user_id: int`
  - Attributes: `valuation_id`, `user_id`, `message`
  - Message: `f"Like for valuation {valuation_id} by user {user_id} already exists."`
- Wzór: `ValuationDuplicateError`, `ValuationNotFoundError` już istniejące

### 9.2. Aktualizacja LikeValuationCommand (datastore/domains/valuation_dto.py)
- Command już istnieje ale brak `user_id` field - dodać
- Obecna struktura: `valuation_id: int`
- Nowa struktura: `valuation_id: int`, `user_id: int`
- Wzór: `CreateValuationCommand` z `brickset_id` i danymi użytkownika

### 9.3. Utworzenie serializers (valuation/serializers/)
- **Nowy plik `like_valuation.py`:**
  - Klasa `LikeValuationSerializer(serializers.Serializer)`
  - Pusta klasa (brak pól) - body jest pusty w API
  - Może mieć docstring opisujący że body jest pusty
  - Nie wymaga `to_command()` - Command tworzony bezpośrednio w view z path param i request.user

- **Nowy plik `like.py`:**
  - Klasa `LikeSerializer(serializers.Serializer)`
  - Fields: `valuation_id`, `user_id`, `created_at` (wszystkie read_only=True)
  - `valuation_id` jako `IntegerField(read_only=True)`
  - `user_id` jako `IntegerField(read_only=True)`
  - `created_at` jako `DateTimeField(read_only=True)`
  - Wzór: `ValuationSerializer` z `valuation/serializers/valuation_detail.py`

### 9.4. Implementacja service layer (valuation/services/like_valuation_service.py)
- Nowy plik `like_valuation_service.py` w `valuation/services/`
- Klasa `LikeValuationService` z jedną metodą
- Wzór: `CreateValuationService` z `valuation/services/`

**Metoda `execute(command: LikeValuationCommand) -> LikeDTO`:**
1. Walidacja wyceny istnieje:
   ```python
   try:
       valuation = Valuation.valuations.get(pk=command.valuation_id)
   except Valuation.DoesNotExist as exc:
       raise ValuationNotFoundError(command.valuation_id) from exc
   ```
2. Walidacja nie polubienie własnej wyceny:
   ```python
   if valuation.user_id == command.user_id:
       raise LikeOwnValuationError(command.valuation_id)
   ```
3. Tworzenie Like z transaction.atomic() + handle IntegrityError:
   ```python
   try:
       with transaction.atomic():
           like = Like.objects.create(
               user_id=command.user_id,
               valuation_id=command.valuation_id,
           )
   except IntegrityError as exc:
       raise LikeDuplicateError(command.valuation_id, command.user_id) from exc
   ```
4. Mapuje do DTO:
   ```python
   return LikeDTO(
       valuation_id=like.valuation_id,
       user_id=like.user_id,
       created_at=like.created_at,
   )
   ```
5. Wzór flow: validation → business rules → create → exception handling → map to DTO

### 9.5. Implementacja view (valuation/views/valuation_like.py)
- Nowy plik `valuation_like.py` w `valuation/views/`
- Klasa `ValuationLikeView(GenericAPIView)` z metodą `post()`

**Struktura klasy:**
- `permission_classes = [IsAuthenticated]`
- `serializer_class = LikeSerializer` (dla response tylko)

**Metoda `post(request, valuation_id)`:**
1. Command creation: `command = LikeValuationCommand(valuation_id=valuation_id, user_id=request.user.id)`
2. Service call: `service = LikeValuationService(); like_dto = service.execute(command)`
3. Exception handling (try-except):
   - `LikeOwnValuationError` → 403 z `{"detail": exc.message}`
   - `LikeDuplicateError` → 409 z `{"detail": exc.message}`
   - `ValuationNotFoundError` → 404 z `{"detail": exc.message}`
4. Serializacja: `serializer = LikeSerializer(like_dto)`
5. Response: `return Response(serializer.data, status=HTTP_201_CREATED)`

**Pattern:** Metoda `post()` praktycznie identyczna jak `BrickSetValuationsView.post()`:
- Build Command z path param + request.user
- Service → DTO
- Catch exceptions → HTTP codes
- Serialize → response 201

**Docstring wzór:**
- Opisać flow, parametry, response format, error codes (401/403/404/409)
- Przykłady response body (success + all error cases)
- Identyczny styl jak w `ValuationDetailView` i `BrickSetValuationsView`

### 9.6. Routing (valuation/urls.py)
- Dodać nowy path w istniejącym pliku `urls.py`
- Pattern: `path("valuations/<int:valuation_id>/likes", ValuationLikeView.as_view(), name="valuation-like")`
- Import: `from valuation.views.valuation_like import ValuationLikeView`
- URL musi być included w `config/urls.py` (valuation app już included - bez zmian)

### 9.7. Testy

**9.7.1. Testy service (valuation/services/tests/test_like_valuation_service.py)**
- Nowy plik testów
- Używamy `django.test.TestCase` (NIE pytest fixtures)
- Setup: utworzyć test users (owner i liker), BrickSet, Valuation w `setUp()`

**Test cases:**
- Test successful like creation → zwraca poprawny `LikeDTO` z wszystkimi polami
- Test like non-existent valuation → rzuca `ValuationNotFoundError`
- Test like own valuation → rzuca `LikeOwnValuationError`
- Test duplicate like → rzuca `LikeDuplicateError`
- Test DTO mapping → sprawdzić wszystkie pola (valuation_id, user_id, created_at)
- Test timestamp → sprawdzić że created_at jest set i w przeszłości/teraz

**9.7.2. Testy API view (valuation/views/tests/test_valuation_like_view.py)**
- Nowy plik testów
- Używamy `APITestCase` z DRF
- Setup: utworzyć test users (owner i liker), BrickSet, Valuation, authenticate client

**Test cases:**
- Test POST success → 201 z pełnym JSON, sprawdzić wszystkie pola
- Test POST non-existent valuation → 404 z detail message
- Test POST own valuation → 403 z detail "Cannot like your own valuation."
- Test POST duplicate like → 409 z detail message
- Test POST unauthenticated → 401
- Test POST verify timestamp → sprawdzić format ISO datetime
- Test POST verify response structure → check all required fields present
- Test POST by different user → 201 success (public like allowed)

**Pattern testów:**
- Używać `reverse("valuation:valuation-like", kwargs={"valuation_id": id})` dla URL
- Tworzyć oddzielne fixtures dla każdego test case (unikać shared state)
- Descriptive test names bez liczb (WPS114): `test_like_own_valuation_returns_forbidden`
- Arrange-Act-Assert structure w każdym teście

### 9.8. Walidacja po implementacji
- Uruchomić `./bin/lint_backend.sh` - zero violations
- Uruchomić `./bin/test_backend.sh` - wszystkie testy pass, coverage ≥90%
- Manualny test przez cURL/Postman:
  - POST z valid valuation_id (not own) → 201 z JSON
  - POST own valuation_id → 403
  - POST duplicate (same user+valuation) → 409
  - POST non-existent valuation_id → 404
  - POST bez auth → 401
- Sprawdzić logs - brak nieobsłużonych exceptions
- Sprawdzić query count (Django Debug Toolbar): powinno być 2 queries (validation + insert)
- Sprawdzić database constraint - unique (user, valuation) działa poprawnie

## 5. Przepływ danych
1. Klient wysyła żądanie POST do `/api/v1/valuations/{valuation_id}/likes` z poprawnym tokenem uwierzytelniającym.
2. Warstwa kontrolera (np. oparta na Django REST Framework – CreateAPIView lub APIView) odbiera `valuation_id` z URL.
3. Kontroler przekazuje `valuation_id` do warstwy serwisowej.
4. W warstwie serwisowej wykonywane są następujące kroki:
   - Weryfikacja, czy wycena o podanym `valuation_id` istnieje.
   - Sprawdzenie, czy użytkownik nie jest autorem wyceny (LIKE_OWN_VALUATION_FORBIDDEN).
   - Weryfikacja, czy użytkownik nie polubił już tej wyceny (LIKE_DUPLICATE), w oparciu o unikalny constraint (user_id, valuation_id).
   - Utworzenie rekordu polubienia w bazie danych.
5. Utworzony rekord jest konwertowany na instancję `LikeDTO` i zwracany jako response JSON.

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie**: Weryfikacja tokenu (np. JWT) na poziomie middleware lub wbudowanych mechanizmów Django REST Framework.
- **Autoryzacja**: Sprawdzenie, czy użytkownik nie próbuje polubić własnej wyceny.
- **Walidacja**: Dokładna weryfikacja, że `valuation_id` jest poprawnym identyfikatorem liczbowym oraz że rekord wyceny istnieje.
- **Dostęp do danych**: Zapewnienie, że operacja jest dostępna tylko dla autoryzowanych użytkowników poprzez stosowanie odpowiednich permission classes.

## 7. Obsługa błędów
- **401 NOT_AUTHENTICATED**: Zwrot gdy użytkownik nie dostarczy prawidłowych danych uwierzytelniających.
- **403 LIKE_OWN_VALUATION_FORBIDDEN**: Jeśli użytkownik próbuje polubić własną wycenę.
- **409 LIKE_DUPLICATE**: Jeśli użytkownik już polubił daną wycenę.
- **404 VALUATION_NOT_FOUND**: Gdy wycena o podanym `valuation_id` nie istnieje.
- **500 INTERNAL_SERVER_ERROR**: Dla nieoczekiwanych wyjątków i błędów serwera.

## 8. Rozważania dotyczące wydajności
- **Baza danych**: Wykorzystanie unikalnego constraintu na kolumnach `(user_id, valuation_id)` by zapobiegać duplikatom oraz użycie indeksów na kolumnach `valuation_id` i `user_id` dla szybkich operacji wyszukiwania.
- **Optymalizacja zapytań**: Upewnienie się, że zapytania do bazy danych są zoptymalizowane, a operacje insert są wykonywane w transakcjach.
- **Caching**: Opcjonalnie, cache'owanie często odczytywanych danych, jeżeli system będzie narażony na duże obciążenia.

## 9. Etapy wdrożenia
1. **Analiza i projektowanie**:
   - Dokładna weryfikacja specyfikacji endpointa ze wszystkimi interesariuszami.
   - Przegląd istniejących modeli (`Valuation`, `Like`) oraz DTO (`LikeDTO`) i Command Model (`LikeValuationCommand`).

2. **Implementacja kontrolera**:
   - Utworzenie klasy widoku (np. opartej na Django REST Framework – CreateAPIView lub APIView) do obsługi żądania POST.
   - Definicja routing’u w `urls.py` dla endpointa `/api/v1/valuations/<int:valuation_id>/likes`.

3. **Implementacja logiki serwisowej**:
   - Wydzielenie logiki do nowej lub istniejącej warstwy serwisowej odpowiedzialnej za obsługę polubień.
   - Sprawdzenie istnienia wyceny, walidacja, czy użytkownik nie jest autorem oraz czy nie ma duplikatu lajkowania.
   - Obsługa transakcji i zapewnienie atomowości operacji.

4. **Testowanie i walidacja**:
   - Implementacja testów jednostkowych (pytest) obejmujących:
     - Sytuację poprawnego dodania polubienia (201).
     - Próby polubienia własnej wyceny (403).
     - Próby duplikacji polubienia (409).
     - Sytuację, gdy wycena nie istnieje (404).
     - Brak autoryzacji (401).
   - Przeprowadzenie testów E2E (np. z użyciem Cypress) dla weryfikacji pełnego przepływu.

5. **Obsługa błędów i logowanie**:
   - Zaimplementowanie mechanizmu globalnej obsługi wyjątków w Django REST Framework.
   - Rejestrowanie krytycznych błędów po stronie serwera.

6. **Weryfikacja wydajności**:
   - Przeprowadzenie testów obciążeniowych i analiza logów w celu identyfikacji ewentualnych wąskich gardeł.
   - Wdrożenie ewentualnych optymalizacji (np. caching, tuning bazy danych).

7. **Deploy i monitorowanie**:
   - Wdrożenie zmiany do środowiska developerskiego, a następnie do testowego i produkcyjnego.
   - Ustawienie monitoringu i alertów związanych z działaniem endpointa.
