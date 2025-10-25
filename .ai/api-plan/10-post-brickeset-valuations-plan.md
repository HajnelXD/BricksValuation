# API Endpoint Implementation Plan: BrickSet Valuations

## 1. Przegląd punktu końcowego
Endpoint umożliwia użytkownikom tworzenie wyceny (valuation) zestawu klocków (BrickSet). System zapewnia, że dla danego użytkownika wycena zestawu może być utworzona tylko raz. Wdrożenie uwzględnia walidację danych, zabezpieczenia autoryzacyjne oraz prawidłową obsługę odpowiedzi i błędów.

## 2. Szczegóły żądania
- **Metoda HTTP:** POST
- **Struktura URL:** /api/v1/bricksets/{brickset_id}/valuations
- **Parametry URL:** 
  - brickset_id (wymagany)
- **Request Body:** JSON
  - **Wymagane:**
    - value (liczba całkowita, zakres 1..999999)
  - **Opcjonalne:**
    - currency (string, domyślnie 'PLN')
    - comment (string, opcjonalny opis)

## 3. Wykorzystywane typy
- **Command Models:**
  - CreateValuationCommand (parametry: brickset_id, value, currency, comment)
- **DTO Models:**
  - ValuationDTO (z polami: id, brickset_id, user_id, value, currency, comment, likes_count, created_at, updated_at)
  - (Dodatkowo inne DTO dla list wycen, ale dla tego endpointu głównie wykorzystywany jest ValuationDTO)

## 4. Szczegóły odpowiedzi
- **Success 201:** Zwraca obiekt ValuationDTO
  ```json
  {
    "id": 77,
    "brickset_id": 10,
    "user_id": 99,
    "value": 400,
    "currency": "PLN",
    "comment": "Looks complete",
    "likes_count": 0,
    "created_at": "...",
    "updated_at": "..."
  }
  ```
- **Kody statusu:** 
  - 201: utworzenie wyceny
  - 400: błąd walidacji (np. niepoprawny zakres value)
  - 401: brak autoryzacji
  - 404: zestaw klocków nie znaleziony
  - 409: duplikat wyceny (użytkownik już dokonał wyceny tego zestawu)
  - 500: błąd serwera

## 5. Przepływ danych
1. Żądanie trafia do endpointu wraz z brickset_id jako parametrem ścieżki i danymi w ciele żądania.
2. Autoryzacja: Sprawdzenie, czy użytkownik jest zalogowany.
3. Walidacja danych: 
   - Sprawdzenie, czy wartość `value` mieści się w zakresie 1..999999.
   - Uzupełnienie pola `currency` domyślną wartością 'PLN', jeśli nie podano.
4. Sprawdzenie duplikatu: Weryfikacja, czy użytkownik już nie dokonał wyceny danego BrickSet (unikatowy klucz: user_id, brickset_id).
5. Utworzenie rekordu w bazie danych (model `valuation_valuation`).
6. Zwrócenie odpowiedzi z danymi nowo utworzonej wyceny zgodnie z modelem ValuationDTO.

## 6. Względy bezpieczeństwa
- **Autoryzacja:** Endpoint wymaga uwierzytelnienia (401 w przypadku braku autoryzacji).
- **Walidacja danych:** Przed przetwarzaniem żądania wszystkie dane wejściowe powinny być walidowane, aby zapobiec wstrzyknięciom lub niepoprawnemu formatowaniu.
- **Obsługa duplikatów:** Zapewnienie unikalności wyceny dla użytkownika i zestawu przez weryfikację przed utworzeniem rekordu.

## 7. Obsługa błędów
- **409 VALUATION_DUPLICATE:** W przypadku próby utworzenia wyceny, która już istnieje dla danego użytkownika i BrickSetu.
- **400 VALIDATION_ERROR:** W przypadku niepoprawnych danych wejściowych (np. wartość `value` poza zakresem).
- **404 BRICKSET_NOT_FOUND:** Gdy BrickSet o podanym identyfikatorze nie istnieje.
- **401 NOT_AUTHENTICATED:** Gdy użytkownik nie jest zalogowany.
- **500 INTERNAL_SERVER_ERROR:** W przypadku nieprzewidzianych błędów serwera.

## 8. Rozważania dotyczące wydajności
- Sprawdzenie duplikatów i walidacja powinny być optymalizowane przez odpowiednie indeksy w bazie danych (indeks na kolumny user_id i brickset_id).
- Użycie Django ORM i Django REST Framework pozwala na efektywne przetwarzanie żądań, natomiast mechanizmy cachowania (np. Redis) mogą być rozważone dla dalszych optymalizacji przy wysokim obciążeniu.

## 9. Etapy wdrożenia
1. **Analiza wymagań:** Potwierdzenie specyfikacji, przegląd typów DTO i command modeli.
2. **Implementacja walidacji:** Dodanie walidacji dla `value`, uzupełnienie pola `currency` oraz zabezpieczenie przed duplikatami.
3. **Stworzenie logiki serwisowej:** Wyodrębnienie logiki biznesowej do warstwy serwisowej (np. w module `valuation/services`).
4. **Integracja z bazą danych:** Upewnienie się, że model danych odpowiada strukturze tabeli oraz, że istnieją odpowiednie indeksy.
5. **Implementacja endpointu:** Utworzenie widoku (class-based view) wykorzystującego Django REST Framework, obsługa autoryzacji oraz walidacji.
6. **Testy jednostkowe i E2E:** Pokrycie implementacji testami, użycie pytest dla backendu oraz dodanie testów dla scenariuszy błędów.
7. **Dokumentacja:** Aktualizacja dokumentacji API, w tym specyfikacji endpointu oraz dokumentacji technicznej.
8. **Code review i wdrożenie:** Przegląd kodu przez zespół, integracja z CI/CD oraz wdrożenie na środowisku testowym, a następnie produkcyjnym.
