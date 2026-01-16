#!/usr/bin/env python3
"""
Test script for Social Media Configuration API endpoints
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8001"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Test: {name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_request(method, endpoint, data=None):
    print(f"\n{Colors.YELLOW}Request:{Colors.END}")
    print(f"  {method} {endpoint}")
    if data:
        print(f"  Data: {json.dumps(data, indent=2)}")

def print_response(response):
    print(f"\n{Colors.YELLOW}Response:{Colors.END}")
    print(f"  Status: {response.status_code}")
    print(f"  Body: {json.dumps(response.json(), indent=2)}")

def test_add_account():
    """Test adding social media accounts"""
    print_test("Add Social Media Account")
    
    # Test 1: Add Instagram account
    print_request("POST", "/api/social-media/account", {
        "user_id": 2,
        "platform": "instagram",
        "username": "techstartup_official",
        "account_email": "instagram@techstartup.com",
        "access_token": "ig_token_abc123xyz789"
    })
    
    response = requests.post(
        f"{BASE_URL}/api/social-media/account",
        json={
            "user_id": 2,
            "platform": "instagram",
            "username": "techstartup_official",
            "account_email": "instagram@techstartup.com",
            "access_token": "ig_token_abc123xyz789"
        },
        headers={"Content-Type": "application/json"}
    )
    
    print_response(response)
    
    if response.status_code == 200 and response.json()['success']:
        print_success("Instagram account added successfully")
        account_id = response.json()['account_id']
        return account_id
    else:
        print_error("Failed to add Instagram account")
        return None

def test_get_accounts():
    """Test retrieving social media accounts"""
    print_test("Get Social Media Accounts")
    
    print_request("GET", "/api/social-media/accounts?user_id=2")
    
    response = requests.get(f"{BASE_URL}/api/social-media/accounts?user_id=2")
    print_response(response)
    
    if response.status_code == 200 and response.json()['success']:
        print_success(f"Retrieved {response.json()['count']} account(s)")
        return response.json()['accounts']
    else:
        print_error("Failed to retrieve accounts")
        return None

def test_update_settings():
    """Test updating social media settings"""
    print_test("Update Social Media Settings")
    
    settings = {
        "user_id": 2,
        "auto_post": 1,
        "auto_schedule": 1,
        "analytics_enabled": 1,
        "notifications_enabled": 1,
        "sync_followers": 1,
        "sync_engagement": 1,
        "sync_analytics": 1
    }
    
    print_request("POST", "/api/social-media/settings", settings)
    
    response = requests.post(
        f"{BASE_URL}/api/social-media/settings",
        json=settings,
        headers={"Content-Type": "application/json"}
    )
    
    print_response(response)
    
    if response.status_code == 200 and response.json()['success']:
        print_success("Settings updated successfully")
        return True
    else:
        print_error("Failed to update settings")
        return False

def test_get_settings():
    """Test retrieving social media settings"""
    print_test("Get Social Media Settings")
    
    print_request("GET", "/api/social-media/settings?user_id=2")
    
    response = requests.get(f"{BASE_URL}/api/social-media/settings?user_id=2")
    print_response(response)
    
    if response.status_code == 200 and response.json()['success']:
        print_success("Settings retrieved successfully")
        return response.json()['settings']
    else:
        print_error("Failed to retrieve settings")
        return None

def test_add_more_accounts():
    """Test adding multiple accounts"""
    print_test("Add Multiple Social Media Accounts")
    
    platforms = [
        {
            "platform": "facebook",
            "username": "techstartup",
            "account_email": "facebook@techstartup.com",
            "token": "fb_token_xyz789abc123"
        },
        {
            "platform": "tiktok",
            "username": "techstartup_official",
            "account_email": "tiktok@techstartup.com",
            "token": "tt_token_abc123xyz789"
        },
        {
            "platform": "linkedin",
            "username": "techstartup-company",
            "account_email": "linkedin@techstartup.com",
            "token": "li_token_xyz789abc123"
        }
    ]
    
    for platform_data in platforms:
        print_request("POST", "/api/social-media/account", {
            "user_id": 2,
            "platform": platform_data["platform"],
            "username": platform_data["username"],
            "account_email": platform_data["account_email"],
            "access_token": platform_data["token"]
        })
        
        response = requests.post(
            f"{BASE_URL}/api/social-media/account",
            json={
                "user_id": 2,
                "platform": platform_data["platform"],
                "username": platform_data["username"],
                "account_email": platform_data["account_email"],
                "access_token": platform_data["token"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200 and response.json()['success']:
            print_success(f"{platform_data['platform'].upper()} account added")
        else:
            print_error(f"Failed to add {platform_data['platform'].upper()} account")

def test_disconnect_account(account_id):
    """Test disconnecting an account"""
    print_test("Disconnect Social Media Account")
    
    print_request("POST", "/api/social-media/disconnect", {"account_id": account_id})
    
    response = requests.post(
        f"{BASE_URL}/api/social-media/disconnect",
        json={"account_id": account_id},
        headers={"Content-Type": "application/json"}
    )
    
    print_response(response)
    
    if response.status_code == 200 and response.json()['success']:
        print_success("Account disconnected successfully")
        return True
    else:
        print_error("Failed to disconnect account")
        return False

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}🎬 SHOTLIST Social Media Configuration API Tests{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    try:
        # Test 1: Add account
        account_id = test_add_account()
        
        # Test 2: Get accounts
        test_get_accounts()
        
        # Test 3: Add more accounts
        test_add_more_accounts()
        
        # Test 4: Get accounts again
        test_get_accounts()
        
        # Test 5: Update settings
        test_update_settings()
        
        # Test 6: Get settings
        test_get_settings()
        
        # Test 7: Disconnect account (only if we have an account_id)
        if account_id:
            test_disconnect_account(account_id)
        
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}✅ All tests completed!{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
        
    except Exception as e:
        print_error(f"Test failed with error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

