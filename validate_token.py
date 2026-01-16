#!/usr/bin/env python3
"""
Validate Figma token and provide clear guidance
"""

def validate_token(token):
    """Validate the provided token"""
    print("🔍 FIGMA TOKEN VALIDATOR")
    print("=" * 40)
    print()
    print(f"Token provided: {token}")
    print(f"Length: {len(token)} characters")
    print()

    # Check if it's a valid access token
    if token.startswith('figd_') and len(token) >= 40:
        print("✅ VALID FIGMA ACCESS TOKEN!")
        print("This token can be used for API requests.")
        return True

    # Diagnose the issue
    print("❌ INVALID TOKEN FORMAT")
    print()

    if len(token) == 22:
        print("📄 This looks like a FIGMA FILE KEY")
        print("• File keys are 22 characters long")
        print("• Used to identify existing files")
        print("• Example: 82tzTpDl0f7STkO9Wty1So")
        print()
        print("❌ File keys CANNOT be used for API authentication")
    elif not token.startswith('figd_'):
        print("❌ Missing 'figd_' prefix")
        print(f"❌ Too short: {len(token)} characters (need 40+)")

    print()
    print("=" * 40)
    print("🔑 HOW TO GET A VALID ACCESS TOKEN:")
    print("=" * 40)
    print()
    print("1. Open your browser and go to:")
    print("   https://www.figma.com/developers/api#access-tokens")
    print()
    print("2. Log in to your Figma account")
    print()
    print("3. Click 'Get personal access token'")
    print()
    print("4. Give it a name (e.g., 'CMO Agent')")
    print()
    print("5. Copy the FULL token that appears")
    print("   It should look like:")
    print("   figd_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz")
    print()
    print("6. Come back and provide that token")
    print()

    return False

def main():
    """Main function"""
    # Test with the tokens you provided
    tokens_to_test = [
        "JuesMl2RlG4SiJxHtYFObpfL6y6QrJ",
        "82tzTpDl0f7STkO9Wty1So"
    ]

    print("🎨 TESTING YOUR TOKENS")
    print("=" * 40)
    print()

    for i, token in enumerate(tokens_to_test, 1):
        print(f"\n{'='*40}")
        print(f"TOKEN #{i}")
        validate_token(token)

    print("\n" + "=" * 40)
    print("📋 SUMMARY")
    print("=" * 40)
    print()
    print("❌ Neither token is a valid Figma access token")
    print("✅ Both appear to be file keys or other identifiers")
    print()
    print("🎯 NEXT STEP:")
    print("Get a personal access token from:")
    print("https://www.figma.com/developers/api#access-tokens")
    print()
    print("Then run: python validate_token.py")
    print("Or just paste it here and I'll help you set it up!")

if __name__ == "__main__":
    main()
