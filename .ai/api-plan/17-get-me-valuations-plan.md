# API Endpoint Implementation Plan: GET /api/v1/users/me/valuations

## 1. Przegląd punktu końcowego
Ten endpoint umożliwia uwierzytelnionemu użytkownikowi pobranie listy jego wycen. Umożliwia przeglądanie historycznych wycen zestawów LEGO dokonanych przez użytkownika. Endpoint jest chroniony i dostępny tylko dla autoryzowanych użytkowników.

## 2. Szczegóły żądania
- **Metoda HTTP:** GET
- **Struktura URL:** /api/v1/users/me/valuations
- **Parametry:**
  - Wymagane: Brak dodatkowych parametrów poza danymi uwierzytelniającymi
  - Opcjonalne: Możliwość implementacji paginacji (np. `page`, `page_size`), jeżeli zajdzie potrzeba
- **Request Body:** Brak

## 3. Wykorzystywane typy
- **DTO:**
  - `OwnedValuationListItemDTO`: zawiera pola:
    - id: int
    - brickset: obiekt zawierający: { id: int, number: int }
    - value: int
    - currency: string
    - likes_count: int
    - created_at: datetime
- **Command Models:** Brak – operacja jest typu odczytu, nie wymaga komend do modyfikacji danych

## 4. Szczegóły odpowiedzi
- **Kod 200 (OK):**
  ```json
  {
    "count": 7,
    "results": [
      {
        "id": 77,
        "brickset": {
          "id": 10,
          "number": 12345
        },
        "value": 400,
        "currency": "PLN",
        "likes_count": 9,
        "created_at": "..."
      }
    ]
  }
  ```
- **Kody błędów:**
  - 401: NOT_AUTHENTICATED, gdy użytkownik nie jest zalogowany
  - 500: Błąd serwera w przypadku nieoczekiwanych problemów

## 5. Przepływ danych
1. Użytkownik wysyła żądanie GET do endpointu `/api/v1/users/me/valuations` z poprawnymi danymi uwierzytelniającymi (np. token JWT).
2. Warstwa uwierzytelniania (middleware DRF) weryfikuje tożsamość użytkownika.
3. Widok pobiera obiekt `request.user` i filtruje rekordy w tabeli `valuation_valuation` według `user_id` odpowiadającego autoryzowanemu użytkownikowi.
4. Wyniki są serializowane przy użyciu serializer'a opartego na `OwnedValuationListItemDTO`.
5. Serwer zwraca odpowiedź JSON zawierającą liczbę całkowitą (`count`) oraz tablicę wyników (`results`).

## 6. Względy bezpieczeństwa
- Endpoint jest dostępny **tylko dla uwierzytelnionych użytkowników** – brak tokena lub sesji skutkuje zwróceniem 401.
- Upewnienie się, że użytkownik może przeglądać **tylko swoje wyceny** (filtracja na podstawie `request.user`).
- Wykorzystanie Django ORM chroni przed SQL Injection.
- Zabezpieczenie przed wyciekiem danych wrażliwych – odpowiedź zawiera tylko niezbędne informacje.

## 7. Obsługa błędów
- **401 Unauthorized:** gdy użytkownik nie jest zalogowany.
- **500 Internal Server Error:** w przypadku wystąpienia nieprzewidzianych problemów, np. błąd bazy danych.
- (Opcjonalnie) **400 Bad Request:** w przypadku implementacji dodatkowych parametrów (np. paginacji) i wystąpienia niepoprawnych wartości.

## 8. Rozważania dotyczące wydajności
- **Indeksacja:** Upewnić się, że kolumna `user_id` w tabeli `valuation_valuation` ma założony odpowiedni indeks.
- **Paginacja:** Rozważenie implementacji mechanizmu paginacji, aby ograniczyć ilość zwracanych rekordów przy bardzo dużej liczbie wycen.
- **Cache:** Opcjonalne wykorzystanie cache'owania wyników przy częstym odczycie danych.

## 9. Etapy wdrożenia
1. **Implementacja serializer'a:** Utworzenie serializer'a w DRF zgodnie z modelem `OwnedValuationListItemDTO`.
2. **Implementacja widoku:** Zaimplementowanie klasy View (np. `ListAPIView`), która:
   - sprawdza autoryzację użytkownika,
   - filtruje rekordy wg `request.user`,
   - serializuje dane do formatu JSON.
3. **Konfiguracja routingu:** Dodanie ścieżki URL `/api/v1/users/me/valuations` do konfiguracji routingowej DRF.
4. **Testy jednostkowe:** Napisanie testów dla endpointu przy użyciu pytest, weryfikujących poprawność logiki oraz autoryzację.
5. **Testy E2E:** Implementacja testów E2E np. przy użyciu Cypress, aby zweryfikować pełen przepływ od wysłania żądania do uzyskania odpowiedzi.
6. **Przegląd bezpieczeństwa:** Weryfikacja, że endpoint nie wycieka danych i że wszelkie operacje są bezpieczne.
7. **Dokumentacja:** Aktualizacja dokumentacji API (Swagger/OpenAPI) o nowy endpoint.
8. **Wdrożenie:** Po pozytywnym przejściu testów i przeglądzie kodu – wdrożenie do środowiska produkcyjnego.
