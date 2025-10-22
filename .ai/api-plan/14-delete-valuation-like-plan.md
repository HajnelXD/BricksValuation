# API Endpoint Implementation Plan: DELETE /api/v1/valuations/{valuation_id}/likes

## 1. Przegląd punktu końcowego

Endpoint umożliwia usunięcie polubienia (like) wyceny przez użytkownika. Funkcjonalność ta pozwala na cofnięcie akcji polubienia, zapewniając spójność danych oraz możliwość anulowania wcześniejszej interakcji.

## 2. Szczegóły żądania

- **Metoda HTTP:** DELETE
- **Struktura URL:** /api/v1/valuations/{valuation_id}/likes
- **Parametry ścieżki:**
  - `valuation_id` (wymagany): Identyfikator wyceny, której like ma zostać usunięty.
- **Request Body:** Brak

## 3. Wykorzystywane typy

- **Command Model:** `UnlikeValuationCommand`
  - Definiowany w `valuation_dto.py`.
  - Atrybuty:
    - `valuation_id: int`
- **DTO Models:** (W przypadku endpointu DELETE, odpowiedź zwykle nie wymaga DTO, gdyż zwracany jest status 204 - No Content.)

## 4. Szczegóły odpowiedzi

- **Sukces:**
  - Status: 204 No Content
  - Brak treści odpowiedzi
- **Błędy:**
  - 401 NOT_AUTHENTICATED: Użytkownik nie jest zalogowany.
  - 404 LIKE_NOT_FOUND: Polubienie nie zostało znalezione (np. nie istnieje like danego użytkownika dla danej wyceny).
  - Opcjonalnie: 405 METHOD_NOT_ALLOWED, jeśli endpoint nie zostanie wdrożony.
  - 500 INTERNAL SERVER ERROR: Błąd po stronie serwera.

## 5. Przepływ danych

1. Użytkownik wysyła żądanie DELETE z `valuation_id` w URL.
2. Warstwa uwierzytelniania sprawdza, czy użytkownik jest zalogowany (w przypadku braku – 401).
3. Kontroler (widok Django) pobiera `valuation_id` i tworzy instancję `UnlikeValuationCommand`.
4. Service layer przetwarza komendę:
   - Weryfikacja istnienia rekordu like powiązanego z danym `valuation_id` i aktualnym `user_id`.
   - Usunięcie rekordu w bazie danych.
5. W przypadku powodzenia, zwracany jest status 204.

## 6. Względy bezpieczeństwa

- **Uwierzytelnianie:** Endpoint wymaga autoryzacji. Żądania bez ważnego tokena autoryzacyjnego powinny zwrócić 401.
- **Autoryzacja:** Użytkownik może usuwać jedynie własne polubienia. Należy zweryfikować, że `user_id` powiązany z like jest zgodny z aktualnym użytkownikiem.
- **Walidacja:** Sprawdzenie poprawności `valuation_id` oraz istnienia odpowiedniego rekordu w bazie.

## 7. Obsługa błędów

- **401 NOT_AUTHENTICATED:** Gdy żądanie pochodzi od niezalogowanego użytkownika.
- **404 LIKE_NOT_FOUND:** Gdy rekord like dla danego `valuation_id` i `user_id` nie istnieje.
- **500 INTERNAL SERVER ERROR:** W przypadku nieoczekiwanych błędów podczas przetwarzania żądania.

Dodatkowo, można logować błędy aplikacyjne w celu ich analizy i śledzenia nieudanych prób usunięcia like.

## 8. Rozważania dotyczące wydajności

- Wykonanie operacji usunięcia rekordu z bazy danych powinno być szybkie, pod warunkiem odpowiednich indeksów na polach `user_id` oraz `valuation_id` w tabeli `valuation_like`.
- W razie potrzeby można rozważyć cache'owanie wyników zapytań, ale dla operacji DELETE nie jest to zwykle wymagane.

## 9. Etapy wdrożenia

1. **Definicja endpointu:**
   - Utworzenie nowej ścieżki URL w pliku `urls.py` konfiguracji API.
   - Definicja klasy widoku (class-based view) korzystającej z Django REST Framework.

2. **Implementacja walidacji:**
   - Sprawdzenie uwierzytelnienia użytkownika.
   - Weryfikacja obecności like dla danego `valuation_id` i aktualnego `user_id`.

3. **Implementacja service layer:**
   - Utworzenie lub rozszerzenie istniejącej logiki serwisowej, która przyjmie `UnlikeValuationCommand`.
   - Przeprowadzenie usunięcia rekordu i obsługa potencjalnych wyjątków.

4. **Testy jednostkowe i integracyjne:**
   - Przygotowanie testów za pomocą pytest (i ewentualnie fixtures, monkeypatch, baker) dla endpointu DELETE.
   - Testowanie zarówno scenariuszy sukcesu (204), jak i błędów (401, 404, 500).

5. **Dokumentacja:**
   - Aktualizacja dokumentacji API, uwzględniając nowe endpointy i odpowiadające im przykłady żądań oraz odpowiedzi.

6. **Przegląd zabezpieczeń:**
   - Weryfikacja testów bezpieczeństwa, m.in. sprawdzenie, że użytkownicy nie mogą usuwać like innych użytkowników.

7. **Wdrożenie i monitorowanie:**
   - Wdrożenie zmian w środowisku developerskim, a następnie testy w środowisku staging.
   - Monitorowanie logów i wydajności po wdrożeniu do produkcji.
