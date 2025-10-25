# API Endpoint Implementation Plan: GET /api/v1/bricksets

## 1. Przegląd punktu końcowego
Endpoint ten służy do pobierania listy zestawów LEGO (BrickSets) wraz z możliwością wyszukiwania i filtrowania wyników. Funkcjonalność obejmuje paginację, sortowanie oraz filtrowanie po różnych kryteriach, co pozwala klientom na szybkie odnalezienie pożądanych danych.

## 2. Szczegóły żądania
- **Metoda HTTP:** GET
- **Struktura URL:** /api/v1/bricksets
- **Parametry zapytania:**
  - **Wymagane:**
    - `page` (int, ≥1) 
    - `page_size` (int, 1-100; domyślnie 20)
  - **Opcjonalne:**
    - `q` (string) – wyszukiwanie według numeru (częściowe dopasowanie)
    - `production_status` (enum: np. `ACTIVE`, `RETIRED`)
    - `completeness` (enum: np. `COMPLETE`, `INCOMPLETE`)
    - `has_instructions` (bool)
    - `has_box` (bool)
    - `is_factory_sealed` (bool)
    - `ordering` (string); dozwolone wartości: `-created_at`, `created_at`, `-popular`, `-valuations` (domyślnie `-created_at`)
- **Request Body:** Brak

## 3. Wykorzystywane typy
- **DTO:**
  - `BrickSetListItemDTO` – główny typ odpowiedzi zawierający dane o zestawach LEGO, w tym dane agregowane (liczba wycen, suma polubień) oraz dodatkowe podsumowanie:
    - `TopValuationSummaryDTO` (opcjonalnie, wewnątrz `BrickSetListItemDTO`)

- **Command Modele:** (niewymagane w przypadku GET) 
  - `CreateBrickSetCommand`
  - `UpdateBrickSetCommand`

## 4. Szczegóły odpowiedzi
- **Kod stanu:** 200 przy sukcesie
- **Struktura odpowiedzi (przykład):**
  ```json
  {
    "count": 57,
    "next": "https://.../bricksets?page=2",
    "previous": null,
    "results": [
      {
        "id": 10,
        "number": 12345,
        "production_status": "ACTIVE",
        "completeness": "COMPLETE",
        "has_instructions": true,
        "has_box": false,
        "is_factory_sealed": false,
        "owner_id": 42,
        "owner_initial_estimate": 350,
        "valuations_count": 5,
        "total_likes": 12,
        "top_valuation": {
          "id": 77,
          "value": 400,
          "currency": "PLN",
          "likes_count": 9,
          "user_id": 99
        },
        "created_at": "...",
        "updated_at": "..."
      }
    ]
  }
  ```

- **Kody błędów:**
  - 400 – Błędne dane wejściowe (np. niepoprawne parametry zapytania)
  - 401 – Brak uwierzytelnienia, w przypadku gdy dostęp do wyszukiwania wymaga logowania (FR-18)
  - 500 – Błąd serwera

## 5. Przepływ danych
1. Klient wysyła zapytanie GET z opcjonalnymi parametrami do endpointu `/api/v1/bricksets`.
2. Warstwa widoku (np. Django REST Framework view) odbiera żądanie i przekazuje dane do warstwy serwisowej.
3. Warstwa serwisowa wykonuje walidację parametrów oraz buduje zapytanie do bazy danych (uwzględniając filtrowanie, sortowanie i paginację).
4. Dane są pobierane z tabeli `catalog_brickset` oraz powiązanych danych (np. agregaty wyliczane z `valuations`).
5. Wyniki są mapowane do DTO `BrickSetListItemDTO` wraz z opcjonalnym `TopValuationSummaryDTO` dla najpopularniejszej wyceny.
6. Warstwa serwisowa zwraca dane do widoku, który serializuje wynik do formatu JSON.
7. Odpowiedź jest wysyłana do klienta.

## 6. Względy bezpieczeństwa
- **Uwierzytelnianie:** Sprawdzić, czy użytkownik jest zalogowany (jeśli wymagane przez FR-18).
- **Autoryzacja:** Pełny dostęp do odczytu zestawów LEGO; dodatkowe pola lub filtrowanie mogą być zabezpieczone regułami aplikacji.
- **Walidacja:** Dokładna walidacja parametrów wejściowych w celu zapobiegania atakom na bazę danych (np. SQL Injection) oraz błędy w typach danych.
- **Logowanie:** Monitorowanie błędów i nieautoryzowanych prób dostępu z wykorzystaniem mechanizmów logowania.

## 7. Obsługa błędów
- **400 VALIDATION_ERROR:** Przy błędach walidacji parametrów wejściowych.
- **401 NOT_AUTHENTICATED:** Jeżeli wymaga się logowania, a użytkownik nie jest zalogowany.
- **404 NOT_FOUND:** W sytuacji, gdy zasób nie istnieje (choć ten endpoint zwykle zwraca pustą listę zamiast 404).
- **500 SERVER_ERROR:** Błędy nieoczekiwane po stronie serwera.

## 8. Rozważania dotyczące wydajności
- Wykorzystanie paginacji, aby ograniczyć liczbę zwracanych rekordów.
- Indeksy na krytycznych kolumnach, takich jak `number`, `completeness` czy `production_status`, w celu zoptymalizowania zapytań filtrowania.
- Cache'owanie wyników wyszukiwania przy dużej liczbie odczytów.

## 9. Etapy wdrożenia
1. **Analiza wymagań:** Przejrzenie specyfikacji API oraz typów DTO.
2. **Implementacja widoku:** Stworzenie endpointu GET w Django REST Framework zgodnie z wymaganiami.
3. **Warstwa serwisowa:** Wyodrębnienie logiki filtrowania, sortowania i paginacji do osobnej warstwy serwisowej.
4. **Walidacja zapytań:** Implementacja walidacji parametrów wejściowych (np. przy użyciu serializerów DRF).
5. **Mapowanie danych:** Implementacja mapowania wyników z bazy danych do DTO `BrickSetListItemDTO`.
6. **Testy jednostkowe i integracyjne:** Testowanie poprawności działania endpointu oraz zachowania przy błędach.
7. **Logowanie i monitoring:** Dodanie mechanizmów logowania oraz monitorowania błędów.
8. **Code review i wdrożenie:** Audyt kodu przez zespół, poprawki oraz wdrożenie na środowisko testowe i produkcyjne.

---

Plan ten ma na celu zapewnienie wysokiej jakości implementacji punktu końcowego, zgodnej z wymaganiami biznesowymi, najlepszymi praktykami oraz zapewniającą bezpieczeństwo i wydajność aplikacji.
