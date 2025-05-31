# IssarVideos

FastAPI application for managing video narratives with Excel database backend.

## Features

- 🎥 Video narrative management with Excel storage
- 🔄 CRUD operations via REST API
- 🏷️ Tagging system with result tracking (`Tagger_1_Result`, `Tagger_2_Result`)
- 🧪 Comprehensive testing suite with safe database handling
- 📊 Web interface for data visualization

## Quick Start

### Running the Application

```bash
# Install dependencies
poetry install

# Start the server
python3 main.py
```

The API will be available at `http://localhost:8000`

### 🚀 Safe Testing System

```bash
# Run comprehensive test suite (RECOMMENDED)
python3 tests/run_tests.py --type comprehensive --no-prompt
```

**🛡️ Production Database Protection:**

- All tests use isolated temporary copies of your Excel database
- Original database is NEVER modified during testing
- Each test gets a fresh copy with automatic cleanup
- Tests start their own isolated servers

### Testing Options

```bash
# Comprehensive suite with isolated servers (RECOMMENDED)
python3 tests/run_tests.py --type comprehensive --no-prompt

# Database tests only (safe, isolated)
python3 tests/run_tests.py --type db

# API tests only (with isolated server)
python3 tests/run_tests.py --type api --no-prompt

# All tests separately (legacy mode)
python3 tests/run_tests.py --type all
```

# Using pytest

pytest # All tests
pytest tests/test_db.py # Database only
pytest -v # Verbose output

```

## API Endpoints

- `GET /random-narrative` - Get random untagged record
- `POST /add-record` - Add new video record
- `PUT /update-record/{link}` - Update existing record
- `GET /all-records` - Get all records
- `GET /records-by-sheet/{sheet_name}` - Get records by sheet

## Database Schema

Updated schema includes new result tracking fields:

- `Tagger_1_Result` - Integer result from first tagger
- `Tagger_2_Result` - Integer result from second tagger

## Testing

- ✅ **Safe Testing**: All tests use temporary database copies
- ✅ **Comprehensive Coverage**: Database operations, API endpoints, error handling
- ✅ **Auto Cleanup**: Temporary files automatically removed
- ✅ **Multiple Options**: Unified runner, pytest, or direct execution

See `tests/README.md` for detailed testing documentation.
```
