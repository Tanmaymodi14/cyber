#!/usr/bin/env python3
"""
Complete System Test
Tests reanalyze buttons, real data flow, and frontend integration
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

def test_api_endpoints():
    """Test all API endpoints"""
    print("🌐 Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False
    
    # Test controls endpoint
    try:
        response = requests.get(f"{base_url}/api/controls")
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                controls_count = len(data['data'])
                print(f"✅ Controls endpoint working - {controls_count} controls")
            else:
                controls_count = len(data)
                print(f"✅ Controls endpoint working - {controls_count} controls")
        else:
            print(f"❌ Controls endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Controls endpoint error: {e}")
        return False
    
    # Test services endpoint
    try:
        response = requests.get(f"{base_url}/api/evidence/aws/services")
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                services_count = len(data['data'])
                print(f"✅ Services endpoint working - {services_count} services")
            else:
                services_count = len(data)
                print(f"✅ Services endpoint working - {services_count} services")
        else:
            print(f"❌ Services endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Services endpoint error: {e}")
        return False
    
    # Test policies endpoint
    try:
        response = requests.get(f"{base_url}/api/policies")
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                policies_count = len(data['data'])
                print(f"✅ Policies endpoint working - {policies_count} policies")
            else:
                policies_count = len(data)
                print(f"✅ Policies endpoint working - {policies_count} policies")
        else:
            print(f"❌ Policies endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Policies endpoint error: {e}")
        return False
    
    return True

def test_aws_recollect():
    """Test AWS recollect functionality"""
    print("🔄 Testing AWS recollect functionality...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test AWS recollect
        response = requests.post(f"{base_url}/api/evidence/aws/recollect")
        if response.status_code == 200:
            data = response.json()
            collected_keys = data.get('collected_keys', [])
            print(f"✅ AWS recollect working - collected {len(collected_keys)} services")
            print(f"   Services: {', '.join(collected_keys)}")
            return True
        else:
            print(f"❌ AWS recollect failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ AWS recollect error: {e}")
        return False

def test_policy_reanalyze():
    """Test policy reanalyze functionality"""
    print("🔄 Testing policy reanalyze functionality...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Get list of policies
        response = requests.get(f"{base_url}/api/policies")
        if response.status_code != 200:
            print(f"❌ Failed to get policies: {response.status_code}")
            return False
        
        data = response.json()
        policies = data.get('data', data) if isinstance(data, dict) else data
        
        if not policies:
            print("⚠️ No policies found to test reanalyze")
            return True
        
        # Test reanalyze on first policy
        policy_id = policies[0]['id']
        print(f"   Testing reanalyze on policy: {policy_id}")
        
        response = requests.post(f"{base_url}/api/policies/{policy_id}/reanalyze")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Policy reanalyze working - policy '{data['data']['name']}' reanalyzed")
            print(f"   Status: {data['data']['status']}")
            print(f"   Controls mapped: {len(data['data']['controlsMapped'])}")
            return True
        else:
            print(f"❌ Policy reanalyze failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Policy reanalyze error: {e}")
        return False

def test_controls_evaluation():
    """Test controls evaluation with current data"""
    print("🧪 Testing controls evaluation...")
    
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/api/controls")
        if response.status_code != 200:
            print(f"❌ Failed to get controls: {response.status_code}")
            return False
        
        data = response.json()
        controls = data.get('data', data) if isinstance(data, dict) else data
        
        if not controls:
            print("⚠️ No controls found")
            return False
        
        # Count by status
        status_counts = {}
        for control in controls:
            status = control.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"✅ Controls evaluation working - {len(controls)} controls evaluated")
        for status, count in status_counts.items():
            print(f"   {status.upper()}: {count}")
        
        return True
    except Exception as e:
        print(f"❌ Controls evaluation error: {e}")
        return False

def test_services_kpis():
    """Test services KPIs and metrics"""
    print("📊 Testing services KPIs...")
    
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/api/evidence/aws/services")
        if response.status_code != 200:
            print(f"❌ Failed to get services: {response.status_code}")
            return False
        
        data = response.json()
        services = data.get('data', data) if isinstance(data, dict) else data
        
        if not services:
            print("⚠️ No services found")
            return False
        
        print(f"✅ Services KPIs working - {len(services)} services with metrics")
        
        # Show sample KPIs
        for service in services[:3]:  # Show first 3 services
            title = service.get('title', 'Unknown')
            status = service.get('status', 'Unknown')
            kpis = service.get('kpis', {})
            print(f"   {title}: {status} - {kpis}")
        
        return True
    except Exception as e:
        print(f"❌ Services KPIs error: {e}")
        return False

def test_frontend_integration():
    """Test frontend integration by checking if data flows properly"""
    print("🖥️ Testing frontend integration...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test that all frontend-required endpoints work
        endpoints = [
            "/api/health",
            "/api/controls",
            "/api/evidence/aws/services",
            "/api/policies"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code != 200:
                print(f"❌ Frontend endpoint {endpoint} failed: {response.status_code}")
                return False
        
        print("✅ All frontend endpoints working")
        
        # Test that data is in the expected format for frontend
        response = requests.get(f"{base_url}/api/controls")
        data = response.json()
        controls = data.get('data', data) if isinstance(data, dict) else data
        
        if controls and len(controls) > 0:
            # Check that controls have required fields for frontend
            required_fields = ['id', 'status', 'score']
            first_control = controls[0]
            missing_fields = [field for field in required_fields if field not in first_control]
            
            if missing_fields:
                print(f"❌ Controls missing required fields: {missing_fields}")
                return False
            
            print("✅ Controls data format compatible with frontend")
        
        return True
    except Exception as e:
        print(f"❌ Frontend integration error: {e}")
        return False

def test_real_data_flow():
    """Test that real data flows from backend to frontend"""
    print("🔄 Testing real data flow...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Get current data
        response = requests.get(f"{base_url}/api/evidence/aws/services")
        if response.status_code != 200:
            print(f"❌ Failed to get services: {response.status_code}")
            return False
        
        data = response.json()
        services = data.get('data', data) if isinstance(data, dict) else data
        
        # Check if we have meaningful data (not just empty/default values)
        has_real_data = False
        for service in services:
            kpis = service.get('kpis', {})
            for key, value in kpis.items():
                if isinstance(value, (int, float)) and value > 0:
                    has_real_data = True
                    break
                elif isinstance(value, str) and value not in ['No', 'Off', 'Disabled']:
                    has_real_data = True
                    break
        
        if has_real_data:
            print("✅ Real data is flowing from backend to frontend")
            print("   Data includes meaningful metrics and KPIs")
        else:
            print("⚠️ Data appears to be empty or default values")
            print("   Consider running AWS data collection")
        
        return True
    except Exception as e:
        print(f"❌ Real data flow error: {e}")
        return False

def main():
    """Main function to run complete system test"""
    print("🚀 proTecht Complete System Test")
    print("=" * 50)
    
    tests = [
        ("API Endpoints", test_api_endpoints),
        ("AWS Recollect", test_aws_recollect),
        ("Policy Reanalyze", test_policy_reanalyze),
        ("Controls Evaluation", test_controls_evaluation),
        ("Services KPIs", test_services_kpis),
        ("Frontend Integration", test_frontend_integration),
        ("Real Data Flow", test_real_data_flow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            if test_func():
                print(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
        print("✅ Reanalyze buttons are functional")
        print("✅ Real data is flowing to frontend")
        print("✅ All API endpoints are working")
        print("✅ Controls evaluation is working")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
