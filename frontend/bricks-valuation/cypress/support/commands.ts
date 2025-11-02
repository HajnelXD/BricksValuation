/// <reference types="cypress" />

// Custom command types
declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to register a new user
       * @param username - Username (3-50 chars)
       * @param email - Valid email address
       * @param password - Password (>=8 chars)
       * @example cy.register('testuser', 'test@example.com', 'password123')
       */
      register(username: string, email: string, password: string): Chainable<void>;

      /**
       * Custom command to login a user
       * @param username - Username
       * @param password - Password
       * @example cy.login('testuser', 'password123')
       */
      login(username: string, password: string): Chainable<void>;

      /**
       * Custom command to logout current user
       * @example cy.logout()
       */
      logout(): Chainable<void>;
    }
  }
}

// Custom command to register a new user
Cypress.Commands.add('register', (username: string, email: string, password: string) => {
  cy.request({
    method: 'POST',
    url: '/api/v1/auth/register',
    body: {
      username,
      email,
      password,
    },
    failOnStatusCode: false,
  }).then((response) => {
    expect(response.status).to.eq(201);
    expect(response.body).to.have.property('id');
    expect(response.body).to.have.property('username', username);
    expect(response.body).to.have.property('email', email);
    expect(response.body).to.have.property('created_at');
  });
});

// Custom command to login a user
Cypress.Commands.add('login', (username: string, password: string) => {
  cy.request({
    method: 'POST',
    url: '/api/v1/auth/login',
    body: {
      username,
      password,
    },
    failOnStatusCode: false,
  }).then((response) => {
    expect(response.status).to.eq(200);
    expect(response.body).to.have.property('user');
    expect(response.body.user).to.have.property('username', username);
    // Token is set in HttpOnly cookie, not in response body
    expect(response.body).to.not.have.property('token');
  });
});

// Custom command to logout current user
Cypress.Commands.add('logout', () => {
  cy.request({
    method: 'POST',
    url: '/api/v1/auth/logout',
    failOnStatusCode: false,
  }).then((response) => {
    expect(response.status).to.eq(204);
  });
});

export {};
