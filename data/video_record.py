from dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional


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
