describe('Authentication Flow', () => {
  // Generate unique user data for each test run to avoid conflicts
  const timestamp = Date.now();
  const testUser = {
    username: `testuser${timestamp}`,
    email: `testuser${timestamp}@example.com`,
    password: 'SecurePassword123!',
  };

  before(() => {
    // Ensure clean state before tests
    cy.clearCookies();
    cy.clearLocalStorage();
  });

  describe('User Registration', () => {
    it('should successfully register a new user', () => {
      cy.request({
        method: 'POST',
        url: '/api/v1/auth/register',
        body: {
          username: testUser.username,
          email: testUser.email,
          password: testUser.password,
        },
      }).then((response) => {
        // Verify response status
        expect(response.status).to.eq(201);

        // Verify response body structure
        expect(response.body).to.have.property('id');
        expect(response.body.id).to.be.a('number');
        expect(response.body).to.have.property('username', testUser.username);
        expect(response.body).to.have.property('email', testUser.email);
        expect(response.body).to.have.property('created_at');

        // Verify created_at is a valid ISO timestamp
        const createdAt = new Date(response.body.created_at);
        expect(createdAt.toString()).to.not.eq('Invalid Date');
      });
    });

    it('should fail to register with duplicate username', () => {
      cy.request({
        method: 'POST',
        url: '/api/v1/auth/register',
        body: {
          username: testUser.username,
          email: `different${timestamp}@example.com`,
          password: testUser.password,
        },
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(409);
      });
    });

    it('should fail to register with duplicate email', () => {
      cy.request({
        method: 'POST',
        url: '/api/v1/auth/register',
        body: {
          username: `different${timestamp}`,
          email: testUser.email,
          password: testUser.password,
        },
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(409);
      });
    });

    it('should fail to register with invalid email', () => {
      cy.request({
        method: 'POST',
        url: '/api/v1/auth/register',
        body: {
          username: `newuser${timestamp}`,
          email: 'invalid-email',
          password: testUser.password,
        },
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(400);
      });
    });

    it('should fail to register with short password', () => {
      cy.request({
        method: 'POST',
        url: '/api/v1/auth/register',
        body: {
          username: `newuser${timestamp}`,
          email: `newuser${timestamp}@example.com`,
          password: 'short',
        },
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(400);
      });
    });

    it('should fail to register with short username', () => {
      cy.request({
        method: 'POST',
        url: '/api/v1/auth/register',
        body: {
          username: 'ab',
          email: `newuser${timestamp}@example.com`,
          password: testUser.password,
        },
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(400);
      });
    });
  });

  describe('User Login', () => {
    it('should successfully login with valid credentials', () => {
      cy.request({
        method: 'POST',
        url: '/api/v1/auth/login',
        body: {
          username: testUser.username,
          password: testUser.password,
        },
      }).then((response) => {
        // Verify response status
        expect(response.status).to.eq(200);

        // Verify response body structure
        expect(response.body).to.have.property('user');
        expect(response.body.user).to.have.property('id');
        expect(response.body.user).to.have.property('username', testUser.username);
        expect(response.body.user).to.have.property('email', testUser.email);

        // Verify JWT token is NOT in response body (it's HttpOnly cookie only)
        expect(response.body).to.not.have.property('token');

        // Verify auth cookie is set
        const cookies = response.headers['set-cookie'];
        if (cookies) {
          const authCookie = Array.isArray(cookies)
            ? cookies.find((cookie) => cookie.includes('jwt_token'))
            : cookies.includes('jwt_token');
          expect(authCookie).to.exist;
        }
      });
    });

    it('should fail to login with invalid password', () => {
      cy.request({
        method: 'POST',
        url: '/api/v1/auth/login',
        body: {
          username: testUser.username,
          password: 'WrongPassword123!',
        },
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(401);
      });
    });

    it('should fail to login with non-existent username', () => {
      cy.request({
        method: 'POST',
        url: '/api/v1/auth/login',
        body: {
          username: 'nonexistentuser',
          password: testUser.password,
        },
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(401);
      });
    });

    it('should fail to login with missing fields', () => {
      cy.request({
        method: 'POST',
        url: '/api/v1/auth/login',
        body: {
          username: testUser.username,
        },
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(400);
      });
    });
  });

  describe('User Logout', () => {
    beforeEach(() => {
      // Login before each logout test
      cy.login(testUser.username, testUser.password);
    });

    it('should successfully logout authenticated user', () => {
      cy.request({
        method: 'POST',
        url: '/api/v1/auth/logout',
      }).then((response) => {
        // Verify response status
        expect(response.status).to.eq(204);

        // Verify no response body
        expect(response.body).to.be.empty;
      });
    });

    it('should clear authentication cookie on logout', () => {
      cy.request({
        method: 'POST',
        url: '/api/v1/auth/logout',
      }).then((response) => {
        expect(response.status).to.eq(204);

        // After logout, trying to access protected resources should fail
        // This verifies the cookie was invalidated
        cy.getCookie('jwt_token').should('be.null');
      });
    });
  });

  describe('Complete Authentication Flow', () => {
    it('should successfully register, login, and logout a user', () => {
      const flowTimestamp = Date.now();
      const flowUser = {
        username: `flowuser${flowTimestamp}`,
        email: `flowuser${flowTimestamp}@example.com`,
        password: 'FlowPassword123!',
      };

      // Step 1: Register
      cy.register(flowUser.username, flowUser.email, flowUser.password);

      // Step 2: Login
      cy.login(flowUser.username, flowUser.password);

      // Step 3: Logout
      cy.logout();

      // Verify we can login again after logout
      cy.login(flowUser.username, flowUser.password);
    });
  });
});
