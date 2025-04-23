# Endpoint guidelines

- Create a centralized function for accessing data
- Endpoints are created in Flask using blueprints
- All endpoints require tests
- Tests must use mock objects rather than real database calls
- Use dictionaries rather than classes for the mocked data
- Use the `unittest` module for testing
- All tests must pass
- The Python virtual environment is located in the root of the project in a **venv** folder

## Prototype files

- [Endpoint blueprint](../../server/routes/games.py)
- [Tests blueprint](../../server/tests/test_games.py)