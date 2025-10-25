# BricksValuation – Schemat bazy danych (PostgreSQL)

## 1. Tabele i kolumny

### 1.1 Typy ENUM
- production_status_enum: 'ACTIVE', 'RETIRED'
- completeness_enum: 'COMPLETE', 'INCOMPLETE'

Migracje utworzą typy ENUM (RunSQL lub narzędzie Django). Rozszerzenia w przyszłości przez `ALTER TYPE ... ADD VALUE`.

### 1.2 `account_account` (Custom AbstractUser rozszerzony)
Przechowuje dane użytkownika.

| Kolumna | Typ | Constraints | Uwagi |
|---------|-----|------------|-------|
| id | BIGSERIAL | PK | BigAutoField (globalne ustawienie) |
| username | VARCHAR(50) | NOT NULL, UNIQUE, CHECK (length(username) BETWEEN 3 AND 50) | Login (FR-01) |
| email | VARCHAR(254) | NOT NULL, UNIQUE, CHECK (length(email) > 2) | Format walidowany aplikacyjnie (FR-16) |
| password | VARCHAR(128) | NOT NULL | Hashed (FR-17) |
| is_active | BOOLEAN | NOT NULL DEFAULT TRUE |  |
| is_staff | BOOLEAN | NOT NULL DEFAULT FALSE |  |
| is_superuser | BOOLEAN | NOT NULL DEFAULT FALSE |  |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL DEFAULT CURRENT_TIMESTAMP | Mixin |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL DEFAULT CURRENT_TIMESTAMP | Mixin + trigger aktualizacji |

Triggers: BEFORE UPDATE set updated_at = CURRENT_TIMESTAMP.

### 1.3 `catalog_brickset`
Unikalny zestaw LEGO w systemie (globalna kombinacja cech, bez ownera w UNIQUE). (FR-04, FR-05)

| Kolumna | Typ | Constraints | Uwagi |
|---------|-----|------------|-------|
| id | BIGSERIAL | PK |  |
| owner_id | BIGINT | NOT NULL, FK -> account(id) ON DELETE CASCADE | Właściciel rekordu (FR-14) |
| number | INTEGER | NOT NULL, CHECK (number >= 0 AND number <= 9999999) | Numer zestawu (max 7 cyfr) |
| production_status | production_status_enum | NOT NULL | 'ACTIVE' lub 'RETIRED' |
| completeness | completeness_enum | NOT NULL | 'COMPLETE' lub 'INCOMPLETE' |
| has_instructions | BOOLEAN | NOT NULL DEFAULT FALSE | instrukcja (FR-04) |
| has_box | BOOLEAN | NOT NULL DEFAULT FALSE | pudełko (FR-04) |
| is_factory_sealed | BOOLEAN | NOT NULL DEFAULT FALSE | fabrycznie nowy (FR-04) |
| owner_initial_estimate | INTEGER | NULL, CHECK (owner_initial_estimate > 0 AND owner_initial_estimate < 1000000) | Opcjonalna wstępna wycena |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL DEFAULT CURRENT_TIMESTAMP |  |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL DEFAULT CURRENT_TIMESTAMP |  |

UNIQUE Constraint (globalny): (number, completeness, has_instructions, has_box, is_factory_sealed)

Indeksy dodatkowe przyszłe (deferred): partial index po number (pattern), indeksy filtrujące po completeness.

### 1.4 `valuation_valuation`
Wycena zestawu przez użytkownika (jedna per user-set) (FR-10, FR-11)

| Kolumna | Typ | Constraints | Uwagi |
|---------|-----|------------|-------|
| id | BIGSERIAL | PK |  |
| user_id | BIGINT | NOT NULL, FK -> account_user(id) ON DELETE CASCADE | Autor wyceny |
| brickset_id | BIGINT | NOT NULL, FK -> catalog_brickset(id) ON DELETE CASCADE | Zestaw |
| value | INTEGER | NOT NULL, CHECK (value > 0 AND value < 1000000) | Kwota w PLN (FR-10) |
| currency | CHAR(3) | NOT NULL DEFAULT 'PLN' | Future-proof |
| comment | TEXT | NULL | Opcjonalny opis |
| likes_count | INTEGER | NOT NULL DEFAULT 0 | Denormalizacja (FR-12) |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL DEFAULT CURRENT_TIMESTAMP |  |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL DEFAULT CURRENT_TIMESTAMP |  |

UNIQUE Constraint: (user_id, brickset_id)

Triggers: AFTER INSERT/DELETE na `like_like` aktualizują likes_count.

### 1.5 `valuation_like`
Polubienie wyceny przez innego użytkownika (FR-12, FR-13)

| Kolumna | Typ | Constraints | Uwagi |
|---------|-----|------------|-------|
| id | BIGSERIAL | PK |  |
| user_id | BIGINT | NOT NULL, FK -> account_user(id) ON DELETE CASCADE | Lajkujący |
| valuation_id | BIGINT | NOT NULL, FK -> valuation_valuation(id) ON DELETE CASCADE | Wycena |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL DEFAULT CURRENT_TIMESTAMP |  |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL DEFAULT CURRENT_TIMESTAMP |  |

UNIQUE Constraint: (user_id, valuation_id)

Check/Trigger (opcjonalnie baza; preferencja warstwa aplikacyjna): blokada lajkowania własnej wyceny.

### 1.6 `valuation_metrics`
Przechowuje bieżące zagregowane wartości (jednowierszowa tabela) (FR-19).

| Kolumna | Typ | Constraints | Uwagi |
|---------|-----|------------|-------|
| id | SMALLINT | PK | Można wymusić zawsze id=1 |
| total_sets | INTEGER | NOT NULL DEFAULT 0 | Liczba zestawów |
| serviced_sets | INTEGER | NOT NULL DEFAULT 0 | Zestawy wycenione wg definicji |
| active_users | INTEGER | NOT NULL DEFAULT 0 | Użytkownicy z >=1 zestawem lub wyceną |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL DEFAULT CURRENT_TIMESTAMP | Aktualizacja przy zmianie |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL DEFAULT CURRENT_TIMESTAMP |  |

Triggers: aktualizacja przy INSERT/DELETE na brickset, valuation, like (dla serviced_sets) – szczegóły w sekcji triggerów.

## 2. Relacje
- account_account (1) --- (N) catalog_brickset via owner_id.
- catalog_brickset (1) --- (N) valuation_valuation via brickset_id.
- account_account (1) --- (N) valuation_valuation via user_id.
- valuation_valuation (1) --- (N) valuation_like via valuation_id.
- account_account (1) --- (N) valuation_like via user_id.

Cardinalities:
- Użytkownik może mieć wiele zestawów i wycen; jeden zestaw ma wiele wycen od różnych użytkowników; każda wycena może mieć wiele lajków od różnych użytkowników (z wyłączeniem autora). Wycena jest unikalna per (user, brickset).

## 3. Indeksy

### 3.1 Obowiązkowe (zdefiniowane przez constraints)
- PK: account_account(id)
- UNIQUE: account_account(username), account_account(email)
- PK: catalog_brickset(id)
- UNIQUE: catalog_brickset(number, production_status, completeness, has_instructions, has_box, is_factory_sealed)
- PK: valuation_valuation(id)
- UNIQUE: valuation_valuation(user_id, brickset_id)
- PK: valuation_like(id)
- UNIQUE: valuation_like(user_id, valuation_id)
- PK: valuation_metrics(id)

### 3.2 Relacyjne / FK (PostgreSQL automatyczne lub manualne dla performance)
- INDEX valuation_valuation(brickset_id)
- INDEX valuation_valuation(user_id)
- INDEX valuation_like(valuation_id)
- INDEX valuation_like(user_id)

### 3.3 Przyszłe (deferred)
- GIN/BTREE index na catalog_brickset(number) dla wyszukiwania częściowego (lub BTREE + ILIKE pattern; ewentualnie trigram `pg_trgm`).
- BTREE composite index na (completeness) dla filtrów.
- Partial index na valuation_valuation(likes_count) WHERE likes_count > 0 (sortowanie popularnych wycen).
- Index na valuation_valuation(value) dla analiz rozkładu (opcjonalne).

## 4. Triggery i funkcje (PL/pgSQL)

### 4.1 Aktualizacja `updated_at`
Funkcja: `fn_touch_updated_at()` – BEFORE UPDATE na każdej tabeli głównej ustawia `NEW.updated_at = CURRENT_TIMESTAMP`.

### 4.2 Utrzymanie `likes_count`
Funkcja: `fn_increment_likes_count()` – AFTER INSERT ON like_like:
```
UPDATE valuation_valuation SET likes_count = likes_count + 1 WHERE id = NEW.valuation_id;
```
Funkcja: `fn_decrement_likes_count()` – AFTER DELETE ON like_like:
```
UPDATE valuation_valuation SET likes_count = likes_count - 1 WHERE id = OLD.valuation_id AND likes_count > 0;
```
(Plus CHECK aby likes_count >= 0.)

### 4.3 Aktualizacja metryk `valuation_metrics`
Założenie: pojedynczy rekord id=1.

Funkcja: `fn_refresh_total_sets()` – AFTER INSERT/DELETE ON catalog_brickset:
```
UPDATE metrics_systemmetrics SET total_sets = (
  SELECT COUNT(*) FROM catalog_brickset
), updated_at = CURRENT_TIMESTAMP WHERE id = 1;
```

Funkcja: `fn_refresh_active_users()` – AFTER INSERT/DELETE ON catalog_brickset, valuation_valuation:
```
UPDATE metrics_systemmetrics SET active_users = (
  SELECT COUNT(DISTINCT user_id) FROM (
    SELECT owner_id AS user_id FROM catalog_brickset
    UNION ALL
    SELECT user_id FROM valuation_valuation
  ) t
), updated_at = CURRENT_TIMESTAMP WHERE id = 1;
```

Funkcja: `fn_refresh_serviced_sets()` – AFTER INSERT/DELETE ON valuation_valuation, like_like:
Definicja zestawu obsłużonego:
```
UPDATE metrics_systemmetrics SET serviced_sets = (
  SELECT COUNT(*) FROM catalog_brickset bs
  WHERE EXISTS (
    SELECT 1 FROM valuation_valuation v
    WHERE v.brickset_id = bs.id AND v.user_id <> bs.owner_id
  )
  OR EXISTS (
    SELECT 1 FROM valuation_valuation v
    WHERE v.brickset_id = bs.id AND v.user_id = bs.owner_id AND v.likes_count > 0
  )
), updated_at = CURRENT_TIMESTAMP WHERE id = 1;
```

Optymalizacja przyszła: inkrementalne aktualizacje zamiast pełnych COUNT.

### 4.4 Blokada lajkowania własnej wyceny (opcjonalny trigger)
Zamiast aplikacyjnej walidacji można użyć BEFORE INSERT na like_like:
```
IF (SELECT user_id FROM valuation_valuation WHERE id = NEW.valuation_id) = NEW.user_id THEN
  RAISE EXCEPTION 'Cannot like own valuation';
END IF;
```
(MVP: realizacja w warstwie aplikacji; trigger jako dokumentacja.)

## 5. Row Level Security (RLS) – koncepcja (DEFERRED)
RLS nie jest wdrożony w MVP, lecz plan:
- Tabela `catalog_brickset`: polityka allow SELECT dla wszystkich zalogowanych; UPDATE/DELETE tylko gdy brak obcej wyceny i brak lajków – wymaga złożonego warunku (prawdopodobnie funkcja `can_edit_brickset(user_id, brickset_id)`).
- Tabela `valuation_valuation`: SELECT dla zalogowanych; DELETE/UPDATE (gdyby w przyszłości) tylko autor.
- Tabela `valuation_like`: SELECT dla zalogowanych; DELETE tylko autor.
- `valuation_metrics`: SELECT rola staff/admin.

Implementacja przez:
```
ALTER TABLE catalog_brickset ENABLE ROW LEVEL SECURITY;
CREATE POLICY brickset_select ON catalog_brickset FOR SELECT USING (true);
-- Kolejne polityki w przyszłości.
```

## 6. Normalizacja i denormalizacja
- Modele w 3NF: brak redundancji poza kontrolowaną `likes_count` (denormalizacja uzasadniona wydajnością sortowania FR-09/FR-12).
- `likes_count` aktualizowane atomowo triggerami.
- Brak przechowywania agregatów na BrickSet (np. liczba wycen) – liczone dynamicznie lub dodane później jeśli performance uzasadni.

## 7. Dodatkowe uwagi projektowe
- Globalna unikalność BrickSet może ograniczać dodanie identycznego zestawu przez innego użytkownika; w przyszłości rozważ usunięcie globalnego UNIQUE na rzecz per-user unikalności + centralny katalog zestawów referencyjnych.
- Walidacja email i hasła głównie w aplikacji; baza zapewnia unikalność i minimalną długość.
- Brak soft delete upraszcza COUNT i metryki; ewentualne archiwum w przyszłości.
- Migracje ENUM: używać dedykowanych operacji; zmiana wartości wymaga rewizji.
- Potencjalne indeksy dla wyszukiwania (ILIKE) mogą korzystać z rozszerzenia `pg_trgm` (CREATE EXTENSION pg_trgm;).
- Warto rozważyć materializowany widok dla raportu metryk przy większej skali.
- currency pozostaje stałe 'PLN'; możliwość dodania tabeli `currency_rate` w przyszłości.
- W przyszłości audyt poprzez dodatkowe tabele *_history lub rozszerzenie (np. django-simple-history) – poza zakresem.

## 8. Podsumowanie zgodności z wymaganiami
- FR-01..FR-03: User model wspiera rejestrację/logowanie (hash hasła, unikalność login/email).
- FR-04..FR-09: BrickSet + Valuation + Like struktury odzwierciedlają dodawanie, unikalność, wyceny, lajki, podgląd.
- FR-10..FR-13: Constraints i triggery zapewniają jedną wycenę, lajki, blokadę lajkowania własnej (aplikacja / trigger).
- FR-14..FR-15: Relacje umożliwiają listy własnych zestawów i wycen.
- FR-16..FR-17: Email/hasło – walidacja i bezpieczne przechowywanie.
- FR-18: RLS koncepcja + aplikacyjna autoryzacja.
- FR-19: Tabela metryk + triggery aktualizujące.
- FR-20: Constraints i opcjonalne triggery wspierają komunikaty walidacji.

## 9. Przykładowe definicje SQL (fragmenty)

```sql
CREATE TYPE production_status_enum AS ENUM ('ACTIVE', 'RETIRED');
CREATE TYPE completeness_enum AS ENUM ('COMPLETE', 'INCOMPLETE');

CREATE TABLE catalog_brickset (
  id BIGSERIAL PRIMARY KEY,
  owner_id BIGINT NOT NULL REFERENCES account_user(id) ON DELETE CASCADE,
  number INTEGER NOT NULL CHECK (number >= 0 AND number <= 9999999),
  production_status production_status_enum NOT NULL,
  completeness completeness_enum NOT NULL,
  has_instructions BOOLEAN NOT NULL DEFAULT FALSE,
  has_box BOOLEAN NOT NULL DEFAULT FALSE,
  is_factory_sealed BOOLEAN NOT NULL DEFAULT FALSE,
  owner_initial_estimate INTEGER NULL CHECK (owner_initial_estimate > 0 AND owner_initial_estimate < 1000000),
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (number, production_status, completeness, has_instructions, has_box, is_factory_sealed)
);

CREATE TABLE valuation_valuation (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES account_user(id) ON DELETE CASCADE,
  brickset_id BIGINT NOT NULL REFERENCES catalog_brickset(id) ON DELETE CASCADE,
  value INTEGER NOT NULL CHECK (value > 0 AND value < 1000000),
  currency CHAR(3) NOT NULL DEFAULT 'PLN',
  comment TEXT NULL,
  likes_count INTEGER NOT NULL DEFAULT 0 CHECK (likes_count >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (user_id, brickset_id)
);

CREATE TABLE like_like (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES account_user(id) ON DELETE CASCADE,
  valuation_id BIGINT NOT NULL REFERENCES valuation_valuation(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (user_id, valuation_id)
);

CREATE TABLE metrics_systemmetrics (
  id SMALLINT PRIMARY KEY,
  total_sets INTEGER NOT NULL DEFAULT 0,
  serviced_sets INTEGER NOT NULL DEFAULT 0,
  active_users INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

(Implementacje triggerów PL/pgSQL w migracjach; pominięte dla zwięzłości.)

---
Gotowe do wykorzystania przy tworzeniu modeli Django i migracji.
