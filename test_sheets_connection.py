#!/usr/bin/env python3
"""
Test script to validate Google Sheets integration
"""

import os
import sys
import logging
from clients.sheets_client import SheetsClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sheets_connection():
    """Test Google Sheets connection and basic operations"""
    
    # Check environment variables
    credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
    sheet_id = os.getenv("GOOGLE_SHEETS_ID", "1OYF8OH41MiZUEtKA5y8O-vklnVPpYmZUrnNxiIWtryU")
    
    if not credentials_path:
        print("❌ GOOGLE_SHEETS_CREDENTIALS_PATH environment variable not set")
        print("This is REQUIRED as the application no longer supports Excel fallback.")
        print("Please set it to the path of your service account JSON file:")
        print("export GOOGLE_SHEETS_CREDENTIALS_PATH='/path/to/your/credentials.json'")
        return False
    
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        return False
    
    print(f"🔑 Using credentials: {credentials_path}")
    print(f"📊 Testing Google Sheet: {sheet_id}")
    
    try:
        # Initialize client
        client = SheetsClient(credentials_path, sheet_id)
        
        # Test basic connection
        if client.validate_connection():
            print("✅ Connection to Google Sheets successful!")
            
            # List worksheets
            worksheets = client.get_all_worksheets()
            print(f"📋 Found {len(worksheets)} worksheets: {worksheets}")
            
            # Test reading data from first worksheet if available
            if worksheets:
                df = client.read_sheet_to_dataframe(worksheets[0])
                print(f"📖 Read {len(df)} rows from worksheet '{worksheets[0]}'")
                if not df.empty:
                    print(f"🔍 Columns: {list(df.columns)}")
                    print(f"📄 Sample data (first 3 rows):")
                    print(df.head(3).to_string())
                else:
                    print("📄 No data found in the worksheet")
            
            return True
        else:
            print("❌ Connection validation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Google Sheets connection: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Google Sheets Integration")
    print("=" * 50)
    
    success = test_sheets_connection()
    
    print("=" * 50)
    if success:
        print("✅ Google Sheets integration test PASSED!")
        print("\nNext steps:")
        print("1. Your Google Sheets integration is working correctly")
        print("2. You can now run your main application with Google Sheets")
        print("3. Make sure to set the environment variables in production")
    else:
        print("❌ Google Sheets integration test FAILED!")
        print("\nTroubleshooting:")
        print("1. Make sure you've created a service account in Google Cloud Console")
        print("2. Download the JSON credentials file")
        print("3. Share your Google Sheet with the service account email")
        print("4. Set GOOGLE_SHEETS_CREDENTIALS_PATH environment variable")
    
    sys.exit(0 if success else 1)
