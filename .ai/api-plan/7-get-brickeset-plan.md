/# API Endpoint Implementation Plan: GET /api/v1/bricksets/{id}

## 1. Przegląd punktu końcowego
Endpoint służy do pobierania szczegółowych informacji o zestawie LEGO (BrickSet) wraz z listą ocen (valuations) i podsumowaniem wycen. Ma na celu umożliwienie klientowi uzyskania pełnych danych o BrickSecie, które uwzględniają podstawowe metryki (liczba wycen, suma polubień) oraz szczegóły poszczególnych ocen.

## 2. Szczegóły żądania
- **Metoda HTTP:** GET
- **Struktura URL:** `/api/v1/bricksets/{id}`
- **Parametry:**
  - **Wymagane:** 
    - `id` (path parameter) – unikalny identyfikator BrickSetu.
  - **Opcjonalne:** 
    - Nagłówki autoryzacyjne (np. token JWT) zapewniające uwierzytelnienie.
- **Request Body:** Brak

## 3. Wykorzystywane typy
- **DTOs:**
  - `BrickSetDetailDTO` – zawiera pełne szczegóły BrickSetu: dane podstawowe, listę wartościacji (`valuations`), agregacje (`valuations_count`, `total_likes`), daty utworzenia i aktualizacji.
  - `ValuationInlineDTO` – reprezentacja pojedynczej wyceny w ramach bricksetu.
- **Command Modele:** Nie dotyczy GET

## 4. Szczegóły odpowiedzi
- **Sukces (200 OK):**
  - Struktura JSON odpowiadająca `BrickSetDetailDTO`, np.:
    ```json
    {
      "id": 10,
      "number": 12345,
      "production_status": "ACTIVE",
      "completeness": "COMPLETE",
      "has_instructions": true,
      "has_box": true,
      "is_factory_sealed": false,
      "owner_initial_estimate": 360,
      "owner_id": 42,
      "valuations": [
        {
          "id": 77,
          "user_id": 99,
          "value": 400,
          "currency": "PLN",
          "comment": "Looks complete",
          "likes_count": 9,
          "created_at": "..."
        }
      ],
      "valuations_count": 5,
      "total_likes": 12,
      "created_at": "...",
      "updated_at": "..."
    }
    ```
- **Błędy:**
  - `401 NOT_AUTHENTICATED` – gdy użytkownik nie dostarczy poprawnych danych autoryzacyjnych.
  - `404 BRICKSET_NOT_FOUND` – gdy BrickSet o podanym id nie został znaleziony.
  - `500 INTERNAL_SERVER_ERROR` – dla nieobsłużonych wyjątków i błędów serwera.

## 5. Przepływ danych
1. Żądanie trafia do kontrolera (Django class-based view) po uwierzytelnieniu.
2. Warstwa serwisowa (np. BrickSetService) wykonuje zapytanie do bazy danych w poszukiwaniu BrickSetu z danym id, wraz z powiązanymi wycenami.
3. Pobierane są agregaty: liczba wycen oraz suma polubień.
4. Dane są mapowane do struktury `BrickSetDetailDTO` przy użyciu serializerów Django REST Framework.
5. Wynik jest zwracany w formacie JSON do klienta.

## 6. Względy bezpieczeństwa
- **Uwierzytelnienie:** Endpoint powinien być zabezpieczony mechanizmem uwierzytelniania (np. JWT).
- **Autoryzacja:** Sprawdzenie, czy użytkownik posiada uprawnienia do dostępu do danego zasobu.
- **Ochrona danych:** Stosowanie ORM Django do bezpiecznego wykonywania zapytań i zapobieganie SQL Injection.
- **Logika wyjątków:** Poprawne logowanie błędów przy jednoczesnym ukrywaniu szczegółowych informacji przed użytkownikami.

## 7. Obsługa błędów
- **401 NOT_AUTHENTICATED:** Brak lub niewłaściwy token uwierzytelniający.
- **404 BRICKSET_NOT_FOUND:** BrickSet o podanym `id` nie został znaleziony.
- **500 INTERNAL_SERVER_ERROR:** W przypadku nieoczekiwanych błędów – zalecane logowanie błędu oraz zwrócenie odpowiedniego komunikatu.

## 8. Rozważania dotyczące wydajności
- **Optymalizacja zapytań:** Użycie metody `select_related` i/lub `prefetch_related` dla wydajnego pobierania powiązanych danych (np. wycen).
- **Indeksy bazy danych:** Zapewnienie odpowiednich indeksów w tabeli `catalog_brickset` dla pola `id` oraz potencjalnych kolumn używanych do agregacji.
- **Cache'owanie:** Rozważenie cache’owania wyników dla endpointów o wysokiej częstotliwości odczytów.

## 9. Etapy wdrożenia
1. **Projektowanie i dokumentacja:**
   - Zebranie wymagań i omówienie specyfikacji API.
   - Ustalenie struktury DTO i mapowania danych.
2. **Implementacja widoku:**
   - Utworzenie Django class-based view wykorzystującej DRF.
   - Wdrożenie logiki walidacji parametru `id`.
3. **Warstwa serwisowa:**
   - Stworzenie metody w istniejącej lub nowej klasie serwisowej do pobierania szczegółów BrickSetu wraz z wycenami.
   - Zastosowanie optymalizacji zapytań przy użyciu `select_related`/`prefetch_related`.
4. **Serializacja danych:**
   - Implementacja serializerów na bazie `BrickSetDetailDTO` i `ValuationInlineDTO`.
5. **Bezpieczeństwo:**
   - Walidacja tokenu i autoryzacja żądania.
6. **Obsługa błędów:**
   - Wdrożenie mechanizmów zwracających odpowiednie kody statusu (401, 404, 500).
   - Testowanie scenariuszy błędów.
7. **Testy jednostkowe i integracyjne:**
   - Pokrycie endpointu testami jednostkowymi (pytest) i e2e (Cypress) w celu walidacji poprawności działania.
8. **Wdrożenie i monitorowanie:**
   - Wdrożenie rozwiązania na środowisku testowym.
   - Monitorowanie wydajności i logów aplikacji.
