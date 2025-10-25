# API Endpoint Implementation Plan: GET /api/v1/metrics/system

## 1. Przegląd punktu końcowego
Endpoint służy do pobierania zagregowanych danych systemowych dotyczących zestawów i użytkowników. Dane pobierane są z tabeli `valuation_metrics`, która operuje na jednym wierszu (id=1). Endpoint ma umożliwić dostęp wszystkim uwierzytelnionym użytkownikom.

## 2. Szczegóły żądania
- **Metoda HTTP:** GET
- **Struktura URL:** /api/v1/metrics/system
- **Parametry:**
  - **Wymagane:** Brak (poza nagłówkiem autoryzacji)
  - **Opcjonalne:** Brak
- **Request Body:** Nie dotyczy

## 3. Wykorzystywane typy
- **DTO:** SystemMetricsDTO (z polami: total_sets, serviced_sets, active_users, serviced_sets_ratio, active_users_ratio, updated_at)
- **Command Model:** Brak – metoda GET nie wymaga modelu komend

## 4. Szczegóły odpowiedzi
- **Kod 200:** Sukces – zwraca strukturę JSON:
  ```json
  {
    "total_sets": 57,
    "serviced_sets": 44,
    "active_users": 20,
    "serviced_sets_ratio": 0.7719,
    "active_users_ratio": 0.9091,
    "updated_at": "..."
  }
  ```
- **Kody błędów:**
  - 401 NOT_AUTHENTICATED – użytkownik nie jest zalogowany
  - 403 FORBIDDEN – użytkownik nie posiada odpowiednich uprawnień (choć w MVP wszyscy uwierzytelnieni mają dostęp)
  - 500 Internal Server Error – błąd po stronie serwera (np. problem z bazą danych)

## 5. Przepływ danych
1. Uwierzytelnienie użytkownika przez Django REST Framework (np. przy użyciu tokena lub sesji).
2. Wywołanie metody w warstwie service, która pobiera wiersz z tabeli `valuation_metrics` (id=1).
3. Zmapowanie danych z rekordu bazy danych na obiekt DTO (`SystemMetricsDTO`).
4. Zwrócenie odpowiedzi jako JSON przez widok API.

## 6. Względy bezpieczeństwa
- **Uwierzytelnienie i Autoryzacja:** 
  - Sprawdzenie tokena autoryzacyjnego w nagłówku.
  - Weryfikacja, czy użytkownik jest uwierzytelniony (w MVP wszyscy zalogowani mają dostęp).
- **Walidacja:** 
  - Minimalna walidacja, ponieważ nie są przesyłane dane wejściowe poza nagłówkiem.
- **Logowanie:** 
  - Rejestrowanie nieudanych prób dostępu (401/403).

## 7. Obsługa błędów
- **401 Unauthorized:** Gdy token nie został przekazany lub jest nieprawidłowy.
- **403 Forbidden:** Gdy istnieje ograniczenie dostępu dla danego użytkownika (w przyszłości, np. tylko pracownicy mogą mieć dostęp).
- **500 Internal Server Error:** W przypadku awarii po stronie serwera (np. problem z dostępem do bazy danych).

## 8. Rozważenia dotyczące wydajności
- Pobranie pojedynczego wiersza z tabeli `valuation_metrics` gwarantuje minimalny narzut czasowy.
- Istnieje możliwość wprowadzenia mechanizmu cache’owania danych w przyszłych iteracjach w celu jeszcze szybszego odczytu, jednak na obecnym etapie nie jest to krytyczne.

## 9. Etapy wdrożenia
1. **Przygotowanie struktury DTO:**
   - Utworzenie klasy `SystemMetricsDTO` z odpowiednimi polami.
2. **Implementacja warstwy service:**
   - Utworzenie funkcji/metody pobierającej dane z tabeli `valuation_metrics` (id=1).
3. **Implementacja widoku API:**
   - Utworzenie widoku opartego na klasie (CBV) z użyciem Django REST Framework.
   - Dodanie metody GET, która wywołuje warstwę service i serializuje wynik za pomocą `SystemMetricsDTO`.
4. **Walidacja i zabezpieczenia:**
   - Konfiguracja mechanizmów uwierzytelniania oraz autoryzacji.
5. **Testy:**
   - Implementacja testów jednostkowych (pytest) dla scenariuszy:
     - Poprawny odczyt danych (200).
     - Brak autoryzacji (401).
     - Ewentualna odmowa dostępu (403).
     - Obsługa błędów serwera (500).
6. **Dokumentacja:**
   - Aktualizacja dokumentacji API oraz dodanie przykładowych wywołań w README.
7. **Deploy oraz monitoring:**
   - Wdrożenie endpointu wraz z monitorowaniem logów błędów.
