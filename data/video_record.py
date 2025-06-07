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
