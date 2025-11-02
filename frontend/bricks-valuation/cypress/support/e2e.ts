// Import commands.js using ES2015 syntax
import './commands';

// Alternatively you can use CommonJS syntax:
// require('./commands')

// This will run before each test
beforeEach(() => {
  // Clear cookies and local storage before each test
  cy.clearCookies();
  cy.clearLocalStorage();
});
