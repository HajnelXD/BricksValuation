# API Endpoint Implementation Plan: GET Single Valuation

## 1. Przegląd punktu końcowego
Endpoint służy do pobierania pojedynczej wyceny (valuation) na podstawie identyfikatora. Umożliwia autoryzowanym użytkownikom pobranie szczegółowych informacji o wycenie zestawu, takich jak wartość, komentarz oraz liczba polubień.

## 2. Szczegóły żądania
- **Metoda HTTP**: GET
- **Struktura URL**: /api/v1/valuations/{id}
- **Parametry**:
  - **Wymagane**: 
    - `id` (ścieżka) – identyfikator wyceny
  - **Opcjonalne**: Brak
- **Request Body**: Brak

## 3. Wykorzystywane typy
- **DTO**:
  - `ValuationDTO` – pełna reprezentacja wyceny z polami `id`, `brickset_id`, `user_id`, `value`, `currency`, `comment`, `likes_count`, `created_at`, `updated_at`.
- **Command Model**: Brak dedykowanego modelu komend dla odczytu (GET) wyceny

## 4. Szczegóły odpowiedzi
- **Sukces (200)**: 
  ```json
  {
    "id": 77,
    "brickset_id": 10,
    "user_id": 99,
    "value": 400,
    "currency": "PLN",
    "comment": "Looks complete",
    "likes_count": 9,
    "created_at": "...",
    "updated_at": "..."
  }
  ```
- **Błędy**:
  - **404** – VALUATION_NOT_FOUND, gdy wycena nie istnieje
  - **401** – NOT_AUTHENTICATED, gdy użytkownik nie jest zalogowany

## 5. Przepływ danych
1. Klient wysyła żądanie GET do `/api/v1/valuations/{id}` wraz z autoryzacją.
2. Warstwa kontrolera (np. Django REST Framework View) przekazuje `id` do warstwy serwisowej.
3. Warstwa serwisowa wykonuje zapytanie do bazy danych na modelu `Valuation` (używając właściwego managera lub ORM).
4. Wynik zostaje przekształcony do formatu DTO (`ValuationDTO`).
5. DTO jest serializowane i zwracane jako odpowiedź JSON.

## 6. Względy bezpieczeństwa
- Weryfikacja tokenu autoryzacyjnego (np. JWT) w warstwie uwierzytelniania.
- Autoryzacja dostępu – sprawdzenie, czy użytkownik ma prawo do odczytu danej wyceny (np. przez reguły business logic lub polityki).
- Walidacja wejściowego identyfikatora wyceny (musi być liczbą całkowitą).

## 7. Obsługa błędów
- **401 NOT_AUTHENTICATED**: Brak prawidłowych danych uwierzytelniających.
- **404 VALUATION_NOT_FOUND**: W przypadku, gdy wycena o podanym identyfikatorze nie istnieje.
- **500 INTERNAL_SERVER_ERROR**: Dla nieoczekiwanych błędów po stronie serwera.

## 8. Rozważania dotyczące wydajności
- Optymalizacja zapytań do bazy danych (np. select_related lub prefetch_related w celu ograniczenia liczby zapytań).
- Cache'owanie wyników dla często odczytywanych wycen (opcjonalnie, jeżeli wymaga tego obciążenie systemu).

## 9. Etapy wdrożenia
1. **Projektowanie**: 
   - Zweryfikować specyfikację endpointa oraz istniejący model `Valuation`.
   - Przegląd istniejących DTO (`ValuationDTO`) i odpowiednich serializerów.

2. **Implementacja Warstwy Kontrolera**:
   - Utworzyć widok (class-based) przy użyciu Django REST Framework, np. `RetrieveAPIView`.
   - Skonfigurować routing w `urls.py` dla endpointa `/api/v1/valuations/<int:id>`.

3. **Implementacja Warstwy Serwisowej**:
   - Jeżeli logika pobierania wyceny jest złożona, wydzielić ją do serwisu.
   - Zaimplementować mechanizmy walidacji wejścia (np. sprawdzanie, czy `id` jest liczbą) oraz autoryzacji.

4. **Walidacja i Testy**:
   - Napisać testy jednostkowe (pytest) dla widoku i warstwy serwisowej.
   - Przeprowadzić testy E2E przy użyciu Cypress (jeśli dotyczy) w celu weryfikacji całego przepływu.

5. **Obsługa Błędów**:
   - Skonfigurować custom exception handling w Django REST Framework, aby odpowiednio zwracać kody 401, 404 oraz 500.

6. **Weryfikacja Wydajności**:
   - Przetestować endpoint pod kątem obciążenia, zwracając uwagę na optymalizację zapytań i ewentualne caching.

7. **Deploy i Monitorowanie**:
   - Wdrążyć zmiany w środowisku developerskim i testowym.
   - Monitorować logi serwera i zbierać feedback od użytkowników w celu dalszych optymalizacji.
