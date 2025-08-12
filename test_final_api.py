#!/usr/bin/env python3
"""Final test demonstrating recent_patterns_with_timestamps feature."""

import requests
import json
import numpy as np

def create_pattern_data():
    """Create data designed to trigger multiple patterns."""
    
    # Use numpy for reproducible patterns
    np.random.seed(42)
    
    data_points = []
    base_price = 100.0
    
    # Create 30 data points with forced patterns
    for i in range(30):
        hour = i % 24
        day = 1 + (i // 24)
        time = f"2025-01-{day:02d}T{hour:02d}:00:00"
        
        trend = base_price + i * 0.2
        
        if i == 5:
            # Force DOJI pattern
            open_price = trend
            close_price = trend + 0.01  # Very small body
            high_price = trend + 0.5
            low_price = trend - 0.5
        elif i == 10:
            # Force HAMMER pattern
            open_price = trend - 0.1
            close_price = trend + 0.05  # Small bullish body
            high_price = trend + 0.2
            low_price = trend - 1.0  # Long lower shadow
        elif i == 15:
            # Force SHOOTING STAR
            open_price = trend
            close_price = trend - 0.1  # Small bearish body
            high_price = trend + 1.0  # Long upper shadow
            low_price = trend - 0.2
        elif i == 20:
            # Force ENGULFING pattern
            if len(data_points) > 0:
                prev = data_points[-1]
                open_price = max(prev["open"], prev["close"]) + 0.2
                close_price = min(prev["open"], prev["close"]) - 0.2
                high_price = open_price + 0.1
                low_price = close_price - 0.1
            else:
                open_price = trend + 0.3
                close_price = trend - 0.3
                high_price = trend + 0.4
                low_price = trend - 0.4
        elif i == 25:
            # Force another DOJI
            open_price = trend
            close_price = trend + 0.02
            high_price = trend + 0.6
            low_price = trend - 0.6
        else:
            # Regular candles with some randomness
            open_price = trend + np.random.normal(0, 0.1)
            close_price = trend + np.random.normal(0, 0.2)
            high_price = max(open_price, close_price) + abs(np.random.normal(0, 0.1))
            low_price = min(open_price, close_price) - abs(np.random.normal(0, 0.1))
        
        volume = int(1000 + np.random.randint(0, 500))
        
        data_points.append({
            "time": time,
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": volume
        })
    
    return {
        "ohlc_data": data_points,
        "indicators": {"EMA": [12]},
        "include_patterns": True
    }

def test_final_api():
    print("🧪 FINAL TEST: recent_patterns_with_timestamps Feature")
    print("="*60)
    
    test_data = create_pattern_data()
    
    print(f"📊 Data points: {len(test_data['ohlc_data'])}")
    print(f"🕒 Time span: {test_data['ohlc_data'][0]['time']} to {test_data['ohlc_data'][-1]['time']}")
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get("data", {})
            patterns_data = data.get("candlestick_patterns", {})
            
            print(f"\n✅ API RESPONSE STRUCTURE VERIFICATION:")
            print(f"Main response keys: {list(result.keys())}")
            print(f"Patterns section keys: {list(patterns_data.keys())}")
            
            # Verify our new key exists
            if "recent_patterns_with_timestamps" in patterns_data:
                print(f"\n🎯 ✅ SUCCESS! recent_patterns_with_timestamps KEY FOUND!")
                
                recent_patterns = patterns_data["recent_patterns_with_timestamps"]
                print(f"📊 Recent patterns count: {len(recent_patterns)}")
                
                if recent_patterns:
                    print(f"\n🕒 RECENT PATTERNS WITH TIMESTAMPS:")
                    print("-" * 45)
                    for i, pattern in enumerate(recent_patterns, 1):
                        direction_icon = "🟢" if pattern.get('direction') == 'Bullish' else "🔴"
                        print(f"{i:2d}. {direction_icon} {pattern.get('pattern', 'Unknown').upper()}")
                        print(f"     📅 When: {pattern.get('timestamp', 'N/A')}")
                        print(f"     📊 Type: {pattern.get('direction', 'N/A')}")
                        print(f"     💪 Strength: {pattern.get('strength', 'N/A')}")
                        print()
                    
                    print(f"🎯 FEATURE WORKING PERFECTLY! ✅")
                else:
                    print("ℹ️ No recent patterns detected (empty list)")
            else:
                print("❌ recent_patterns_with_timestamps key MISSING!")
            
            # Show quick pattern summary
            detected_patterns = patterns_data.get("detected_patterns", {})
            detected_count = sum(1 for name, data in detected_patterns.items() 
                               if (isinstance(data, dict) and data.get('status', '') != "Not Detected") or
                                  (isinstance(data, str) and data != "Not Detected"))
            
            print(f"\n📈 PATTERN DETECTION SUMMARY:")
            print(f"🎯 Patterns detected: {detected_count}/{len(detected_patterns)}")
            
            # Show signals
            signals = patterns_data.get("signals", {})
            if signals:
                print(f"📡 Market signal: {signals.get('overall_signal', 'N/A').upper()}")
                print(f"💪 Signal strength: {signals.get('signal_strength', 'N/A').upper()}")
                print(f"📊 Total occurrences: {signals.get('total_occurrences', 0)}")
            
            # Market info
            market_info = data.get("market_info", {})
            if market_info:
                print(f"\n💹 CURRENT MARKET:")
                print(f"💰 Price: ${market_info.get('current_price', 0):.2f}")
                print(f"🕒 Time: {market_info.get('timestamp', 'N/A')}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_final_api()
