from dataclasses import dataclass
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any


class TagRecordRequest(BaseModel):
    """Model for tagging a record with username and result"""

    link: str
    username: str
    result: int


class VideoRecord(BaseModel):
    Sheet: str
    Narrative: str
    Story: Optional[str] = None
    Tagger_1: Optional[str] = None
    Tagger_1_Result: Optional[int] = None
    Link: Optional[str] = None


class VideoRecordUpdate(BaseModel):
    """Model for updating video record fields"""

    Sheet: Optional[str] = None
    Narrative: Optional[str] = None
    Story: Optional[str] = None
    Tagger_1: Optional[str] = None
    Tagger_1_Result: Optional[int] = None
    Link: Optional[str] = None


class VideoRecordCreate(BaseModel):
    """Model for creating new video records"""

    Sheet: str
    Narrative: str
    Story: Optional[str] = None
    Tagger_1: Optional[str] = None
    Tagger_1_Result: Optional[int] = None
    Link: str


class AddNarrativeRequest(BaseModel):
    """Model for adding new narrative records"""

    Sheet: str
    Narrative: str
    Story: str
    Link: str


class StoryGenerationRequest(BaseModel):
    """Model for generating a story from a narrative"""

    narrative: str
    style: Optional[str] = "engaging"
    additional_context: Optional[str] = None

    @validator("narrative")
    def narrative_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Narrative cannot be empty")
        return v


class StoryVariantsRequest(BaseModel):
    """Model for generating multiple story variants"""

    narrative: str
    count: Optional[int] = 3
    style: Optional[str] = "engaging"
    additional_context: Optional[str] = None

    @validator("narrative")
    def narrative_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Narrative cannot be empty")
        return v


class StoryRefinementRequest(BaseModel):
    """Model for refining an existing story"""

    original_story: str
    refinement_request: str
    narrative: str

    @validator("original_story", "refinement_request", "narrative")
    def strings_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v


class StoryResponse(BaseModel):
    """Model for story generation response"""

    story: str
    narrative: str
    metadata: Dict[str, Any]


class CustomPromptStoryRequest(BaseModel):
    """Model for generating a story with a custom prompt"""

    narrative: str
    custom_prompt: str
    style: Optional[str] = "engaging"

    @validator("narrative", "custom_prompt")
    def strings_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v


class VideoSearchRequest(BaseModel):
    """Model for searching videos based on a story"""

    story: str
    max_duration: Optional[int] = 300  # 5 minutes in seconds
    platforms: Optional[List[str]] = ["youtube", "tiktok", "instagram"]

    @validator("story")
    def story_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Story cannot be empty")
        return v

    @validator("max_duration")
    def duration_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Max duration must be positive")
        return v


class VideoResult(BaseModel):
    """Model for a single video search result"""

    title: str
    url: str
    platform: str
    duration: Optional[int] = None  # in seconds
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None


class VideoSearchResponse(BaseModel):
    """Model for video search response"""

    query: str
    results: List[VideoResult]
    metadata: Dict[str, Any]
