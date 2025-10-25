# API Endpoint Implementation Plan: POST /api/v1/auth/register

## 1. Przegląd punktu końcowego
Celem endpointu jest umożliwienie rejestracji nowego użytkownika. Przyjmuje on dane niezbędne do utworzenia konta użytkownika i zwraca pełny profil nowo utworzonego użytkownika. Domyślnie, bez automatycznego logowania (auth cookie), wymagana jest jawna procedura logowania po rejestracji.

## 2. Szczegóły żądania
- **Metoda HTTP:** POST
- **Struktura URL:** /api/v1/auth/register
- **Parametry:**
  - **Wymagane:**
    - username (string, 3-50 znaków)
    - email (string, poprawny format email)
    - password (string, min. 8 znaków)
  - **Opcjonalne:**
    - Brak dodatkowych parametrów; ewentualnie obsługa ciasteczka autoryzacji może być rozważona w przyszłości
- **Request Body (JSON):**
  ```json
  {
    "username": "user123",
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```

## 3. Wykorzystywane typy
- **Command Models:**
  - `RegisterUserCommand` (definiowany w account_dto.py) - zawiera pola: username, email, password
- **DTO Models:**
  - `UserProfileDTO` - służy do zwracania szczegółowego profilu użytkownika (id, username, email, created_at) po pomyślnej rejestracji

## 4. Szczegóły odpowiedzi
- **Sukces (201 Created):**
  ```json
  {
    "id": 123,
    "username": "user123",
    "email": "user@example.com",
    "created_at": "2025-10-21T12:34:56Z"
  }
  ```
- **Kody statusu:**
  - 201 - Konto utworzone pomyślnie
  - 400 - Błędy walidacyjne (np. niepoprawny email, za krótki username lub hasło)
  - 409 - Konflikt: username lub email już zajęty
  - 500 - Błąd serwera

## 5. Przepływ danych
1. Klient wysyła żądanie POST z danymi rejestracyjnymi.
2. Warstwa walidacji sprawdza poprawność danych wejściowych pod kątem:
   - długości username (3-50 znaków)
   - formatu email
   - długości password (min. 8 znaków)
3. Kontroler (widok Django REST Framework oparty na klasach) oddelegowuje przetwarzanie do warstwy serwisów, która:
   - sprawdza unikalność username oraz email w bazie danych (tabela account_account)
   - hashuje hasło
   - zapisuje nowego użytkownika
4. Po utworzeniu, dane użytkownika są mapowane do `UserProfileDTO` i zwracane do klienta z kodem statusu 201.

## 6. Względy bezpieczeństwa
- Walidacja danych wejściowych z użyciem serializerów Django REST Framework.
- Użycie silnego hashowania haseł (np. PBKDF2, bcrypt) zgodnie z ustawieniami Django.
- Sprawdzenie unikalności email oraz username w bazie danych, aby zapobiec atakom na unikalność danych.
- Ochrona przed atakami typu injection poprzez sanityzację danych wejściowych i korzystanie z ORM Django.
- Zabezpieczenie endpointu przed nieautoryzowanym dostępem (endpoint publiczny, ale logika autoryzacji powinna być starannie przemyślana w przypadku ewentualnego auto-logowania w przyszłości).

## 7. Obsługa błędów
- **400 VALIDATION_ERROR:** Gdy dane wejściowe nie spełniają wymagań (np. niepoprawny email, nieodpowiednia długość pola).
- **409 USERNAME_TAKEN / EMAIL_TAKEN:** Gdy użytkownik próbuje zarejestrować się z już istniejącym username lub email.
- **500 INTERNAL SERVER ERROR:** W przypadku nieoczekiwanych problemów serwerowych.

## 8. Rozważania dotyczące wydajności
- Optymalizacja zapytań do bazy danych poprzez odpowiednie indeksy na kolumnach `username` i `email`.
- Użycie cache (jeśli wymagane) dla statycznych danych lub monitorowania liczby prób rejestracji w celu wykrywania ataków DDoS.
- Implementacja asynchronicznych zadań (np. wysyłanie maili w tle) w przypadku dodatkowych funkcji powiązanych z rejestracją.

## 9. Etapy wdrożenia
1. Utworzenie endpointu rejestracji jako klasy-based view z użyciem Django REST Framework.
2. Implementacja walidacji danych wejściowych oraz mapowania do `RegisterUserCommand`.
3. Delegacja logiki rejestracji do warstwy serwisów, obejmującej sprawdzenie unikalności, hashowanie hasła oraz zapis do bazy danych.
4. Opracowanie odpowiedniego serializera, który przetwarza dane wejściowe i wyjściowe (mapując na `UserProfileDTO`).
5. Implementacja mechanizmu obsługi błędów, zwracającego odpowiednie kody statusu (400, 409, 500).
6. Testowanie endpointu przy użyciu pytest oraz narzędzi do testów integracyjnych (np. Django test client, Cypress dla testów E2E frontendowych).
7. Przegląd kodu oraz walidacja zgodności zmian z zasadami bezpieczeństwa i wydajności.
8. Dokumentacja API oraz aktualizacja dokumentacji technicznej.


---
**Uwaga:** Plan wdrożenia zakłada że istniejące modele Django, DTO i konfiguracja projektu są zgodne z wymaganiami specyfikacji API rejestracji. Każda zmiana powinna być testowana zgodnie z wytycznymi zespołu.
