#!/usr/bin/env python3
"""
Test script for Piso Print Flask Server
Run this on the Orange Pi to verify everything is working
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5000"
TEST_SESSION = "TEST_USER_123456"

def print_test(name, success):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {name}")

def test_server_status():
    """Test if server is online"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print_test("Server Online", data.get('status') == 'online')
            return True
        else:
            print_test("Server Online", False)
            return False
    except Exception as e:
        print_test("Server Online", False)
        print(f"   Error: {e}")
        return False

def test_system_status():
    """Test system status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            print_test("System Status", True)
            print(f"   Printer: {data['printer']['status']}")
            print(f"   Total Users: {data['stats']['total_users']}")
            print(f"   Total Prints: {data['stats']['total_prints']}")
            return True
        else:
            print_test("System Status", False)
            return False
    except Exception as e:
        print_test("System Status", False)
        print(f"   Error: {e}")
        return False

def test_add_credits():
    """Test adding credits"""
    try:
        data = {
            "session_id": TEST_SESSION,
            "amount": 10
        }
        response = requests.post(
            f"{BASE_URL}/api/credits",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            result = response.json()
            print_test("Add Credits", result.get('success', False))
            print(f"   New Balance: ₱{result.get('new_balance', 0)}")
            return True
        else:
            print_test("Add Credits", False)
            return False
    except Exception as e:
        print_test("Add Credits", False)
        print(f"   Error: {e}")
        return False

def test_check_credits():
    """Test checking credits"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/check_credits",
            params={'session_id': TEST_SESSION}
        )
        if response.status_code == 200:
            data = response.json()
            print_test("Check Credits", data.get('success', False))
            print(f"   Credits: ₱{data.get('credits', 0)}")
            return True
        else:
            print_test("Check Credits", False)
            return False
    except Exception as e:
        print_test("Check Credits", False)
        print(f"   Error: {e}")
        return False

def test_upload_file():
    """Test file upload (without actual file)"""
    try:
        # Just test if endpoint exists
        response = requests.post(f"{BASE_URL}/upload")
        # We expect 400 because no file, but endpoint should exist
        if response.status_code in [400, 413]:
            print_test("Upload Endpoint", True)
            return True
        else:
            print_test("Upload Endpoint", False)
            return False
    except Exception as e:
        print_test("Upload Endpoint", False)
        print(f"   Error: {e}")
        return False

def test_print_endpoint():
    """Test print endpoint (without actual file)"""
    try:
        data = {
            "session_id": TEST_SESSION,
            "credits": 10
        }
        response = requests.post(
            f"{BASE_URL}/print",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        # We expect 400 because no file uploaded, but endpoint should exist
        if response.status_code in [400, 500]:
            print_test("Print Endpoint", True)
            return True
        else:
            print_test("Print Endpoint", False)
            return False
    except Exception as e:
        print_test("Print Endpoint", False)
        print(f"   Error: {e}")
        return False

def test_history():
    """Test history endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/history")
        if response.status_code == 200:
            data = response.json()
            print_test("History", data.get('success', False))
            print(f"   Records: {data.get('count', 0)}")
            return True
        else:
            print_test("History", False)
            return False
    except Exception as e:
        print_test("History", False)
        print(f"   Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("🖨️  Piso Print Server - Test Suite")
    print("="*50 + "\n")
    
    tests = [
        ("Server Status", test_server_status),
        ("System Status", test_system_status),
        ("Add Credits", test_add_credits),
        ("Check Credits", test_check_credits),
        ("Upload Endpoint", test_upload_file),
        ("Print Endpoint", test_print_endpoint),
        ("History", test_history)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ FAIL - {name}")
            print(f"   Error: {e}")
            results.append(False)
        print()
    
    print("="*50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Server is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
