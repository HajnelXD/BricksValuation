# AI Rules for BricksValuation

An app for pricing used Lego bricks.

## BACKEND

### Guidelines for PYTHON

#### DJANGO
English version:
- Use class-based views (APIView / GenericAPIView). A view must remain a thin layer: input validation via serializer + delegation to the service layer.
- Service layer (`account/services/*.py`) coordinates domain logic, business validation and handles transactions (`transaction.atomic()`). Never place domain logic inside views or serializers beyond simple structural validation.
- Serializers validate field format and basic constraints; they convert validated data to Command objects (e.g. `RegisterUserCommand`) via `to_command()`. Do not add side-effects or database writes in serializers.
- Commands & DTOs (`datastore/domains/*_dto.py`) are dataclasses with `slots=True`; they declare explicit mapping to models (`source_model`) and separate inbound payload (Command) from outbound data (DTO). Never expose sensitive fields (e.g. raw password) in DTOs.
- Enforce uniqueness and length rules both with model validators and (if needed) DB-level `CheckConstraint` (see `User` model). When adding constraints: first validator, then constraint for immediate feedback and consistency.
- Domain exceptions (e.g. `RegistrationConflictError`, `RegistrationValidationError`) signal controlled error states; the view maps them to proper HTTP codes (400 / 409). Avoid catching broad exceptions; introduce targeted exception classes for new scenarios.
- Wrap persistence in transactions where races or atomicity are required. For expected uniqueness conflicts, catch only specific `IntegrityError` and map to domain exception.
- Set passwords using `User.set_password`; never store raw password outside the transient Command object processed in the service.
- Limit Django signals; prefer explicit service calls. If a signal is necessary (e.g. side-effect after record creation) document it in the module docstring and test in isolation.
- Adding a new endpoint: (1) create Serializer + `to_command()`, (2) add Command/DTO if needed, (3) create Service with `execute()`, (4) create class-based view delegating to service, (5) add tests: serializer, service (unit), view (API). Keep naming consistent.
- Do not bloat models – complex business logic belongs in services. Models keep validators, constraints, simple behaviors (timestamps, etc.).
- After EVERY backend code change before committing run linter: `./bin/lint_backend.sh` and tests: `./bin/test_backend.sh` (see PYTEST section). Commit only if both pass.
- After adding any new code changes, always run the backend linter using the command `./bin/lint_backend.sh` as specified in the README.md to ensure adherence to coding standards.
- Ensure that after code updates, the full backend test suite is executed via `./bin/test_backend.sh` to maintain quality and test coverage (minimum 90%).

## DEVOPS

### Guidelines for CONTAINERIZATION

#### DOCKER

- Use multi-stage builds to create smaller production images
- Implement layer caching strategies to speed up builds
- Use non-root users in containers for better security

## TESTING

### Guidelines for UNIT

#### PYTEST
English version:
- Always run backend tests via the script: `./bin/test_backend.sh` – it sets correct environment, coverage and uses `--nomigrations` for speed.
- Minimum coverage threshold is 90% (enforced by `--cov-fail-under=90`). Adding code without tests must not drop coverage; if it does, add missing tests instead of lowering the threshold.
- Test structure: each implementation module has a sibling `tests/` folder (e.g. `account/services/tests/test_registration_service.py`). Follow this for new elements (serializers, services, views, utils). Do not add tests to a global root folder.
- File naming: `test_<name>_<type>.py` or `test_<function>.py`. Test classes end with suffix `Tests` (e.g. `RegistrationServiceTests`).
- Categories: (1) Unit – service layer, serializers, exceptions; (2) API/integration – DRF views with `APIRequestFactory` or `APITestCase`. In view tests assert status, payload and side-effects (e.g. user persisted). Avoid end-to-end tests except critical flows.
- Use `pytest.raises` for asserting domain & validation exceptions. Within `django.test.TestCase`/`APITestCase` classes plain `assert` is acceptable (pytest compatible).
- Arrange-Act-Assert: build helper `_build_command()` methods for repeated payloads – improves readability & reuse.
- Serializer tests must not write to DB – limit to data validation and `to_command()` conversion.
- Mocking: use `unittest.mock.patch` / `monkeypatch` selectively to isolate costly dependencies (e.g. external services). Do not mock the ORM where in‑memory test DB suffices.
- Every error scenario (uniqueness conflict, validation failure, whitespace in username, etc.) requires a dedicated clearly named test.
- When introducing new domain exceptions immediately add a test for its HTTP mapping in the view.
- Do not skip tests without a justification comment and planned fix.
- Before push: (1) `./bin/lint_backend.sh` (2) `./bin/test_backend.sh` – both must exit 0. In PR describe new scenarios under "Test coverage".
- After adding any new code changes, always run the backend linter using the command `./bin/lint_backend.sh` as specified in the README.md to ensure adherence to coding standards.
- Ensure that after code updates, the full backend test suite is executed via `./bin/test_backend.sh` to maintain quality and test coverage (minimum 90%).

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
- Use the Cypress Dashboard for CI integration and test analytics
- Leverage visual testing for UI regression testing

## FRONTEND

### Guidelines for VUE

#### VUE_CODING_STANDARDS

- Use the Composition API instead of the Options API for better type inference and code reuse
- Implement <script setup> for more concise component definitions
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

## CODING_PRACTICES

### Guidelines for VERSION_CONTROL

#### GIT

- Use conventional commits to create meaningful commit messages
- Use feature branches with descriptive names following BV-1234
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
