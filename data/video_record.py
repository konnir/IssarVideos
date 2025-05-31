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
    Platform: str
    Title: str
    Hebrew_Title: str
    Tagger_1: str
    Tagger_1_Result: Optional[int] = None
    Tagger_2: str
    Tagger_2_Result: Optional[int] = None
    Link: str
    Length: Optional[float] = None


class VideoRecordUpdate(BaseModel):
    """Model for updating video record fields"""

    Sheet: Optional[str] = None
    Narrative: Optional[str] = None
    Platform: Optional[str] = None
    Title: Optional[str] = None
    Hebrew_Title: Optional[str] = None
    Tagger_1: Optional[str] = None
    Tagger_1_Result: Optional[int] = None
    Tagger_2: Optional[str] = None
    Tagger_2_Result: Optional[int] = None
    Link: Optional[str] = None
    Length: Optional[float] = None


class VideoRecordCreate(BaseModel):
    """Model for creating new video records"""

    Sheet: str
    Narrative: str
    Platform: str
    Title: str
    Hebrew_Title: str
    Tagger_1: str = "Init"
    Tagger_1_Result: Optional[int] = 0
    Tagger_2: str = "Init"
    Tagger_2_Result: Optional[int] = 0
    Link: str
    Length: Optional[float] = None
