# AI Rules for BricksValuation - Claude Code

An app for pricing used Lego bricks.

## GENERAL WORKFLOW

- Always use TodoWrite tool to plan and track tasks for non-trivial work
- Before committing code changes, always run linter and tests (see BACKEND section)
- Use Task tool with Explore subagent for codebase exploration and understanding architecture
- Use markdown link syntax for file references: [filename.ts:42](src/filename.ts#L42)
- Keep responses concise and avoid emojis unless explicitly requested
- Prefer editing existing files over creating new ones

## BACKEND

### Guidelines for PYTHON

#### DJANGO

**Architecture & Layers:**
- Use class-based views (APIView / GenericAPIView). Views must remain thin: input validation via serializer + delegation to service layer
- Service layer (`account/services/*.py`) coordinates domain logic, business validation and handles transactions (`transaction.atomic()`). Never place domain logic inside views or serializers beyond simple structural validation
- Every service must have a single responsibility and expose a clear public interface (typically `execute()` method)
- Service methods should return DTOs (outbound data structures) not Models. DTOs ensure clean separation and allow field filtering

**Error Handling:**
- Raise domain exceptions in services (not generic Exception or ValidationError)
- Map domain exceptions to HTTP codes in the view layer
- For security: implement generic error messages in authentication services. Do not expose whether a username exists or password is correct

**Transaction Handling:**
- Wrap business operations in `transaction.atomic()` when atomicity matters
- For expected uniqueness conflicts, catch only specific `IntegrityError` and map to domain exception

**Serializers:**
- Serializers validate field format and basic constraints
- Convert validated data to Command objects (e.g. `RegisterUserCommand`) via `to_command()`
- Do not add side-effects or database writes in serializers

**Commands & DTOs:**
- Commands & DTOs (`datastore/domains/*_dto.py`) are dataclasses with `slots=True`
- Declare explicit mapping to models (`source_model`)
- Separate inbound payload (Command) from outbound data (DTO)
- Never expose sensitive fields (e.g. raw password) in DTOs
- Commands represent validated user intent; DTOs are output structures from services
- Never store sensitive data in DTOs or return it in API responses

**Model Constraints:**
- Enforce uniqueness and length rules with both model validators and DB-level `CheckConstraint`
- Do not bloat models – complex business logic belongs in services

**Code Quality:**
- After EVERY backend code change before committing run:
  1. Linter: `./bin/lint_backend.sh`
  2. Tests: `./bin/test_backend.sh`
- Commit only if both pass

#### JWT_AND_AUTHENTICATION

**JWT Configuration:**
- JWT configuration must be centralized in `config/jwt_config.py`
- Create dedicated `TokenProvider` service class for all JWT operations: generation, validation, and decoding
- Include minimal payload in JWT: user_id, username, exp, iat. Never include sensitive data

**Cookie Security:**
- Always use HttpOnly cookies for JWT storage in web applications
- Set security attributes: `secure=True` (production), `samesite="Strict"`, `path="/"`, `max_age=expiration_seconds`
- Never return JWT tokens in response body when using cookies

**Security Best Practices:**
- Token expiration should be short-lived (24 hours typical)
- Implement token refresh mechanism separately for longer sessions
- Use generic error messages like "Invalid username or password" to prevent user enumeration attacks
- Set passwords using `User.set_password`; never store raw password

**Domain Exceptions:**
- Domain exceptions (e.g. `RegistrationConflictError`, `RegistrationValidationError`) signal controlled error states
- View maps them to proper HTTP codes (400 / 409)
- Introduce targeted exception classes for new scenarios

**Adding New Endpoints:**
1. Create Serializer + `to_command()`
2. Add Command/DTO if needed
3. Create Service with `execute()`
4. Create class-based view delegating to service
5. Add tests: serializer, service (unit), view (API)

#### DRF_API_VIEWS

**View Responsibilities:**
- APIView must be a thin routing layer: deserialize input → validate via serializer → call service → map service result to Response
- Never put domain logic in views; delegate to service layer
- Views handle HTTP concerns only (status codes, cookies, headers)

**Response Format:**
- Always use `Response(data, status=HTTP_XXX)` for consistency
- For success responses, wrap data in a dict with semantic keys (e.g., `{"user": user_dto}`), not bare lists

**Error Handling:**
- View must catch domain exceptions and map to HTTP codes
- Example: catch `InvalidCredentialsError` → return `Response({...}, HTTP_401_UNAUTHORIZED)`
- Use descriptive error messages in responses

**Cookie Handling:**
- Use `response.set_cookie(key, value, httponly=True, secure=SECURE_SETTING, samesite="Strict", path="/")`
- Never return JWT token in response body when using cookies

**Throttling:**
- If adding throttle_classes to view, ensure DRF THROTTLE_RATES is configured in settings.py
- Example: `REST_FRAMEWORK = {"DEFAULT_THROTTLE_RATES": {"login": "5/min"}}`

**URL Generation:**
- Always use reverse_lazy or get_absolute_url for URL generation in views; avoid hardcoded paths

#### SERIALIZERS

**Responsibilities:**
- Serializers are thin validation layers only
- Validate input format and call `to_command()` to convert to Command object
- Add `to_command()` method to every Serializer that receives external input
- Never add side-effects (database writes, API calls, signal emissions)

**Validation:**
- Use `trim_whitespace=True` in CharField for fields that should have whitespace removed
- Implement custom `validate_fieldname()` methods for field-level checks
- Use `validate()` for cross-field validation only

**Security:**
- All password fields must have `write_only=True`
- Sensitive fields (passwords, tokens) must never appear in serializer output representations

#### EXCEPTIONS_AND_ERROR_HANDLING

**Domain Exceptions:**
- Create domain-specific exception classes for each error scenario (e.g., `LoginValidationError`, `InvalidCredentialsError`)
- Each custom exception must have a clear purpose and be used consistently
- Service layer raises domain exceptions; view layer catches them and maps to HTTP status codes

**HTTP Mapping:**
- 400 for validation errors
- 401 for authentication failures
- 409 for conflicts (uniqueness violations)

**Security:**
- Use generic error messages in public APIs to prevent user enumeration
- Example: always say "Invalid username or password" instead of "User not found" or "Password incorrect"

## TESTING

### Guidelines for UNIT

#### PYTEST

**Running Tests:**
- Always run backend tests via: `./bin/test_backend.sh`
- Script sets correct environment, coverage and uses `--nomigrations` for speed
- Minimum coverage threshold is 90% (enforced by `--cov-fail-under=90`)

**Test Structure:**
- Each implementation module has a sibling `tests/` folder (e.g. `account/services/tests/test_registration_service.py`)
- File naming: `test_<name>_<type>.py` or `test_<function>.py`
- Test classes end with suffix `Tests` (e.g. `RegistrationServiceTests`)

**CRITICAL Django Testing Rules:**
- Use `django.test.TestCase` for service/model tests, **NOT pytest fixtures**
- Fixtures with `@pytest.fixture` do NOT work with Django ORM inside TestCase classes
- Use `setUp()` and `tearDown()` methods for fixture setup/cleanup
- Use `unittest.mock.patch` for selective mocking, not pytest's monkeypatch

**Test Naming:**
- AVOID numbers directly in method names (WPS114)
- Instead of `test_returns_400`, use `test_validation_fails_with_bad_request` or `test_missing_field_returns_bad_request`
- Use descriptive names without underscored numbers

**Test Categories:**
1. Unit – service layer, serializers, exceptions
2. API/integration – DRF views with `APIRequestFactory` or `APITestCase`
- In view tests assert status, payload and side-effects (e.g. user persisted)

**DRF View Testing Pattern:**
- Use `reverse_lazy("route-name")` instead of hardcoded paths
- Always call `response.render()` before accessing `response.data` when using APIRequestFactory
- Example: `request = self.factory.post(self.url, payload); response = self.view(request); response.render(); assert response.data["field"]`

**Assertions:**
- Use `pytest.raises` ONLY in pytest module functions, never in TestCase classes
- Within `django.test.TestCase`/`APITestCase` use `with self.assertRaises(ExceptionType)` or plain `assert` statements

**Naming Conventions:**
- Use descriptive variable names, NOT single letters
- Bad: `result = service.execute()`
- Good: `user_dto = service.execute()` or `authenticated_user = service.execute()`
- Avoids WPS110 "wrong variable name" violations

**Best Practices:**
- Arrange-Act-Assert: build helper `_build_command()` methods for repeated payloads
- Serializer tests must not write to DB – limit to data validation and `to_command()` conversion
- Use `unittest.mock.patch` / `monkeypatch` selectively to isolate costly dependencies
- Every error scenario requires a dedicated clearly named test
- When introducing new domain exceptions immediately add a test for its HTTP mapping in the view

**Before Push:**
1. `./bin/lint_backend.sh`
2. `./bin/test_backend.sh`
- Both must exit 0

### Guidelines for E2E

#### CYPRESS

- Use component testing for testing components in isolation
- Implement E2E testing for critical user flows
- Use cy.intercept() for network request mocking and stubbing
- Leverage custom commands for reusable test steps
- Implement fixtures for test data
- Use data-* attributes for test selectors instead of CSS classes or IDs
- Leverage the Testing Library integration for better queries
- Implement retry-ability for flaky tests

## FRONTEND

### Guidelines for VUE

#### VUE_CODING_STANDARDS

- Use the Composition API instead of the Options API for better type inference and code reuse
- Implement `<script setup>` for more concise component definitions
- Use Suspense and async components for handling loading states during code-splitting
- Leverage the defineProps and defineEmits macros for type-safe props and events
- Use the new defineOptions for additional component options
- Implement provide/inject for dependency injection instead of prop drilling in deeply nested components
- Use the Teleport component for portal-like functionality to render UI elsewhere in the DOM
- Leverage ref over reactive for primitive values to avoid unintended unwrapping
- Use v-memo for performance optimization in render-heavy list rendering scenarios
- Implement shallow refs for large objects that don't need deep reactivity

#### VUE_ROUTER

- Use route guards (beforeEach, beforeEnter) for authentication and authorization checks
- Implement lazy loading with dynamic imports for route components to improve performance
- Use named routes instead of hardcoded paths for better maintainability
- Leverage route meta fields to store additional route information like permissions or layout data
- Implement scroll behavior options to control scrolling between route navigations
- Use navigation duplicates handling to prevent redundant navigation to the current route
- Implement the composition API useRouter and useRoute hooks instead of this.$router
- Use nested routes for complex UIs with parent-child relationships
- Leverage route params validation with sensitive: true for parameters that shouldn't be logged
- Implement dynamic route matching with path parameters and regex patterns for flexible routing

#### PINIA

- Create multiple stores based on logical domains instead of a single large store
- Use the setup syntax (defineStore with setup function) for defining stores for better TypeScript inference
- Implement getters for derived state to avoid redundant computations
- Leverage the storeToRefs helper to extract reactive properties while maintaining reactivity
- Use plugins for cross-cutting concerns like persistence, state resets, or dev tools
- Implement actions for asynchronous operations and complex state mutations
- Use composable stores by importing and using stores within other stores
- Leverage the $reset() method to restore initial state when needed
- Implement $subscribe for reactive store subscriptions
- Use TypeScript with proper return type annotations for maximum type safety

### Guidelines for STYLING

#### TAILWIND

- Use the @layer directive to organize styles into components, utilities, and base layers
- Implement Just-in-Time (JIT) mode for development efficiency and smaller CSS bundles
- Use arbitrary values with square brackets (e.g., w-[123px]) for precise one-off designs
- Leverage the @apply directive in component classes to reuse utility combinations
- Implement the Tailwind configuration file for customizing theme, plugins, and variants
- Use component extraction for repeated UI patterns instead of copying utility classes
- Leverage the theme() function in CSS for accessing Tailwind theme values
- Implement dark mode with the dark: variant
- Use responsive variants (sm:, md:, lg:, etc.) for adaptive designs
- Leverage state variants (hover:, focus:, active:, etc.) for interactive elements

## DEVOPS

### Guidelines for CONTAINERIZATION

#### DOCKER

- Use multi-stage builds to create smaller production images
- Implement layer caching strategies to speed up builds
- Use non-root users in containers for better security

## CODING_PRACTICES

### Guidelines for VERSION_CONTROL

#### GIT

- Use conventional commits to create meaningful commit messages
- Use feature branches with descriptive names following BV-1234 pattern
- Write meaningful commit messages that explain why changes were made, not just what
- Keep commits focused on single logical changes to facilitate code review and bisection
- Use interactive rebase to clean up history before merging feature branches
- Leverage git hooks to enforce code quality checks before commits and pushes

#### GITHUB

- Use pull request templates to standardize information provided for code reviews
- Implement branch protection rules for development to enforce quality checks
- Configure required status checks to prevent merging code that fails tests or linting
- Use GitHub Actions for CI/CD workflows to automate testing and deployment
- Implement CODEOWNERS files to automatically assign reviewers based on code paths
- Use GitHub Projects for tracking work items and connecting them to code changes

### Guidelines for STATIC_ANALYSIS

#### ESLINT

- Configure project-specific rules in eslint.config.js to enforce consistent coding standards
- Use shareable configs like eslint-config-airbnb or eslint-config-standard as a foundation
- Configure integration with Prettier to avoid rule conflicts for code formatting
- Use the --fix flag in CI/CD pipelines to automatically correct fixable issues
- Implement staged linting with husky and lint-staged to prevent committing non-compliant code

#### PRETTIER

- Configure editor integration to format on save for immediate feedback
- Set printWidth based on team preferences (80-120 characters) to improve code readability
- Configure consistent quote style and semicolon usage to match team conventions
- Implement CI checks to ensure all committed code adheres to the defined style
