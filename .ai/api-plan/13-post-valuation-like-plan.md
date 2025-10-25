# API Endpoint Implementation Plan: POST Valuation Like

## 1. Przegląd punktu końcowego
Endpoint umożliwia dodanie polubienia (like) do wyceny przez użytkownika. W momencie, gdy użytkownik dodaje like do wyceny, zwracany jest obiekt z identyfikatorem wyceny, identyfikatorem użytkownika oraz datą utworzenia polubienia.

## 2. Szczegóły żądania
- **Metoda HTTP**: POST
- **Struktura URL**: /api/v1/valuations/{valuation_id}/likes
- **Parametry**:
  - **Wymagane**:
    - `valuation_id` – identyfikator wyceny (liczba całkowita) pobierany z URL
  - **Opcjonalne**: Body może być puste
- **Request Body**: Brak (opcjonalne, ponieważ wszystkie dane są przekazywane w URL i kontekście uwierzytelnienia)

## 3. Wykorzystywane typy
- **Command Model**:
  - `LikeValuationCommand` – zawiera `valuation_id` z ścieżki
- **DTO**:
  - `LikeDTO` – reprezentacja odpowiedzi z polami: `valuation_id`, `user_id`, `created_at`

## 4. Szczegóły odpowiedzi
- **Sukces (201)**:
  ```json
  {
    "valuation_id": 77,
    "user_id": 42,
    "created_at": "..."
  }
  ```
- **Błędy**:
  - **403 LIKE_OWN_VALUATION_FORBIDDEN** – użytkownik próbuje polubić własną wycenę
  - **409 LIKE_DUPLICATE** – próba dodania duplikatu lajkowania
  - **404 VALUATION_NOT_FOUND** – wycena o podanym `valuation_id` nie istnieje
  - **401 NOT_AUTHENTICATED** – brak autoryzacji
  - **500 INTERNAL_SERVER_ERROR** – nieoczekiwany błąd po stronie serwera

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
