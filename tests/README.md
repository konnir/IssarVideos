# Video Narratives - Test Suite

This directory contains the comprehensive test suite for the Video Narratives FastAPI application.

## Quick Start

Run all tests from the project root:

```bash
# Comprehensive test suite (recommended)
python run_tests.py

# Or run directly
python tests/test_runner.py
```

## Test Structure

### Core Test Files

- `test_runner.py` - **Main comprehensive test runner** with isolated database testing
- `test_api.py` - API integration tests for all FastAPI endpoints
- `test_db.py` - Unit tests for the NarrativesDB class
- `test_protection.py` - Production database protection tests
- `conftest.py` - Test configuration and utilities (DBTestManager)

### Legacy/Compatibility

- `run_tests.py` - Legacy test runner (redirects to test_runner.py)

### Test Organization

- `debug/` - Debug and development test files
- `html_tests/` - HTML/UI test files and validation
- `integration/` - Integration test demos and utilities

## Test Types

### 1. Comprehensive Test Suite (Default)

```bash
python tests/test_runner.py
# or
python run_tests.py
```

Runs all tests in the correct order with full isolation and cleanup.

### 2. Individual Test Types

```bash
# Database unit tests only
python tests/test_runner.py --type db

# API integration tests only
python tests/test_runner.py --type api

# UI/HTML validation tests only
python tests/test_runner.py --type ui

# Production protection tests only
python tests/test_runner.py --type protection

# All tests individually
python tests/test_runner.py --type all
```

### 3. Non-Interactive Mode

```bash
python tests/test_runner.py --no-prompt
```

## Features

### ✅ Safe Database Testing

- **Automatic DB Copy**: Tests use temporary copies of the production database
- **Automatic Cleanup**: Test databases are automatically deleted after completion
- **Production Protection**: Original database is never modified during tests
- **Environment Validation**: Prevents accidental production database usage

### ✅ Comprehensive Coverage

- **Database Operations**: CRUD operations, queries, validation
- **API Endpoints**: All REST endpoints with proper error handling
- **UI Components**: HTML file validation and structure checks
- **Integration Flows**: End-to-end testing with isolated test server

### ✅ Production Protection

- Database path validation
- Environment variable checks
- Safe test isolation
- Automatic cleanup on failures

## Test Results

The test runner provides detailed results:

- ✅ **SUCCESS**: Test passed
- ❌ **ERROR**: Test failed
- ⚠️ **WARNING**: Non-critical issue
- 🧪 **TEST**: Test running
- ℹ️ **INFO**: Information message

## Development

### Adding New Tests

1. Add test functions to appropriate test files
2. Follow the existing naming convention (`test_*`)
3. Use the logging methods for consistent output
4. Ensure proper cleanup and isolation

### Test Database Management

The `DBTestManager` in `conftest.py` provides:

- Temporary database creation
- Automatic cleanup
- Safe isolation from production data

### Best Practices

- Always use the test runner for comprehensive testing
- Test individual components during development
- Verify production protection before deploying
- Keep test data separate from production data

## Troubleshooting

### Common Issues

1. **"Production database protection failed"**

   - Ensure `NARRATIVES_DB_PATH` points to a test database
   - Use paths containing "test" or "temp"

2. **"Test server not accessible"**

   - Check if port 8000 is available
   - Ensure no other instances are running

3. **Import errors**
   - Run tests from the project root directory
   - Ensure all dependencies are installed

### Getting Help

- Check test output for specific error messages
- Verify your environment setup
- Run individual test types to isolate issues
