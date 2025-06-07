# Video Narratives - Test Suite

This directory contains the comprehensive test suite for the Video Narratives FastAPI application.

## Quick Start

Run all tests from the project root:

```bash
# Comprehensive test suite (recommended)
python tests/run_all_tests.py

# Or run from tests directory
cd tests
python run_all_tests.py
```

## Test Structure

The test suite is organized into three main categories:

### Directory Structure

```
tests/
├── unittest/           # Database unit tests
│   └── test_db.py     # NarrativesDB class unit tests
├── integration/        # API integration tests
│   └── test_api_endpoints.py  # FastAPI endpoint tests
├── ui/                # UI validation tests
│   └── test_ui_validation.py  # HTML/UI component tests
├── run_all_tests.py   # Unified test runner
├── conftest.py        # Test configuration and utilities
└── README.md          # This file
```

### Core Files

- `run_all_tests.py` - **Main unified test runner** with comprehensive test execution
- `conftest.py` - Test configuration and utilities (DBTestManager for safe database testing)

## Test Categories

### 1. Unit Tests (`unittest/`)

Database layer tests focusing on the NarrativesDB class:

- CRUD operations
- Query methods
- Data validation
- Empty/null value handling

### 2. Integration Tests (`integration/`)

API endpoint tests for the FastAPI application:

- All REST endpoints
- Request/response validation
- Error handling
- Authentication flows

### 3. UI Tests (`ui/`)

User interface validation tests:

- HTML structure validation
- CSS styling checks
- JavaScript functionality
- Form validation

## Running Tests

### 1. All Tests (Recommended)

```bash
python tests/run_all_tests.py
```

### 2. Individual Test Categories

```bash
# Unit tests only
python tests/run_all_tests.py --type unittest

# Integration tests only
python tests/run_all_tests.py --type integration

# UI tests only
python tests/run_all_tests.py --type ui
```

### 3. Specific Test Files

```bash
# Database unit tests
python -m pytest tests/unittest/test_db.py -v

# API integration tests
python -m pytest tests/integration/test_api_endpoints.py -v

# UI validation tests
python -m pytest tests/ui/test_ui_validation.py -v
```

### 4. Non-Interactive Mode

```bash
python tests/run_all_tests.py --no-prompt
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

### ✅ New Data Structure Support

- **Empty Value Handling**: Tests validate empty/null values instead of "Init"
- **Story Field**: Tests include the new Story field validation
- **Updated Tagging**: Tests validate 1-4 tag values (removed 0/"Init")

## Test Results

The test runner provides detailed results:

- ✅ **SUCCESS**: Test passed
- ❌ **ERROR**: Test failed
- ⚠️ **WARNING**: Non-critical issue
- 🧪 **TEST**: Test running
- ℹ️ **INFO**: Information message

## Development

### Adding New Tests

1. **Unit Tests**: Add to `tests/unittest/` for database layer testing
2. **Integration Tests**: Add to `tests/integration/` for API endpoint testing
3. **UI Tests**: Add to `tests/ui/` for frontend validation
4. Follow the existing naming convention (`test_*`)
5. Use the logging methods for consistent output
6. Ensure proper cleanup and isolation

### Test Database Management

The `DBTestManager` in `conftest.py` provides:

- Temporary database creation
- Automatic cleanup
- Safe isolation from production data
- Support for new data structure (empty Tagger_1, Story field)

### Best Practices

- Always use the unified test runner for comprehensive testing
- Test individual components during development
- Verify production protection before deploying
- Keep test data separate from production data
- Test both empty and populated field values

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

4. **Data validation errors**
   - Verify test data matches new structure (no Platform, Hebrew_Title, Length, Title fields)
   - Check that Story field is properly handled as optional
   - Ensure Tagger_1 empty values are correctly processed

### Getting Help

- Check test output for specific error messages
- Verify your environment setup
- Run individual test categories to isolate issues
- Review the unified test runner logs for detailed execution flow
