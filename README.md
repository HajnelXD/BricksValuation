# BricksValuation

## Development scripts

- **Initialise stack**: `bin/dev_init.sh` copies the backend env file, builds the Docker images, and starts the containers.
- **Clean up**: `bin/dev_clear.sh` stops and removes the project's containers, images, volumes, and deletes `env/.backend-env`.

## Linter
To run the backend linter, use the following command:

```bash
./bin/lint_backend.sh
```

To run the frontend linter, use the following command:

```bash
./bin/lint_frontend.sh
```

## Backend Tests

To run the backend tests, execute:

```bash
./bin/test_backend.sh
```
