"""
Integration tests for tagging functionality to verify records are saved to correct sheets.
"""

import pytest
import requests
import time
from typing import List, Dict, Any


class TestTaggingSheetsIntegration:
    """Test that tagging saves records to the correct sheets instead of copying to first sheet."""

    BASE_URL = "http://localhost:8000"

    def test_tagging_saves_to_correct_sheet(self):
        """Test that tagging a record updates it in the correct sheet, not copies to first sheet."""

        # Get all records to find one to test with
        response = requests.get(f"{self.BASE_URL}/all-records")
        assert (
            response.status_code == 200
        ), f"Failed to get records: {response.status_code}"

        records = response.json()
        assert len(records) > 0, "No records found to test with"

        print(f"📋 Found {len(records)} records across sheets")

        # Find an untagged record (preferably not from the first sheet)
        untagged_record = None
        sheet_names = set()

        for record in records:
            sheet_names.add(record.get("Sheet", "Unknown"))
            # Look for untagged records
            if not record.get("Tagger_1") or record.get("Tagger_1") == "":
                untagged_record = record
                # Prefer records from non-first sheets to better test the fix
                if record.get("Sheet") != list(sheet_names)[0]:
                    break

        print(f"📊 Found records from sheets: {sorted(sheet_names)}")

        assert untagged_record is not None, "No untagged records found to test with"

        original_sheet = untagged_record.get("Sheet")
        original_link = untagged_record.get("Link")

        print(f"🎯 Testing tagging on record from sheet: '{original_sheet}'")
        print(f"   Link: {original_link}")
        print(f"   Original Tagger_1: {untagged_record.get('Tagger_1', 'None')}")
        print(
            f"   Original Tagger_1_Result: {untagged_record.get('Tagger_1_Result', 'None')}"
        )

        # Tag the record
        tag_data = {
            "link": original_link,
            "username": "TestUser_SheetsFix",
            "result": 1,  # Yes
        }

        response = requests.post(f"{self.BASE_URL}/tag-record", json=tag_data)
        assert (
            response.status_code == 200
        ), f"Failed to tag record: {response.status_code} - {response.text}"

        result = response.json()
        print(f"✅ Successfully tagged record: {result}")

        # Wait for changes to be saved to Google Sheets
        time.sleep(3)

        # Verify the change by getting all records again
        response = requests.get(f"{self.BASE_URL}/all-records")
        assert response.status_code == 200, "Failed to get updated records"

        updated_records = response.json()

        # Find the tagged record
        tagged_record = None
        for record in updated_records:
            if record.get("Link") == original_link:
                tagged_record = record
                break

        assert (
            tagged_record is not None
        ), f"Could not find tagged record with link: {original_link}"

        # Verify the record was updated correctly
        print(f"🔍 Updated record details:")
        print(f"   Sheet: {tagged_record.get('Sheet')}")
        print(f"   Tagger_1: {tagged_record.get('Tagger_1')}")
        print(f"   Tagger_1_Result: {tagged_record.get('Tagger_1_Result')}")

        # Key assertions
        assert (
            tagged_record.get("Sheet") == original_sheet
        ), f"Record moved to wrong sheet! Expected: {original_sheet}, Got: {tagged_record.get('Sheet')}"

        assert (
            tagged_record.get("Tagger_1") == "TestUser_SheetsFix"
        ), f"Tagger_1 not set correctly. Expected: TestUser_SheetsFix, Got: {tagged_record.get('Tagger_1')}"

        assert (
            tagged_record.get("Tagger_1_Result") == 1
        ), f"Tagger_1_Result not set correctly. Expected: 1, Got: {tagged_record.get('Tagger_1_Result')}"

        print("✅ Record correctly updated in its original sheet!")

    def test_multiple_sheets_tagging(self):
        """Test tagging records from different sheets to ensure they stay in their respective sheets."""

        # Get all records
        response = requests.get(f"{self.BASE_URL}/all-records")
        assert response.status_code == 200

        records = response.json()

        # Group records by sheet
        records_by_sheet = {}
        for record in records:
            sheet = record.get("Sheet", "Unknown")
            if sheet not in records_by_sheet:
                records_by_sheet[sheet] = []
            records_by_sheet[sheet].append(record)

        print(f"📊 Found records in {len(records_by_sheet)} sheets:")
        for sheet, sheet_records in records_by_sheet.items():
            untagged_count = sum(
                1
                for r in sheet_records
                if not r.get("Tagger_1") or r.get("Tagger_1") == ""
            )
            print(f"   {sheet}: {len(sheet_records)} total, {untagged_count} untagged")

        # Try to find at least 2 untagged records from different sheets
        test_records = []
        used_sheets = set()

        for sheet, sheet_records in records_by_sheet.items():
            if len(test_records) >= 2:
                break

            for record in sheet_records:
                if (
                    not record.get("Tagger_1") or record.get("Tagger_1") == ""
                ) and sheet not in used_sheets:
                    test_records.append(record)
                    used_sheets.add(sheet)
                    break

        if len(test_records) < 2:
            pytest.skip(
                "Need at least 2 untagged records from different sheets to run this test"
            )

        print(
            f"🎯 Testing tagging on {len(test_records)} records from different sheets"
        )

        # Tag each record
        for i, record in enumerate(test_records):
            sheet = record.get("Sheet")
            link = record.get("Link")

            tag_data = {
                "link": link,
                "username": f"TestUser_Multi_{i}",
                "result": 2 + i,  # Use different results (2=No, 3=Too Obvious)
            }

            print(f"   Tagging record {i+1} from sheet '{sheet}'")

            response = requests.post(f"{self.BASE_URL}/tag-record", json=tag_data)
            assert response.status_code == 200, f"Failed to tag record {i+1}"

        # Wait for all changes to be saved
        time.sleep(5)

        # Verify all records were updated in their correct sheets
        response = requests.get(f"{self.BASE_URL}/all-records")
        assert response.status_code == 200

        updated_records = response.json()

        for i, original_record in enumerate(test_records):
            original_sheet = original_record.get("Sheet")
            original_link = original_record.get("Link")
            expected_username = f"TestUser_Multi_{i}"
            expected_result = 2 + i

            # Find the updated record
            updated_record = None
            for record in updated_records:
                if record.get("Link") == original_link:
                    updated_record = record
                    break

            assert updated_record is not None, f"Could not find updated record {i+1}"

            # Verify it's in the correct sheet
            assert (
                updated_record.get("Sheet") == original_sheet
            ), f"Record {i+1} moved to wrong sheet! Expected: {original_sheet}, Got: {updated_record.get('Sheet')}"

            # Verify tagging data
            assert (
                updated_record.get("Tagger_1") == expected_username
            ), f"Record {i+1} has wrong tagger. Expected: {expected_username}, Got: {updated_record.get('Tagger_1')}"

            assert (
                updated_record.get("Tagger_1_Result") == expected_result
            ), f"Record {i+1} has wrong result. Expected: {expected_result}, Got: {updated_record.get('Tagger_1_Result')}"

            print(f"   ✅ Record {i+1} correctly updated in sheet '{original_sheet}'")

        print("✅ All records correctly updated in their respective sheets!")

    def test_get_sheets_statistics(self):
        """Test that we can get statistics showing records are distributed across sheets."""

        response = requests.get(f"{self.BASE_URL}/tagging-stats")
        assert (
            response.status_code == 200
        ), f"Failed to get tagging stats: {response.status_code}"

        stats = response.json()

        assert "summary" in stats, "Response missing summary"
        assert "data" in stats, "Response missing data"

        summary = stats["summary"]
        data = stats["data"]

        print(f"📊 Tagging Statistics Summary:")
        print(f"   Total Topics (Sheets): {summary.get('total_topics', 0)}")
        print(f"   Total Narratives: {summary.get('total_narratives', 0)}")
        print(f"   Total Done Narratives: {summary.get('total_done_narratives', 0)}")

        # Verify we have multiple sheets
        sheets_in_data = set(item.get("sheet") for item in data)
        print(f"   Sheets with data: {sorted(sheets_in_data)}")

        assert (
            len(sheets_in_data) > 1
        ), f"Expected multiple sheets, but only found: {sheets_in_data}"

        print("✅ Statistics correctly show data across multiple sheets!")


if __name__ == "__main__":
    # Run tests directly if executed as script
    test_instance = TestTaggingSheetsIntegration()

    print("🧪 Running Tagging Sheets Integration Tests")
    print("=" * 50)

    try:
        print("\n1. Testing single record tagging...")
        test_instance.test_tagging_saves_to_correct_sheet()

        print("\n2. Testing multiple sheets tagging...")
        test_instance.test_multiple_sheets_tagging()

        print("\n3. Testing statistics...")
        test_instance.test_get_sheets_statistics()

        print("\n" + "=" * 50)
        print("🎉 All tests passed! Tagging fix is working correctly.")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise
