#!/usr/bin/env python3
"""
Unit Tests for Data Models
===========================

Tests for Pydantic models in video_record.py
"""
import pytest
import sys
from pathlib import Path
from pydantic import ValidationError

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.video_record import (
    VideoRecord,
    VideoRecordUpdate,
    VideoRecordCreate,
    TagRecordRequest,
)


class TestVideoRecord:
    """Test the VideoRecord model"""

    def test_valid_video_record(self):
        """Test creating a valid VideoRecord"""
        record = VideoRecord(
            Sheet="Test Sheet",
            Narrative="Test narrative",
            Story="Test story",
            Tagger_1="Test User",
            Tagger_1_Result=1,
            Link="https://example.com/video",
        )

        assert record.Sheet == "Test Sheet"
        assert record.Narrative == "Test narrative"
        assert record.Story == "Test story"
        assert record.Tagger_1 == "Test User"
        assert record.Tagger_1_Result == 1
        assert record.Link == "https://example.com/video"

    def test_video_record_with_minimal_fields(self):
        """Test VideoRecord with only required fields"""
        record = VideoRecord(
            Sheet="Test Sheet",
            Narrative="Test narrative",
            Link="https://example.com/video",
        )

        assert record.Sheet == "Test Sheet"
        assert record.Narrative == "Test narrative"
        assert record.Link == "https://example.com/video"
        assert record.Story is None
        assert record.Tagger_1 is None
        assert record.Tagger_1_Result is None

    def test_video_record_missing_required_fields(self):
        """Test that VideoRecord fails without required fields"""
        with pytest.raises(ValidationError):
            VideoRecord()

        with pytest.raises(ValidationError):
            VideoRecord(Sheet="Test Sheet")

        with pytest.raises(ValidationError):
            VideoRecord(Sheet="Test Sheet", Narrative="Test narrative")


class TestVideoRecordUpdate:
    """Test the VideoRecordUpdate model"""

    def test_video_record_update_all_fields(self):
        """Test VideoRecordUpdate with all fields"""
        update = VideoRecordUpdate(
            Sheet="Updated Sheet",
            Narrative="Updated narrative",
            Story="Updated story",
            Tagger_1="Updated User",
            Tagger_1_Result=2,
            Link="https://example.com/updated",
        )

        assert update.Sheet == "Updated Sheet"
        assert update.Narrative == "Updated narrative"
        assert update.Story == "Updated story"
        assert update.Tagger_1 == "Updated User"
        assert update.Tagger_1_Result == 2
        assert update.Link == "https://example.com/updated"

    def test_video_record_update_partial(self):
        """Test VideoRecordUpdate with partial fields"""
        update = VideoRecordUpdate(Tagger_1="New User", Tagger_1_Result=3)

        assert update.Tagger_1 == "New User"
        assert update.Tagger_1_Result == 3
        assert update.Sheet is None
        assert update.Narrative is None
        assert update.Story is None
        assert update.Link is None

    def test_video_record_update_empty(self):
        """Test VideoRecordUpdate with no fields (should be valid)"""
        update = VideoRecordUpdate()

        assert update.Sheet is None
        assert update.Narrative is None
        assert update.Story is None
        assert update.Tagger_1 is None
        assert update.Tagger_1_Result is None
        assert update.Link is None


class TestVideoRecordCreate:
    """Test the VideoRecordCreate model"""

    def test_video_record_create_valid(self):
        """Test creating a valid VideoRecordCreate"""
        create = VideoRecordCreate(
            Sheet="New Sheet",
            Narrative="New narrative",
            Story="New story",
            Tagger_1="Creator User",
            Tagger_1_Result=4,
            Link="https://example.com/new",
        )

        assert create.Sheet == "New Sheet"
        assert create.Narrative == "New narrative"
        assert create.Story == "New story"
        assert create.Tagger_1 == "Creator User"
        assert create.Tagger_1_Result == 4
        assert create.Link == "https://example.com/new"

    def test_video_record_create_minimal(self):
        """Test VideoRecordCreate with minimal required fields"""
        create = VideoRecordCreate(
            Sheet="New Sheet", Narrative="New narrative", Link="https://example.com/new"
        )

        assert create.Sheet == "New Sheet"
        assert create.Narrative == "New narrative"
        assert create.Link == "https://example.com/new"
        assert create.Story is None
        assert create.Tagger_1 is None
        assert create.Tagger_1_Result is None

    def test_video_record_create_missing_required(self):
        """Test that VideoRecordCreate fails without required fields"""
        with pytest.raises(ValidationError):
            VideoRecordCreate()

        with pytest.raises(ValidationError):
            VideoRecordCreate(Sheet="New Sheet")

        with pytest.raises(ValidationError):
            VideoRecordCreate(Sheet="New Sheet", Narrative="New narrative")


class TestTagRecordRequest:
    """Test the TagRecordRequest model"""

    def test_tag_record_request_valid(self):
        """Test creating a valid TagRecordRequest"""
        request = TagRecordRequest(
            link="https://example.com/video", username="Test User", result=1
        )

        assert request.link == "https://example.com/video"
        assert request.username == "Test User"
        assert request.result == 1

    def test_tag_record_request_different_results(self):
        """Test TagRecordRequest with different result values"""
        for result in [1, 2, 3, 4]:
            request = TagRecordRequest(
                link="https://example.com/video", username="Test User", result=result
            )
            assert request.result == result

    def test_tag_record_request_missing_fields(self):
        """Test that TagRecordRequest fails without required fields"""
        with pytest.raises(ValidationError):
            TagRecordRequest()

        with pytest.raises(ValidationError):
            TagRecordRequest(link="https://example.com/video")

        with pytest.raises(ValidationError):
            TagRecordRequest(link="https://example.com/video", username="Test User")

    def test_tag_record_request_type_validation(self):
        """Test type validation for TagRecordRequest fields"""
        # Test that string numbers are converted to int (Pydantic coercion)
        request = TagRecordRequest(
            link="https://example.com/video",
            username="Test User",
            result="1",  # String that can be converted to int
        )
        assert request.result == 1  # Should be converted to int

        # Test that invalid string raises ValidationError
        with pytest.raises(ValidationError):
            TagRecordRequest(
                link="https://example.com/video",
                username="Test User",
                result="invalid",  # String that can't be converted to int
            )

        # Test that all fields must be provided
        with pytest.raises(ValidationError):
            TagRecordRequest(
                link="https://example.com/video", username="Test User", result=None
            )


class TestModelSerialization:
    """Test model serialization and deserialization"""

    def test_video_record_serialization(self):
        """Test VideoRecord serialization to dict"""
        record = VideoRecord(
            Sheet="Test Sheet",
            Narrative="Test narrative",
            Story="Test story",
            Tagger_1="Test User",
            Tagger_1_Result=1,
            Link="https://example.com/video",
        )

        data = record.model_dump()

        assert data["Sheet"] == "Test Sheet"
        assert data["Narrative"] == "Test narrative"
        assert data["Story"] == "Test story"
        assert data["Tagger_1"] == "Test User"
        assert data["Tagger_1_Result"] == 1
        assert data["Link"] == "https://example.com/video"

    def test_video_record_deserialization(self):
        """Test VideoRecord creation from dict"""
        data = {
            "Sheet": "Test Sheet",
            "Narrative": "Test narrative",
            "Story": "Test story",
            "Tagger_1": "Test User",
            "Tagger_1_Result": 1,
            "Link": "https://example.com/video",
        }

        record = VideoRecord(**data)

        assert record.Sheet == "Test Sheet"
        assert record.Narrative == "Test narrative"
        assert record.Story == "Test story"
        assert record.Tagger_1 == "Test User"
        assert record.Tagger_1_Result == 1
        assert record.Link == "https://example.com/video"

    def test_update_model_excludes_none(self):
        """Test that VideoRecordUpdate properly handles None values"""
        update = VideoRecordUpdate(Tagger_1="New User", Tagger_1_Result=2)

        # Test excluding None values
        data = update.model_dump(exclude_none=True)

        assert "Tagger_1" in data
        assert "Tagger_1_Result" in data
        assert "Sheet" not in data
        assert "Narrative" not in data
        assert "Story" not in data
        assert "Link" not in data


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])
