# API Endpoint Implementation Plan: GET Valuations Likes

## 1. Przegląd punktu końcowego
Endpoint ten służy do pobierania listy użytkowników, którzy polubili daną wycenę. Umożliwia zwrócenie minimalnych referencji użytkowników (np. `user_id` oraz czas polubienia `liked_at`).

## 2. Szczegóły żądania
- **Metoda HTTP**: GET
- **Struktura URL**: `/api/v1/valuations/{valuation_id}/likes`
- **Parametry**:
  - **Wymagane**: 
    - `valuation_id` (ścieżka): identyfikator wyceny, dla której pobierane są lajki
  - **Opcjonalne**: brak
- **Nagłówki**: 
  - Autoryzacja (np. token JWT) - endpoint wymaga uwierzytelnienia

## 3. Wykorzystywane typy
- **DTO**: 
  - `LikeListItemDTO` - reprezentacja pojedynczego wpisu lajku z polami `user_id` oraz `liked_at`
- **Command Models**: W tym przypadku endpoint nie wymaga wejściowych command modeli, gdyż jest operacją typu GET.

## 4. Szczegóły odpowiedzi
- **Kod 200 - OK**: 
  ```json
  {
    "count": 9,
    "results": [
      { "user_id": 42, "liked_at": "2025-10-22T12:34:56Z" },
      ...
    ]
  }
  ```
- **Błędy**:
  - 404 (VALUATION_NOT_FOUND): jeśli wycena o podanym `valuation_id` nie istnieje
  - 401 (NOT_AUTHENTICATED): jeśli użytkownik nie jest zalogowany

## 5. Przepływ danych
1. Otrzymanie żądania GET z `valuation_id` jako parametrem ścieżki.
2. Walidacja tokena uwierzytelniającego.
3. Sprawdzenie istnienia wyceny o podanym `valuation_id`:
   - Jeśli nie istnieje, zwrócenie 404
4. Pobranie rekordów z tabeli `valuation_like` powiązanych z wyceną.
5. Mapowanie rekordów na `LikeListItemDTO` (wyciągając `user_id` oraz `liked_at`).
6. Zliczenie wszystkich wyników i przygotowanie odpowiedzi.
7. Zwrócenie odpowiedzi JSON z kodem 200.

## 6. Względy bezpieczeństwa
- Endpoint wymaga autoryzacji; użytkownik musi być zalogowany (np. za pomocą JWT lub sesji Django).
- Walidacja `valuation_id` – upewnij się, że parametr jest liczbą całkowitą.
- Rozważ dodatkowe ograniczenia dostępu (np. prywatność danych) w zależności od kontekstu aplikacji.

## 7. Obsługa błędów
- **401 NOT_AUTHENTICATED**: gdy użytkownik nie poda prawidłowych danych uwierzytelniających.
- **404 VALUATION_NOT_FOUND**: gdy wycena o podanym ID nie istnieje.
- **500 SERVER ERROR**: dla nieoczekiwanych błędów serwera.

## 8. Rozważania dotyczące wydajności
- Zastosowanie paginacji, jeżeli liczba lajków może być duża, aby zmniejszyć obciążenie bazy danych i sieci.
- Optymalizacja zapytań do bazy, np. przez select_related/prefetch_related, aby minimalizować liczbę zapytań.
- Cache'owanie wyników, jeśli wyceny nie zmieniają się często.

## 9. Etapy wdrożenia
1. **Analiza i projekt**: 
   - Potwierdzenie wymagań funkcjonalnych i bezpieczeństwa z zespołem.
2. **Implementacja widoku**: 
   - Utworzenie klasy-based view z wykorzystaniem Django REST Framework.
   - Dodanie walidacji autoryzacji i istnienia wyceny.
3. **Implementacja serializera**: 
   - Stworzenie serializera dla `LikeListItemDTO`.
4. **Integracja logiki biznesowej**: 
   - Wydzielenie logiki pobierania lajków do warstwy serwisowej, jeśli jeszcze nie istnieje.
5. **Testy jednostkowe i integracyjne**: 
   - Zastosowanie Pytest do testowania walidacji, poprawności danych oraz obsługi błędów.
6. **Testy E2E**: 
   - Implementacja testów przy użyciu Cypress dla interakcji API (weryfikacja kodów statusu i struktury odpowiedzi).
7. **Code review i walidacja**: 
   - Przegląd zmian z zespołem i testy na środowisku deweloperskim.
8. **Wdrożenie**: 
   - Aktualizacja dokumentacji API oraz wdrożenie na środowisko produkcyjne.

---

Komentarz: Plan ten dostarcza kompleksowy opis implementacji, od warstwy interfejsu API, przez logikę biznesową, aż po testy i aspekty wydajnościowe, zgodnie z obowiązującymi wytycznymi technicznymi i zasadami bezpieczeństwa.
