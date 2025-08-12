#!/usr/bin/env python3
"""Test exact API response format for patterns."""

import requests
import json

def test_exact_patterns_format():
    """Test the exact patterns API response format."""
    
    # Simple test data
    test_data = {
        "ohlc_data": [
            {"time": "2025-08-12T10:00:00", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1000},
            {"time": "2025-08-12T11:00:00", "open": 100.5, "high": 101.2, "low": 99.8, "close": 100.0, "volume": 1100},
            {"time": "2025-08-12T12:00:00", "open": 100.0, "high": 100.8, "low": 99.5, "close": 100.3, "volume": 1200},
            {"time": "2025-08-12T13:00:00", "open": 100.3, "high": 101.0, "low": 99.9, "close": 100.1, "volume": 950},
            {"time": "2025-08-12T14:00:00", "open": 100.1, "high": 100.9, "low": 99.7, "close": 100.4, "volume": 1050}
        ],
        "indicators": {"EMA": [12]},
        "include_patterns": True
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n=== FULL API RESPONSE ===")
            print(json.dumps(result, indent=2))
            
            # Focus on patterns section
            patterns = result.get("data", {}).get("candlestick_patterns", {})
            
            print("\n=== PATTERNS SECTION ONLY ===")
            print(json.dumps(patterns, indent=2))
            
            print(f"\n=== PATTERNS KEYS ===")
            print(f"Keys: {list(patterns.keys())}")
            
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_exact_patterns_format()
