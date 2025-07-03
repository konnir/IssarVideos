# Video Narratives Platform

A comprehensive FastAPI-based platform for managing video narratives with Google Sheets integration, AI-powered story generation, and YouTube search query optimization for content creators.

## 🚀 Features

### Core Functionality

- **Google Sheets Integration**: Store and manage video narratives directly in Google Sheets
- **Real-time Data Sync**: Refresh data from Google Sheets after manual edits
- **User Management**: Track users and their contributions to the narrative database
- **Tagging System**: Collaborative tagging system for narrative classification
- **Leaderboard**: Track top contributors and user statistics
- **Report Dashboard**: View comprehensive statistics and data insights

### 🤖 AI-Powered Content Generation

- **Story Generation**: Generate compelling 2-3 sentence story concepts from narrative inputs
- **Story Variants**: Create multiple story variations for the same narrative
- **Story Refinement**: Improve existing stories based on specific feedback
- **Custom Prompts**: Use custom prompts for specialized story generation
- **YouTube Search Optimization**: Generate optimal YouTube search queries from stories
- **Multiple Styles**: Support for various storytelling styles (dramatic, suspenseful, comedic, etc.)
- **OpenAI Integration**: Powered by GPT-4 for high-quality content generation

## 📋 Prerequisites

- Python 3.8+
- Poetry (for dependency management)
- Google Cloud Project with Sheets API enabled
- Service Account with Google Sheets access
- OpenAI API Key (for AI-powered features)

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

   - Create a Google Cloud Project and enable the Google Sheets API
   - Create a Service Account and download the JSON credentials file
   - Share your Google Sheet with the service account email
   - Set the environment variables:

   ```bash
   export GOOGLE_SHEETS_CREDENTIALS_PATH="/path/to/your/credentials.json"
   export GOOGLE_SHEETS_ID="your_google_sheet_id"
   ```

4. **Set up OpenAI API Key**:
   Create a `.env` file in the project root:

   ```bash
   echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
   ```

5. **Activate the virtual environment**:

```bash
poetry shell
```

## 🚀 Running the Application

### Development Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc

### Production Deployment

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
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

### 🤖 AI-Powered Content Generation

#### Story Generation

**Generate a Single Story**

```bash
POST /generate-story
{
    "narrative": "A mysterious package arrives at someone's door",
    "style": "suspenseful",
    "additional_context": "Focus on family secrets"
}
```

**Generate Multiple Story Variants**

```bash
POST /generate-story-variants
{
    "narrative": "A mysterious package arrives at someone's door",
    "count": 3,
    "style": "varied"
}
```

**Refine an Existing Story**

```bash
POST /refine-story
{
    "original_story": "A simple story about finding something.",
    "refinement_request": "Make it more mysterious and add character development",
    "narrative": "Original narrative context"
}
```

**Custom Prompt Story Generation**

```bash
POST /generate-story-custom-prompt
{
    "narrative": "A mysterious package arrives",
    "custom_prompt": "Create a thriller story focused on psychological suspense",
    "style": "thriller"
}
```

#### YouTube Search Query Generation

**Generate Optimized YouTube Search Query**

```bash
POST /generate-video-keywords
{
    "story": "When Sarah finds an old family photo, she discovers her grandmother had a secret twin sister.",
    "max_keywords": 5
}
```

**Response Format**

```json
{
  "search_query": "family secret discovery"
}
```

The system generates a single, optimized YouTube search query (typically 2-6 words) that is most likely to find relevant videos for your story.

#### Response Formats

**Story Generation Response**

```json
{
  "story": "When Sarah finds an old family photo in a mysterious package, she discovers her grandmother had a secret twin sister. The photo leads her to uncover decades of family mysteries and hidden letters that change everything she thought she knew about her heritage.",
  "word_count": 42
}
```

## 🧪 Testing

The application includes a comprehensive test suite covering all functionality.

### Run All Tests

```bash
python tests/run_all_tests.py
```

### Test Categories

#### Unit Tests

```bash
python tests/run_all_tests.py --type unit
```

- Data models validation
- Story generation logic
- Video keyword generation
- Custom prompt handling

#### Integration Tests

```bash
python tests/run_all_tests.py --type integration
```

- API endpoints testing
- Google Sheets integration
- Authentication flows
- AI service integration

#### UI Tests

```bash
python tests/run_all_tests.py --type ui
```

- HTML structure validation
- JavaScript functionality
- Form validation

### Specific Test Commands

```bash
# Test video keyword generation
python -m pytest tests/unittest/test_video_keyword_generator.py -v
python -m pytest tests/integration/test_video_keyword_generation_api.py -v

# Test story generation
python -m pytest tests/unittest/test_story_generation.py -v
python -m pytest tests/integration/test_story_generation.py -v
```

## 📁 Project Structure

```
IssarVideos/
├── clients/                    # External API clients
│   ├── openai_client.py       # OpenAI API wrapper
│   └── sheets_client.py       # Google Sheets API client
├── data/                       # Data models and schemas
│   └── video_record.py        # Pydantic models for API
├── db/                         # Database utilities
│   └── sheets_narratives_db.py # Google Sheets operations
├── llm/                        # AI/LLM functionality
│   ├── get_story.py           # Story generation logic
│   └── get_videos.py          # YouTube search query generation
├── static/                     # Static web assets
│   ├── tagger.html            # Main UI
│   ├── report.html            # Analytics dashboard
│   └── *.js, *.css           # Frontend assets
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

| Variable                         | Description                          | Default       | Required |
| -------------------------------- | ------------------------------------ | ------------- | -------- |
| `OPENAI_API_KEY`                 | OpenAI API key for AI features       | None          | Yes\*    |
| `GOOGLE_SHEETS_CREDENTIALS_PATH` | Path to Google service account JSON  | None          | Yes      |
| `GOOGLE_SHEETS_ID`               | Google Sheet ID for data storage     | None          | Yes      |
| `PORT`                           | Server port                          | `8000`        | No       |
| `ENVIRONMENT`                    | Environment (development/production) | `development` | No       |

\*Required for AI-powered story generation and video search features

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

### Complete Workflow: From Narrative to YouTube Search

1. **Generate a Story from Narrative**:

```python
import requests

# Generate a story
story_response = requests.post("http://localhost:8000/generate-story", json={
    "narrative": "A young artist discovers their paintings predict the future",
    "style": "mysterious",
    "additional_context": "Focus on the emotional journey"
})

story = story_response.json()["story"]
print(f"Generated Story: {story}")
```

2. **Generate YouTube Search Query from Story**:

```python
# Generate YouTube search query
search_response = requests.post("http://localhost:8000/generate-video-keywords", json={
    "story": story,
    "max_keywords": 5
})

search_query = search_response.json()["search_query"]
print(f"YouTube Search Query: {search_query}")
# Output: "artist future prediction mystery"
```

3. **Use the Search Query for YouTube**:

```python
# You can now search YouTube with this optimized query
youtube_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
print(f"YouTube Search URL: {youtube_url}")
```

### Python Integration

```python
from llm.get_story import StoryGenerator
from llm.get_videos import VideoKeywordGenerator

# Initialize generators
story_gen = StoryGenerator()
video_gen = VideoKeywordGenerator()

# Generate a story
story = story_gen.get_story(
    narrative="A time traveler gets stuck in the wrong era",
    style="dramatic"
)

# Generate YouTube search query from the story
search_result = video_gen.generate_keywords(
    story=story["story"],
    max_keywords=5
)

print(f"Story: {story['story']}")
print(f"YouTube Search: {search_result['search_query']}")
```

## ️ Security

- Environment-based configuration
- Safe database operations with Google Sheets backend
- Input validation and sanitization
- Secure API key management
- CORS middleware for web security

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API errors**:

   - Verify your API key is set in `.env` file
   - Check your OpenAI account has sufficient credits
   - Test with `/test-openai-connection`

2. **Google Sheets issues**:

   - Verify service account has sheet access
   - Check Google Sheets API is enabled
   - Ensure correct sheet ID

3. **YouTube search queries**:
   - The system generates 2-6 word queries optimized for YouTube
   - Queries are designed to be broad enough to find relevant content
   - If queries seem too general, provide more specific story context

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Run the test suite (`python tests/run_all_tests.py`)
5. Commit your changes (`git commit -m 'Add new feature'`)
6. Push to the branch (`git push origin feature/new-feature`)
7. Open a Pull Request

## 📝 Recent Updates

### Video Search Optimization (Latest)

- **Simplified YouTube Search**: Now generates single, optimized search queries instead of multiple keyword lists
- **LLM-Powered Queries**: Uses AI to create effective 2-6 word YouTube search terms
- **Streamlined API**: Single endpoint `/generate-video-keywords` returns one optimal search string
- **Clean Codebase**: Removed legacy keyword generation methods and unused models

### Test Coverage

- **Comprehensive Testing**: Full test suite covering unit, integration, and UI tests
- **Video Keyword Tests**: Updated for new single-query functionality
- **Story Generation Tests**: Complete coverage of all story generation features

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- Powered by [OpenAI GPT-4](https://openai.com/) for content generation
- Uses [Poetry](https://python-poetry.org/) for dependency management
- Google Sheets integration for data management
- Comprehensive testing with [pytest](https://pytest.org/)
