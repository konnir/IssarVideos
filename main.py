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

    # Validate result value
    if request.result not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="Result must be 1, 2, 3, or 4")

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
    valid_users = {"Nir Kon": "originai", "Issar Tzachor": "originai"}

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


@app.get("/download-excel")
def download_excel():
    """Download the complete Excel file"""
    try:
        excel_bytes = db.get_excel_bytes()
        from fastapi.responses import Response

        headers = {
            "Content-Disposition": 'attachment; filename="narratives_report.xlsx"',
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

        return Response(
            content=excel_bytes,
            headers=headers,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate Excel file: {str(e)}"
        )


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
        yes_count = len(subset[subset["Tagger_1_Result"] == 1])
        no_count = len(subset[subset["Tagger_1_Result"] == 2])
        too_obvious_count = len(subset[subset["Tagger_1_Result"] == 3])
        problem_count = len(subset[subset["Tagger_1_Result"] == 4])

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

    # Total counts across all narratives
    total_initial = sum(stat["initial_count"] for stat in grouped_stats)
    total_yes = sum(stat["yes_count"] for stat in grouped_stats)
    total_no = sum(stat["no_count"] for stat in grouped_stats)
    total_too_obvious = sum(stat["too_obvious_count"] for stat in grouped_stats)
    total_problem = sum(stat["problem_count"] for stat in grouped_stats)

    # Missing narratives (narratives with <5 yes responses)
    total_missing_narratives = sum(1 for stat in grouped_stats if stat["yes_count"] < 5)

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


if __name__ == "__main__":
    # Use environment PORT for Cloud Run compatibility
    reload_setting = ENVIRONMENT != "production"
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=reload_setting)
