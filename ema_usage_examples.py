#!/usr/bin/env python3
"""
Example: How to use different EMA periods (EMA 50, EMA 100, etc.)
"""

import requests
import json

# Example 1: Request EMA 50 and EMA 100
def example_ema_50_100():
    sample_data = {
        "ohlc_data": [
            # You need enough data points for the largest EMA period
            # For EMA 100, you need at least 100+ data points
            {"time": "2025-08-12T10:00:00", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1000},
            {"time": "2025-08-12T11:00:00", "open": 100.5, "high": 101.2, "low": 99.8, "close": 100.8, "volume": 1100},
            # ... (add more data points for real usage)
        ],
        "indicators": {
            "EMA": [50, 100]  # Request EMA 50 and EMA 100
        },
        "include_patterns": False
    }
    
    print("📊 Example 1: EMA 50 and EMA 100")
    print("Request format:")
    print(json.dumps({"indicators": {"EMA": [50, 100]}}, indent=2))

# Example 2: Request multiple EMAs (common trading setup)  
def example_multiple_emas():
    sample_data = {
        "indicators": {
            "EMA": [12, 26, 50, 100, 200]  # Multiple EMAs for comprehensive analysis
        }
    }
    
    print("\n📊 Example 2: Multiple EMAs (12, 26, 50, 100, 200)")
    print("Request format:")
    print(json.dumps(sample_data, indent=2))

# Example 3: Mix EMAs with other indicators
def example_ema_with_others():
    sample_data = {
        "indicators": {
            "EMA": [50, 100],      # EMA 50 and 100
            "RSI": [14],           # RSI 14
            "MACD": [12, 26, 9]    # MACD with standard settings
        }
    }
    
    print("\n📊 Example 3: EMAs with other indicators")
    print("Request format:")
    print(json.dumps(sample_data, indent=2))

def show_expected_response():
    print("\n✅ Expected API Response:")
    response_example = {
        "data": {
            "EMA": {
                "ema_50": 104.78,   # EMA 50 value
                "ema_100": 103.52   # EMA 100 value  
            },
            "RSI": {
                "rsi": 56.00
            }
        }
    }
    print(json.dumps(response_example, indent=2))

if __name__ == "__main__":
    print("🎯 HOW TO GET DIFFERENT EMA PERIODS (EMA 50, EMA 100, etc.)")
    print("="*60)
    
    example_ema_50_100()
    example_multiple_emas() 
    example_ema_with_others()
    show_expected_response()
    
    print("\n💡 KEY POINTS:")
    print("1. Use 'EMA': [50, 100] to get both EMA 50 and EMA 100")
    print("2. Response will have 'ema_50' and 'ema_100' keys")
    print("3. You can request any number of EMA periods: [12, 26, 50, 100, 200]")
    print("4. Make sure you have enough data points (at least 100+ for EMA 100)")
    print("5. Works with other indicators simultaneously")
    
    print("\n🚀 Your API now supports multiple EMA periods!")
