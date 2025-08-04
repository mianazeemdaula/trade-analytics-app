"""
Test script for the Technical Analysis API

This script demonstrates how to use the API with sample data.
"""

import requests
import json
from datetime import datetime, timedelta

# API endpoint
API_URL = "http://localhost:8000"

def generate_sample_data(days=30):
    """Generate sample OHLC data for testing"""
    base_date = datetime.now() - timedelta(days=days)
    sample_data = []
    
    # Generate some realistic-looking price data
    base_price = 100.0
    
    for i in range(days * 24):  # 24 data points per day (hourly)
        current_time = base_date + timedelta(hours=i)
        
        # Simple random walk with some volatility
        import random
        price_change = random.uniform(-2, 2)
        base_price = max(50, base_price + price_change)  # Prevent negative prices
        
        open_price = base_price
        high_price = open_price + random.uniform(0, 3)
        low_price = open_price - random.uniform(0, 3)
        close_price = random.uniform(low_price, high_price)
        volume = random.randint(1000, 5000)
        
        sample_data.append({
            "time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": volume
        })
        
        base_price = close_price
    
    return sample_data

def test_api():
    """Test the API with sample data"""
    
    print("🚀 Testing Technical Analysis API...")
    
    # Test 1: Check if API is running
    try:
        response = requests.get(f"{API_URL}/")
        print(f"✅ API Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("❌ API is not running. Please start the server first with: uvicorn main:app --reload")
        return
    
    # Test 2: Get supported indicators
    print("\n📊 Supported Indicators:")
    response = requests.get(f"{API_URL}/supported-indicators")
    if response.status_code == 200:
        indicators = response.json()["supported_indicators"]
        for name, info in indicators.items():
            print(f"   {name.upper()}: {info['name']} - Parameters: {info['parameters']}")
    
    # Test 3: Analyze with sample data
    print("\n📈 Testing Analysis Endpoint...")
    
    sample_data = generate_sample_data(days=30)
    
    test_request = {
        "indicators": {
            "rsi": [14],
            "macd": [12, 26, 9],
            "sma": [20],
            "ema": [20],
            "bb": [20, 2.0],
            "stoch": [14, 3, 3]
        },
        "ohlc_data": sample_data
    }
    
    response = requests.post(
        f"{API_URL}/analyze",
        json=test_request,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        results = response.json()
        print("✅ Analysis Results:")
        for indicator, value in results.items():
            print(f"   {indicator.upper()}: {value}")
    else:
        print(f"❌ Analysis failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 4: Test with the exact example from the requirements
    print("\n📝 Testing with Example Data...")
    
    example_request = {
        "indicators": {
            "rsi": [14],
            "macd": [12, 26, 9],
            "sma": [20]
        },
        "ohlc_data": [
            {"time": "2025-07-01 07:45:25", "open": 100, "high": 105, "low": 98, "close": 103, "volume": 1000},
            {"time": "2025-07-01 07:50:00", "open": 103, "high": 108, "low": 102, "close": 107, "volume": 1200},
            {"time": "2025-07-01 07:55:00", "open": 107, "high": 110, "low": 106, "close": 109, "volume": 1500},
            {"time": "2025-07-01 08:00:00", "open": 109, "high": 112, "low": 108, "close": 111, "volume": 1300},
            {"time": "2025-07-01 08:05:00", "open": 111, "high": 115, "low": 110, "close": 114, "volume": 1400},
            {"time": "2025-07-01 08:10:00", "open": 114, "high": 116, "low": 113, "close": 115, "volume": 1600},
            {"time": "2025-07-01 08:15:00", "open": 115, "high": 118, "low": 114, "close": 117, "volume": 1700},
            {"time": "2025-07-01 08:20:00", "open": 117, "high": 119, "low": 116, "close": 118, "volume": 1800},
            {"time": "2025-07-01 08:25:00", "open": 118, "high": 120, "low": 117, "close": 119, "volume": 1900},
            {"time": "2025-07-01 08:30:00", "open": 119, "high": 121, "low": 118, "close": 120, "volume": 2000},
            {"time": "2025-07-01 08:35:00", "open": 120, "high": 122, "low": 119, "close": 121, "volume": 2100},
            {"time": "2025-07-01 08:40:00", "open": 121, "high": 123, "low": 120, "close": 122, "volume": 2200},
            {"time": "2025-07-01 08:45:00", "open": 122, "high": 124, "low": 121, "close": 123, "volume": 2300},
            {"time": "2025-07-01 08:50:00", "open": 123, "high": 125, "low": 122, "close": 124, "volume": 2400},
            {"time": "2025-07-01 08:55:00", "open": 124, "high": 126, "low": 123, "close": 125, "volume": 2500},
            {"time": "2025-07-01 09:00:00", "open": 125, "high": 127, "low": 124, "close": 126, "volume": 2600},
            {"time": "2025-07-01 09:05:00", "open": 126, "high": 128, "low": 125, "close": 127, "volume": 2700},
            {"time": "2025-07-01 09:10:00", "open": 127, "high": 129, "low": 126, "close": 128, "volume": 2800},
            {"time": "2025-07-01 09:15:00", "open": 128, "high": 130, "low": 127, "close": 129, "volume": 2900},
            {"time": "2025-07-01 09:20:00", "open": 129, "high": 131, "low": 128, "close": 130, "volume": 3000}
        ]
    }
    
    response = requests.post(
        f"{API_URL}/analyze",
        json=example_request,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        results = response.json()
        print("✅ Example Analysis Results:")
        for indicator, value in results.items():
            print(f"   {indicator}: {value}")
    else:
        print(f"❌ Example analysis failed: {response.status_code}")
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    test_api()
