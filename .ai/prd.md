# Dokument wymagań produktu (PRD) - BricksValuation

## 1. Przegląd produktu
1.1 Cel produktu
BricksValuation (MVP) to prosta aplikacja webowa pozwalająca użytkownikom dodawać używane zestawy klocków LEGO do wyceny, wyszukiwać istniejące zestawy oraz uzyskiwać wyceny od innych użytkowników. Ułatwia orientację w wartości zestawu w oparciu o jego cechy (kompletność, instrukcja, pudełko, zapieczętowanie) oraz aktywność społeczności (wyceny, lajki).

1.2 Główne korzyści
- Skrócenie czasu potrzebnego na oszacowanie wartości używanego zestawu.
- Zwiększenie trafności wyceny poprzez efekt crowdsourcingu (wiele niezależnych wycen, lajki sugerujące zaufanie).
- Redukcja duplikatów i chaosu dzięki mechanizmowi wyszukiwania oraz regułom edycji/usuwania.

1.3 Docelowy użytkownik (persona w MVP)
- Kolekcjoner lub sprzedający zestawy LEGO na rynku wtórnym (hobbysta) chcący poznać rynkową wycenę.
- Aplikacja dostępna wyłącznie w języku polskim.

1.4 Zakres MVP (wysoki poziom)
- Rejestracja i logowanie użytkownika (walidacja poprawności formatu email, brak potwierdzenia email).
- Dodawanie, edycja i usuwanie zestawów przed uzyskaniem pierwszej wyceny innego użytkownika lub lajka wyceny właściciela.
- Dodawanie pojedynczej wyceny na zestaw per użytkownik.
- Lajkowanie wycen innych użytkowników (zakaz lajkowania własnej).
- Wyszukiwanie zestawów i przegląd szczegółów wraz z wycenami i lajkami.

1.5 Założenia projektowe (architektura i proces)
- Architektura modularna przygotowana pod przyszłą rozbudowę (np. dodanie zdjęć, powiadomień, ról, backupów).
- Brak integracji z oficjalną bazą LEGO (numer zestawu traktowany jako dowolny identyfikator tekstowy spełniający prostą walidację syntaktyczną – np. niepusty, numeryczny).
- Brak wymagań wydajnościowych i wysokiej dostępności.

1.6 Interesariusze
- Użytkownicy końcowi (kolekcjonerzy / sprzedawcy).
- Zespół produktowy (Product Manager, Analityk, UX/UI, Developer, QA – potencjalnie jedna osoba pełniąca wiele ról w MVP).
- W przyszłości: moderatorzy (poza zakresem MVP).

1.7 Definicje i słowniczek
- Zestaw: rekord reprezentujący unikalny wpis o zestawie LEGO (nie gwarantuje oficjalności danych).
- Wycena: pojedyncza liczbowo-opisowa ocena wartości zestawu dodana przez użytkownika.
- Lajk (polubienie): sygnał zaufania do wyceny, unikalny per (użytkownik, wycena).
- Zestaw wyceniony (na potrzeby metryk): posiada przynajmniej jedną wycenę innego użytkownika niż właściciel lub właścicielowską wycenę, która otrzymała co najmniej jeden lajk od innego użytkownika.

## 2. Problem użytkownika
2.1 Opis problemu
Osoby chcące sprzedać lub ubezpieczyć używany zestaw LEGO mają trudność w oszacowaniu jego aktualnej wartości rynkowej. Wpływ na cenę ma wiele zmiennych (kompletność, stan, dostępność w sprzedaży, akcesoria). Brak szybkiego dostępu do zbiorczej oceny przez społeczność prowadzi do nieoptymalnych decyzji cenowych (zbyt wysoka lub zaniżona cena, dłuższy czas sprzedaży). 

2.2 Konsekwencje braku rozwiązania
- Zwiększony czas potrzebny na research (porównywanie aukcji, forów).
- Brak standaryzacji sposobu opisu stanu zestawu.
- Mniej trafne ceny sprzedaży, potencjalna utrata wartości lub brak sprzedaży.

2.3 Jak BricksValuation rozwiązuje problem
- Ujednolica podstawowe atrybuty zestawu (kompletność, instrukcja, pudełko, zapieczętowanie, status produkcji).
- Konsoliduje opinie (wyceny) wielu użytkowników w jednym miejscu.
- Daje lekki sygnał jakości poprzez lajki wycen.
- Umożliwia szybkie sprawdzenie, czy dany zestaw był już oceniany.

2.4 Ograniczenia aktualnego podejścia (świadome trade-offy MVP)
- Brak zdjęć może ograniczać dokładność stanu faktycznego.
- Brak walidacji numeru zestawu w oficjalnej bazie może skutkować niejednoznacznościami.
- Brak mechanizmów moderacji i zgłaszania nadużyć (ryzyko błędnych lub trollujących wycen) – zaakceptowane w MVP.

## 3. Wymagania funkcjonalne
(Każde wymaganie otrzymuje identyfikator FR dla możliwości śledzenia do historyjek użytkownika.)

FR-01 Rejestracja użytkownika: możliwość utworzenia konta z loginem (unikalna nazwa), hasłem (minimalne kryteria złożoności – min długość), email (format). 
FR-02 Logowanie użytkownika: uwierzytelnianie po loginie (lub emailu) i haśle; utworzenie sesji. 
FR-03 Wylogowanie: zakończenie sesji (inwalidacja tokena/ciasteczka lokalnego mechanizmu). 
FR-04 Dodanie zestawu: użytkownik (po zalogowaniu) może dodać nowy zestaw z atrybutami: numer (liczba), status produkcji (aktywny / wycofany), kompletność (enum: kompletny / niekompletny), instrukcja (bool), pudełko (bool), fabrycznie nowy (bool), własna wstępna wycena (opcjonalna). 
FR-05 Unikanie duplikatów: przed dodaniem sprawdzana jest istnienie zestawu po kombinacji numer + status produkcji + kompletność + instrukcja + pudełko + fabrycznie nowy. 
FR-06 Edycja zestawu: dozwolona tylko jeśli zestaw nie ma żadnej wyceny innego użytkownika ORAZ wycena właściciela nie otrzymała żadnego lajka. 
FR-07 Usunięcie zestawu: dozwolone przy tych samych warunkach co edycja (brak zewnętrznych wycen i brak lajków wyceny właściciela). 
FR-08 Wyszukiwanie zestawów: po numerze (częściowe dopasowanie), filtrach statusu (produkowany/wycofany), kompletności, atrybutach (instrukcja, pudełko, fabrycznie nowy). 
FR-09 Podgląd szczegółów zestawu: wyświetla atrybuty + wycena z największą ilością lajków, jeśli kilka wycen ma tę samą to najwyższa. 
FR-10 Dodanie wyceny: zalogowany użytkownik może dodać wycenę do zestawu. Pole wartości (liczbowe – waluta logiczna, bez integracji płatniczej). 
FR-11 Limit jednej wyceny per zestaw per użytkownik: dodanie drugiej wyceny przez tego samego użytkownika blokowane (zwrócenie błędu). 
FR-12 Lajkowanie wycen: zalogowany użytkownik może polubić wycenę innego użytkownika maksimum raz (unikalne para użytkownik-wycena). 
FR-13 Blokada lajkowania własnej wyceny: system odrzuca próbę. 
FR-14 Wyświetlanie własnych zestawów: lista zestawów utworzonych przez użytkownika z podstawowymi statystykami (liczba wycen, suma lajków wszystkich wycen). 
FR-15 Wyświetlanie własnych wycen: lista wycen dodanych przez użytkownika (z linkiem do zestawu). 
FR-16 Walidacja formatu email: regex / podstawowe zasady (znak @, domena) – brak wysyłki email. 
FR-17 Bezpieczne przechowywanie haseł: hasła nigdy nieprzechowywane w formie jawnej. 
FR-18 Uprawnienia dostępu: wszystkie operacje na zestawach, wycenach, lajkach wymagają zalogowania (poza publicznym wyszukiwaniem – decyzja: w MVP wyszukiwanie i podgląd mogą być publiczne? Przyjmujemy: NIE, wszystko wymaga logowania dla uproszczenia śledzenia aktywności). 
FR-19 Metryki sukcesu: system rejestruje (min. w pamięci lub prostym rejestrze) liczbę zestawów, liczbę zestawów z obcą wyceną lub polajkowaną wyceną właściciela oraz liczbę użytkowników, którzy dodali lub wycenili przynajmniej jeden zestaw (do raportu). 
FR-20 Obsługa błędów walidacji: formularze zwracają jasne komunikaty (np. pole wymagane, duplikat, brak uprawnień). 

3.1 Reguły biznesowe
RB-01 Edycja/Usunięcie zestawu tylko przy braku obcej wyceny i lajków wyceny właściciela.
RB-02 Jedna wycena użytkownika na zestaw.
RB-03 Jeden lajk użytkownika na jedną wycenę; brak lajkowania własnej.
RB-04 Zestaw uznany za obsłużony jeśli ma obcą wycenę lub polajkowaną wycenę właściciela.
RB-05 Numer zestawu nie musi być weryfikowany względem oficjalnej bazy.
RB-06 Wszystkie operacje (poza rejestracją/logowaniem oraz przeglądaniem zestawów i ich wycen) wymagają bycia zalogowanym.

3.2 Walidacje danych (wysoki poziom)
- Numer zestawu: numer do 7 cyfr.
- Wartość wyceny: liczba dodatnia (np. > 0 i < 1 000 000) – waluta przyjmowana logicznie jako PLN (oznaczenie w UI).
- Hasło: min 8 znaków (litera + cyfra rekomendowane – miękka walidacja jeśli chcemy prostotę; przyjmujemy twardą regułę: min 8).
- Email: poprawny format (regex). 

3.3 Raportowanie / obserwowalność (MVP minimalne)
- Liczniki: całkowita liczba zestawów; liczba zestawów wycenionych; liczba użytkowników aktywnych (dodali zestaw lub wycenę). 
- Dostęp: prosty endpoint

3.4 Przyszłe rozszerzenia (poza MVP – informacyjne)
- Dodawanie zdjęć.
- Wysyłanie email potwierdzającego rejestrację oraz reset hasła.
- System reputacji / ranking użytkowników.
- Role (admin, moderator) i zgłaszanie nadużyć.
- Backup i logi audytowe.

## 4. Granice produktu
4.1 W zakresie (In-Scope MVP)
- Rejestracja/logowanie/wylogowanie.
- Zarządzanie zestawami (dodanie, edycja, usunięcie – z ograniczeniami).
- Dodawanie wycen i lajków (bez edycji wycen w MVP – decyzja: prostota; modyfikacja wyceny traktowana jako poza zakresem by uniknąć złożonych reguł).
- Wyszukiwanie i przegląd detaili (po zalogowaniu).
- Minimalna walidacja danych formularzy.
- Minimalne mechanizmy metryczne do oceny kryteriów sukcesu.

4.2 Poza zakresem (Out-of-Scope MVP)
- Dodawanie zdjęć / multimediów.
- Edycja lub usuwanie wyceny po jej dodaniu (ew. przyszłe wydanie).
- Proponowanie ceny automatycznej (algorytmy rekomendacji / ML).
- Wysyłanie maili (potwierdzenie konta, reset hasła, powiadomienia).
- Zaawansowane bezpieczeństwo (2FA, captcha, rate limiting – poza podstawowym hashowaniem haseł).
- Moderacja treści / zgłaszanie nadużyć.
- Backup i disaster recovery.
- Audyt/logi szczegółowe aktywności.
- Międzynarodowość i wielojęzyczność (tylko PL).
- Integracje z zewnętrznymi API (oficjalna baza LEGO, portale aukcyjne).
- FAQ, strona informacyjna, system help.
- Role użytkowników (admin, moderator). 
- Polityka prywatności i pełne zgodności regulacyjne (RODO) – do późniejszego opracowania (nota ryzyka).

4.3 Założenia technologiczne
- Brak wymogów dotyczących wydajności (testy wydajnościowe odroczone).
- Możliwość łatwego rozszerzenia modelu danych (np. migracje).

4.4 Ograniczenia i ryzyka
- Brak backupu => ryzyko utraty danych (akceptowane w MVP). 
- Brak moderacji => ryzyko spamu / zaniżonych lub zawyżonych wycen. 
- Brak potwierdzenia email => możliwe konta jednorazowe.
- Brak szczegółowej polityki RODO => ograniczyć wykorzystanie danych (tylko login + email + hash hasła).

4.5 Strategia ograniczania ryzyk (MVP)
- Wyraźne zaznaczenie w README ograniczeń i przeznaczenia edukacyjnego / testowego.
- Minimalizacja danych osobowych (tylko niezbędne pola).
- Możliwość łatwego wprowadzenia warstwy moderacji w przyszłości (oddzielenie modeli wycen od logiki autoryzacji).

## 5. Historyjki użytkowników
(Każda historyjka posiada unikalny ID oraz powiązanie z wymaganiami FR w akceptacji.)

US-001
Tytuł: Rejestracja nowego użytkownika
Opis: Jako nowy użytkownik chcę utworzyć konto podając login, email i hasło, aby móc korzystać z funkcji aplikacji.
Kryteria akceptacji:
- [ ] Podaję unikalny login, poprawny format email, hasło zgodne z regułą min 8 znaków (FR-01, FR-16, FR-17).
- [ ] Przy duplikacie loginu lub email otrzymuję czytelny komunikat błędu (FR-01, FR-20).
- [ ] Hasło jest przechowywane jako hash (test: w bazie brak jawnego hasła) (FR-17).
- [ ] Po rejestracji mogę się zalogować tymi samymi danymi (FR-02).

US-002
Tytuł: Logowanie użytkownika
Opis: Jako zarejestrowany użytkownik chcę się zalogować, żeby mieć dostęp do funkcji zarządzania zestawami i wycenami.
Kryteria akceptacji:
- [ ] Logowanie wymaga poprawnej pary (login/email + hasło) (FR-02).
- [ ] Błędne dane zwracają komunikat w stylu: Nieprawidłowe dane logowania (FR-20).
- [ ] Po zalogowaniu otrzymuję aktywną sesję (FR-02, FR-18).

US-003
Tytuł: Wylogowanie
Opis: Jako zalogowany użytkownik chcę się wylogować, aby zakończyć moją sesję.
Kryteria akceptacji:
- [ ] Po wylogowaniu chronione operacje zwracają błąd nieautoryzowany (FR-03, FR-18).
- [ ] Sesja/token zostaje unieważniony (FR-03).

US-004
Tytuł: Dodanie nowego zestawu
Opis: Jako zalogowany użytkownik chcę dodać nowy zestaw wraz z jego atrybutami, aby społeczność mogła go wycenić.
Kryteria akceptacji:
- [ ] Formularz wymaga pól: numer (niepusty), kompletność, status produkcji, flagi instrukcja/pudełko/fabrycznie nowy (FR-04).
- [ ] Walidacje pól działają (FR-04, FR-20).
- [ ] Po zapisie zestaw pojawia się na liście moich zestawów (FR-14).

US-005
Tytuł: Wykrycie duplikatu zestawu
Opis: Jako użytkownik dodający zestaw chcę otrzymać informację o istniejącym zestawie o tym samym numerze (lub numerze i nazwie), aby uniknąć duplikatu.
Kryteria akceptacji:
- [ ] Próba dodania zestawu z istniejącą kombinacją krytycznych pól skutkuje komunikatem o duplikacie (FR-05, FR-20).
- [ ] Nie powstaje drugi identyczny rekord (FR-05).

US-006
Tytuł: Edycja zestawu przed wyceną
Opis: Jako właściciel zestawu chcę móc edytować jego dane zanim ktoś inny doda wycenę lub zanim moja wycena zostanie polubiona.
Kryteria akceptacji:
- [ ] Mogę edytować zestaw, gdy brak obcej wyceny i brak lajków mojej wyceny (FR-06, RB-01).
- [ ] Próba edycji po spełnieniu warunków blokujących daje komunikat odmowy (FR-06, FR-20, RB-01).

US-007
Tytuł: Usunięcie zestawu przed wyceną
Opis: Jako właściciel chcę usunąć zestaw, jeśli jeszcze nie został zweryfikowany przez społeczność (brak obcych wycen i lajków).
Kryteria akceptacji:
- [ ] Usunięcie działa przy spełnieniu warunków (FR-07, RB-01).
- [ ] Po usunięciu rekord nie jest dostępny w wyszukiwaniu (FR-07).
- [ ] Przy naruszeniu warunków otrzymuję komunikat odmowy (FR-07, FR-20).

US-008
Tytuł: Dodanie wyceny zestawu
Opis: Jako zalogowany użytkownik chcę dodać wycenę wartości zestawu, aby podzielić się opinią.
Kryteria akceptacji:
- [ ] Formularz wyceny wymaga wartości > 0 oraz opcjonalnego komentarza (FR-10, FR-20).
- [ ] Po dodaniu wycena widoczna na stronie szczegółów zestawu (FR-09, FR-10).

US-009
Tytuł: Ograniczenie jednej wyceny na użytkownika na zestaw
Opis: Jako użytkownik nie mogę dodać więcej niż jednej wyceny dla tego samego zestawu, by uniknąć sztucznego zawyżania.
Kryteria akceptacji:
- [ ] Druga próba dodania wyceny dla tego samego zestawu zwraca błąd (FR-11, RB-02, FR-20).
- [ ] W bazie pozostaje tylko jedna wycena użytkownika dla zestawu (FR-11).

US-010
Tytuł: Lajkowanie wyceny innego użytkownika
Opis: Jako zalogowany użytkownik chcę polubić wycenę innej osoby, by wyrazić zaufanie.
Kryteria akceptacji:
- [ ] Mogę polubić wycenę, której autorem nie jestem (FR-12, FR-13, RB-03).
- [ ] Kolejna próba lajkowania tej samej wyceny przez mnie jest blokowana (FR-12, RB-03, FR-20).
- [ ] Licznik lajków zwiększa się o 1 po pierwszym lajku (FR-12).

US-011
Tytuł: Blokada lajkowania własnej wyceny
Opis: Jako autor wyceny nie mogę lajknąć własnej wyceny.
Kryteria akceptacji:
- [ ] Próba lajkowania własnej wyceny zwraca komunikat (FR-13, RB-03, FR-20).
- [ ] Licznik lajków nie zmienia się (FR-13).

US-012
Tytuł: Wyszukiwanie zestawów
Opis: Jako zalogowany użytkownik chcę wyszukać zestawy po numerze/nazwie i filtrach stanu, aby szybko odnaleźć interesujący zestaw.
Kryteria akceptacji:
- [ ] Mogę wyszukiwać po fragmencie numeru lub nazwy (FR-08).
- [ ] Mogę stosować filtry: status produkcji, kompletność, instrukcja, pudełko, zapieczętowany (FR-08).
- [ ] Wyniki zawierają podstawowe atrybuty i liczby wycen (FR-08, FR-14 opcjonalnie rozszerzone).

US-013
Tytuł: Podgląd szczegółów zestawu
Opis: Jako użytkownik chcę zobaczyć wszystkie atrybuty zestawu i listę wycen z lajkami.
Kryteria akceptacji:
- [ ] Strona szczegółów zawiera atrybuty zestawu (FR-09).
- [ ] Lista wycen pokazuje wartość, autora, datę i liczbę lajków (FR-09, FR-12).
- [ ] Wyceny posortowane domyślnie malejąco po liczbie lajków, następnie rosnąco po dacie (preferencja – jeśli wdrożenie uprości, można w pierwszej wersji sortować po dacie; uznać to za rekomendację a nie twardy wymóg).

US-014
Tytuł: Lista moich zestawów
Opis: Jako użytkownik chcę widzieć listę dodanych przeze mnie zestawów i podstawowe statystyki.
Kryteria akceptacji:
- [ ] Lista pokazuje każdy mój zestaw z liczbą wycen i sumą lajków (FR-14).
- [ ] Z kliknięcia przechodzę do szczegółów (FR-09).

US-015
Tytuł: Lista moich wycen
Opis: Jako użytkownik chcę zobaczyć wszystkie moje wyceny, by ocenić mój wkład.
Kryteria akceptacji:
- [ ] Lista zawiera zestaw (referencja), wartość wyceny, liczbę lajków (FR-15, FR-12).
- [ ] Z kliknięcia przechodzę do szczegółów zestawu (FR-09).

US-016
Tytuł: Informacja o błędach walidacji
Opis: Jako użytkownik chcę otrzymać czytelne komunikaty podczas błędów w formularzach.
Kryteria akceptacji:
- [ ] Przy błędnym formacie email komunikat wskazuje problem (FR-16, FR-20).
- [ ] Przy numerze zestawu pustym otrzymuję komunikat (FR-04, FR-20).
- [ ] Przy próbie duplikatu wyceny komunikat wskazuje limit (FR-11, FR-20).
- [ ] Przy braku uprawnień (np. edycja po blokadzie) komunikat informuje o regule (FR-06, FR-07, FR-20).

US-017
Tytuł: Uwierzytelnienie i ochrona zasobów
Opis: Jako system chcę uniemożliwić dostęp do operacji zarządzania zestawami, wycenami i lajkami użytkownikom niezalogowanym.
Kryteria akceptacji:
- [ ] Próba dodania/edycji/usunięcia zestawu bez sesji zwraca 401/odmowę (FR-18).
- [ ] Próba dodania wyceny lub lajka bez sesji zwraca 401 (FR-18).
- [ ] Dane sesji nie ujawniają hasła (FR-17).

US-018
Tytuł: Podstawowe metryki pokrycia
Opis: Jako Product Owner chcę monitorować procent zestawów obsłużonych oraz aktywność użytkowników.
Kryteria akceptacji:
- [ ] System potrafi policzyć liczbę zestawów całkowitą i liczbę obsłużonych wg definicji (FR-19, RB-04).
- [ ] System potrafi policzyć liczbę użytkowników, którzy dodali zestaw lub wycenę (FR-19).
- [ ] Wygenerowanie raportu (np. endpoint/panel/wyświetlenie) prezentuje wskaźniki w czytelnej formie (FR-19).

5.1 Kompletność zestawu historyjek
- Pokrycie tworzenia kont, uwierzytelniania, zarządzania zestawami, wycenami, lajkami, wyszukiwaniem, prezentacją danych oraz metrykami i walidacjami.
- Historia bezpieczeństwa (US-017) zapewnia wymagania uwierzytelniania.

## 6. Metryki sukcesu
6.1 Metryki główne (zgodnie z kryteriami sukcesu)
M1 Odsetek zestawów obsłużonych = (Liczba zestawów z obcą wyceną lub polajkowaną wyceną właściciela) / (Liczba wszystkich zestawów) * 100%. Cel: ≥ 75%.
M2 Odsetek aktywnych użytkowników = (Użytkownicy, którzy dodali zestaw lub wycenę) / (Wszyscy zarejestrowani użytkownicy) * 100%. Cel: ≥ 90%.

6.2 Definicje operacyjne
- Zestaw obsłużony: co najmniej jedna wycena innego użytkownika LUB wycena właściciela z ≥ 1 lajkiem od innego użytkownika.
- Użytkownik aktywny: dodał ≥ 1 zestaw lub ≥ 1 wycenę.

6.3 Sposób zbierania metryk
- Liczniki aktualizowane przy dodaniu/wycenie/lajku (FR-19).
- Dane mogą być przechowywane w pamięci (MVP) – brak trwałej analityki (ograniczenie).

6.4 Harmonogram oceny
- Po uzyskaniu co najmniej 30 zestawów w systemie: pierwsza ocena M1 i M2.
- Następnie okresowe manualne odczyty (np. co sprint / iteracja).

6.5 Ryzyka metryczne
- Brak backupu => utrata danych wpływa na trend.
- Niska liczba użytkowników testowych może zafałszować procenty.

6.6 Wskaźniki wtórne (opcjonalne)
- Średnia liczba wycen na zestaw.
- Średnia liczba lajków na wycenę.
- Rozkład wartości wycen (min/median/max). (Może być generowane ad-hoc – poza twardymi wymaganiami.)

6.7 Kryteria zakończenia MVP
- Osiągnięcie M1 ≥ 75% i M2 ≥ 90% w co najmniej dwóch kolejnych pomiarach w odstępie czasu (np. tygodniowym) lub przy stabilizacji liczby nowych zestawów.

6.8 Plan działań po nieosiągnięciu metryk
- Analiza przyczyn (brak zachęt do wyceny? interfejs utrudnia dodawanie?).
- Ewentualne dodanie funkcji motywacyjnych (gamifikacja, reputacja) – po MVP.

6.9 Monitoring jakości danych
- Okresowa kontrola ręczna duplikatów (przy braku systemowej walidacji zewnętrznej bazy).

---
Checklist przeglądu (wewnętrzna):
- Każda historyjka ma jasne, testowalne kryteria.
- Uwzględniono uwierzytelnianie i bezpieczeństwo minimalne (US-017, FR-17, FR-18).
- Funkcjonalności MVP pokryte FR i US (dodawanie/edycja/usuwanie zestawów, wyceny, lajki, wyszukiwanie, rejestracja/logowanie, metryki).
- Elementy poza zakresem jasno wymienione.
- Metryki sukcesu zdefiniowane i mierzalne.

Koniec dokumentu.

