# API Endpoint Implementation Plan: GET /api/v1/auth/me

## 1. Przegląd punktu końcowego
Endpoint służy do pobrania profilu aktualnie uwierzytelnionego użytkownika. Głównym celem jest umożliwienie klientom aplikacji uzyskania danych swojego konta, takich jak identyfikator, nazwa użytkownika, adres email oraz data utworzenia konta. Endpoint jest dostępny jedynie dla użytkowników, którzy przeszli uwierzytelnienie.

## 2. Szczegóły żądania
- **Metoda HTTP**: GET
- **Struktura URL**: /api/v1/auth/me
- **Parametry**:
  - **Wymagane**: Brak, ale niezbędne jest uwierzytelnienie (np. token lub sesja cookie).
  - **Opcjonalne**: Brak
- **Request Body**: Nie dotyczy

## 3. Wykorzystywane typy
- **DTO**:
  - `UserProfileDTO` – pełny profil użytkownika, zawiera: id, username, email, created_at.
  - *Opcjonalnie*: `UserRefDTO` – minimalna referencja do użytkownika, stosowana w innych endpointach.
- **Command Modele**: Brak, ponieważ endpoint nie przyjmuje danych wejściowych do modyfikacji.

## 4. Szczegóły odpowiedzi
- **Kod 200**: Zwracany w przypadku poprawnego pobrania profilu z przykładową strukturą:
  ```json
  {
    "id": 123,
    "username": "user123",
    "email": "user@example.com",
    "created_at": "2025-10-21T12:34:56Z"
  }
  ```
- **Kod 401**: Zwracany, gdy użytkownik nie jest uwierzytelniony.
- **Inne kody**: 500 dla błędów serwera, ewentualnie 400 dla nieprawidłowych żądań, choć w przypadku GET nie są typowe.

## 5. Przepływ danych
1. Klient wysyła żądanie GET do `/api/v1/auth/me` z ważnym tokenem autoryzacyjnym lub sesją.
2. Warstwa uwierzytelniania (np. Django REST Framework authentication classes) weryfikuje token.
3. Po pomyślnej weryfikacji, system pobiera dane użytkownika z bazy danych (tabela `account_account`).
4. Dane są mapowane do modelu DTO (`UserProfileDTO`), który ogranicza informacje (np. pomija dane wrażliwe takie jak hasło, aktualizacje itd.).
5. Serwer zwraca dane w formacie JSON z kodem 200.

## 6. Względy bezpieczeństwa
- Endpoint musi być zabezpieczony mechanizmem autoryzacji (np. JWT, sesje).
- Weryfikacja uprawnień: Tylko uwierzytelniony użytkownik może pobierać swój profil.
- Minimalizacja danych: Upewnić się, że wysyłane są tylko niezbędne informacje (np. pomija się pola wrażliwe takie jak hasło).

## 7. Obsługa błędów
- **401 NOT_AUTHENTICATED**: Zwracany, gdy żądanie pochodzi od niezautoryzowanego użytkownika.
- **500 INTERNAL SERVER ERROR**: W przypadku nieoczekiwanych błędów serwera (np. problemy z bazą danych).
- Ewentualna logika rejestrowania błędów w przypadku wystąpienia krytycznych awarii (monitoring i alerting).

## 8. Rozważania dotyczące wydajności
- Użycie odpowiednich optymalizacji na poziomie bazy danych (np. indeksy na kolumnach kluczowych, jeśli odpowiednie).
- Cache’owanie profilu użytkownika w krótkich interwałach, jeżeli obciążenie serwera staje się problemem.
- Minimalizacja zapytań do bazy danych przez selektywne wyciąganie tylko wymaganych pól.

## 9. Etapy wdrożenia
1. **Uwierzytelnienie**: Upewnić się, że mechanizm uwierzytelniania (token lub sesja) jest poprawnie skonfigurowany w projekcie.
2. **Utworzenie widoku**: Implementacja class-based view w Django wykorzystująca Django REST Framework. Widok ma zwracać dane użytkownika po weryfikacji autoryzacji.
3. **Serializer**: Stworzenie serializera mapującego model użytkownika na `UserProfileDTO`.
4. **Routing**: Dodanie ścieżki `/api/v1/auth/me` do konfiguracji URL w aplikacji.
5. **Walidacja**: Testowanie endpointu przy użyciu narzędzi jak Postman lub testy jednostkowe w pytest, upewniając się, że przypadki brzegowe są odpowiednio obsłużone.
6. **Obsługa błędów**: Implementacja globalnego handlera dla błędów w DRF, logowanie błędów krytycznych.
7. **Dokumentacja**: Uaktualnienie dokumentacji API z przykładowymi żądaniami i odpowiedziami.
8. **Testy**: Utworzenie testów jednostkowych oraz e2e, aby zapewnić poprawne działanie endpointu pod rząd różnorakich przypadków, w tym nieważnego tokena.
9. **Code Review**: Przejrzenie zmian z zespołem i wdrożenie zgodnie z zasadami kontroli wersji oraz przeglądu kodu.




