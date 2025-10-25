# API Endpoint Implementation Plan: GET /api/v1/users/me/bricksets

## 1. Przegląd punktu końcowego
Endpoint umożliwia pobranie listy zestawów LEGO należących do aktualnie zalogowanego użytkownika. Zestawy są wzbogacone o statystyki, takie jak liczba wycen i łączna liczba lajków, a także flagę określającą możliwość edycji. Endpoint jest zgodny z FR-14 i wykorzystuje logikę oceny edytowalności na podstawie reguły RB-01.

## 2. Szczegóły żądania
- **Metoda HTTP:** GET
- **Struktura URL:** /api/v1/users/me/bricksets
- **Parametry zapytania:**
  - **Wymagane:** Brak
  - **Opcjonalne:**
    - `page` - numer strony
    - `page_size` - liczba elementów na stronie
    - `ordering` - sortowanie, z dopuszczalnymi wartościami np. `-created_at`, `-valuations`, `-likes`
- **Request Body:** Brak

## 3. Wykorzystywane typy
- **DTO:**
  - `OwnedBrickSetListItemDTO` (zawiera m.in. pola: id, number, production_status, completeness, valuations_count, total_likes, editable)
- **Command Modele:** Endpoint nie modyfikuje danych, więc nie wymaga command modeli związanych z tworzeniem lub aktualizacją.

## 4. Szczegóły odpowiedzi
- **Kod odpowiedzi:** 200 OK - przy poprawnym pobraniu danych
- Struktura odpowiedzi:
  ```json
  {
    "count": <int>,
    "results": [
      {
        "id": <int>,
        "number": <int>,
        "production_status": "ACTIVE" | "RETIRED",
        "completeness": "COMPLETE" | "INCOMPLETE",
        "valuations_count": <int>,
        "total_likes": <int>,
        "editable": <boolean>
      },
      ...
    ]
  }
  ```
- **Błędy:**
  - 401 NOT_AUTHENTICATED - gdy użytkownik nie jest zalogowany

## 5. Przepływ danych
1. Użytkownik wysyła zapytanie GET do endpointu z opcjonalnymi parametrami paginacji i sortowania.
2. Warstwa autoryzacji weryfikuje token/ sesję użytkownika.
3. Backend wykorzystuje odpowiednią logikę serwisową, aby pobrać dane z tabeli `catalog_brickset`, powiązanych wycen z `valuation_valuation` oraz ocenić regułę RB-01 w celu wskazania pola `editable`.
4. Wyniki są mapowane do DTO: `OwnedBrickSetListItemDTO`.
5. Dane są opakowane w paginowaną odpowiedź zawierającą łączną liczbę rekordów oraz listę elementów.

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie i autoryzacja:** Endpoint musi być dostępny tylko dla zalogowanych użytkowników (sprawdzenie tokena JWT lub sesji).
- **Weryfikacja uprawnień:** Upewnić się, że użytkownik uzyskuje dostęp tylko do własnych zasobów (sprawdzenie `owner_id`).
- **Walidacja parametrów:** Walidacja parametrów `page`, `page_size` oraz `ordering` na poziomie serializera lub warstwy widoku.

## 7. Obsługa błędów
- **Brak autoryzacji:**
  - Warunek: Użytkownik nie jest zalogowany
  - Odpowiedź: 401 NOT_AUTHENTICATED
- **Nieprawidłowe parametry:**
  - Warunek: Parametry zapytania nie spełniają wymagań walidacji (np. nieprawidłowy format `ordering` lub niepoprawne numery stron)
  - Odpowiedź: 400 BAD_REQUEST
- **Błąd serwera:**
  - Warunek: Niespodziewane wyjątki w trakcie przetwarzania zapytania
  - Odpowiedź: 500 INTERNAL_SERVER_ERROR

## 8. Rozważania dotyczące wydajności
- **Optymalizacja zapytań:** Upewnić się, że zapytania SQL są zoptymalizowane, np. poprzez indeksowanie kolumn używanych przy sortowaniu i filtrowaniu.
- **Paginacja:** Implementacja paginacji na poziomie bazy danych, aby minimalizować ilość danych przetwarzanych i przesyłanych.
- **Cache:** Rozważyć mechanizmy cache’owania wyników, jeśli dane rzadko się zmieniają.

## 9. Etapy wdrożenia
1. **Analiza i projekt:**
   - Zdefiniowanie specyfikacji endpointu oraz mapowania danych do DTO.
2. **Implementacja widoku:**
   - Utworzenie klasy-based view w Django REST Framework.
   - Zaimplementowanie klasy widoku z walidacją parametrów i paginacją.
3. **Implementacja logiki serwisowej:**
   - Wydzielenie logiki pobierania danych i mapowania do DTO w warstwie service (jeżeli nie istnieje, utworzyć nową).
4. **Testy jednostkowe i integracyjne:**
   - Przygotowanie testów z użyciem pytest i narzędzi do testowania API.
   - Zdefiniowanie scenariuszy testowych dla poprawnych żądań oraz obsługi błędów.
5. **Walidacja bezpieczeństwa:**
   - Upewnienie się, że endpoint odpowiednio weryfikuje uwierzytelnienie i autoryzację.
6. **Dokumentacja:**
   - Uaktualnienie dokumentacji API w projekcie.
7. **Code review oraz merge:**
   - Przeprowadzenie code review, testy na środowisku developerskim, a następnie merge do głównej gałęzi.
