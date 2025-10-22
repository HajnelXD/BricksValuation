# API Endpoint Implementation Plan: POST /api/v1/bricksets

## 1. Przegląd punktu końcowego

Endpoint POST /api/v1/bricksets służy do tworzenia nowego rekordu BrickSet. Jego głównym celem jest przyjmowanie danych wejściowych z interfejsu API, walidacja danych oraz zapisanie nowego rekordu w bazie danych, przy jednoczesnym uwzględnieniu reguł biznesowych (np. unikalność kombinacji cech) i zabezpieczeń (uwierzytelnianie użytkownika).

## 2. Szczegóły żądania

- **Metoda HTTP:** POST
- **URL:** /api/v1/bricksets
- **Parametry (w treści żądania JSON):**
  - **Wymagane:**
    - `number` (liczba całkowita, max 7 cyfr, >=0)
    - `production_status` (łańcuch znaków, np. "ACTIVE" lub "RETIRED")
    - `completeness` (łańcuch znaków, np. "COMPLETE" lub "INCOMPLETE")
    - `has_instructions` (boolean)
    - `has_box` (boolean)
    - `is_factory_sealed` (boolean)
  - **Opcjonalne:**
    - `owner_initial_estimate` (liczba całkowita, > 0 i < 1000000)

Przykładowe żądanie:
```json
{
  "number": 12345,
  "production_status": "ACTIVE",
  "completeness": "COMPLETE",
  "has_instructions": true,
  "has_box": true,
  "is_factory_sealed": false,
  "owner_initial_estimate": 360
}
```

## 3. Wykorzystywane typy

- **Command Model:**
  - `CreateBrickSetCommand` (definiowany w `catalog_dto.py`)

- **DTO Model (odpowiedź):**
  - `BrickSetListItemDTO` (dla listy lub szczegółowy BrickSet) z dodatkowymi polami takimi jak `valuations_count`, `total_likes`, `created_at`, `updated_at`.

## 4. Szczegóły odpowiedzi

- **Sukces (201 Created):**

  Przykładowa odpowiedź:
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
    "valuations_count": 0,
    "total_likes": 0,
    "created_at": "...",
    "updated_at": "..."
  }
  ```

- **Błędy:**
  - 400 VALIDATION_ERROR (błędne typy, zakresy)
  - 409 BRICKSET_DUPLICATE (naruszenie reguły unikalnej kombinacji cech)
  - 401 NOT_AUTHENTICATED (nieautoryzowany dostęp)

## 5. Przepływ danych

1. **Odbiór żądania:** Endpoint odbiera dane JSON od klienta.
2. **Walidacja danych:** Walidacja zarówno na poziomie serializera DRF (jak i niestandardowe walidatory) jak i na poziomie modelu (CHECK constraints w bazie danych).
3. **Mapowanie:** Przekształcenie danych wejściowych przy użyciu `CreateBrickSetCommand` do obiektu domenowego BrickSet.
4. **Operacja na bazie:** Wywołanie logiki w warstwie service, która zapisuje rekord w bazie danych przy uwzględnieniu reguły unikalności.
5. **Budowanie odpowiedzi:** Na podstawie zapisanego rekordu, odpowiedź jest budowana przy użyciu odpowiedniego DTO, np. `BrickSetListItemDTO`.
6. **Reakcja na błędy:** W przypadku naruszeń walidacji lub duplikacji, odpowiednie kody statusu są zwracane.

## 6. Względy bezpieczeństwa

- **Uwierzytelnianie:** Endpoint powinien być dostępny tylko dla zalogowanych użytkowników (np. przy użyciu Token Auth lub JWT).
- **Autoryzacja:** Sprawdzenie, czy użytkownik ma prawo tworzyć nowy BrickSet.
- **Walidacja:** Szczegółowa walidacja danych wejściowych, aby zapobiec SQL Injection, przekroczeniu limitów liczbowych i innym nieprawidłowościom.
- **Kontrola unikalności:** Sprawdzenie globalnej unikalności kombinacji (number, completeness, has_instructions, has_box, is_factory_sealed) przed zapisaniem.

## 7. Obsługa błędów

- **400 VALIDATION_ERROR:** Gdy walidacja danych wejściowych nie powiedzie się (np. niepoprawny format lub wartości poza zakresem).
- **409 BRICKSET_DUPLICATE:** Gdy nowy BrickSet narusza unikalność połączenia cech.
- **401 NOT_AUTHENTICATED:** Gdy użytkownik nie jest zalogowany.
- **500 INTERNAL_SERVER_ERROR:** Dla niespodziewanych błędów po stronie serwera.

## 8. Rozważania dotyczące wydajności

- **Indeksy:** Wykorzystanie indeksów na kolumnach `number` oraz użycie częściowych indeksów dla kolumn filtrujących (np. completeness), co przyspiesza wyszukiwanie i sprawdzanie unikalności.
- **Warstwa service:** Oddzielenie logiki biznesowej od kontrolerów w celu umożliwienia łatwiejszej optymalizacji i rozproszenia obliczeń w przyszłości.

## 9. Etapy wdrożenia

1. **Analiza wymagań:** Omówienie specyfikacji z zespołem i potwierdzenie wymagań biznesowych oraz technicznych.
2. **Projekt modelu:** Przegląd i ewentualna modyfikacja modelu BrickSet i jego constraintów w bazie danych.
3. **Implementacja serializera:** Utworzenie lub modyfikacja serializera DRF, który mapuje dane wejściowe na `CreateBrickSetCommand`.
4. **Warstwa service:** Implementacja logiki biznesowej w nowej lub istniejącej warstwie service, która:
   - Wykonuje walidację dodatkową,
   - Sprawdza unikalność rekordu,
   - Przekazuje dane do modelu i zapisuje w bazie.
5. **Implementacja endpointu:** Utworzenie klasy widoku (np. opartej o Django REST Framework) obsługującej POST /api/v1/bricksets.
6. **Testy jednostkowe i integracyjne:** Opracowanie testów walidujących poprawne działanie endpointu, obsługę błędów i integrację z bazą danych.
7. **Code review i dokumentacja:** Przegląd kodu przez zespół oraz aktualizacja dokumentacji API.
8. **Wdrożenie:** Wdrożenie rozwiązania w środowisku testowym, a następnie produkcyjnym.


---

Plan wdrożenia powinien zapewnić jasne wytyczne dla zespołu programistów, uwzględniając specyfikację techniczną, zasady bezpieczeństwa oraz wymagania biznesowe. Każdy krok musi być starannie przetestowany przed wdrożeniem w środowisku produkcyjnym.