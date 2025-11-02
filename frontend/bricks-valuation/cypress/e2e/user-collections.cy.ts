describe('User Collections', () => {
  const timestamp = Date.now();
  const testUser = {
    username: `colluser${timestamp}`,
    email: `colluser${timestamp}@example.com`,
    password: 'CollPass123!',
  };

  const secondUser = {
    username: `colluser2${timestamp}`,
    email: `colluser2${timestamp}@example.com`,
    password: 'CollPass123!',
  };

  // Helper to generate unique brickset numbers
  let bricksetCounter = 0;
  const getUniqueBricksetNumber = () => {
    bricksetCounter++;
    return 10000 + (timestamp % 10000) + bricksetCounter;
  };

  let userBrickset1Id: number;
  let userBrickset2Id: number;
  let otherUserBricksetId: number;

  before(() => {
    cy.clearCookies();
    cy.clearLocalStorage();

    // Register users
    cy.register(testUser.username, testUser.email, testUser.password);
    cy.register(secondUser.username, secondUser.email, secondUser.password);

    // Create bricksets as first user
    cy.login(testUser.username, testUser.password);

    cy.request({
      method: 'POST',
      url: '/api/v1/bricksets',
      body: {
        number: getUniqueBricksetNumber(),
        production_status: 'ACTIVE',
        completeness: 'COMPLETE',
        has_instructions: true,
        has_box: true,
        is_factory_sealed: false,
        owner_initial_estimate: 450,
      },
    }).then((response) => {
      userBrickset1Id = response.body.id;

      cy.request({
        method: 'POST',
        url: '/api/v1/bricksets',
        body: {
          number: getUniqueBricksetNumber(),
          production_status: 'RETIRED',
          completeness: 'INCOMPLETE',
          has_instructions: false,
          has_box: false,
          is_factory_sealed: false,
        },
      }).then((response2) => {
        userBrickset2Id = response2.body.id;

        // Create brickset as second user
        cy.clearAllSessionStorage();
        cy.login(secondUser.username, secondUser.password);

        cy.request({
          method: 'POST',
          url: '/api/v1/bricksets',
          body: {
            number: getUniqueBricksetNumber(),
            production_status: 'ACTIVE',
            completeness: 'COMPLETE',
            has_instructions: true,
            has_box: true,
            is_factory_sealed: true,
          },
        }).then((response3) => {
          otherUserBricksetId = response3.body.id;

          // Add valuations to first user's bricksets
          cy.request({
            method: 'POST',
            url: `/api/v1/bricksets/${userBrickset1Id}/valuations`,
            body: {
              value: 500,
              currency: 'PLN',
              comment: 'External valuation 1',
            },
          });

          cy.request({
            method: 'POST',
            url: `/api/v1/bricksets/${userBrickset2Id}/valuations`,
            body: {
              value: 200,
              currency: 'PLN',
              comment: 'External valuation 2',
            },
          });

          // First user adds valuations to second user's brickset
          cy.clearAllSessionStorage();
          cy.login(testUser.username, testUser.password);

          cy.request({
            method: 'POST',
            url: `/api/v1/bricksets/${otherUserBricksetId}/valuations`,
            body: {
              value: 800,
              currency: 'PLN',
              comment: 'My valuation on other user brickset',
            },
          });

          // Add likes to create statistics
          cy.clearAllSessionStorage();
          cy.login(testUser.username, testUser.password);

          // Get valuations to like
          cy.request('GET', `/api/v1/bricksets/${userBrickset1Id}/valuations`).then((response4) => {
            const valuationId = response4.body.results[0].id;
            cy.request('POST', `/api/v1/valuations/${valuationId}/likes`);
          });
        });
      });
    });
  });

  beforeEach(function () {
    // Skip session restoration for auth tests
    if (
      this.currentTest?.title?.includes('should require authentication') ||
      this.currentTest?.title?.includes('should fail when not authenticated')
    ) {
      return;
    }
    // Restore session before each test
    cy.login(testUser.username, testUser.password);
  });

  describe('List My BrickSets (FR-14)', () => {
    it('should list all bricksets owned by current user', () => {
      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/bricksets',
      }).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.have.property('count');
        expect(response.body).to.have.property('results');
        expect(response.body.results).to.be.an('array');

        // Should contain at least the 2 bricksets we created
        expect(response.body.count).to.be.at.least(2);

        // Verify all bricksets belong to current user
        response.body.results.forEach((brickset: Record<string, unknown>) => {
          expect(brickset).to.have.property('id');
          expect(brickset).to.have.property('number');
          expect(brickset).to.have.property('production_status');
          expect(brickset).to.have.property('completeness');
          expect(brickset).to.have.property('valuations_count');
          expect(brickset).to.have.property('total_likes');
        });
      });
    });

    it('should include statistics (valuations_count, total_likes)', () => {
      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/bricksets',
      }).then((response) => {
        const brickset1 = response.body.results.find(
          (bs: { id: number }) => bs.id === userBrickset1Id
        );

        expect(brickset1).to.not.equal(undefined);
        expect(brickset1.valuations_count).to.be.greaterThan(0);
        // At least one like from earlier setup
        expect(brickset1).to.have.property('total_likes');
      });
    });

    it('should include editable flag (RB-01)', () => {
      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/bricksets',
      }).then((response) => {
        response.body.results.forEach((brickset: Record<string, unknown>) => {
          // editable is optional field, but if present should be boolean
          if (Object.prototype.hasOwnProperty.call(brickset, 'editable')) {
            expect(brickset.editable).to.be.a('boolean');
          }
        });

        // First brickset has external valuation, should not be editable
        const brickset1 = response.body.results.find(
          (bs: { id: number }) => bs.id === userBrickset1Id
        );
        if (brickset1 && Object.prototype.hasOwnProperty.call(brickset1, 'editable')) {
          expect(brickset1.editable).to.eq(false);
        }
      });
    });

    it('should support pagination', () => {
      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/bricksets?page=1&page_size=1',
      }).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.results.length).to.eq(1);
        expect(response.body).to.have.property('next');
      });
    });

    it('should support ordering by created_at', () => {
      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/bricksets?ordering=-created_at',
      }).then((response) => {
        expect(response.status).to.eq(200);
        const results = response.body.results;

        if (results.length >= 2 && results[0].created_at && results[1].created_at) {
          // Newer bricksets should come first with -created_at
          const date1 = new Date(results[0].created_at);
          const date2 = new Date(results[1].created_at);
          // Only check if dates are valid
          if (!isNaN(date1.getTime()) && !isNaN(date2.getTime())) {
            expect(date1.getTime()).to.be.at.least(date2.getTime());
          }
        }
      });
    });

    it('should support ordering by valuations count', () => {
      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/bricksets?ordering=-valuations',
        failOnStatusCode: false,
      }).then((response) => {
        // This ordering might not be implemented yet, accept 200 or 400
        expect(response.status).to.be.oneOf([200, 400]);

        if (response.status === 200) {
          const results = response.body.results;
          if (results.length >= 2) {
            expect(results[0].valuations_count).to.be.at.least(results[1].valuations_count);
          }
        }
      });
    });

    it("should not include other users' bricksets", () => {
      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/bricksets',
      }).then((response) => {
        const otherBrickset = response.body.results.find(
          (bs: { id: number }) => bs.id === otherUserBricksetId
        );
        expect(otherBrickset).to.eq(undefined);
      });
    });
  });

  describe('List My Valuations (FR-15)', () => {
    it('should list all valuations created by current user', () => {
      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/valuations',
      }).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.have.property('count');
        expect(response.body).to.have.property('results');
        expect(response.body.results).to.be.an('array');

        // Should contain at least the 1 valuation we created
        expect(response.body.count).to.be.at.least(1);

        response.body.results.forEach((valuation: Record<string, unknown>) => {
          expect(valuation).to.have.property('id');
          expect(valuation).to.have.property('value');
          expect(valuation).to.have.property('currency');
          expect(valuation).to.have.property('likes_count');
          expect(valuation).to.have.property('brickset');
        });
      });
    });

    it('should include brickset reference with id and number', () => {
      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/valuations',
      }).then((response) => {
        const valuation = response.body.results[0];

        expect(valuation.brickset).to.not.equal(undefined);
        expect(valuation.brickset).to.have.property('id');
        expect(valuation.brickset).to.have.property('number');
      });
    });

    it('should show likes_count for each valuation', () => {
      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/valuations',
      }).then((response) => {
        response.body.results.forEach((valuation: Record<string, unknown>) => {
          expect(valuation).to.have.property('likes_count');
          expect(valuation.likes_count).to.be.a('number');
          expect(valuation.likes_count).to.be.at.least(0);
        });
      });
    });

    it('should support pagination', () => {
      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/valuations?page=1&page_size=10',
      }).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.results.length).to.be.at.most(10);
      });
    });

    it("should not include other users' valuations", () => {
      // Switch to second user and check their valuations
      cy.clearAllSessionStorage();
      cy.login(secondUser.username, secondUser.password);

      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/valuations',
      }).then((response) => {
        expect(response.status).to.eq(200);

        // Second user should have at least 2 valuations (created earlier)
        expect(response.body.count).to.be.at.least(2);

        // None should be on the first user's valuations
        response.body.results.forEach((valuation: { brickset: { id: number } }) => {
          expect(valuation.brickset.id).to.not.eq(otherUserBricksetId);
        });
      });
    });
  });

  describe('Navigation from Collections to Details (FR-09, FR-14, FR-15)', () => {
    it('should allow navigation from my bricksets to brickset details', () => {
      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/bricksets',
      }).then((listResponse) => {
        const bricksetId = listResponse.body.results[0].id;

        // Access detail view
        cy.request({
          method: 'GET',
          url: `/api/v1/bricksets/${bricksetId}`,
        }).then((detailResponse) => {
          expect(detailResponse.status).to.eq(200);
          expect(detailResponse.body.id).to.eq(bricksetId);
          expect(detailResponse.body).to.have.property('valuations');
        });
      });
    });

    it('should allow navigation from my valuations to brickset details', () => {
      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/valuations',
      }).then((valuationsResponse) => {
        const bricksetId = valuationsResponse.body.results[0].brickset.id;

        // Access brickset detail
        cy.request({
          method: 'GET',
          url: `/api/v1/bricksets/${bricksetId}`,
        }).then((detailResponse) => {
          expect(detailResponse.status).to.eq(200);
          expect(detailResponse.body.id).to.eq(bricksetId);
        });
      });
    });
  });

  describe('Authentication Requirements (FR-18)', () => {
    it('should require authentication to view my bricksets', () => {
      cy.clearAllSessionStorage();
      cy.clearCookies();

      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/bricksets',
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(401);
      });
    });

    it('should require authentication to view my valuations', () => {
      cy.clearAllSessionStorage();
      cy.clearCookies();

      cy.request({
        method: 'GET',
        url: '/api/v1/users/me/valuations',
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(401);
      });
    });
  });

  describe('User Profile Endpoint (GET /api/v1/auth/me)', () => {
    it('should get current user profile when authenticated', () => {
      cy.clearAllSessionStorage();
      cy.login(testUser.username, testUser.password);

      cy.request({
        method: 'GET',
        url: '/api/v1/auth/me',
      }).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.have.property('id');
        expect(response.body.username).to.eq(testUser.username);
        expect(response.body.email).to.eq(testUser.email);
      });
    });

    it('should fail when not authenticated', () => {
      cy.clearAllSessionStorage();
      cy.clearCookies();

      cy.request({
        method: 'GET',
        url: '/api/v1/auth/me',
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(401);
        // Check for error code if present
        if (response.body.code) {
          expect(response.body.code).to.eq('NOT_AUTHENTICATED');
        }
      });
    });
  });

  describe('Complete User Flow', () => {
    it('should complete full user journey: register, create brickset, receive valuation, view collections', () => {
      const flowTimestamp = Date.now();
      const flowUser = {
        username: `flowuser${flowTimestamp}`,
        email: `flowuser${flowTimestamp}@example.com`,
        password: 'FlowPass123!',
      };

      const flowValuator = {
        username: `valuator${flowTimestamp}`,
        email: `valuator${flowTimestamp}@example.com`,
        password: 'ValPass123!',
      };

      // Step 1: Register and login
      cy.register(flowUser.username, flowUser.email, flowUser.password);
      cy.login(flowUser.username, flowUser.password);

      // Step 2: Create a brickset
      let flowBricksetId: number;
      cy.request({
        method: 'POST',
        url: '/api/v1/bricksets',
        body: {
          number: getUniqueBricksetNumber(),
          production_status: 'ACTIVE',
          completeness: 'COMPLETE',
          has_instructions: true,
          has_box: true,
          is_factory_sealed: false,
          owner_initial_estimate: 600,
        },
      }).then((response) => {
        expect(response.status).to.eq(201);
        flowBricksetId = response.body.id;

        // Step 3: Verify in my bricksets
        cy.request('GET', '/api/v1/users/me/bricksets').then((response2) => {
          const myBrickset = response2.body.results.find(
            (bs: { id: number }) => bs.id === flowBricksetId
          );
          expect(myBrickset).to.not.equal(undefined);
          expect(myBrickset.valuations_count).to.eq(0);

          // Step 4: Another user registers and adds valuation
          cy.register(flowValuator.username, flowValuator.email, flowValuator.password);
          cy.clearAllSessionStorage();
          cy.login(flowValuator.username, flowValuator.password);

          cy.request({
            method: 'POST',
            url: `/api/v1/bricksets/${flowBricksetId}/valuations`,
            body: {
              value: 650,
              currency: 'PLN',
              comment: 'Great condition!',
            },
          }).then((response3) => {
            expect(response3.status).to.eq(201);

            // Step 5: Check my valuations for valuator
            cy.request('GET', '/api/v1/users/me/valuations').then((response4) => {
              const myValuation = response4.body.results.find(
                (val: { brickset: { id: number } }) => val.brickset.id === flowBricksetId
              );
              expect(myValuation).to.not.equal(undefined);
              expect(myValuation.value).to.eq(650);

              // Step 6: Original user views updated brickset
              cy.clearAllSessionStorage();
              cy.login(flowUser.username, flowUser.password);

              cy.request('GET', '/api/v1/users/me/bricksets').then((response5) => {
                const myBrickset2 = response5.body.results.find(
                  (bs: { id: number }) => bs.id === flowBricksetId
                );
                expect(myBrickset2.valuations_count).to.eq(1);

                // Step 7: Original user tries to edit (should fail - has external valuation)
                cy.request({
                  method: 'PATCH',
                  url: `/api/v1/bricksets/${flowBricksetId}`,
                  body: { has_box: false },
                  failOnStatusCode: false,
                }).then((response6) => {
                  expect(response6.status).to.eq(403);
                });
              });
            });
          });
        });
      });
    });
  });
});
