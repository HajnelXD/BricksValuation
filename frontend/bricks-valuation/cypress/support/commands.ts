/// <reference types="cypress" />

// Custom command types
/* eslint-disable @typescript-eslint/no-namespace */
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
  });
});

// Custom command to login a user using cy.session for cookie persistence
Cypress.Commands.add('login', (username: string, password: string) => {
  cy.session(
    [username, password],
    () => {
      cy.request({
        method: 'POST',
        url: '/api/v1/auth/login',
        body: {
          username,
          password,
        },
      }).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.have.property('user');
      });
    },
    {
      validate() {
        // Validate session by checking if we can access authenticated endpoint
        cy.request({
          method: 'GET',
          url: '/api/v1/users/me/bricksets',
          failOnStatusCode: false,
        }).then((response) => {
          expect(response.status).to.be.oneOf([200, 404]); // 200 OK or 404 if no bricksets
        });
      },
      cacheAcrossSpecs: true,
    }
  );
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
