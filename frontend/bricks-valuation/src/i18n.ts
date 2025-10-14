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
  },
};

export const i18n = createI18n({
  locale: 'pl',
  fallbackLocale: 'pl',
  legacy: false,
  messages,
});
