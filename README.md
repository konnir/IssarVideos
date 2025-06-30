# Video Narratives Application

A comprehensive FastAPI-based platform for managing video narratives with Google Sheets integration and AI-powered story generation capabilities for content creators.

## 🚀 Features

### Core Functionality

- **Google Sheets Integration**: Store and manage video narratives directly in Google Sheets
- **Real-time Data Sync**: Refresh data from Google Sheets with manual edits
- **User Management**: Track users and their contributions to the narrative database
- **Tagging System**: Collaborative tagging system for narrative classification
- **Leaderboard**: Track top contributors and user statistics
- **Report Dashboard**: View comprehensive statistics and data insights

### 🤖 AI-Powered Story Generation

- **Story Generation**: Generate compelling 2-3 sentence story concepts from narrative inputs
- **Story Variants**: Create multiple story variations for the same narrative
- **Story Refinement**: Improve existing stories based on specific feedback
- **Custom Prompts**: Use custom prompts for specialized story generation
- **Multiple Styles**: Support for various storytelling styles (dramatic, suspenseful, comedic, etc.)
- **OpenAI Integration**: Powered by GPT-4 for high-quality story generation

## 📋 Prerequisites

- Python 3.8+
- Poetry (for dependency management)
- Google Cloud Project with Sheets API enabled
- Service Account with Google Sheets access
- OpenAI API Key (for story generation features)

## 🛠️ Installation

1. **Clone the repository**:

```bash
git clone <repository-url>
cd IssarVideos
```

2. **Install dependencies using Poetry**:

```bash
poetry install
```

3. **Set up Google Sheets Integration**:

   a. Create a Google Cloud Project and enable the Google Sheets API
   b. Create a Service Account and download the JSON credentials file
   c. Share your Google Sheet with the service account email
   d. Set the environment variables:

   ```bash
   export GOOGLE_SHEETS_CREDENTIALS_PATH="/path/to/your/credentials.json"
   export GOOGLE_SHEETS_ID="your_google_sheet_id"
   ```

4. **Set up OpenAI API Key**:

   You have multiple options to configure your OpenAI API key:

   **Option 1: Environment Variable (Traditional)**

   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

   **Option 2: .env File in Project Root**

   ```bash
   # Create .env file in project root
   echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
   ```

   **Option 3: .env File in clients Folder**

   ```bash
   # Create .env file in clients folder (takes priority)
   echo "OPENAI_API_KEY=your-openai-api-key-here" > clients/.env
   ```

   > **Note**: The OpenAI client automatically looks for `.env` files in this order:
   >
   > 1. `clients/.env` (highest priority)
   > 2. Project root `.env` (fallback)
   > 3. System environment variables (fallback)

   You can use the provided example file:

   ```bash
   cp clients/.env.example clients/.env
   # Edit the file and add your actual API key
   ```

5. **Activate the virtual environment**:

```bash
poetry shell
```

## 🚀 Running the Application

### Development Server

```bash
# Start the FastAPI development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc

### Production Deployment

```bash
# Using uvicorn with multiple workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Or using the provided deployment script
./deploy.sh
```

## 📚 API Documentation

### Core Endpoints

#### Health & Status

- `GET /health` - Application health check
- `GET /test-openai-connection` - Test OpenAI API connectivity

#### Narrative Management

- `GET /random-narrative` - Get a random narrative for tagging
- `POST /add-record` - Add a new video record
- `POST /add-narrative` - Add a new narrative
- `GET /all-records` - Get all video records
- `GET /records-by-sheet/{sheet_name}` - Get records from specific sheet

#### User Management

- `GET /random-narrative-for-user/{username}` - Get personalized random narrative
- `GET /user-tagged-count/{username}` - Get user's tagging statistics
- `GET /leaderboard` - Get user leaderboard

#### Tagging System

- `POST /tag-record` - Tag a narrative record
- `GET /tagged-records` - Get all tagged records
- `POST /auth-report` - Submit authentication report

### 🤖 Story Generation Endpoints

#### Generate Stories

```bash
# Generate a single story
POST /generate-story
{
    "narrative": "A mysterious package arrives at someone's door",
    "style": "suspenseful",
    "additional_context": "Focus on family secrets"
}

# Generate multiple story variants
POST /generate-story-variants
{
    "narrative": "A mysterious package arrives at someone's door",
    "count": 3,
    "style": "varied"
}

# Refine an existing story
POST /refine-story
{
    "current_story": "A simple story about finding something.",
    "feedback": "Make it more mysterious and add character development",
    "style": "thriller"
}
```

#### Response Format

```json
{
  "story": "When Sarah finds an old family photo in a mysterious package, she discovers her grandmother had a secret twin sister. The photo leads her to uncover decades of family mysteries and hidden letters that change everything she thought she knew about her heritage.",
  "word_count": 42
}
```

## 🧪 Testing

The application includes a comprehensive test suite covering Google Sheets integration, API endpoints, UI components, and AI functionality.

### Quick Start

Run all tests from the project root:

```bash
# Comprehensive test suite (recommended)
python tests/run_all_tests.py

# With verbose output
python tests/run_all_tests.py --verbose
```

### Test Categories

The test suite is organized into three main categories:

#### Unit Tests

Tests for individual components and database functionality:

```bash
python tests/run_all_tests.py --type unit
```

- **Google Sheets Integration**: SheetsClient and SheetsNarrativesDB functionality
- **Data Models**: Pydantic model validation and serialization
- **Story Generation**: AI-powered story creation components
- **Custom Prompts**: Custom prompt handling and validation

#### Integration Tests

Tests for API endpoints and system integration:

```bash
python tests/run_all_tests.py --type integration
```

- **All 21 API Endpoints**: Comprehensive endpoint testing including `/refresh-data`
- **Authentication**: User login and authorization flows
- **Google Sheets Operations**: Data synchronization and refresh functionality
- **Story Generation APIs**: AI story creation endpoints
- **Error Handling**: Proper error responses and edge cases

#### UI Tests

Tests for frontend components and validation:

```bash
python tests/run_all_tests.py --type ui
```

- **HTML Structure**: Page validation and element testing
- **JavaScript Functionality**: UI interactions and AJAX calls
- **CSS Validation**: Style consistency and responsive design
- **Form Validation**: Input handling and user interactions

### Specific Test Commands

```bash
# Test Google Sheets integration specifically
python -m pytest tests/integration/test_google_sheets_integration.py -v

# Test story generation functionality
python -m pytest tests/unittest/test_story_generation.py -v
python -m pytest tests/integration/test_story_generation.py -v

# Test custom prompt functionality
python -m pytest tests/unittest/test_custom_prompt.py -v
python -m pytest tests/integration/test_custom_prompt_api.py -v

# Test comprehensive API coverage
python -m pytest tests/integration/test_comprehensive_api.py -v
```

### Test Coverage

The test suite provides comprehensive coverage for:

- ✅ **Google Sheets Integration**: Connection validation, data operations, environment setup
- ✅ **All API Endpoints**: Complete coverage of all 21 FastAPI endpoints
- ✅ **Authentication**: User login and authorization flows
- ✅ **Database Operations**: CRUD operations with Google Sheets backend
- ✅ **UI Components**: HTML, CSS, and JavaScript functionality
- ✅ **Data Models**: Video record and story generation models
- ✅ **Environment Loading**: `.env` file handling and OpenAI client configuration
- ✅ **Story Generation**: AI-powered story creation and refinement
- ✅ **Error Handling**: Comprehensive error scenarios and edge cases

### Environment Setup for Testing

Some integration tests require Google Sheets credentials:

```bash
export GOOGLE_SHEETS_CREDENTIALS_PATH="/path/to/credentials.json"
export GOOGLE_SHEETS_ID="your_sheet_id"
```

Tests will automatically skip Google Sheets functionality if credentials are not configured.

### Test Structure

```
tests/
├── conftest.py                 # Test configuration and fixtures
├── run_all_tests.py           # Comprehensive test runner
├── integration/               # API and system integration tests
│   ├── test_comprehensive_api.py    # All endpoint coverage
│   ├── test_google_sheets_integration.py  # Google Sheets specific tests
│   ├── test_authentication.py       # Auth and security tests
│   ├── test_story_generation.py     # Story generation API tests
│   └── test_custom_prompt_api.py    # Custom prompt API tests
├── unittest/                  # Component unit tests
│   ├── test_story_generation.py     # Story generation logic tests
│   ├── test_custom_prompt.py        # Custom prompt handling tests
│   └── test_data_models.py         # Pydantic model tests
└── ui/                       # Frontend validation tests
    ├── test_ui_validation.py        # HTML/CSS validation
    ├── test_javascript_functionality.py  # JS functionality tests
    └── test_edit_prompt_functionality.py # Prompt editing UI tests
```

## 📁 Project Structure

```
IssarVideos/
├── clients/                    # External API clients
│   └── openai_client.py       # OpenAI API wrapper
├── data/                       # Data models and schemas
│   └── video_record.py        # Pydantic models for API
├── db/                         # Database utilities
│   └── sheets_narratives_db.py # Google Sheets operations
├── llm/                        # AI/LLM functionality
│   └── get_story.py           # Story generation logic
├── static/                     # Static web assets
├── tests/                      # Comprehensive test suite
│   ├── unittest/              # Unit tests
│   ├── integration/           # API integration tests
│   └── ui/                    # UI validation tests
├── main.py                     # FastAPI application
├── pyproject.toml             # Poetry configuration
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

| Variable                         | Description                         | Default | Required |
| -------------------------------- | ----------------------------------- | ------- | -------- |
| `OPENAI_API_KEY`                 | OpenAI API key for story generation | None    | No\*     |
| `GOOGLE_SHEETS_CREDENTIALS_PATH` | Path to Google service account JSON | None    | Yes      |
| `GOOGLE_SHEETS_ID`               | Google Sheet ID for data storage    | None    | Yes      |
| `PORT`                           | Server port                         | `8000`  | No       |

\*Required for story generation functionality to work

### Story Generation Styles

The application supports various storytelling styles:

- `dramatic` - Emotional and character-driven narratives
- `suspenseful` - Mystery and thriller elements
- `comedic` - Light-hearted and humorous approaches
- `romantic` - Love and relationship-focused stories
- `action` - Fast-paced, adventure-oriented narratives
- `horror` - Dark and scary themes
- `documentary` - Factual and informative style
- `engaging` - General audience appeal (default)

## 🚀 Usage Examples

### Story Generation Workflow

1. **Test OpenAI Connection**:

```bash
curl http://localhost:8000/test-openai-connection
```

2. **Generate a Story**:

```bash
curl -X POST "http://localhost:8000/generate-story" \
     -H "Content-Type: application/json" \
     -d '{
       "narrative": "A time traveler gets stuck in the wrong era",
       "style": "dramatic",
       "additional_context": "Focus on the emotional impact of being displaced"
     }'
```

3. **Get Multiple Variants**:

```bash
curl -X POST "http://localhost:8000/generate-story-variants" \
     -H "Content-Type: application/json" \
     -d '{
       "narrative": "A time traveler gets stuck in the wrong era",
       "count": 3,
       "style": "varied"
     }'
```

4. **Refine a Story**:

```bash
curl -X POST "http://localhost:8000/refine-story" \
     -H "Content-Type: application/json" \
     -d '{
       "current_story": "A time traveler gets lost in time.",
       "feedback": "Add more emotional depth and specific time period details",
       "style": "dramatic"
     }'
```

### Python Integration

```python
from llm.get_story import StoryGenerator

# Initialize the story generator
generator = StoryGenerator()

# Generate a story
story = generator.get_story(
    narrative="A mysterious old book appears in a library",
    style="suspenseful",
    additional_context="The book contains secrets about the town's history"
)

# Generate multiple variants
variants = generator.get_story_variants(
    narrative="A mysterious old book appears in a library",
    count=3,
    style="varied"
)

# Refine an existing story
refined = generator.refine_story(
    current_story="Someone finds an old book with secrets.",
    feedback="Make it more suspenseful and add character motivation",
    style="thriller"
)
```

## 📖 Additional Documentation

- **[Testing Documentation](tests/README.md)** - Comprehensive testing guide
- **[API Documentation](http://localhost:8000/docs)** - Interactive API documentation (when server is running)

## 🛡️ Security

- Environment-based configuration
- Safe database operations with automatic backups
- Input validation and sanitization
- Secure API key management
- Production database protection in tests

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API errors**:

   - Verify your API key is set correctly
   - Check your OpenAI account has sufficient credits
   - Test the connection with `/test-openai-connection`

2. **Google Sheets issues**:

   - Verify your service account has access to the Google Sheet
   - Check that the Google Sheets API is enabled in your Google Cloud project
   - Ensure the sheet ID is correct and the sheet exists
   - Test the connection with the Google Sheets integration endpoints

3. **Import errors**:

   - Make sure you're running from the project root
   - Activate the Poetry virtual environment
   - Install dependencies with `poetry install`

4. **Server not starting**:
   - Check if port 8000 is available
   - Verify all dependencies are installed
   - Check for any configuration errors

### Getting Help

- Check the application logs for detailed error messages
- Review the test suite output for systematic issues
- Consult the API documentation at `/docs`
- Verify your environment configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the test suite (`python tests/run_all_tests.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- Powered by [OpenAI GPT-4](https://openai.com/) for story generation
- Uses [Poetry](https://python-poetry.org/) for dependency management
- Tested with [pytest](https://pytest.org/) for comprehensive testing
