# API Endpoint Implementation Plan: POST /api/v1/auth/login

## 1. Przegląd punktu końcowego
Endpoint służy do uwierzytelnienia użytkownika poprzez weryfikację podanych danych logowania. W przypadku poprawnych danych serwer generuje i zwraca token JWT, który jest zapisywany w HttpOnly secure cookie oraz opcjonalnie dołączany do odpowiedzi.

## 2. Szczegóły żądania
- **Metoda HTTP:** POST
- **Adres URL:** /api/v1/auth/login
- **Parametry:**
  - **Wymagane:**
    - `username` (string): Nazwa użytkownika
    - `password` (string): Hasło użytkownika
  - **Opcjonalne:** Brak
- **Request Body (JSON):**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

## 3. Wykorzystywane typy
- **Command Model:** `LoginCommand`
- **DTO:** `UserRefDTO`, `LoginSuccessDTO`

## 4. Szczegóły odpowiedzi
- **Sukces (200):**
  ```json
  {
    "user": {"id": 123, "username": "user123", "email": "user@example.com"},
    "token": "<jwt>"
  }
  ```
- **Błędy:**
  - 400 VALIDATION_ERROR – brak wymaganych pól lub nieprawidłowy format danych
  - 401 INVALID_CREDENTIALS – niepoprawne dane logowania
  - 500 INTERNAL_SERVER_ERROR – błąd po stronie serwera

## 5. Przepływ danych
1. Klient wysyła żądanie POST z danymi `username` i `password` w ciele żądania.
2. Dane są walidowane poprzez serializer w Django REST Framework.
3. Warstwa serwisowa weryfikuje dane logowania (wyszukiwanie użytkownika, weryfikacja hasła).
4. W przypadku sukcesu generowany jest token JWT, który:
   - Zostaje zapisany w HttpOnly secure cookie
   - Opcjonalnie jest dołączany do odpowiedzi JSON
5. Odpowiedź jest wysyłana do klienta.

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie/Autoryzacja:** Weryfikacja danych przy użyciu istniejącej logiki Django oraz Django REST Framework.
- **Bezpieczeństwo danych:** Hasła przesyłane w żądaniu są walidowane, a następnie porównywane z haszami w bazie danych.
- **Tokeny JWT:** Tokeny są generowane i przesyłane w HttpOnly secure cookie, aby zabezpieczyć je przed atakami XSS.
- **Rate Limiting:** Rozważenie implementacji ograniczenia liczby prób logowania w celu ochrony przed atakami brute-force.

## 7. Obsługa błędów
- **400 VALIDATION_ERROR:** Błąd walidacji, gdy brakuje wymaganych pól lub dane są nieprawidłowe.
- **401 INVALID_CREDENTIALS:** Brak autoryzacji przy nieprawidłowych danych logowania.
- **500 INTERNAL_SERVER_ERROR:** Błąd serwera, np. problem z generowaniem tokena lub dostępem do bazy danych.

## 8. Rozważenia dotyczące wydajności
- Minimalizowanie liczby zapytań do bazy danych poprzez efektywną obsługę sesji i cache’owanie wyników.
- Użycie indeksów w tabeli użytkowników dla szybszych zapytań.
- Optymalizacja logiki autoryzacji, aby zminimalizować opóźnienia w responsie.

## 9. Etapy wdrożenia
1. **Stworzenie endpointu:** Utworzenie widoku opartego na klasach w Django REST Framework dedykowanego do obsługi logowania.
2. **Walidacja danych:** Implementacja serializerów do walidacji danych wejściowych (`LoginCommand`).
3. **Logika autentykacji:** Integracja z warstwą serwisową odpowiedzialną za weryfikację hasła oraz generowanie tokena JWT.
4. **Bezpieczeństwo:** Ustawienie HttpOnly secure cookie z tokenem JWT oraz implementacja mechanizmów ograniczających liczbę prób logowania.
5. **Testy:** 
   - Testy jednostkowe przy użyciu pytest
   - Testy end-to-end przy użyciu Cypress dla scenariuszy: poprawne logowanie, błędy walidacji, nieudane logowanie.
6. **Code Review i Deployment:** Przegląd kodu, wdrożenie w środowisku testowym oraz monitorowanie działania endpointu po wdrożeniu.
