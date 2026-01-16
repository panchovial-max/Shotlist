#!/usr/bin/env python3
"""
Test different Figma authentication methods
"""

import requests
import json

def test_bearer_token(token):
    """Test token as Bearer authentication"""
    print(f"\n{'='*50}")
    print("Testing: Bearer Token Authentication")
    print(f"{'='*50}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            "https://api.figma.com/v1/me",
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS with Bearer token!")
            print(f"User: {data.get('email', 'N/A')}")
            print(f"Handle: {data.get('handle', 'N/A')}")
            return True
        else:
            print(f"❌ Failed: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_x_figma_token(token):
    """Test token as X-Figma-Token header"""
    print(f"\n{'='*50}")
    print("Testing: X-Figma-Token Header")
    print(f"{'='*50}")

    headers = {
        "X-Figma-Token": token,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            "https://api.figma.com/v1/me",
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS with X-Figma-Token!")
            print(f"User: {data.get('email', 'N/A')}")
            print(f"Handle: {data.get('handle', 'N/A')}")
            return True
        else:
            print(f"❌ Failed: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_oauth_token(token):
    """Test as OAuth token"""
    print(f"\n{'='*50}")
    print("Testing: OAuth Token")
    print(f"{'='*50}")

    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            "https://api.figma.com/v1/me",
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS with OAuth token!")
            print(f"User: {data.get('email', 'N/A')}")
            print(f"Handle: {data.get('handle', 'N/A')}")
            return True
        else:
            print(f"❌ Failed: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("🔍 FIGMA TOKEN AUTHENTICATION TESTING")
    print("="*50)
    print("\n📝 According to Figma documentation:")
    print("   Personal Access Tokens should start with 'figd_'")
    print("   But let's test your token with different methods...")

    # The token you provided
    token = "z8vKmHLszDpJFqzTplMPtmUITdvxKq"

    print(f"\n🔑 Testing token: {token}")
    print(f"   Length: {len(token)} characters")

    # Try different authentication methods
    methods = [
        ("Bearer", test_bearer_token),
        ("X-Figma-Token", test_x_figma_token),
        ("OAuth", test_oauth_token)
    ]

    success = False
    for method_name, test_func in methods:
        if test_func(token):
            print(f"\n🎉 SUCCESS! Token works with {method_name} authentication")
            success = True
            break

    if not success:
        print("\n" + "="*50)
        print("❌ TOKEN VERIFICATION FAILED")
        print("="*50)
        print("\n📋 What this means:")
        print("   • The token doesn't work with any standard Figma auth method")
        print("   • It might be:")
        print("     - A partial token (incomplete copy)")
        print("     - An expired token")
        print("     - A different type of identifier (like a file key)")
        print("     - From a different service")

        print("\n💡 SOLUTION:")
        print("   1. Go to Figma Settings")
        print("   2. Look for 'Personal Access Tokens'")
        print("   3. Click 'Generate new token'")
        print("   4. Give it a descriptive name")
        print("   5. Copy the ENTIRE token shown")
        print("   6. Paste it here")

        print("\n📚 Official docs:")
        print("   https://help.figma.com/hc/en-us/articles/8085703771159")
        print("   https://www.figma.com/developers/api#access-tokens")

if __name__ == "__main__":
    main()
