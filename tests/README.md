# Video Narratives - Test Suite

This directory contains the comprehensive test suite for the Video Narratives FastAPI application with Google Sheets integration.

## Quick Start

Run all tests from the project root:

```bash
# Comprehensive test suite (recommended)
python tests/run_all_tests.py

# Or run from tests directory
cd tests
python run_all_tests.py
```

## Test Coverage

The test suite now includes comprehensive coverage for:

- **Google Sheets Integration**: Connection validation, data operations, and environment configuration
- **API Endpoints**: All 21 FastAPI endpoints including the new `/refresh-data` endpoint
- **Authentication**: User login and authorization flows
- **Database Operations**: CRUD operations with Google Sheets backend
- **UI Components**: HTML, CSS, and JavaScript functionality
- **Data Models**: Video record and story generation models
- **Environment Loading**: `.env` file handling and OpenAI client configuration

## Test Structure

The test suite is organized into three main categories:

### Directory Structure

```
tests/
├── unittest/           # Component unit tests
│   ├── test_story_generation.py  # Story generation component tests
│   ├── test_data_models.py       # Data model tests
│   └── test_custom_prompt.py     # Custom prompt functionality tests
├── integration/        # API integration tests
│   ├── test_api_endpoints.py        # Core FastAPI endpoint tests
│   ├── test_story_generation.py     # Story generation API tests
│   ├── test_comprehensive_api.py    # Comprehensive API tests
│   ├── test_custom_prompt_api.py    # Custom prompt API tests
│   ├── test_authentication.py       # Authentication flow tests
│   └── test_google_sheets_integration.py  # Google Sheets integration tests
├── ui/                # UI validation tests
│   ├── test_ui_validation.py      # HTML/UI component tests
│   ├── test_javascript_functionality.py  # JavaScript tests
│   └── test_edit_prompt_functionality.py # UI prompt editing tests
├── run_all_tests.py   # Unified test runner
├── conftest.py        # Test configuration and fixtures
└── README.md          # This file
```

### Core Files

- `run_all_tests.py` - **Main unified test runner** with comprehensive test execution
- `conftest.py` - Test configuration and Google Sheets fixtures

## Test Categories

### 1. Unit Tests (`unittest/`)

**Story generation component tests** (`test_story_generation.py`):

- OpenAI client wrapper functionality
- Story generator class methods
- Error handling and validation
- Prompt construction and response parsing

**Data model tests** (`test_data_models.py`):

- Pydantic model validation
- Request/response model structure
- Field validation and constraints

**Custom prompt tests** (`test_custom_prompt.py`):

- Custom prompt functionality
- Prompt template validation
- Custom story generation flows

### 2. Integration Tests (`integration/`)

**Core API endpoint tests** (`test_api_endpoints.py`):

- Health check endpoint
- Main application endpoints
- Static file serving
- HTTP method validation

**Story generation API tests** (`test_story_generation.py`):

- Story generation endpoints (`/generate-story`, `/generate-story-variants`, `/refine-story`)
- OpenAI connection testing (`/test-openai-connection`)
- Request validation and error handling
- Mock testing for API responses
- End-to-end story generation workflow

**Comprehensive API tests** (`test_comprehensive_api.py`):

- Full workflow testing
- Cross-feature integration
- Performance and reliability tests

**Custom prompt API tests** (`test_custom_prompt_api.py`):

- Custom prompt API endpoints
- Custom story generation workflows
- Request validation and error handling

**Authentication tests** (`test_authentication.py`):

- User authentication flows
- Authorization validation
- Security testing

**Google Sheets integration tests** (`test_google_sheets_integration.py`):

- Google Sheets API connectivity
- Data synchronization testing
- Environment configuration validation

### 3. UI Tests (`ui/`)

**HTML/UI validation tests** (`test_ui_validation.py`):

- All REST endpoints
- Request/response validation
- Error handling
- Authentication flows

**JavaScript functionality tests** (`test_javascript_functionality.py`):

- Interactive UI components
- Client-side validation
- Dynamic content updates

**Edit prompt functionality tests** (`test_edit_prompt_functionality.py`):

- Prompt editing interface
- Real-time prompt validation
- UI feedback mechanisms

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
python -m pytest tests/unittest/test_story_generation.py -v

# Custom prompt unit tests
python -m pytest tests/unittest/test_custom_prompt.py -v

# API integration tests
python -m pytest tests/integration/test_api_endpoints.py -v

# Story generation unit tests
python -m pytest tests/unittest/test_story_generation.py -v

# Story generation API tests (requires OpenAI API key for full testing)
python -m pytest tests/integration/test_story_generation.py -v

# Google Sheets integration tests
python -m pytest tests/integration/test_google_sheets_integration.py -v

# Custom prompt API tests
python -m pytest tests/integration/test_custom_prompt_api.py -v

# Authentication tests
python -m pytest tests/integration/test_authentication.py -v

# UI validation tests
python -m pytest tests/ui/test_ui_validation.py -v

# JavaScript functionality tests
python -m pytest tests/ui/test_javascript_functionality.py -v

# Edit prompt functionality tests
python -m pytest tests/ui/test_edit_prompt_functionality.py -v
```

### 4. Non-Interactive Mode

```bash
python tests/run_all_tests.py --no-prompt
```

## Features

## Features

### ✅ Google Sheets Integration Testing

- **API Connectivity**: Tests Google Sheets API connection and authentication
- **Data Synchronization**: Validates data read/write operations with Google Sheets
- **Environment Configuration**: Ensures proper setup of Google Sheets credentials and configuration
- **Real-time Updates**: Tests the `/refresh-data` endpoint and data synchronization

### ✅ Comprehensive Coverage

- **Story Generation**: CRUD operations, AI integration, custom prompts
- **API Endpoints**: All REST endpoints with proper error handling
- **UI Components**: HTML file validation and interactive functionality
- **Integration Flows**: End-to-end testing with isolated test server

### ✅ Production Protection

- Environment variable validation
- Google Sheets credentials verification
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

1. **Unit Tests**: Add to `tests/unittest/` for component testing (story generation, data models, custom prompts)
2. **Integration Tests**: Add to `tests/integration/` for API endpoint testing (including Google Sheets integration)
3. **UI Tests**: Add to `tests/ui/` for frontend validation
4. Follow the existing naming convention (`test_*`)
5. Use the logging methods for consistent output
6. Ensure proper cleanup and isolation

### Google Sheets Test Configuration

The test fixtures in `conftest.py` provide:

- Google Sheets API connectivity testing
- Environment variable validation
- Mock data for testing scenarios
- Safe isolation from production Google Sheets

### Best Practices

- Always use the unified test runner for comprehensive testing
- Test individual components during development
- Verify Google Sheets connectivity before deploying
- Keep test data separate from production Google Sheets
- Test both authenticated and unauthenticated scenarios

## Troubleshooting

### Common Issues

1. **"Google Sheets API connection failed"**

   - Verify `GOOGLE_SHEETS_CREDENTIALS_PATH` points to a valid service account JSON file
   - Ensure `GOOGLE_SHEETS_ID` is set to a valid Google Sheet ID
   - Check that the service account has access to the specified Google Sheet

2. **"Test server not accessible"**

   - Check if port 8000 is available
   - Ensure no other instances are running

3. **Import errors**

   - Run tests from the project root directory
   - Ensure all dependencies are installed

4. **Environment configuration errors**
   - Verify Google Sheets credentials are properly configured
   - Check that all required environment variables are set
   - Ensure the Google Sheet has the correct structure and permissions

### Getting Help

- Check test output for specific error messages
- Verify your environment setup
- Run individual test categories to isolate issues
- Review the unified test runner logs for detailed execution flow
