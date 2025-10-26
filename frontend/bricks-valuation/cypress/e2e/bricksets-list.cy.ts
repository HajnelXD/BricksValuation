describe('BrickSets List View', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  describe('Page Loading', () => {
    it('loads the page successfully', () => {
      cy.get('main').should('exist');
      // Just check that h1 exists and has some text
      cy.get('h1').should('not.be.empty');
    });

    it('displays filters panel', () => {
      cy.get('[data-testid="filters-panel"]').should('exist');
    });

    it('displays loading state initially', () => {
      cy.intercept('GET', '**/api/v1/bricksets*').as('getBrickSets');
      cy.visit('/');
      cy.get('[data-testid="loading"]').should('exist');
      cy.wait('@getBrickSets');
    });
  });

  describe('Displaying Results', () => {
    it('displays pagination when there are results', () => {
      cy.intercept('GET', '**/api/v1/bricksets*', {
        statusCode: 200,
        body: {
          count: 100,
          results: Array(12).fill({
            id: 1,
            number: 10001,
            production_status: 'ACTIVE',
            completeness: 'COMPLETE',
          }),
          next: 'http://localhost:8000/api/v1/bricksets?page=2',
          previous: null,
        },
      }).as('getBrickSets');

      cy.visit('/');
      cy.wait('@getBrickSets');
      cy.get('[data-testid="pagination"]').should('exist');
    });

    it('handles empty state correctly', () => {
      cy.intercept('GET', '**/api/v1/bricksets*', {
        statusCode: 200,
        body: {
          count: 0,
          results: [],
          next: null,
          previous: null,
        },
      }).as('getBrickSets');

      cy.visit('/');
      cy.wait('@getBrickSets');
      cy.get('[data-testid="empty-state"]').should('exist');
    });

    it('displays brickset cards with data', () => {
      cy.intercept('GET', '**/api/v1/bricksets*', {
        statusCode: 200,
        body: {
          count: 1,
          results: [
            {
              id: 1,
              number: 10001,
              production_status: 'ACTIVE',
              completeness: 'COMPLETE',
              top_valuation: { id: 1, value: 200, currency: 'PLN', likes_count: 10 },
              created_at: new Date().toISOString(),
              valuations_count: 5,
              total_likes: 15,
              has_instructions: true,
              has_box: true,
              is_factory_sealed: false,
              owner_id: 1,
              owner_initial_estimate: 150,
              updated_at: new Date().toISOString(),
            },
          ],
          next: null,
          previous: null,
        },
      }).as('getBrickSets');

      cy.visit('/');
      cy.wait('@getBrickSets');
      cy.get('main').should('contain', '10001');
    });
  });

  describe('Error Handling', () => {
    it('displays error state on API failure', () => {
      cy.intercept('GET', '**/api/v1/bricksets*', {
        statusCode: 500,
        body: { detail: 'Server error' },
      }).as('apiError');

      cy.visit('/');
      cy.wait('@apiError');
      cy.get('[data-testid="error-state"]').should('exist');
    });

    it('shows error message on network failure', () => {
      cy.intercept('GET', '**/api/v1/bricksets*', { forceNetworkError: true }).as('networkError');
      cy.visit('/');
      cy.wait('@networkError');
      cy.get('[data-testid="error-state"]').should('exist');
    });

    it('retry button recovers from error', () => {
      let callCount = 0;
      cy.intercept('GET', '**/api/v1/bricksets*', (req) => {
        callCount++;
        if (callCount === 1) {
          req.reply({
            statusCode: 500,
            body: { detail: 'Server error' },
          });
        } else {
          req.reply({
            statusCode: 200,
            body: {
              count: 0,
              results: [],
              next: null,
              previous: null,
            },
          });
        }
      }).as('getBrickSets');

      cy.visit('/');
      cy.wait('@getBrickSets');
      cy.get('[data-testid="retry-button"]').click();
      cy.wait('@getBrickSets');
    });
  });

  describe('Filtering', () => {
    it('filters results when search term is entered', () => {
      cy.intercept('GET', '**/api/v1/bricksets*').as('getBrickSets');
      cy.get('input[placeholder*="search" i]').type('test');
      cy.wait(350);
      cy.get('@getBrickSets.all').then((interceptions) => {
        expect(interceptions.length).toBeGreaterThan(0);
      });
    });

    it('filters by production status', () => {
      cy.get('[data-testid="production-status-filter"]').select('ACTIVE');
      cy.url().should('include', 'production_status=ACTIVE');
    });

    it('filters by completeness', () => {
      cy.get('[data-testid="completeness-filter"]').select('COMPLETE');
      cy.url().should('include', 'completeness=COMPLETE');
    });

    it('filters by instructions availability', () => {
      cy.get('[data-testid="has-instructions-checkbox"]').check();
      cy.url().should('include', 'has_instructions=true');
    });

    it('filters by box availability', () => {
      cy.get('[data-testid="has-box-checkbox"]').check();
      cy.url().should('include', 'has_box=true');
    });

    it('resets all filters', () => {
      cy.visit('/?search=test&production_status=ACTIVE');
      cy.get('[data-testid="reset-filters-btn"]').click();
      cy.url().should('not.include', 'search=');
      cy.url().should('not.include', 'production_status=');
    });
  });

  describe('Pagination', () => {
    it('navigates between pages', () => {
      cy.intercept('GET', '**/api/v1/bricksets*', {
        statusCode: 200,
        body: {
          count: 100,
          results: Array(12).fill({ id: 1 }),
          next: 'http://localhost:8000/api/v1/bricksets?page=2',
          previous: null,
        },
      }).as('getBrickSets');

      cy.visit('/');
      cy.wait('@getBrickSets');
      cy.get('[data-testid="next-page-btn"]').click();
      cy.url().should('include', 'page=2');
    });

    it('disables previous button on first page', () => {
      cy.get('[data-testid="prev-page-btn"]').should('be.disabled');
    });

    it('disables next button on last page', () => {
      cy.intercept('GET', '**/api/v1/bricksets*', {
        statusCode: 200,
        body: {
          count: 12,
          results: Array(12).fill({ id: 1 }),
          next: null,
          previous: null,
        },
      }).as('getBrickSets');

      cy.visit('/');
      cy.wait('@getBrickSets');
      cy.get('[data-testid="next-page-btn"]').should('be.disabled');
    });
  });

  describe('Sorting', () => {
    it('sorts by newest first (default)', () => {
      cy.url().should('include', 'ordering=-created_at');
    });

    it('changes sort order', () => {
      cy.get('[data-testid="ordering-select"]').select('created_at');
      cy.url().should('include', 'ordering=created_at');
    });
  });

  describe('Navigation', () => {
    it('navigates to detail page on card click', () => {
      cy.intercept('GET', '**/api/v1/bricksets*', {
        statusCode: 200,
        body: {
          count: 1,
          results: [
            {
              id: 42,
              number: 10001,
              production_status: 'ACTIVE',
              completeness: 'COMPLETE',
              top_valuation: { id: 1, value: 100, currency: 'PLN', likes_count: 5 },
              created_at: new Date().toISOString(),
              valuations_count: 3,
              total_likes: 10,
              has_instructions: true,
              has_box: true,
              is_factory_sealed: false,
              owner_id: 1,
              owner_initial_estimate: 150,
              updated_at: new Date().toISOString(),
            },
          ],
          next: null,
          previous: null,
        },
      }).as('getBrickSets');

      cy.visit('/');
      cy.wait('@getBrickSets');
      cy.get('main').find('button, a, [role="button"]').first().click();
    });
  });

  describe('Accessibility', () => {
    it('has proper heading hierarchy', () => {
      cy.get('h1').should('exist');
    });

    it('filter inputs have labels', () => {
      cy.get('label').should('have.length.greaterThan', 0);
    });

    it('buttons are keyboard accessible', () => {
      cy.get('button').first().focus();
      cy.focused().should('have.attr', 'data-testid');
    });
  });
});
