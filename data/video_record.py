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


class VideoKeywordRequest(BaseModel):
    """Model for generating YouTube search keywords from a story"""

    story: str
    narrative: Optional[str] = ""
    max_keywords: Optional[int] = 10

    @validator("story")
    def story_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Story cannot be empty")
        return v

    @validator("max_keywords")
    def max_keywords_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Max keywords must be positive")
        return v


class VideoKeywordResponse(BaseModel):
    """Model for video keyword generation response"""

    search_query: str


class YouTubeVideo(BaseModel):
    title: str
    url: str
    id: str
    uploader: str
    duration: int
    view_count: int
    description: str


class YouTubeSearchResponse(BaseModel):
    videos: List[YouTubeVideo]
