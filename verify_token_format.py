#!/usr/bin/env python3
"""
Verify the token format and test both versions
"""

import requests

def test_token(token, description):
    """Test a token"""
    print(f"\n{'='*50}")
    print(f"Testing: {description}")
    print(f"{'='*50}")
    print(f"Token: {token}")
    print(f"Length: {len(token)} characters")
    print(f"Starts with 'figd_': {token.startswith('figd_')}")

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
            print("✅ SUCCESS!")
            print(f"User: {data.get('email', 'N/A')}")
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("🔍 FIGMA TOKEN VERIFICATION")
    print("="*50)

    # Test the token you provided (with figd_ prefix)
    token_with_prefix = "figd_z8vKmHLszDpJFqzTplMPtmUITdvxKq"
    test_token(token_with_prefix, "Token WITH 'figd_' prefix")

    # Test without prefix (just in case)
    token_without_prefix = "z8vKmHLszDpJFqzTplMPtmUITdvxKq"
    test_token(token_without_prefix, "Token WITHOUT prefix (raw)")

    print("\n" + "="*50)
    print("📋 ANALYSIS")
    print("="*50)
    print("\nThe token you provided is:")
    print("z8vKmHLszDpJFqzTplMPtmUITdvxKq")
    print(f"Length: {len(token_without_prefix)} characters")
    print("\nIf neither version works, please:")
    print("1. Go to: https://www.figma.com/developers/api#access-tokens")
    print("2. Generate a NEW token")
    print("3. Copy it EXACTLY as shown (should start with 'figd_')")
    print("4. Paste the COMPLETE token here")
    print("\nNote: Sometimes tokens are shown in parts or truncated.")
    print("Make sure you're copying the full token!")

if __name__ == "__main__":
    main()
