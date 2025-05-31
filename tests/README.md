# Tests Directory

This directory contains comprehensive tests for the Video Narratives API project.

## Test Structure

- `conftest.py` - Test configuration and utilities including the TestDBManager for safe database testing
- `test_db.py` - Unit tests for the NarrativesDB class
- `test_api.py` - Integration tests for the FastAPI endpoints (includes both integration and standalone test styles)
- `run_tests.py` - Main test runner script with multiple options
- `pytest.ini` - Pytest configuration for easy test execution

## Features

### Safe Database Testing

- **Automatic DB Copy**: Tests use a temporary copy of the production database
- **Automatic Cleanup**: Test databases are automatically deleted after tests complete
- **No Production Impact**: Original database is never modified during tests

### Test Coverage

- Database operations (add, update, query)
- API endpoints (GET, POST, PUT)
- Error handling (duplicate records, non-existent records)
- Data validation and serialization
- Comprehensive API flow testing

## Running Tests

### 🚀 One Command - Run All Tests (Recommended)

```bash
python3 tests/run_tests.py
```

This will:

1. Run all database unit tests
2. Prompt you to start the server
3. Run all API integration tests
4. Show comprehensive test summary

### Quick Test Options

```bash
# Run only database tests (no server needed)
python3 tests/run_tests.py --type db

# Run only API tests (server must be running)
python3 tests/run_tests.py --type api

# Run all tests without prompts (assumes server is already running)
python3 tests/run_tests.py --no-prompt
```

### Using Pytest (Alternative)

```bash
# Run all tests with pytest
pytest

# Run only database tests
pytest tests/test_db.py

# Run only API tests (server must be running)
pytest tests/test_api.py
```

### Run Individual Test Files

```bash
# Database tests only
python3 tests/test_db.py

# API tests only (requires server)
python3 tests/test_api.py
```

## Test Database Management

The `TestDBManager` context manager handles all database operations safely:

```python
from tests.conftest import TestDBManager

# Automatic setup and cleanup
with TestDBManager() as test_db_path:
    db = NarrativesDB(test_db_path)
    # ... run tests ...
# Database automatically cleaned up here
```

## Expected Output

Successful test runs will show:

- ✅ Individual test results
- 📁 Database copy creation messages
- 🗑️ Cleanup confirmation messages
- 🎉 Final success summary

Failed tests will show:

- ❌ Error messages with details
- Stack traces for debugging
- Clear indication of which tests failed
