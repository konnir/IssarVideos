#!/usr/bin/env python3
"""
Test script to demonstrate the new .env file loading functionality in OpenAI client.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_env_file_loading():
    """Test that the OpenAI client can load API key from .env files."""
    
    # Import after adding to path
    from clients.openai_client import OpenAIClient
    
    print("🧪 Testing .env file loading functionality...")
    
    # Save original environment
    original_api_key = os.environ.get("OPENAI_API_KEY")
    
    try:
        # Remove API key from environment
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        # Test 1: No API key should raise an error
        print("\n1. Testing without API key or .env file...")
        try:
            client = OpenAIClient()
            print("❌ Expected error but client was created successfully")
        except ValueError as e:
            print(f"✅ Expected error: {e}")
        
        # Test 2: Create .env file in clients folder
        print("\n2. Testing with .env file in clients folder...")
        clients_dir = project_root / "clients"
        env_file = clients_dir / ".env"
        
        with open(env_file, "w") as f:
            f.write("OPENAI_API_KEY=test-key-from-clients-env\n")
        
        try:
            client = OpenAIClient()
            if client.api_key == "test-key-from-clients-env":
                print("✅ Successfully loaded API key from clients/.env file")
            else:
                print(f"❌ Wrong API key loaded: {client.api_key}")
        except Exception as e:
            print(f"❌ Error loading from clients/.env: {e}")
        finally:
            # Clean up
            if env_file.exists():
                env_file.unlink()
        
        # Test 3: Create .env file in project root
        print("\n3. Testing with .env file in project root...")
        
        # Clear any loaded environment variables first
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        root_env_file = project_root / ".env"
        
        with open(root_env_file, "w") as f:
            f.write("OPENAI_API_KEY=test-key-from-root-env\n")
        
        try:
            client = OpenAIClient()
            if client.api_key == "test-key-from-root-env":
                print("✅ Successfully loaded API key from project root .env file")
            else:
                print(f"❌ Wrong API key loaded: {client.api_key}")
        except Exception as e:
            print(f"❌ Error loading from root .env: {e}")
        finally:
            # Clean up
            if root_env_file.exists():
                root_env_file.unlink()
            # Clear environment
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
        
        # Test 4: Test priority (clients folder should take precedence)
        print("\n4. Testing priority (clients/.env should override root/.env)...")
        
        # Clear environment first
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        # Create both files
        with open(env_file, "w") as f:
            f.write("OPENAI_API_KEY=clients-folder-key\n")
        
        with open(root_env_file, "w") as f:
            f.write("OPENAI_API_KEY=root-folder-key\n")
        
        try:
            client = OpenAIClient()
            if client.api_key == "clients-folder-key":
                print("✅ Clients folder .env takes precedence over root .env")
            else:
                print(f"❌ Wrong priority, got: {client.api_key}")
        except Exception as e:
            print(f"❌ Error testing priority: {e}")
        finally:
            # Clean up both files
            if env_file.exists():
                env_file.unlink()
            if root_env_file.exists():
                root_env_file.unlink()
        
    finally:
        # Restore original environment
        if original_api_key:
            os.environ["OPENAI_API_KEY"] = original_api_key
    
    print("\n🎉 .env file loading test completed!")

if __name__ == "__main__":
    test_env_file_loading()
