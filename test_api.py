#!/usr/bin/env python3
"""
API Test Script
Test all API endpoints to ensure they're working
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_endpoint(name, endpoint):
    """Test a single endpoint"""
    try:
        response = requests.get(f'{BASE_URL}{endpoint}', timeout=5)
        if response.status_code == 200:
            print(f'✅ {name}: OK')
            return True
        else:
            print(f'❌ {name}: Failed (Status {response.status_code})')
            return False
    except Exception as e:
        print(f'❌ {name}: Error - {str(e)}')
        return False

def main():
    print('=' * 50)
    print('StreamLive API Test')
    print('=' * 50)
    print()
    
    # Test main page
    print('Testing Pages:')
    test_endpoint('Main Dashboard', '/')
    test_endpoint('Simple View', '/simple')
    print()
    
    # Test API endpoints
    print('Testing API Endpoints:')
    test_endpoint('Channels API', '/api/channels')
    test_endpoint('Videos API', '/api/videos')
    test_endpoint('Status API', '/api/status')
    test_endpoint('Stats API', '/api/stats')
    test_endpoint('Logs API', '/api/logs')
    test_endpoint('History API', '/api/history?limit=5')
    test_endpoint('System Metrics API', '/api/system/metrics')
    print()
    
    print('=' * 50)
    print('Test Complete!')
    print('=' * 50)

if __name__ == '__main__':
    main()
