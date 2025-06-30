#!/bin/bash

# IssarVideos - Google Sheets Setup Script
echo "🚀 Setting up IssarVideos with Google Sheets"
echo "============================================="

# Check if credentials file is provided as argument
if [ "$1" != "" ]; then
    CREDS_PATH="$1"
    echo "📁 Using credentials file: $CREDS_PATH"
    
    if [ ! -f "$CREDS_PATH" ]; then
        echo "❌ Credentials file not found: $CREDS_PATH"
        exit 1
    fi
    
    export GOOGLE_SHEETS_CREDENTIALS_PATH="$CREDS_PATH"
else
    echo "❓ No credentials file provided as argument"
    echo "Usage: ./setup_sheets.sh /path/to/your/service-account.json"
    echo ""
    echo "Or set the environment variable manually:"
    echo "export GOOGLE_SHEETS_CREDENTIALS_PATH='/path/to/your/service-account.json'"
    echo ""
    exit 1
fi

# Set default Google Sheets ID if not already set
if [ -z "$GOOGLE_SHEETS_ID" ]; then
    export GOOGLE_SHEETS_ID="1OYF8OH41MiZUEtKA5y8O-vklnVPpYmZUrnNxiIWtryU"
    echo "📊 Using default Google Sheets ID: $GOOGLE_SHEETS_ID"
fi

echo ""
echo "🧪 Testing Google Sheets connection..."
poetry run python test_sheets_connection.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Google Sheets connection successful!"
    echo ""
    echo "🚀 Starting the application..."
    echo "Press Ctrl+C to stop"
    echo ""
    poetry run python main.py
else
    echo ""
    echo "❌ Google Sheets connection failed!"
    echo "Please check your credentials and sheet configuration."
    exit 1
fi
