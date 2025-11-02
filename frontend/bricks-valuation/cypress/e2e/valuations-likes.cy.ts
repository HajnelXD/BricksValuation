describe('Valuations and Likes', () => {
  const timestamp = Date.now();
  const testUser = {
    username: `valuser${timestamp}`,
    email: `valuser${timestamp}@example.com`,
    password: 'ValPass123!',
  };

  const secondUser = {
    username: `valuser2${timestamp}`,
    email: `valuser2${timestamp}@example.com`,
    password: 'ValPass123!',
  };

  const thirdUser = {
    username: `valuser3${timestamp}`,
    email: `valuser3${timestamp}@example.com`,
    password: 'ValPass123!',
  };

  // Helper to generate unique brickset numbers
  let bricksetCounter = 0;
  const getUniqueBricksetNumber = () => {
    bricksetCounter++;
    return 10000 + (timestamp % 10000) + bricksetCounter;
  };

  let testBricksetId: number;

  before(() => {
    cy.clearCookies();
    cy.clearLocalStorage();

    // Register all users
    cy.register(testUser.username, testUser.email, testUser.password);
    cy.register(secondUser.username, secondUser.email, secondUser.password);
    cy.register(thirdUser.username, thirdUser.email, thirdUser.password);

    // Login as first user and create test brickset
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
        owner_initial_estimate: 300,
      },
    }).then((response) => {
      testBricksetId = response.body.id;
    });
  });

  beforeEach(function () {
    // Skip session restoration for auth tests
    if (this.currentTest?.title?.includes('should require authentication')) {
      return;
    }
    // Restore session before each test
    cy.login(testUser.username, testUser.password);
  });

  describe('Add Valuation (FR-10)', () => {
    it('should successfully add valuation to brickset', () => {
      // Second user adds valuation
      cy.clearAllSessionStorage();
      cy.login(secondUser.username, secondUser.password);

      cy.request({
        method: 'POST',
        url: `/api/v1/bricksets/${testBricksetId}/valuations`,
        body: {
          value: 350,
          currency: 'PLN',
          comment: 'Good condition, complete set',
        },
      }).then((response) => {
        expect(response.status).to.eq(201);
        expect(response.body).to.have.property('id');
        expect(response.body.brickset_id).to.eq(testBricksetId);
        expect(response.body.value).to.eq(350);
        expect(response.body.currency).to.eq('PLN');
        expect(response.body.comment).to.eq('Good condition, complete set');
        expect(response.body.likes_count).to.eq(0);
        expect(response.body).to.have.property('user_id');
      });
    });

    it('should add valuation without optional comment', () => {
      cy.clearAllSessionStorage();
      cy.login(thirdUser.username, thirdUser.password);

      cy.request({
        method: 'POST',
        url: `/api/v1/bricksets/${testBricksetId}/valuations`,
        body: {
          value: 400,
          currency: 'PLN',
        },
      }).then((response) => {
        expect(response.status).to.eq(201);
        expect(response.body.value).to.eq(400);
      });
    });

    it('should fail with invalid value (too small)', () => {
      cy.request({
        method: 'POST',
        url: `/api/v1/bricksets/${testBricksetId}/valuations`,
        body: {
          value: 0,
          currency: 'PLN',
        },
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(400);
      });
    });

    it('should fail with invalid value (too large)', () => {
      // Create new brickset for this test
      cy.clearAllSessionStorage();
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
        },
      }).then((bsResponse) => {
        cy.request({
          method: 'POST',
          url: `/api/v1/bricksets/${bsResponse.body.id}/valuations`,
          body: {
            value: 1000000,
            currency: 'PLN',
          },
          failOnStatusCode: false,
        }).then((response) => {
          expect(response.status).to.eq(400);
        });
      });
    });

    it('should fail for non-existent brickset', () => {
      cy.request({
        method: 'POST',
        url: '/api/v1/bricksets/999999/valuations',
        body: {
          value: 200,
          currency: 'PLN',
        },
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(404);
        if (response.body.code) {
          expect(response.body.code).to.eq('BRICKSET_NOT_FOUND');
        }
      });
    });
  });

  describe('One Valuation Per User-Set (FR-11, RB-02)', () => {
    let singleValBricksetId: number;

    before(() => {
      cy.clearAllSessionStorage();
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
        },
      }).then((response) => {
        singleValBricksetId = response.body.id;

        cy.clearAllSessionStorage();
        cy.login(secondUser.username, secondUser.password);

        // Add first valuation
        cy.request({
          method: 'POST',
          url: `/api/v1/bricksets/${singleValBricksetId}/valuations`,
          body: {
            value: 150,
            currency: 'PLN',
          },
        });
      });
    });

    it('should fail to add second valuation for same brickset by same user', () => {
      // Make sure we're logged in as second user (who already added a valuation)
      cy.clearAllSessionStorage();
      cy.login(secondUser.username, secondUser.password);

      cy.request({
        method: 'POST',
        url: `/api/v1/bricksets/${singleValBricksetId}/valuations`,
        body: {
          value: 200,
          currency: 'PLN',
        },
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(409);
        if (response.body.code) {
          expect(response.body.code).to.eq('VALUATION_DUPLICATE');
        }
      });
    });

    it('should allow different users to add valuations to same brickset', () => {
      cy.clearAllSessionStorage();
      cy.login(thirdUser.username, thirdUser.password);

      cy.request({
        method: 'POST',
        url: `/api/v1/bricksets/${singleValBricksetId}/valuations`,
        body: {
          value: 180,
          currency: 'PLN',
        },
      }).then((response) => {
        expect(response.status).to.eq(201);
      });
    });
  });

  describe('List Valuations (FR-09)', () => {
    it('should list all valuations for a brickset', () => {
      cy.request({
        method: 'GET',
        url: `/api/v1/bricksets/${testBricksetId}/valuations`,
      }).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.have.property('count');
        expect(response.body).to.have.property('results');
        expect(response.body.results).to.be.an('array');
        expect(response.body.results.length).to.be.greaterThan(0);

        // Verify valuation structure
        const valuation = response.body.results[0];
        expect(valuation).to.have.property('id');
        expect(valuation).to.have.property('user_id');
        expect(valuation).to.have.property('value');
        expect(valuation).to.have.property('currency');
        expect(valuation).to.have.property('likes_count');
      });
    });

    it('should get single valuation details', () => {
      // First get list to find a valuation ID
      cy.request({
        method: 'GET',
        url: `/api/v1/bricksets/${testBricksetId}/valuations`,
      }).then((listResponse) => {
        const valuationId = listResponse.body.results[0].id;

        cy.request({
          method: 'GET',
          url: `/api/v1/valuations/${valuationId}`,
        }).then((response) => {
          expect(response.status).to.eq(200);
          expect(response.body.id).to.eq(valuationId);
          expect(response.body).to.have.property('brickset_id');
          expect(response.body).to.have.property('user_id');
          expect(response.body).to.have.property('value');
          expect(response.body).to.have.property('currency');
          expect(response.body).to.have.property('likes_count');
        });
      });
    });
  });

  describe('Like Valuation (FR-12)', () => {
    let valuationToLikeId: number;

    before(() => {
      // Login before getting valuations
      cy.clearAllSessionStorage();
      cy.login(testUser.username, testUser.password);

      // Get a valuation to like
      cy.request({
        method: 'GET',
        url: `/api/v1/bricksets/${testBricksetId}/valuations`,
      }).then((response) => {
        valuationToLikeId = response.body.results[0].id;
      });
    });

    it("should successfully like another user's valuation", () => {
      // Make sure we're logged in as a different user than valuation owner
      cy.clearAllSessionStorage();
      cy.login(testUser.username, testUser.password);

      cy.request({
        method: 'POST',
        url: `/api/v1/valuations/${valuationToLikeId}/likes`,
      }).then((response) => {
        expect(response.status).to.eq(201);
        expect(response.body.valuation_id).to.eq(valuationToLikeId);
        expect(response.body).to.have.property('user_id');
      });

      // Verify like count increased
      cy.request({
        method: 'GET',
        url: `/api/v1/valuations/${valuationToLikeId}`,
      }).then((response) => {
        expect(response.body.likes_count).to.be.greaterThan(0);
      });
    });

    it('should fail to like same valuation twice (FR-12, RB-03)', () => {
      cy.request({
        method: 'POST',
        url: `/api/v1/valuations/${valuationToLikeId}/likes`,
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(409);
        if (response.body.code) {
          expect(response.body.code).to.eq('LIKE_DUPLICATE');
        }
      });
    });

    it('should fail for non-existent valuation', () => {
      cy.request({
        method: 'POST',
        url: '/api/v1/valuations/999999/likes',
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(404);
        if (response.body.code) {
          expect(response.body.code).to.eq('VALUATION_NOT_FOUND');
        }
      });
    });
  });

  describe('Block Liking Own Valuation (FR-13, RB-03)', () => {
    let ownValuationId: number;

    before(() => {
      // Create new brickset and add valuation as secondUser
      cy.clearAllSessionStorage();
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
        },
      }).then((bsResponse) => {
        cy.clearAllSessionStorage();
        cy.login(secondUser.username, secondUser.password);

        cy.request({
          method: 'POST',
          url: `/api/v1/bricksets/${bsResponse.body.id}/valuations`,
          body: {
            value: 250,
            currency: 'PLN',
          },
        }).then((valResponse) => {
          ownValuationId = valResponse.body.id;
        });
      });
    });

    it('should fail to like own valuation', () => {
      // Make sure we're logged in as second user (owner of the valuation)
      cy.clearAllSessionStorage();
      cy.login(secondUser.username, secondUser.password);

      cy.request({
        method: 'POST',
        url: `/api/v1/valuations/${ownValuationId}/likes`,
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(403);
        if (response.body.code) {
          expect(response.body.code).to.eq('LIKE_OWN_VALUATION_FORBIDDEN');
        }
      });
    });

    it('should verify likes_count remains 0 after failed like attempt', () => {
      cy.clearAllSessionStorage();
      cy.login(secondUser.username, secondUser.password);

      cy.request({
        method: 'GET',
        url: `/api/v1/valuations/${ownValuationId}`,
      }).then((response) => {
        expect(response.body.likes_count).to.eq(0);
      });
    });
  });

  describe('Unlike Valuation (Optional)', () => {
    let unlikeValuationId: number;

    before(() => {
      // Create brickset and valuation for unlike test
      cy.clearAllSessionStorage();
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
        },
      }).then((bsResponse) => {
        cy.clearAllSessionStorage();
        cy.login(secondUser.username, secondUser.password);

        cy.request({
          method: 'POST',
          url: `/api/v1/bricksets/${bsResponse.body.id}/valuations`,
          body: {
            value: 175,
            currency: 'PLN',
          },
        }).then((valResponse) => {
          unlikeValuationId = valResponse.body.id;

          // Third user likes it
          cy.clearAllSessionStorage();
          cy.login(thirdUser.username, thirdUser.password);

          cy.request({
            method: 'POST',
            url: `/api/v1/valuations/${unlikeValuationId}/likes`,
          });
        });
      });
    });

    it('should successfully unlike a valuation', () => {
      // Make sure we're logged in as third user (who liked it)
      cy.clearAllSessionStorage();
      cy.login(thirdUser.username, thirdUser.password);

      cy.request({
        method: 'DELETE',
        url: `/api/v1/valuations/${unlikeValuationId}/likes`,
        failOnStatusCode: false,
      }).then((response) => {
        // Accept both 204 (success) or 405 (not implemented in MVP)
        expect(response.status).to.be.oneOf([204, 405]);

        if (response.status === 204) {
          // If unlike is implemented, verify count decreased
          cy.request({
            method: 'GET',
            url: `/api/v1/valuations/${unlikeValuationId}`,
          }).then((valResponse) => {
            expect(valResponse.body.likes_count).to.eq(0);
          });
        }
      });
    });
  });

  describe('Valuation Sorting (FR-09)', () => {
    let sortBricksetId: number;

    before(() => {
      // Create brickset with multiple valuations
      cy.clearAllSessionStorage();
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
        },
      }).then((bsResponse) => {
        sortBricksetId = bsResponse.body.id;

        // Add valuation from second user (will get many likes)
        cy.clearAllSessionStorage();
        cy.login(secondUser.username, secondUser.password);

        cy.request({
          method: 'POST',
          url: `/api/v1/bricksets/${sortBricksetId}/valuations`,
          body: {
            value: 500,
            currency: 'PLN',
            comment: 'High value',
          },
        }).then((val1Response) => {
          highLikedValId = val1Response.body.id;

          // Add valuation from third user (will get fewer likes)
          cy.clearAllSessionStorage();
          cy.login(thirdUser.username, thirdUser.password);

          cy.request({
            method: 'POST',
            url: `/api/v1/bricksets/${sortBricksetId}/valuations`,
            body: {
              value: 300,
              currency: 'PLN',
              comment: 'Lower value',
            },
          }).then((val2Response) => {
            lowLikedValId = val2Response.body.id;

            // Add likes to first valuation
            cy.clearAllSessionStorage();
            cy.login(testUser.username, testUser.password);
            cy.request('POST', `/api/v1/valuations/${highLikedValId}/likes`);

            cy.clearAllSessionStorage();
            cy.login(thirdUser.username, thirdUser.password);
            cy.request('POST', `/api/v1/valuations/${highLikedValId}/likes`);
          });
        });
      });
    });

    it('should list valuations sorted by likes_count descending', () => {
      cy.request({
        method: 'GET',
        url: `/api/v1/bricksets/${sortBricksetId}/valuations`,
      }).then((response) => {
        expect(response.status).to.eq(200);
        const results = response.body.results;

        // First result should have most likes
        if (results.length >= 2) {
          expect(results[0].likes_count).to.be.at.least(results[1].likes_count);
        }
      });
    });
  });

  describe('Authentication Requirements (FR-18)', () => {
    it('should require authentication to add valuation', () => {
      cy.clearAllSessionStorage();
      cy.clearCookies();

      cy.request({
        method: 'POST',
        url: `/api/v1/bricksets/${testBricksetId}/valuations`,
        body: {
          value: 200,
          currency: 'PLN',
        },
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(401);
      });
    });

    it('should require authentication to like valuation', () => {
      // First login to get valuation ID
      cy.clearAllSessionStorage();
      cy.login(testUser.username, testUser.password);

      cy.request({
        method: 'GET',
        url: `/api/v1/bricksets/${testBricksetId}/valuations`,
      }).then((listResponse) => {
        const valuationId = listResponse.body.results[0].id;

        // Now logout and try to like without auth
        cy.clearAllSessionStorage();
        cy.clearCookies();

        cy.request({
          method: 'POST',
          url: `/api/v1/valuations/${valuationId}/likes`,
          failOnStatusCode: false,
        }).then((response) => {
          expect(response.status).to.eq(401);
        });
      });
    });
  });
});
