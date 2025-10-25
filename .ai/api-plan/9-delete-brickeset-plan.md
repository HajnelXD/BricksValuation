# API Endpoint Implementation Plan: DELETE /api/v1/bricksets/{id}

## 1. Przegląd punktu końcowego
Endpoint odpowiada za usunięcie encji BrickSet z systemu. Użytkownik autoryzowany przez system może usunąć BrickSet, pod warunkiem spełnienia określonych ograniczeń (analogicznie do logiki edycji). W przypadku pomyślnego wykonania, zwracany jest kod 204 bez treści.

## 2. Szczegóły żądania
- **Metoda HTTP:** DELETE
- **Struktura URL:** /api/v1/bricksets/{id}
- **Parametry:**
  - **Wymagane:**
    - `id` – identyfikator BrickSet, którym operujemy
  - **Opcjonalne:** Brak
- **Request Body:** Brak

## 3. Wykorzystywane typy
- **DTO/Command Model:**
  - `BrickSetDTO` zdefiniowany w `catalog_dto.py` (ewentualnie rozszerzony o DeleteBrickSetCommand, jeśli stosujemy wzorzec CQRS)
  - Ewentualnie dodatkowy model do walidacji parametrów żądania

## 4. Szczegóły odpowiedzi
- **Kod 204:** Usunięcie powiodło się, brak treści w odpowiedzi
- **Kody błędów:**
  - 401 NOT_AUTHENTICATED – brak uwierzytelnienia
  - 403 BRICKSET_DELETE_FORBIDDEN – użytkownik nie ma uprawnień do usunięcia zasobu
  - 404 BRICKSET_NOT_FOUND – BrickSet o podanym id nie istnieje
  - 500 Internal Server Error – niespodziewany błąd po stronie serwera

## 5. Przepływ danych
1. Żądanie DELETE trafia do endpointu wraz z parametrem `id` BrickSet.
2. Middleware uwierzytelniający potwierdza tożsamość użytkownika.
3. Warstwa kontrolera przekazuje `id` do serwisu odpowiedzialnego za usunięcie BrickSet.
4. Serwis:
   - Sprawdza istnienie BrickSet w bazie danych
   - Weryfikuje, czy użytkownik jest uprawniony do usunięcia (sprawdzenie relacji z account oraz statusu rekordu)
   - Wykonuje logikę usuwania oraz ewentualne akcje pokrewne (np. czyszczenie powiązań lub wyzwalanie sygnałów)
5. Po poprawnym wykonaniu, zwracany jest status 204.

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie:** Sprawdzenie, czy żądanie pochodzi od autoryzowanego użytkownika (401 w przypadku niepowodzenia).
- **Autoryzacja:** Weryfikacja, czy użytkownik ma prawo do usunięcia BrickSet (w przeciwnym wypadku 403).
- **Walidacja wejścia:** Sprawdzenie formatu i zakresu parametru `id` oraz konieczność zgodności z wytycznymi modelu bazy danych.
- **Transakcje i spójność:** Upewnienie się, że operacja usuwania jest wykonana w obrębie transakcji, aby zachować spójność danych (np. kasowanie zależnych rekordów dzięki FK ON DELETE CASCADE).

## 7. Obsługa błędów
- **401 NOT_AUTHENTICATED:** Komunikat wskazujący na brak sesji lub poprawnych danych autoryzacyjnych
- **403 BRICKSET_DELETE_FORBIDDEN:** Błąd uprawnień, gdy użytkownik nie jest właścicielem lub nie spełnia innych kryteriów
- **404 BRICKSET_NOT_FOUND:** Informacja, że BrickSet o podanym identyfikatorze nie został odnaleziony
- **500 Internal Server Error:** Zgłoszenie nieoczekiwanego problemu, z możliwością logowania błędów w systemie

## 8. Rozważania dotyczące wydajności
- Operacja usuwa pojedynczy rekord, więc nie powinna być zasobożerna.
- Indeks na kolumnie `id` zapewnia szybkie wyszukiwanie rekordu.
- Wykorzystanie transakcji zapewnia bezpieczeństwo operacji przy jednoczesnym zachowaniu wysokiej wydajności.

## 9. Etapy wdrożenia
1. **Projektowanie kontrolera:** 
   - Utworzenie endpointu DELETE w obrębie istniejącego widoku opartego o Django REST Framework.
2. **Implementacja warstwy serwisowej:**
   - Wyodrębnienie logiki usuwania BrickSet do dedykowanego serwisu. Jeśli nie istnieje taki serwis, utworzenie nowego.
3. **Walidacja danych wejściowych:**
   - Implementacja walidacji parametru `id` oraz autoryzacji użytkownika.
4. **Integracja z bazą danych:**
   - Sprawdzenie istnienia rekordu, weryfikacja uprawnień i wykonanie operacji usuwania z transakcją.
5. **Obsługa błędów:**
   - Przechwytywanie wyjątków i zwracanie odpowiednich kodów statusu oraz komunikatów.
6. **Testy jednostkowe oraz E2E:**
   - Stworzenie zestawu testów sprawdzających poprawność działania endpointu (w tym scenariusze dla 401, 403, 404 i 500).
7. **Wdrożenie i monitoring:**
   - Deploy endpointu oraz konfiguracja logowania błędów i monitorowania stanu aplikacji.



