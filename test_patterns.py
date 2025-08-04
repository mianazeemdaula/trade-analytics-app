"""
Enhanced test script for the Technical Analysis API with candlestick patterns

This script demonstrates how to use the API with both technical indicators
and candlestick pattern recognition.
"""

import requests
import json
from datetime import datetime, timedelta

# API endpoint
API_URL = "http://localhost:8001"

def test_candlestick_patterns_endpoint():
    """Test the candlestick patterns information endpoint"""
    print("📊 Testing Candlestick Patterns Endpoint...")
    
    response = requests.get(f"{API_URL}/candlestick-patterns")
    if response.status_code == 200:
        data = response.json()
        print("✅ Candlestick Patterns Endpoint Working")
        print(f"   Total Categorized Patterns: {data['pattern_count']['total_categorized']}")
        print(f"   Total TA-Lib Patterns Available: {data['pattern_count']['total_ta_lib_available']}")
        
        print("\n📈 Pattern Categories:")
        for category, patterns in data['patterns_by_category'].items():
            print(f"   {category.replace('_', ' ').title()}: {len(patterns)} patterns")
            
        print("\n🔍 Sample Reversal Patterns:")
        for name, info in list(data['patterns_by_category']['reversal_patterns'].items())[:5]:
            print(f"   {info['name']}: {info['type']} - {info['reliability']} reliability")
            
        return True
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return False

def generate_pattern_test_data():
    """Generate OHLC data that might show some candlestick patterns"""
    base_date = datetime.now() - timedelta(hours=24)
    sample_data = []
    
    # Create some data with potential patterns
    patterns_data = [
        # Normal uptrend
        {"open": 100, "high": 102, "low": 99, "close": 101.5, "volume": 1000},
        {"open": 101.5, "high": 103, "low": 101, "close": 102.8, "volume": 1100},
        {"open": 102.8, "high": 104, "low": 102.5, "close": 103.5, "volume": 1200},
        
        # Potential doji pattern
        {"open": 103.5, "high": 104.2, "low": 102.8, "close": 103.4, "volume": 900},
        
        # Potential hammer pattern (small body, long lower shadow)
        {"open": 103, "high": 103.2, "low": 101, "close": 102.8, "volume": 1500},
        
        # Continuation
        {"open": 102.8, "high": 104.5, "low": 102.5, "close": 104.2, "volume": 1300},
        {"open": 104.2, "high": 105.8, "low": 104, "close": 105.5, "volume": 1400},
        
        # Potential shooting star (small body, long upper shadow)
        {"open": 105.5, "high": 108, "low": 105.2, "close": 105.8, "volume": 1600},
        
        # Potential bearish engulfing
        {"open": 105.8, "high": 106, "low": 103.5, "close": 103.8, "volume": 2000},
        
        # More data for better pattern detection
        {"open": 103.8, "high": 105, "low": 103.2, "close": 104.5, "volume": 1200},
        {"open": 104.5, "high": 106, "low": 104, "close": 105.2, "volume": 1100},
        {"open": 105.2, "high": 106.5, "low": 104.8, "close": 106, "volume": 1300},
        {"open": 106, "high": 107, "low": 105.5, "close": 106.8, "volume": 1250},
        {"open": 106.8, "high": 108, "low": 106.5, "close": 107.5, "volume": 1400},
        {"open": 107.5, "high": 108.5, "low": 107, "close": 108.2, "volume": 1350},
    ]
    
    for i, candle in enumerate(patterns_data):
        current_time = base_date + timedelta(hours=i)
        sample_data.append({
            "time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "open": candle["open"],
            "high": candle["high"],
            "low": candle["low"],
            "close": candle["close"],
            "volume": candle["volume"]
        })
    
    return sample_data

def test_comprehensive_analysis():
    """Test the analysis endpoint with both indicators and candlestick patterns"""
    print("\n📈 Testing Comprehensive Analysis (Indicators + Patterns)...")
    
    sample_data = generate_pattern_test_data()
    
    test_request = {
        "indicators": {
            "rsi": [14],
            "sma": [10],
            "ema": [10]
        },
        "candlestick_patterns": [
            "doji", "hammer", "shooting_star", "engulfing", 
            "harami", "marubozu", "spinning_top", "inside",
            "morning_star", "evening_star", "dragonfly_doji"
        ],
        "ohlc_data": sample_data
    }
    
    response = requests.post(
        f"{API_URL}/analyze",
        json=test_request,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        results = response.json()
        print("✅ Comprehensive Analysis Results:")
        
        # Separate indicators and patterns
        indicators = {}
        patterns = {}
        
        for key, value in results.items():
            if key in ['rsi', 'sma', 'ema', 'macd', 'macd_signal', 'bb_upper', 'bb_lower', 'bb_middle']:
                indicators[key] = value
            else:
                patterns[key] = value
        
        if indicators:
            print("\n   📊 Technical Indicators:")
            for indicator, value in indicators.items():
                print(f"      {indicator.upper()}: {value}")
        
        if patterns:
            print("\n   🕯️  Candlestick Patterns:")
            for pattern, signal in patterns.items():
                if signal != "Not Detected":
                    emoji = "🟢" if signal == "Bullish" else "🔴" if signal == "Bearish" else "⚪"
                    print(f"      {emoji} {pattern.replace('_', ' ').title()}: {signal}")
            
            # Show not detected patterns
            not_detected = [p for p, s in patterns.items() if s == "Not Detected"]
            if not_detected:
                print(f"\n   ⚫ Not Detected: {', '.join(not_detected)}")
                
    else:
        print(f"❌ Analysis failed: {response.status_code}")
        print(f"   Error: {response.text}")

def test_pattern_specific_analysis():
    """Test with specific patterns that are more likely to be detected"""
    print("\n🎯 Testing Pattern-Specific Analysis...")
    
    # Create data specifically designed to trigger certain patterns
    specific_data = [
        # Setup for potential inside bar pattern
        {"time": "2025-08-03 10:00:00", "open": 100, "high": 105, "low": 95, "close": 102, "volume": 2000},
        {"time": "2025-08-03 10:05:00", "open": 102, "high": 103, "low": 101, "close": 101.5, "volume": 1000},  # Inside bar
        
        # Setup for doji
        {"time": "2025-08-03 10:10:00", "open": 101.5, "high": 102.5, "low": 100.5, "close": 101.4, "volume": 1200},  # Doji-like
        
        # More data
        {"time": "2025-08-03 10:15:00", "open": 101.4, "high": 103, "low": 101, "close": 102.8, "volume": 1300},
        {"time": "2025-08-03 10:20:00", "open": 102.8, "high": 104, "low": 102.5, "close": 103.5, "volume": 1400},
    ]
    
    test_request = {
        "indicators": {
            "sma": [3]  # Short period for limited data
        },
        "candlestick_patterns": ["inside", "doji"],
        "ohlc_data": specific_data
    }
    
    response = requests.post(f"{API_URL}/analyze", json=test_request)
    
    if response.status_code == 200:
        results = response.json()
        print("✅ Pattern-Specific Results:")
        for key, value in results.items():
            print(f"   {key}: {value}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

def main():
    """Run all tests"""
    print("🚀 Testing Enhanced Technical Analysis API with Candlestick Patterns...")
    
    # Test if API is running
    try:
        response = requests.get(f"{API_URL}/")
        print(f"✅ API Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ API is not running. Please start the server first!")
        return
    
    # Run tests
    if test_candlestick_patterns_endpoint():
        test_comprehensive_analysis()
        test_pattern_specific_analysis()
    
    print("\n🎉 Testing completed!")
    print(f"📚 View API documentation at: {API_URL}/docs")
    print(f"🕯️  View candlestick patterns at: {API_URL}/candlestick-patterns")

if __name__ == "__main__":
    main()
