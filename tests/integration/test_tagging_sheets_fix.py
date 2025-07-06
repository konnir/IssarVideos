"""
Integration tests for tagging functionality to verify records are saved to correct sheets.
All tests use temporary test sheets that are cleaned up after completion.
"""

import pytest
import requests
import time
import uuid
import os
from typing import List, Dict, Any


class TestTaggingSheetsIntegration:
    """Test that tagging saves records to the correct sheets instead of copying to first sheet."""

    BASE_URL = "http://localhost:8000"
    
    def setup_method(self):
        """Setup for each test"""
        self.test_sheets_created = []  # Track sheets created during tests
        
        # Create a unique test sheet name for this test
        self.test_sheet_name = f"TEST_TAGGING_{uuid.uuid4().hex[:8]}"

    def teardown_method(self):
        """Clean up test sheets after each test"""
        if hasattr(self, 'test_sheets_created') and self.test_sheets_created:
            try:
                from clients.sheets_client import SheetsClient
                
                credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
                sheet_id = os.getenv("GOOGLE_SHEETS_ID")
                
                if credentials_path and sheet_id:
                    client = SheetsClient(credentials_path, sheet_id)
                    for sheet_name in self.test_sheets_created:
                        try:
                            client.delete_worksheet(sheet_name)
                            print(f"✓ Cleaned up tagging test sheet: {sheet_name}")
                        except Exception as e:
                            print(f"⚠ Warning: Could not delete tagging test sheet {sheet_name}: {e}")
            except Exception as e:
                print(f"⚠ Warning: Error during tagging test sheet cleanup: {e}")

    def create_test_sheet_if_needed(self, sheet_name=None):
        """Create a test sheet if it doesn't exist and track it for cleanup"""
        if sheet_name is None:
            sheet_name = self.test_sheet_name
            
        try:
            from clients.sheets_client import SheetsClient
            
            credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
            sheet_id = os.getenv("GOOGLE_SHEETS_ID")
            
            if not credentials_path or not sheet_id:
                pytest.skip("Google Sheets credentials not configured")
                
            client = SheetsClient(credentials_path, sheet_id)
            
            # Check if sheet exists
            worksheets = client.get_all_worksheets()
            existing_sheet_names = [ws.title for ws in worksheets]
            
            if sheet_name not in existing_sheet_names:
                # Create the test sheet with standard headers
                headers = [
                    "Sheet", "Narrative", "Story", "Link", "Tagger_1", "Tagger_1_Result",
                    "Tagger_2", "Tagger_2_Result", "Tagger_3", "Tagger_3_Result",
                    "Tagger_4", "Tagger_4_Result", "Total_Tags", "Consensus_Score",
                    "Final_Decision"
                ]
                client.create_worksheet_with_headers(sheet_name, headers)
                self.test_sheets_created.append(sheet_name)
                print(f"✓ Created tagging test sheet: {sheet_name}")
                
        except Exception as e:
            pytest.skip(f"Could not create tagging test sheet: {e}")
            
        return sheet_name

    def test_tagging_saves_to_correct_sheet(self):
        """Test that tagging a record updates it in the correct sheet, not copies to first sheet."""
        
        # Create test sheet and add a test record
        self.create_test_sheet_if_needed()
        
        # Create a test record to tag
        test_record = {
            "Sheet": self.test_sheet_name,
            "Narrative": "Test narrative for tagging verification",
            "Story": "Test story for tagging verification",
            "Link": f"https://example.com/test-tagging-{int(time.time())}"
        }
        
        # Add the test record
        add_response = requests.post(f"{self.BASE_URL}/add-record", json=test_record)
        assert add_response.status_code == 200, f"Failed to add test record: {add_response.status_code} - {add_response.text}"
        
        added_record = add_response.json()
        print(f"✓ Created test record in sheet '{self.test_sheet_name}': {added_record['Link']}")
        
        # Wait for the record to be saved
        time.sleep(2)
        
        # Tag the record
        tag_data = {
            "link": test_record["Link"],
            "username": "TestUser_SheetsFix",
            "result": 1,  # Yes
        }

        print(f"🎯 Testing tagging on record from sheet: '{self.test_sheet_name}'")
        print(f"   Link: {test_record['Link']}")

        response = requests.post(f"{self.BASE_URL}/tag-record", json=tag_data)
        assert response.status_code == 200, f"Failed to tag record: {response.status_code} - {response.text}"

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
            if record.get("Link") == test_record["Link"]:
                tagged_record = record
                break

        assert tagged_record is not None, f"Could not find tagged record with link: {test_record['Link']}"

        # Verify the record was updated correctly
        print(f"🔍 Updated record details:")
        print(f"   Sheet: {tagged_record.get('Sheet')}")
        print(f"   Tagger_1: {tagged_record.get('Tagger_1')}")
        print(f"   Tagger_1_Result: {tagged_record.get('Tagger_1_Result')}")

        # Key assertions
        assert tagged_record.get("Sheet") == self.test_sheet_name, f"Record should remain in sheet '{self.test_sheet_name}', but found in '{tagged_record.get('Sheet')}'"

        assert tagged_record.get("Tagger_1") == "TestUser_SheetsFix", f"Tagger_1 not set correctly. Expected: TestUser_SheetsFix, Got: {tagged_record.get('Tagger_1')}"

        assert tagged_record.get("Tagger_1_Result") == 1, f"Tagger_1_Result not set correctly. Expected: 1, Got: {tagged_record.get('Tagger_1_Result')}"

        print("✅ Record correctly updated in its original sheet!")

    def test_multiple_sheets_tagging(self):
        """Test tagging records from different sheets to ensure they stay in their respective sheets."""
        
        # Create two different test sheets
        test_sheet_1 = f"TEST_MULTI_1_{uuid.uuid4().hex[:8]}"
        test_sheet_2 = f"TEST_MULTI_2_{uuid.uuid4().hex[:8]}"
        
        self.create_test_sheet_if_needed(test_sheet_1)
        self.create_test_sheet_if_needed(test_sheet_2)
        
        # Create test records in each sheet
        test_records = [
            {
                "Sheet": test_sheet_1,
                "Narrative": "Test narrative 1 for multi-sheet tagging",
                "Story": "Test story 1 for multi-sheet tagging",
                "Link": f"https://example.com/test-multi-1-{int(time.time())}"
            },
            {
                "Sheet": test_sheet_2,
                "Narrative": "Test narrative 2 for multi-sheet tagging",
                "Story": "Test story 2 for multi-sheet tagging", 
                "Link": f"https://example.com/test-multi-2-{int(time.time())}"
            }
        ]
        
        # Add the test records
        for record in test_records:
            add_response = requests.post(f"{self.BASE_URL}/add-record", json=record)
            assert add_response.status_code == 200, f"Failed to add test record: {add_response.status_code}"
            print(f"✓ Created test record in sheet '{record['Sheet']}': {record['Link']}")
        
        # Wait for records to be saved
        time.sleep(2)

        print(f"🎯 Testing tagging on {len(test_records)} records from different sheets")

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
        
        # Create some test data for statistics
        test_sheet_stats = f"TEST_STATS_{uuid.uuid4().hex[:8]}"
        self.create_test_sheet_if_needed(test_sheet_stats)
        
        # Add a few test records
        test_records = [
            {
                "Sheet": test_sheet_stats,
                "Narrative": "Test narrative for stats 1",
                "Story": "Test story for stats 1",
                "Link": f"https://example.com/test-stats-1-{int(time.time())}"
            },
            {
                "Sheet": test_sheet_stats,
                "Narrative": "Test narrative for stats 2", 
                "Story": "Test story for stats 2",
                "Link": f"https://example.com/test-stats-2-{int(time.time())}"
            }
        ]
        
        for record in test_records:
            add_response = requests.post(f"{self.BASE_URL}/add-record", json=record)
            assert add_response.status_code == 200
        
        # Wait for records to be saved
        time.sleep(2)

        response = requests.get(f"{self.BASE_URL}/tagging-stats")
        assert response.status_code == 200, f"Failed to get tagging stats: {response.status_code}"

        stats = response.json()

        assert "summary" in stats, "Response missing summary"
        assert "data" in stats, "Response missing data"

        summary = stats["summary"]
        data = stats["data"]

        print(f"📊 Tagging Statistics Summary:")
        print(f"   Total Topics (Sheets): {summary.get('total_topics', 0)}")
        print(f"   Total Narratives: {summary.get('total_narratives', 0)}")
        print(f"   Total Done Narratives: {summary.get('total_done_narratives', 0)}")

        # Verify our test sheet appears in the data
        sheets_in_data = set(item.get("sheet") for item in data if item.get("sheet"))
        print(f"   Sheets with data: {sorted(sheets_in_data)}")

        # We should at least find our test sheet
        assert test_sheet_stats in sheets_in_data, f"Test sheet '{test_sheet_stats}' not found in statistics data"

        print("✅ Statistics correctly show data including test sheets!")


if __name__ == "__main__":
    # Run with pytest for proper test isolation and cleanup
    import pytest
    import sys
    
    print("🧪 Running Tagging Sheets Integration Tests with pytest")
    print("=" * 50)
    
    # Run pytest on this file
    exit_code = pytest.main([__file__, "-v", "-s"])
    sys.exit(exit_code)
