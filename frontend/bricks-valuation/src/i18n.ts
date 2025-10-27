import { createI18n } from 'vue-i18n';

const messages = {
  pl: {
    app: {
      title: 'BricksValuation',
    },
    nav: {
      home: 'Start',
      login: 'Logowanie',
      register: 'Rejestracja',
      sets: 'Zestawy',
      mySets: 'Moje zestawy',
      myValuations: 'Moje wyceny',
    },
    auth: {
      noAccountPrompt: 'Jeśli nie masz konta, kliknij',
    },
    login: {
      title: 'Logowanie',
      username: 'Nazwa użytkownika lub email',
      password: 'Hasło',
      submit: 'Zaloguj się',
      hasAccount: 'Nie masz konta?',
      register: 'Zarejestruj się',
      errors: {
        usernameRequired: 'Nazwa użytkownika jest wymagana',
        passwordRequired: 'Hasło jest wymagane',
        fillAllFields: 'Wypełnij wszystkie pola',
      },
    },
    common: {
      reset: 'Wyczyść filtry',
      showFilters: 'Pokaż filtry',
      retry: 'Spróbuj ponownie',
      previous: 'Poprzednia',
      next: 'Następna',
    },
    errors: {
      serverError: 'Wystąpił błąd serwera. Spróbuj ponownie później',
      networkError: 'Brak połączenia z serwerem. Sprawdź połączenie internetowe',
      timeout: 'Żądanie przekroczyło limit czasu. Spróbuj ponownie',
    },
    register: {
      title: 'Rejestracja',
      username: 'Nazwa użytkownika',
      email: 'Adres email',
      password: 'Hasło',
      confirmPassword: 'Powtórz hasło',
      submit: 'Zarejestruj się',
      hasAccount: 'Masz już konto?',
      login: 'Zaloguj się',
      success: 'Konto utworzone pomyślnie',
      errors: {
        usernameRequired: 'Nazwa użytkownika jest wymagana',
        usernameLength: 'Nazwa użytkownika musi mieć od 3 do 50 znaków',
        usernameFormat:
          'Nazwa użytkownika może zawierać tylko litery, cyfry, kropki, podkreślenia i myślniki',
        emailRequired: 'Adres email jest wymagany',
        emailFormat: 'Wprowadź poprawny adres email',
        passwordRequired: 'Hasło jest wymagane',
        passwordLength: 'Hasło musi mieć co najmniej 8 znaków',
        confirmPasswordRequired: 'Potwierdzenie hasła jest wymagane',
        passwordsNotMatch: 'Hasła nie są identyczne',
        usernameTaken: 'Ta nazwa użytkownika jest już zajęta',
        emailTaken: 'Ten adres email jest już zarejestrowany',
      },
    },
    bricksets: {
      title: 'Zestawy LEGO',
      subtitle: 'zestawów dostępnych',
      authPrompt: 'Zaloguj się aby dodać własny zestaw lub wycenę',
      search: 'Szukaj',
      productionStatus: 'Status produkcji',
      allStatuses: 'Wszystkie',
      active: 'Aktywny',
      retired: 'Wycofany',
      completeness: 'Kompletność',
      allCompletion: 'Wszystkie',
      complete: 'Kompletny',
      incomplete: 'Niekompletny',
      attributes: 'Atrybuty',
      hasInstructions: 'Ma instrukcje',
      hasBox: 'Ma pudełko',
      sealed: 'Zapieczętowany',
      orderBy: 'Sortuj',
      newest: 'Najnowsze',
      oldest: 'Najstarsze',
      popular: 'Najpopularniejsze',
      mostValuations: 'Najwięcej wycen',
      valuations: 'wycen',
      likes: 'lajków',
      noResults: 'Brak zestawów spełniających kryteria.',
      tryAdjustingFilters:
        'Spróbuj dostosować filtry lub wyczyścić je za pomocą przycisku po lewej.',
      clearFilters: 'Wyczyść filtry',
    },
    pages: {
      authenticatedBricksets: {
        title: 'Moje zestawy',
        subtitle: 'Zarządzaj swoją kolekcją',
      },
    },
  },
};

export const i18n = createI18n({
  locale: 'pl',
  fallbackLocale: 'pl',
  legacy: false,
  messages,
});
