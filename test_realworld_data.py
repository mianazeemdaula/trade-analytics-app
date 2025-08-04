#!/usr/bin/env python3
"""Test script for real-world OHLC data format"""

import requests
import json

# Test data from user (simulated format)
real_world_data = [
    {
        "datetime": "2025-07-01 07:45:25",
        "time": "2025-07-01 07:45:25",
        "open": "2642.24",
        "high": "2642.60",
        "low": "2642.24",
        "close": "2642.60"
        # Note: No volume field
    },
    {
        "datetime": "2025-07-01 07:46:25",
        "time": "2025-07-01 07:46:25",
        "open": "2642.60",
        "high": "2642.80",
        "low": "2642.55",
        "close": "2642.75"
    },
    {
        "datetime": "2025-07-01 07:47:25",
        "time": "2025-07-01 07:47:25",
        "open": "2642.75",
        "high": "2643.00",
        "low": "2642.70",
        "close": "2642.90"
    }
]

def test_technical_analysis():
    """Test the technical analysis endpoint with real-world data"""
    url = "http://localhost:8001/analyze"
    
    payload = {
        "indicators": {
            "rsi": [14],
            "sma": [10, 20],
            "ema": [10]
        },
        "ohlc_data": real_world_data
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Technical Analysis SUCCESS!")
            print(json.dumps(result, indent=2))
        else:
            print("❌ Technical Analysis FAILED!")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on localhost:8001")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_candlestick_patterns():
    """Test the candlestick patterns endpoint with real-world data"""
    url = "http://localhost:8001/candlestick-patterns"
    
    # Add more data for pattern recognition
    extended_data = real_world_data + [
        {
            "datetime": "2025-07-01 07:48:25",
            "open": "2642.90",
            "high": "2643.20",
            "low": "2642.85",
            "close": "2643.15"
        },
        {
            "time": "2025-07-01 07:49:25",  # Test with only 'time' field
            "open": "2643.15",
            "high": "2643.40",
            "low": "2643.10",
            "close": "2643.30"
        }
    ]
    
    payload = {
        "ohlc_data": extended_data,
        "patterns": ["doji", "hammer", "engulfing"]
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Candlestick Patterns SUCCESS!")
            print(json.dumps(result, indent=2))
        else:
            print("❌ Candlestick Patterns FAILED!")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on localhost:8001")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_binary_options():
    """Test the binary options prediction endpoint with real-world data"""
    url = "http://localhost:8001/predict-binary-options"
    
    # Use extended data for better prediction
    extended_data = real_world_data + [
        {
            "datetime": "2025-07-01 07:48:25",
            "open": "2642.90",
            "high": "2643.20",
            "low": "2642.85",
            "close": "2643.15"
        },
        {
            "time": "2025-07-01 07:49:25",
            "open": "2643.15",
            "high": "2643.40",
            "low": "2643.10",
            "close": "2643.30"
        },
        {
            "datetime": "2025-07-01 07:50:25",
            "open": "2643.30",
            "high": "2643.50",
            "low": "2643.25",
            "close": "2643.45"
        }
    ]
    
    payload = {
        "ohlc_data": extended_data,
        "prediction_timeframe": 2,
        "confidence_threshold": 0.6
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Binary Options Prediction SUCCESS!")
            print(json.dumps(result, indent=2))
        else:
            print("❌ Binary Options Prediction FAILED!")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on localhost:8001")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing API with Real-World OHLC Data Format")
    print("=" * 50)
    
    print("\n1. Testing Technical Analysis...")
    test_technical_analysis()
    
    print("\n2. Testing Candlestick Patterns...")
    test_candlestick_patterns()
    
    print("\n3. Testing Binary Options Prediction...")
    test_binary_options()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
