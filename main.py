from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
import os
from typing import List
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from data.video_record import (
    VideoRecord,
    VideoRecordUpdate,
    VideoRecordCreate,
    TagRecordRequest,
)
from db.narratives_db import NarrativesDB

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

# Use environment variable for database path, default to production path
DB_PATH = os.getenv("NARRATIVES_DB_PATH", "static/db/narratives_db.xlsx")

# Production database protection: log which database is being used
if "test" in DB_PATH.lower() or "temp" in DB_PATH.lower():
    print(f"🧪 Using test database: {DB_PATH}")
    print("✅ Safe for testing - production database protected")
else:
    print(f"📊 Using production database: {DB_PATH}")
    if ENVIRONMENT == "production":
        print("🚀 PRODUCTION MODE: Running on Cloud Run")
    else:
        print("⚠️  PRODUCTION MODE: Changes will be saved to the main database!")

db = NarrativesDB(DB_PATH)


@app.get("/random-narrative", response_model=VideoRecord)
def get_random_narrative():
    random_row = db.get_random_not_fully_tagged_row()
    if random_row is None:
        raise HTTPException(status_code=404, detail="No untagged narratives found")
    video_record = VideoRecord(**random_row)
    return video_record


@app.put("/update-record/{link:path}")
def update_record(link: str, updated_data: VideoRecordUpdate):
    """Update a video record by its link"""
    import urllib.parse

    # URL decode the link parameter
    decoded_link = urllib.parse.unquote(link)

    # Convert the update model to dict, excluding None values
    update_dict = {k: v for k, v in updated_data.model_dump().items() if v is not None}

    if not update_dict:
        raise HTTPException(status_code=400, detail="No data provided for update")

    success = db.update_record(decoded_link, update_dict)
    if not success:
        raise HTTPException(
            status_code=404, detail=f"Record not found for link: {decoded_link}"
        )

    # Save changes to the Excel file
    try:
        db.save_changes()
        return {
            "message": "Record updated successfully",
            "updated_fields": list(update_dict.keys()),
            "link": decoded_link,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save changes: {str(e)}")


@app.post("/add-record", response_model=VideoRecord)
def add_record(record_data: VideoRecordCreate):
    """Add a new video record to the database"""
    try:
        # Convert to dict for database insertion
        record_dict = record_data.model_dump()

        # Check if record with same link already exists
        existing_records = db.df[db.df["Link"] == record_dict["Link"]]
        if not existing_records.empty:
            raise HTTPException(
                status_code=400, detail="Record with this link already exists"
            )

        # Add the record
        db.add_new_record(record_dict)

        # Save changes to the Excel file
        db.save_changes()

        # Return the created record
        created_record = VideoRecord(**record_dict)
        return created_record

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add record: {str(e)}")


@app.get("/all-records", response_model=List[VideoRecord])
def get_all_records():
    """Get all video records from the database"""
    if db.df.empty:
        return []

    records = []
    for _, row in db.df.iterrows():
        row_dict = row.to_dict()
        # Convert NaN values to None
        for key, value in row_dict.items():
            if pd.isna(value):
                row_dict[key] = None
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
        # Convert NaN values to None
        for key, value in row_dict.items():
            if pd.isna(value):
                row_dict[key] = None
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
    video_record = VideoRecord(**random_row)
    return video_record


@app.get("/user-tagged-count/{username}")
def get_user_tagged_count(username: str):
    """Get count of records tagged by the user"""
    count = db.get_user_tagged_count(username)
    return {"username": username, "tagged_count": count}


@app.post("/tag-record")
def tag_record(request: TagRecordRequest):
    """Tag a record with user's name and result"""
    import urllib.parse

    # URL decode the link parameter
    decoded_link = urllib.parse.unquote(request.link)

    # Validate result value
    if request.result not in [0, 1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="Result must be 0, 1, 2, 3, or 4")

    success = db.tag_record(decoded_link, request.username, request.result)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Record not found or already fully tagged: {decoded_link}",
        )

    # Save changes to the Excel file
    try:
        db.save_changes()
        return {
            "message": "Record tagged successfully",
            "link": decoded_link,
            "username": request.username,
            "result": request.result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save changes: {str(e)}")


@app.get("/")
def serve_tagger():
    """Serve the video tagger UI"""
    return FileResponse("static/tagger.html")


@app.get("/tagger")
def serve_tagger_alt():
    """Alternative route for the video tagger UI"""
    return FileResponse("static/tagger.html")


if __name__ == "__main__":
    # Use environment PORT for Cloud Run compatibility
    reload_setting = ENVIRONMENT != "production"
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=reload_setting)
