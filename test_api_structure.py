#!/usr/bin/env python3
"""Test the API response includes recent_patterns_with_timestamps key."""

import requests
import json
import numpy as np

def create_pattern_rich_data():
    """Create test data with multiple clear patterns."""
    
    base_price = 100.0
    data_points = []
    
    # Create 20 data points with specific patterns
    for i in range(20):
        hour = i % 24
        day = 1 + (i // 24)
        time = f"2025-01-{day:02d}T{hour:02d}:00:00"
        
        trend_price = base_price + i * 0.4
        
        if i == 3:
            # DOJI at 03:00
            open_price = trend_price
            close_price = trend_price + 0.02
            high_price = trend_price + 0.6
            low_price = trend_price - 0.6
        elif i == 7:
            # HAMMER at 07:00
            open_price = trend_price - 0.1
            close_price = trend_price
            high_price = trend_price + 0.2
            low_price = trend_price - 1.2
        elif i == 12:
            # SHOOTING STAR at 12:00
            open_price = trend_price
            close_price = trend_price - 0.15
            high_price = trend_price + 1.3
            low_price = trend_price - 0.2
        elif i == 16:
            # ENGULFING at 16:00
            if i > 0:
                prev_data = data_points[-1]
                open_price = max(prev_data["open"], prev_data["close"]) + 0.4
                close_price = min(prev_data["open"], prev_data["close"]) - 0.4
                high_price = open_price + 0.1
                low_price = close_price - 0.1
            else:
                open_price = trend_price + 0.3
                close_price = trend_price - 0.3
                high_price = trend_price + 0.5
                low_price = trend_price - 0.5
        else:
            # Normal candles
            noise = np.random.normal(0, 0.15)
            open_price = trend_price + noise
            close_price = trend_price + noise + np.random.normal(0, 0.2)
            high_price = max(open_price, close_price) + abs(np.random.normal(0, 0.15))
            low_price = min(open_price, close_price) - abs(np.random.normal(0, 0.15))
        
        volume = int(1000 + np.random.randint(0, 200))
        
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
        "indicators": {
            "EMA": [12]
        },
        "include_patterns": True
    }

def test_api_response_structure():
    print("🧪 Testing API Response Structure with Recent Patterns Timestamps")
    print("="*70)
    
    test_data = create_pattern_rich_data()
    
    print(f"📊 Data points: {len(test_data['ohlc_data'])}")
    print(f"🕒 Time range: {test_data['ohlc_data'][0]['time']} to {test_data['ohlc_data'][-1]['time']}")
    
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
            
            print(f"\n📋 API Response Structure:")
            print(f"Main keys: {list(result.keys())}")
            print(f"Data keys: {list(data.keys())}")
            
            # Check patterns section
            patterns_data = data.get("candlestick_patterns", {})
            if patterns_data:
                print(f"\n🕯️ Candlestick Patterns Section:")
                pattern_keys = list(patterns_data.keys())
                print(f"Pattern keys: {pattern_keys}")
                
                # Check if recent_patterns_with_timestamps is included
                if "recent_patterns_with_timestamps" in patterns_data:
                    recent_patterns = patterns_data["recent_patterns_with_timestamps"]
                    print(f"\n✅ RECENT PATTERNS WITH TIMESTAMPS FOUND!")
                    print(f"📊 Number of recent patterns: {len(recent_patterns)}")
                    
                    if recent_patterns:
                        print(f"\n🕒 Recent Pattern Details:")
                        for i, pattern in enumerate(recent_patterns, 1):
                            direction_icon = "🟢" if pattern.get('direction') == 'Bullish' else "🔴"
                            print(f"   {i}. {direction_icon} {pattern.get('pattern', 'Unknown').upper()}")
                            print(f"      📅 Timestamp: {pattern.get('timestamp', 'N/A')}")
                            print(f"      📊 Direction: {pattern.get('direction', 'N/A')}")
                            print(f"      💪 Strength: {pattern.get('strength', 'N/A')}")
                            print()
                    else:
                        print("   ℹ️ No recent patterns in the data")
                else:
                    print("❌ recent_patterns_with_timestamps key NOT FOUND in response!")
                    print(f"Available keys: {pattern_keys}")
                
                # Also check if it's in signals (as backup)
                signals = patterns_data.get("signals", {})
                if signals and "recent_patterns" in signals:
                    recent_in_signals = signals["recent_patterns"]
                    print(f"\n📡 Recent patterns also available in signals: {len(recent_in_signals)} items")
                
                # Count detected patterns
                detected_patterns = patterns_data.get("detected_patterns", {})
                detected_count = 0
                for name, data_info in detected_patterns.items():
                    if isinstance(data_info, dict) and 'status' in data_info:
                        if data_info['status'] != "Not Detected":
                            detected_count += 1
                    elif isinstance(data_info, str) and data_info != "Not Detected":
                        detected_count += 1
                
                print(f"\n📈 Pattern Detection Summary:")
                print(f"   🎯 Total patterns detected: {detected_count}")
                print(f"   📊 Total patterns checked: {len(detected_patterns)}")
                
                # Show overall signals
                if signals:
                    print(f"\n📡 Overall Market Signal:")
                    print(f"   🎯 Signal: {signals.get('overall_signal', 'N/A').upper()}")
                    print(f"   💪 Strength: {signals.get('signal_strength', 'N/A').upper()}")
                    print(f"   📊 Total occurrences: {signals.get('total_occurrences', 0)}")
            else:
                print("❌ No candlestick_patterns data found in response")
            
            # Show market info
            market_info = data.get("market_info", {})
            if market_info:
                print(f"\n💹 Market Info:")
                print(f"   💰 Price: ${market_info.get('current_price', 'N/A'):.2f}")
                print(f"   🕒 Timestamp: {market_info.get('timestamp', 'N/A')}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api_response_structure()
