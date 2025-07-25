from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
import os
import logging
from typing import List, Dict, Any
from data.video_record import (
    VideoRecord,
    VideoRecordUpdate,
    VideoRecordCreate,
    TagRecordRequest,
    AddNarrativeRequest,
    StoryGenerationRequest,
    StoryVariantsRequest,
    StoryRefinementRequest,
    StoryResponse,
    CustomPromptStoryRequest,
    VideoKeywordRequest,
    VideoKeywordResponse,
    NarrativeExplanationRequest,
    NarrativeExplanationResponse,
)
from db.sheets_narratives_db import SheetsNarrativesDB
from llm.get_story import StoryGenerator
from llm.get_videos import VideoKeywordGenerator
from llm.narrative_explain import NarrativeExplainer
from search.youtube_search import YouTubeSearcher
from data.video_record import YouTubeSearchResponse

# Initialize logger
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Health check endpoint for Cloud Run
@app.get("/health")
def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy", "service": "video-narratives"}


# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
PORT = int(os.getenv("PORT", 8000))

# Google Sheets configuration (required)
GOOGLE_SHEETS_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
GOOGLE_SHEETS_ID = os.getenv(
    "GOOGLE_SHEETS_ID", "1OYF8OH41MiZUEtKA5y8O-vklnVPpYmZUrnNxiIWtryU"
)

# Validate required environment variables
if not GOOGLE_SHEETS_CREDENTIALS:
    raise ValueError(
        "GOOGLE_SHEETS_CREDENTIALS_PATH environment variable is required. "
        "Please set it to the path of your service account JSON file."
    )

# Database initialization - Google Sheets only
print(f"📊 Using Google Sheets database: {GOOGLE_SHEETS_ID}")
if ENVIRONMENT == "production":
    print("🚀 PRODUCTION MODE: Running on Cloud Run with Google Sheets")
else:
    print("⚠️  DEVELOPMENT MODE: Changes will be saved to Google Sheets!")

try:
    # Use credentials file if available (local development)
    # Use default credentials if on Cloud Run with service account
    credentials_path = (
        GOOGLE_SHEETS_CREDENTIALS
        if GOOGLE_SHEETS_CREDENTIALS and os.path.exists(GOOGLE_SHEETS_CREDENTIALS)
        else None
    )
    db = SheetsNarrativesDB(credentials_path, GOOGLE_SHEETS_ID)
    print("✅ Google Sheets connection successful")
except Exception as e:
    print(f"❌ Failed to connect to Google Sheets: {str(e)}")
    raise RuntimeError(f"Unable to initialize Google Sheets database: {str(e)}")


@app.get("/random-narrative", response_model=VideoRecord)
def get_random_narrative():
    random_row = db.get_random_not_fully_tagged_row()
    if random_row is None:
        raise HTTPException(status_code=404, detail="No untagged narratives found")
    # Clean the data for Pydantic validation
    cleaned_row = _clean_row_dict(random_row)
    video_record = VideoRecord(**cleaned_row)
    return video_record


@app.put("/update-record/{link:path}")
def update_record(link: str, updated_data: VideoRecordUpdate):
    """Update a video record by its link"""
    import urllib.parse

    # URL decode the link parameter
    decoded_link = urllib.parse.unquote(link)

    # Convert the update model to dict, excluding None values
    update_dict = {k: v for k, v in updated_data.model_dump().items() if v is not None}

    # Convert YouTube Shorts URLs to regular YouTube URLs if Link is being updated
    if "Link" in update_dict:
        update_dict["Link"] = convert_youtube_shorts_url(update_dict["Link"])

    if not update_dict:
        raise HTTPException(status_code=400, detail="No data provided for update")

    # Use cell-level update instead of full sheet rewrite
    success = db.update_record_cell_update(decoded_link, update_dict)
    if not success:
        raise HTTPException(
            status_code=404, detail=f"Record not found for link: {decoded_link}"
        )

    return {
        "message": "Record updated successfully",
        "updated_fields": list(update_dict.keys()),
        "link": decoded_link,
    }


@app.post("/add-record", response_model=VideoRecord)
def add_record(record_data: VideoRecordCreate):
    """Add a new video record to the database"""
    try:
        # Convert to dict for database insertion
        record_dict = record_data.model_dump()

        # Convert YouTube Shorts URLs to regular YouTube URLs
        if "Link" in record_dict:
            record_dict["Link"] = convert_youtube_shorts_url(record_dict["Link"])

        # Check if record with same link already exists
        existing_records = db.df[db.df["Link"] == record_dict["Link"]]
        if not existing_records.empty:
            raise HTTPException(
                status_code=400, detail="Record with this link already exists"
            )

        # Add the record using append operation instead of full sheet rewrite
        success = db.add_new_record_append(record_dict)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add record")

        # Return the created record
        cleaned_record_dict = _clean_row_dict(record_dict)
        created_record = VideoRecord(**cleaned_record_dict)
        return created_record

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add record: {str(e)}")


@app.post("/add-narrative")
def add_narrative(narrative_data: AddNarrativeRequest):
    """Add a new narrative record to the database"""
    try:
        # Convert YouTube Shorts URLs to regular YouTube URLs
        converted_link = convert_youtube_shorts_url(narrative_data.Link)

        # Convert to dict for database insertion
        record_dict = {
            "Sheet": narrative_data.Sheet,
            "Narrative": narrative_data.Narrative,
            "Story": narrative_data.Story,
            "Link": converted_link,
            "Tagger_1": None,  # Empty as specified
            "Tagger_1_Result": 0,  # Set to 0 as specified
        }

        # Check if record with same link already exists
        existing_records = db.df[db.df["Link"] == record_dict["Link"]]
        if not existing_records.empty:
            raise HTTPException(
                status_code=400, detail="Record with this link already exists"
            )

        # Add the record to the specific sheet using append operation
        success = db.add_record_to_specific_sheet_append(record_dict)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add narrative")

        logger.info(
            f"Successfully added narrative to sheet '{narrative_data.Sheet}': {narrative_data.Narrative}"
        )

        return {
            "message": "Narrative added successfully",
            "sheet": narrative_data.Sheet,
            "narrative": narrative_data.Narrative,
            "link": narrative_data.Link,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding narrative: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to add narrative: {str(e)}"
        )


def _clean_row_dict(row_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Clean row dictionary for Pydantic validation"""
    cleaned = {}

    # Define the expected fields for VideoRecord
    expected_fields = {
        "Sheet",
        "Narrative",
        "Story",
        "Link",
        "Tagger_1",
        "Tagger_1_Result",
    }

    for key, value in row_dict.items():
        # Skip empty or invalid column names
        if not key or key.strip() == "":
            continue

        # Only process expected fields
        if key not in expected_fields:
            continue

        if pd.isna(value):
            cleaned[key] = None
        elif key == "Tagger_1_Result":
            # Handle Tagger_1_Result specifically - convert empty strings to None
            if value == "" or value is None:
                cleaned[key] = None
            else:
                try:
                    cleaned[key] = int(value)
                except (ValueError, TypeError):
                    cleaned[key] = None
        else:
            # For string fields, convert empty strings to None if appropriate
            if value == "":
                cleaned[key] = None if key in ["Tagger_1"] else value
            else:
                cleaned[key] = value

    # Ensure all required fields exist
    for field in expected_fields:
        if field not in cleaned:
            if field == "Sheet":
                # If Sheet is missing, this is a critical error
                raise ValueError(f"Required field 'Sheet' is missing from data")
            cleaned[field] = None
    return cleaned


@app.get("/all-records", response_model=List[VideoRecord])
def get_all_records():
    """Get all video records from the database"""
    if db.df.empty:
        return []

    records = []
    for _, row in db.df.iterrows():
        row_dict = row.to_dict()
        # Clean up the data for Pydantic validation
        row_dict = _clean_row_dict(row_dict)
        records.append(VideoRecord(**row_dict))

    return records


@app.get("/records-by-sheet/{sheet_name}", response_model=List[VideoRecord])
def get_records_by_sheet(sheet_name: str):
    """Get all video records from a specific sheet"""
    if db.df.empty:
        return []

    filtered_df = db.df[db.df["Sheet"] == sheet_name]
    if filtered_df.empty:
        raise HTTPException(
            status_code=404, detail=f"No records found for sheet: {sheet_name}"
        )

    records = []
    for _, row in filtered_df.iterrows():
        row_dict = row.to_dict()
        # Clean up the data for Pydantic validation
        row_dict = _clean_row_dict(row_dict)
        records.append(VideoRecord(**row_dict))

    return records


@app.get("/random-narrative-for-user/{username}", response_model=VideoRecord)
def get_random_narrative_for_user(username: str):
    """Get random narrative that the user hasn't tagged yet"""
    random_row = db.get_random_not_fully_tagged_row_excluding_user(username)
    if random_row is None:
        raise HTTPException(
            status_code=404, detail="No untagged narratives found for this user"
        )

    # Debug logging
    logger.info(f"Raw row data keys: {list(random_row.keys())}")
    logger.info(f"Raw row data: {random_row}")

    # Clean the data for Pydantic validation
    cleaned_row = _clean_row_dict(random_row)
    logger.info(f"Cleaned row data: {cleaned_row}")

    video_record = VideoRecord(**cleaned_row)
    return video_record


@app.get("/user-tagged-count/{username}")
def get_user_tagged_count(username: str):
    """Get count of records tagged by the user"""
    count = db.get_user_tagged_count(username)
    return {"username": username, "tagged_count": count}


@app.get("/leaderboard")
def get_leaderboard():
    """Get leaderboard with tagging statistics for all users"""
    if db.df.empty:
        return []

    # Get all unique users who have tagged records (not empty/null)
    tagger1_users = db.df[~(db.df["Tagger_1"].isna() | (db.df["Tagger_1"] == ""))][
        "Tagger_1"
    ].tolist()
    all_users = list(set(tagger1_users))

    # Calculate statistics for each user
    leaderboard = []
    for username in all_users:
        count = db.get_user_tagged_count(username)
        if count > 0:  # Only include users who have tagged at least one record
            leaderboard.append({"username": username, "tagged_count": count})

    # Sort by tagged count in descending order
    leaderboard.sort(key=lambda x: x["tagged_count"], reverse=True)

    return leaderboard


@app.post("/tag-record")
def tag_record(request: TagRecordRequest):
    """Tag a record with user's name and result"""
    import urllib.parse

    # URL decode the link parameter
    decoded_link = urllib.parse.unquote(request.link)

    # Validate numeric result value (0-6, where 0 is Problem, 6 is Too Obvious)
    if request.numeric_result is not None and request.numeric_result not in [0, 1, 2, 3, 4, 5, 6]:
        raise HTTPException(status_code=400, detail="Numeric result must be 0, 1, 2, 3, 4, 5, or 6")

    # Convert 1-6 scale to backend values
    backend_result = request.result  # This will be calculated from numeric_result
    numeric_result = request.numeric_result
    
    # Logic: 1,2 -> No (2), 3 -> Problem (4), 4,5 -> Yes (1), 6 -> Too Obvious (3)
    # Note: Button 3 (Neutral/Unclear) now saves as Problem instead of being skipped
    
    # Validate final result value for backend
    if backend_result not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="Result must be 1, 2, 3, or 4")

    # Use cell-level update with both values
    success = db.tag_record_cell_update(decoded_link, request.username, backend_result, numeric_result)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Record not found or already fully tagged: {decoded_link}",
        )

    return {
        "message": "Record tagged successfully",
        "link": decoded_link,
        "username": request.username,
        "result": backend_result,
        "numeric_result": numeric_result,
    }


@app.get("/")
def serve_tagger():
    """Serve the video tagger UI"""
    return FileResponse("static/tagger.html")


@app.get("/tagger")
def serve_tagger_alt():
    """Alternative route for the video tagger UI"""
    return FileResponse("static/tagger.html")


# Report endpoints with authentication
@app.post("/auth-report")
def authenticate_report(request: dict):
    """Authenticate user for report access"""
    username = request.get("username")
    password = request.get("password")

    # Handle None values
    if username is None or password is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Convert to string - must match exactly
    username_str = str(username)
    password_str = str(password)

    # Exact match authentication - no modifications allowed
    valid_users = {
        "tagmaster": "splinter1960",
    }

    if username_str in valid_users and valid_users[username_str] == password_str:
        return {"success": True, "message": "Authentication successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/tagged-records")
def get_tagged_records():
    """Get all records that have been tagged by Tagger_1"""
    if db.df.empty:
        return []

    # Filter records where Tagger_1 is not empty/null
    tagged_df = db.df[~(db.df["Tagger_1"].isna() | (db.df["Tagger_1"] == ""))].copy()

    if tagged_df.empty:
        return []

    records = []
    for _, row in tagged_df.iterrows():
        row_dict = row.to_dict()
        # Convert NaN values to None
        for key, value in row_dict.items():
            if pd.isna(value):
                row_dict[key] = None
        records.append(row_dict)

    return records


@app.get("/report")
def serve_report():
    """Serve the report UI"""
    return FileResponse("static/report.html")


@app.get("/tagging-management")
def serve_tagging_management():
    """Serve the tagging management UI"""
    return FileResponse("static/tagging-management.html")


@app.get("/tagging-stats")
def get_tagging_stats():
    """Get aggregated tagging statistics by sheet and narrative"""
    if db.df.empty:
        return {
            "summary": {
                "total_topics": 0,
                "total_narratives": 0,
                "total_full_narratives": 0,
                "total_initial": 0,
                "total_yes": 0,
                "total_no": 0,
                "total_too_obvious": 0,
                "total_problem": 0,
                "total_missing_narratives": 0,
            },
            "data": [],
        }



    # Group by Sheet and Narrative to get statistics
    grouped_stats = []

    # Get unique sheet/narrative combinations
    unique_combinations = (
        db.df.groupby(["Sheet", "Narrative"]).size().reset_index(name="total_count")
    )

    for _, group in unique_combinations.iterrows():
        sheet = group["Sheet"]
        narrative = group["Narrative"]

        # Filter records for this sheet/narrative combination
        subset = db.df[(db.df["Sheet"] == sheet) & (db.df["Narrative"] == narrative)]

        # Count initial records (untagged records: no Tagger_1_Result or Tagger_1_Result = 0)
        initial_count = len(
            subset[
                (subset["Tagger_1_Result"].isna()) | (subset["Tagger_1_Result"] == 0)
            ]
        )

        # Count different tag results (1=Yes, 2=No, 3=Too Obvious, 4=Problem)
        # Use .fillna(0) to handle NaN values consistently
        tagger_results = subset["Tagger_1_Result"].fillna(0)
        yes_count = len(subset[tagger_results == 1])
        no_count = len(subset[tagger_results == 2])
        too_obvious_count = len(subset[tagger_results == 3])
        problem_count = len(subset[tagger_results == 4])

        # Calculate missing (5 - yes - initial)
        missing = max(0, 5 - yes_count - initial_count)

        stat_entry = {
            "sheet": sheet,
            "narrative": (
                narrative[:100] + "..." if len(narrative) > 100 else narrative
            ),  # Truncate long narratives
            "initial_count": initial_count,
            "yes_count": yes_count,
            "no_count": no_count,
            "too_obvious_count": too_obvious_count,
            "problem_count": problem_count,
            "missing": missing,
        }

        grouped_stats.append(stat_entry)

    # Calculate new 9 summary statistics
    total_topics = len(db.df["Sheet"].unique())  # Total unique sheets (topics)
    total_narratives = len(unique_combinations)  # Total unique narratives

    # Total full narratives (narratives with >5 yes responses)
    total_full_narratives = sum(1 for stat in grouped_stats if stat["yes_count"] > 5)

    # Total done narratives (narratives with >=5 yes responses)
    total_done_narratives = sum(1 for stat in grouped_stats if stat["yes_count"] >= 5)

    # Calculate totals directly from DataFrame (more accurate)
    tagger_results = db.df["Tagger_1_Result"].fillna(0)
    total_initial = len(db.df[(db.df["Tagger_1_Result"].isna()) | (db.df["Tagger_1_Result"] == 0)])
    total_yes = len(db.df[tagger_results == 1])
    total_no = len(db.df[tagger_results == 2])
    total_too_obvious = len(db.df[tagger_results == 3])
    total_problem = len(db.df[tagger_results == 4])

    # Missing narratives (narratives where missing column > 0)
    total_missing_narratives = sum(1 for stat in grouped_stats if stat["missing"] > 0)

    summary = {
        "total_topics": total_topics,
        "total_narratives": total_narratives,
        "total_done_narratives": total_done_narratives,
        "total_full_narratives": total_full_narratives,
        "total_initial": total_initial,
        "total_yes": total_yes,
        "total_no": total_no,
        "total_too_obvious": total_too_obvious,
        "total_problem": total_problem,
        "total_missing_narratives": total_missing_narratives,
    }

    return {"summary": summary, "data": grouped_stats}


# Story Generation Endpoints
@app.post("/generate-story", response_model=StoryResponse)
def generate_story(request: StoryGenerationRequest):
    """Generate a story based on a narrative using OpenAI GPT-4"""
    try:
        # Initialize story generator
        generator = StoryGenerator()

        # Generate story
        result = generator.get_story(
            narrative=request.narrative,
            style=request.style,
            additional_context=request.additional_context,
        )

        return StoryResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate story: {str(e)}"
        )


@app.post("/generate-story-variants")
def generate_story_variants(request: StoryVariantsRequest):
    """Generate multiple story variants for the same narrative"""
    try:
        # Initialize story generator
        generator = StoryGenerator()

        # Generate multiple variants
        variants = generator.get_multiple_story_variants(
            narrative=request.narrative,
            count=request.count,
            style=request.style,
            additional_context=request.additional_context,
        )

        return {
            "narrative": request.narrative,
            "count": len(variants),
            "variants": variants,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate story variants: {str(e)}"
        )


@app.post("/refine-story", response_model=StoryResponse)
def refine_story(request: StoryRefinementRequest):
    """Refine an existing story based on feedback"""
    try:
        # Initialize story generator
        generator = StoryGenerator()

        # Refine the story
        result = generator.refine_story(
            original_story=request.original_story,
            refinement_request=request.refinement_request,
            narrative=request.narrative,
        )

        return StoryResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refine story: {str(e)}")


@app.post("/generate-story-custom-prompt", response_model=StoryResponse)
def generate_story_custom_prompt(request: CustomPromptStoryRequest):
    """Generate a story using a custom prompt"""
    try:
        # Initialize story generator
        generator = StoryGenerator()

        # Use the custom prompt directly as the user prompt
        result = generator.get_story_with_custom_prompt(
            narrative=request.narrative,
            custom_prompt=request.custom_prompt,
            style=request.style,
        )

        return StoryResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate story with custom prompt: {str(e)}",
        )


# Video Keyword Generation Endpoints
@app.post("/generate-video-keywords", response_model=VideoKeywordResponse)
def generate_video_keywords(request: VideoKeywordRequest):
    """Generate YouTube search keywords based on a story"""
    try:
        # Initialize video keyword generator
        generator = VideoKeywordGenerator()

        # Generate keywords
        result = generator.generate_keywords(
            narrative=request.narrative or "",
            story=request.story,
            max_keywords=request.max_keywords,
        )

        return VideoKeywordResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video keywords: {str(e)}",
        )


@app.post("/search-videos", response_model=YouTubeSearchResponse)
def search_videos(
    query: str,
    max_results: int = 10,
    max_duration: int = 300,
    min_duration: int = 45,
    narrative: str = None,
):
    """Search for videos on YouTube with duration filtering and narrative-based ranking"""
    try:
        searcher = YouTubeSearcher()
        videos = searcher.search_videos(
            query, max_results, max_duration, min_duration, narrative
        )
        return YouTubeSearchResponse(videos=videos)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to search for videos: {str(e)}"
        )


@app.get("/test-openai-connection")
def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        from clients.openai_client import OpenAIClient

        client = OpenAIClient()
        is_connected = client.validate_connection()

        return {
            "connected": is_connected,
            "message": (
                "OpenAI connection successful"
                if is_connected
                else "OpenAI connection failed"
            ),
        }

    except Exception as e:
        return {"connected": False, "message": f"OpenAI connection error: {str(e)}"}


@app.post("/refresh-data")
def refresh_data():
    """Refresh data from Google Sheets (useful after manual edits)"""
    try:
        db.load_all_sheets_data()
        return {
            "message": "Data refreshed successfully",
            "total_records": len(db.df),
            "timestamp": pd.Timestamp.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh data: {str(e)}")


@app.get("/topics")
def get_all_topics():
    """Get all available topics (worksheets) from the spreadsheet"""
    try:
        # Cache topics for 5 minutes to reduce API calls
        if not hasattr(db, "_cached_topics") or not hasattr(db, "_topics_cache_time"):
            db._cached_topics = None
            db._topics_cache_time = 0

        import time

        current_time = time.time()
        cache_age = current_time - db._topics_cache_time

        # Use cached topics if less than 5 minutes old
        if db._cached_topics is not None and cache_age < 300:  # 5 minutes
            return {"topics": db._cached_topics}

        # Get fresh topics and cache them
        topics = db.sheets_client.get_all_worksheets()
        db._cached_topics = topics
        db._topics_cache_time = current_time

        return {"topics": topics}
    except Exception as e:
        logger.error(f"Error getting topics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get topics: {str(e)}")


@app.get("/narratives/{topic}")
def get_narratives_by_topic(topic: str):
    """Get all narratives for a specific topic"""
    try:
        # Filter dataframe by the specified topic/sheet
        topic_df = db.df[db.df["Sheet"] == topic]

        if topic_df.empty:
            return {"narratives": []}

        # Get unique narratives for this topic
        narratives = topic_df["Narrative"].dropna().unique().tolist()

        return {"narratives": narratives}
    except Exception as e:
        logger.error(f"Error getting narratives for topic {topic}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get narratives: {str(e)}"
        )


def convert_youtube_shorts_url(url: str) -> str:
    """Convert YouTube Shorts URL to regular YouTube URL if applicable"""
    if not url or not isinstance(url, str):
        return url

    # Check if it's a YouTube Shorts URL
    if "youtube.com/shorts/" in url:
        # Extract the video ID from the shorts URL
        # Format: https://www.youtube.com/shorts/VIDEO_ID
        try:
            video_id = url.split("/shorts/")[1]
            # Remove any query parameters or fragments
            video_id = video_id.split("?")[0].split("#")[0]
            # Convert to regular YouTube URL
            converted_url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"Converted YouTube Shorts URL: {url} -> {converted_url}")
            return converted_url
        except (IndexError, AttributeError):
            logger.warning(f"Failed to convert YouTube Shorts URL: {url}")
            return url

    return url


@app.post("/explain-narrative", response_model=NarrativeExplanationResponse)
def explain_narrative(request: NarrativeExplanationRequest):
    """
    Explain an English narrative in Hebrew.
    
    Args:
        request: Contains the narrative to explain
        
    Returns:
        Hebrew translation and explanation of the narrative
    """
    try:
        explainer = NarrativeExplainer()
        result = explainer.explain_narrative(request.narrative)
        
        return NarrativeExplanationResponse(
            narrative_hebrew=result["narrative_hebrew"],
            explanation_hebrew=result["explanation_hebrew"]
        )
    except Exception as e:
        logger.error(f"Error explaining narrative: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to explain narrative: {str(e)}"
        )


if __name__ == "__main__":
    # Use environment PORT for Cloud Run compatibility
    reload_setting = ENVIRONMENT != "production"
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=reload_setting)
