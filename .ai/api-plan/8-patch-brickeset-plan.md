# API Endpoint Implementation Plan: PATCH /api/v1/bricksets/{id}

## 1. Przegląd punktu końcowego

Endpoint służy do edycji istniejącego BrickSet. Edycja jest dozwolona tylko dla właściciela rekordu oraz tylko w przypadku, gdy nie istnieją oceny od innych użytkowników, a ocena właściciela (jeśli istnieje) ma 0 like'ów.

## 2. Szczegóły żądania

- **Metoda HTTP:** PATCH
- **Struktura URL:** /api/v1/bricksets/{id}
- **Parametry URL:**
  - `id` (identyfikator BrickSet)
- **Request Body:** (parsowane częściowo, przykładowa struktura)
  - `has_box` (boolean, opcjonalnie)
  - `owner_initial_estimate` (integer, opcjonalnie, wartość między 1 a 999999)

## 3. Wykorzystywane typy

- **Command Model:**
  - `UpdateBrickSetCommand` (definiuje pola edytowalne: `has_box` oraz `owner_initial_estimate`)

- **DTO:**
  - `BrickSetDetailDTO` (pełen szczegół BrickSet, wykorzystywane przy odpowiedzi)
  - Inne DTO odpowiedzialne za listy, agregacje (np. `BrickSetListItemDTO`) mogą być użyte przy optymalizacji odpowiedzi 

## 4. Szczegóły odpowiedzi

- **Sukces (200):** Zwraca zaktualizowany BrickSet zgodnie z `BrickSetDetailDTO`.
- **Kody błędów:**
  - 403: BRICKSET_EDIT_FORBIDDEN (naruszenie reguł edycji, np. ocena użytkowników lub like > 0 dla oceny właściciela)
  - 404: BRICKSET_NOT_FOUND
  - 400: VALIDATION_ERROR (nieprawidłowe dane wejściowe)
  - 401: NOT_AUTHENTICATED (brak autentykacji)

## 5. Przepływ danych

1. Żądanie trafia do warstwy kontrolera (Django View) z użyciem Django REST Framework.
2. Middleware sprawdza autentykację użytkownika (401 w razie nieautoryzowanego dostępu).
3. Logika biznesowa w serwisie (lub managerze modelu) weryfikuje:
   - Czy użytkownik jest właścicielem BrickSet (autoryzacja).
   - Czy nie występują oceny od innych użytkowników.
   - Czy ocena właściciela, jeśli istnieje, ma 0 like'ów.
4. Po pozytywnej weryfikacji dane są walidowane zgodnie z `UpdateBrickSetCommand`.
5. BrickSet jest aktualizowany w bazie danych (PostgreSQL) przy zachowaniu integralności kluczy i unikalnych indeksów.
6. Odpowiedź zaktualizowanego BrickSet wysyłana jest do klienta.

## 6. Względy bezpieczeństwa

- **Autoryzacja:** Tylko właściciel BrickSet może dokonać edycji.
- **Walidacja danych:** Każde pole w żądaniu musi przejść walidację (np. owner_initial_estimate musi być w odpowiednim zakresie).
- **Sprawdzanie reguł biznesowych:** Upewnij się, że nie można edytować BrickSet, jeśli już dokonano oceny przez innych użytkowników lub wartość oceny właściciela ma więcej niż 0 like'ów.
- **Logowanie błędów:** Mechanizm zapisywania prób naruszenia uprawnień lub nieprawidłowych aktualizacji wdrożyć w systemach logowania i monitoringu.

## 7. Obsługa błędów

- **403 BRICKSET_EDIT_FORBIDDEN:** Gdy reguły edycji są naruszone (np. oceny od innych użytkowników lub 0 like'ów nie zostanie spełnione).
- **404 BRICKSET_NOT_FOUND:** BrickSet o podanym `id` nie istnieje.
- **400 VALIDATION_ERROR:** Gdy dane wejściowe nie spełniają wymagań walidacyjnych (np. typy danych, zakres owner_initial_estimate).
- **401 NOT_AUTHENTICATED:** Gdy użytkownik nie jest zalogowany.
- **500 Internal Server Error:** W razie nieoczekiwanych błędów backendu.

## 8. Rozważania dotyczące wydajności

- Wykorzystanie indeksów na kolumnach używanych w zapytaniach (np. `id`, `owner_id`).
- Efektywna walidacja danych po stronie modelu przy użyciu managerów i metod serwisowych.
- Cache'owanie jeżeli to możliwe przy odczytach BrickSet, lecz należy pamiętać o spójności danych przy aktualizacjach.

## 9. Etapy wdrożenia

1. **Implementacja walidacji:**
   - Utworzenie lub modyfikacja serwisu odpowiedzialnego za logikę edycji BrickSet.
   - Implementacja walidacji reguł biznesowych (FR-06, RB-01).
2. **Aktualizacja kontrolera:**
   - Wdrożenie klasy widoku (Django REST Framework) obsługującej PATCH /api/v1/bricksets/{id}.
   - Wstrzyknięcie zależności (serwis, walidatory).
3. **Integracja z modelem:**
   - Użycie `UpdateBrickSetCommand` dla parsowania i walidacji danych wejściowych.
   - Aktualizacja modelu BrickSet z wykorzystaniem managerów lub metod serwisowych.
4. **Testy jednostkowe i integracyjne:**
   - Pokrycie krytycznych ścieżek testami (pytest) oraz scenariuszami błędów.
5. **Dokumentacja i przegląd kodu:**
   - Przygotowanie dokumentacji dla API endpointu i umieszczenie przykładów użycia.
6. **Deploy i monitorowanie:**
   - Wdrożenie na środowisku testowym, monitorowanie logów i feedbacku z użytkowania.


---

Plan wdrożenia ten jest zgodny z przyjętymi normami wewnętrznymi oraz wykorzystuje technologie: Django, Django REST Framework, PostgreSQL. Wszystkie kroki są niezbędne dla zapewnienia bezpieczeństwa, integralności danych oraz prawidłowego działania endpointu.
