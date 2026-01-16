#!/usr/bin/env python3
"""
Test Figma API connection with the new token
"""

import os
import requests
from dotenv import load_dotenv

def test_figma_connection():
    """Test connection to Figma API"""
    print("🔍 TESTING FIGMA CONNECTION")
    print("=" * 40)
    print()

    # Load environment variables
    load_dotenv()

    token = os.getenv('FIGMA_ACCESS_TOKEN', '')

    if not token:
        print("❌ No token found in .env file")
        return False

    print(f"✅ Token found: {token[:10]}...")
    print(f"   Length: {len(token)} characters")
    print()

    # Validate token format
    if not token.startswith('figd_'):
        print("❌ Invalid token format (should start with 'figd_')")
        return False

    if len(token) < 30:
        print(f"❌ Token too short ({len(token)} characters)")
        return False

    print("✅ Token format valid")
    print()

    # Test API connection
    print("🔗 Testing Figma API connection...")

    headers = {
        "X-Figma-Token": token,
        "Content-Type": "application/json"
    }

    try:
        # Test with /v1/me endpoint (get user info)
        response = requests.get(
            "https://api.figma.com/v1/me",
            headers=headers,
            timeout=10
        )

        print(f"   Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print()
            print("✅ CONNECTION SUCCESSFUL!")
            print("=" * 40)
            print(f"👤 User: {data.get('email', 'N/A')}")
            print(f"🆔 ID: {data.get('id', 'N/A')}")
            print(f"📛 Handle: {data.get('handle', 'N/A')}")
            print()

            # Test file listing
            print("📁 Testing file access...")
            files_response = requests.get(
                "https://api.figma.com/v1/teams",
                headers=headers,
                timeout=10
            )

            if files_response.status_code == 200:
                teams_data = files_response.json()
                teams = teams_data.get('teams', [])
                print(f"✅ Found {len(teams)} teams")
                if teams:
                    print(f"   First team: {teams[0].get('name', 'N/A')}")

            print()
            print("🎉 FIGMA API READY!")
            print("=" * 40)
            print()
            print("✅ You can now:")
            print("   • Create new Figma files")
            print("   • Access existing files")
            print("   • Export assets")
            print("   • Manage designs programmatically")

            return True

        elif response.status_code == 403:
            print()
            print("❌ AUTHENTICATION FAILED")
            print("   Token is invalid or expired")
            print("   Please generate a new token")
            return False

        else:
            print()
            print(f"❌ API ERROR: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except requests.exceptions.RequestException as e:
        print()
        print(f"❌ CONNECTION ERROR: {e}")
        return False

def main():
    """Main function"""
    print()
    print("🎨 SHOTLIST AGENCY - FIGMA SETUP")
    print("=" * 40)
    print()

    if test_figma_connection():
        print()
        print("🚀 NEXT STEPS:")
        print("=" * 40)
        print("1. Create Figma design system for Shotlist")
        print("2. Build component library")
        print("3. Create website mockups")
        print("4. Design client presentation templates")
        print()
    else:
        print()
        print("❌ Setup incomplete - please check your token")

if __name__ == "__main__":
    main()
