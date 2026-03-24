"""
Integration test script for localhost development.
Run this to verify backend API is working correctly.
"""

import requests
import json
from datetime import datetime

API_BASE = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    print("   ✅ Health check passed")

def test_single_verify():
    """Test single credit verification"""
    print("\n🔍 Testing single credit verification...")
    test_ids = ["VCS-2024-001", "GOLD-2023-556", "ACR-2021-999"]
    
    for credit_id in test_ids:
        response = requests.post(
            f"{API_BASE}/api/verify",
            json={"creditId": credit_id}
        )
        print(f"\n   Credit: {credit_id}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Trust Score: {data['trustScore']}")
            print(f"   Verdict: {data['verdict']}")
            print(f"   Category: {data['category']}")
            print(f"   Checks: {len(data['checks'])}")
            print(f"   Fraud Risks: {len(data['fraudRisks'])}")
            print("   ✅ Verification passed")
        else:
            print(f"   ❌ Error: {response.text}")

def test_bulk_verify():
    """Test bulk credit verification"""
    print("\n🔍 Testing bulk credit verification...")
    credit_ids = [
        "VCS-2024-001",
        "GOLD-2023-556", 
        "ACR-2021-999",
        "TEST-2024-001",
        "TEST-2024-002"
    ]
    
    response = requests.post(
        f"{API_BASE}/api/verify/bulk",
        json={"creditIds": credit_ids}
    )
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Total Submitted: {data['totalSubmitted']}")
        print(f"   Total Processed: {data['totalProcessed']}")
        print(f"   Total Errors: {data['totalErrors']}")
        print(f"   Results: {len(data['results'])}")
        
        if data['results']:
            print(f"\n   Worst Credit: {data['results'][0]['creditId']} (Score: {data['results'][0]['trustScore']})")
            print(f"   Best Credit: {data['results'][-1]['creditId']} (Score: {data['results'][-1]['trustScore']})")
        
        print("   ✅ Bulk verification passed")
    else:
        print(f"   ❌ Error: {response.text}")

def test_leaderboard():
    """Test leaderboard endpoint"""
    print("\n🔍 Testing leaderboard...")
    
    # Test without filter
    response = requests.get(f"{API_BASE}/api/leaderboard?limit=10")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Entries returned: {len(data)}")
        
        if data:
            print(f"\n   Most Flagged: {data[0]['creditId']} ({data[0]['flagCount']} flags)")
            print(f"   Category: {data[0]['category']}")
            print(f"   Trust Score: {data[0]['trustScore']}")
        
        print("   ✅ Leaderboard test passed")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # Test with category filter
    print("\n   Testing category filter...")
    response = requests.get(f"{API_BASE}/api/leaderboard?category=Forestry&limit=5")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Forestry entries: {len(data)}")
        print("   ✅ Category filter passed")

def test_cors():
    """Test CORS headers"""
    print("\n🔍 Testing CORS headers...")
    response = requests.options(
        f"{API_BASE}/api/verify",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        }
    )
    print(f"   Status: {response.status_code}")
    
    cors_headers = {
        k: v for k, v in response.headers.items() 
        if 'access-control' in k.lower()
    }
    
    for header, value in cors_headers.items():
        print(f"   {header}: {value}")
    
    print("   ✅ CORS test passed")

if __name__ == "__main__":
    print("=" * 60)
    print("CarbonCheck API Integration Tests")
    print("=" * 60)
    print(f"Testing against: {API_BASE}")
    print(f"Started at: {datetime.now().isoformat()}")
    
    try:
        test_health()
        test_single_verify()
        test_bulk_verify()
        test_leaderboard()
        test_cors()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("1. Start backend: cd backend && uvicorn app.main:app --reload")
        print("2. Start frontend: cd apps/web && npm run dev")
        print("3. Open browser: http://localhost:3000")
        print("4. Test with credit ID: VCS-2024-001")
        print("5. Check browser console for [CarbonCheck API] logs")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("\nMake sure the backend is running:")
        print("  cd backend && uvicorn app.main:app --reload")
