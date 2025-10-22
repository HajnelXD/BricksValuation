# API Endpoint Implementation Plan: GET /api/v1/bricksets/{brickset_id}/valuations

## 1. Przegląd punktu końcowego
Endpoint umożliwia pobranie listy wycen powiązanych z określonym zestawem LEGO. Wyniki są sortowane malejąco według liczby polubień (likes_count) oraz rosnąco według daty utworzenia (created_at). Endpoint jest częścią systemu REST API opartego na Django oraz Django REST Framework.

## 2. Szczegóły żądania
- **Metoda HTTP:** GET
- **Struktura URL:** `/api/v1/bricksets/{brickset_id}/valuations`
- **Parametry:**
  - **Wymagane:** 
    - `brickset_id` – ID zestawu, przekazywane w ścieżce URL
  - **Opcjonalne:**
    - `page` – numer strony (dla paginacji)
    - `page_size` – liczba elementów na stronie
- **Request Body:** Brak

## 3. Wykorzystywane typy
- **DTOs:**
  - `ValuationListItemDTO` – reprezentuje pojedynczy rekord wyceny w liście
  - `ValuationDTO` – pełna reprezentacja wyceny (używana w innych endpointach)
- **Command Modele:**
  - `CreateValuationCommand` – dla tworzenia wyceny (podstawowa znajomość modelu jest istotna dla logiki walidacji)
  - Inne modele, jak `LikeValuationCommand`, mogą być używane w powiązanych operacjach

## 4. Szczegóły odpowiedzi
- **Status Code:** 200
- **Struktura odpowiedzi:**
  ```json
  {
    "count": 5,
    "results": [
      {
        "id": 77,
        "user_id": 99,
        "value": 400,
        "currency": "PLN",
        "comment": "Looks complete",
        "likes_count": 9,
        "created_at": "..."
      }
    ]
  }
  ```
- W przypadku błędów:
  - **401:** NOT_AUTHENTICATED – gdy użytkownik nie jest uwierzytelniony
  - **404:** BRICKSET_NOT_FOUND – gdy nie znaleziono zestawu o podanym `brickset_id`
  - **400:** VALIDATION_ERROR – dla nieprawidłowych parametrów (np. błędna paginacja)

## 5. Przepływ danych
1. Żądanie trafia do widoku (klasa opartej na CBV) w Django REST Framework.
2. Widok:
   - Wykonuje weryfikację autentykacji użytkownika.
   - Waliduje parametr `brickset_id` i opcjonalnie parametry paginacji (`page`, `page_size`).
3. Warstwa serwisowa:
   - Sprawdza istnienie zestawu (brickset) w bazie danych.
   - Pobiera powiązane rekordy z tabeli `valuation_valuation`, stosując sortowanie (`likes_count` DESC, `created_at` ASC) oraz ewentualną paginację.
4. Serializacja:
   - Przekształcenie wyników do formatu zgodnego z `ValuationListItemDTO`.
5. Odpowiedź jest zwracana do klienta.

## 6. Względy bezpieczeństwa
- **Autentykacja:** Endpoint wymaga ważnego tokena JWT.
- **Autoryzacja:** Upewnić się, że użytkownik ma dostęp do zasobów (choć sam dostęp do listy wycen zwykle nie modyfikuje danych).
- **Walidacja:** Walidacja parametrów wejściowych (`brickset_id` powinno być liczbą, page i page_size muszą być dodatnimi wartościami).

## 7. Obsługa błędów
- **404 BRICKSET_NOT_FOUND:** Gdy zestaw o podanym `brickset_id` nie istnieje.
- **401 NOT_AUTHENTICATED:** Gdy żądanie nie zawiera poprawnych danych autentykacyjnych.
- **400 VALIDATION_ERROR:** W przypadku błędnych parametrów zapytania (np. nieprawidłowy format paginacji).
- **500 INTERNAL_SERVER_ERROR:** Dla nieprzewidzianych błędów serwera, logowanych zgodnie z best practices.

## 8. Rozważania dotyczące wydajności
- **Query Optimization:** Użycie metod Django ORM w celu optymalizacji zapytań (np. `select_related` lub `prefetch_related`, jeśli wymagane).
- **Paginacja:** Wdrożenie paginacji, aby zapobiec przeciążeniu przy dużej liczbie rekordów.
- **Caching (opcjonalnie):** Rozważenie buforowania wyników dla endpointów o wysokiej częstotliwości zapytań.

## 9. Etapy wdrożenia
1. **Projekt widoku:**
   - Utworzenie klasy widoku opartego na CBV w Django REST Framework.
   - Dodanie logiki autentykacji oraz walidacji parametrów (`brickset_id`, `page`, `page_size`).
2. **Implementacja serwisu:**
   - Wydzielenie logiki pobierania wycen do warstwy serwisowej lub managera modelu.
   - Implementacja logiki sortowania i paginacji.
3. **Serializacja:**
   - Utworzenie serializerów dla `ValuationListItemDTO` i ewentualnie `ValuationDTO`.
4. **Testowanie walidacji:**
   - Utworzenie testów jednostkowych sprawdzających:
     - Poprawność zapytań.
     - Obsługę błędów (404, 401, 400).
5. **Integracja:**
   - Integracja endpointu z resztą API.
   - Rejestracja routingu w konfiguracji Django.
6. **Optymalizacja i monitoring:**
   - Weryfikacja działania endpointu pod kątem wydajności.
   - Implementacja logowania błędów i monitoringu aplikacji.
7. **Dokumentacja:**
   - Aktualizacja dokumentacji API oraz planu wdrożenia.
   - Przegląd z zespołem oraz iteracyjne usprawnienia.
