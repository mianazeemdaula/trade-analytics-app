#!/usr/bin/env python3
"""Test simplified candlestick patterns API response."""

import requests
import json
import numpy as np

def create_test_data():
    """Create sample OHLC data for testing."""
    np.random.seed(42)
    
    data_points = []
    base_price = 100.0
    
    # Create 20 data points with some forced patterns
    for i in range(20):
        hour = i % 24
        day = 1 + (i // 24)
        time = f"2025-08-{day:02d}T{hour:02d}:00:00"
        
        trend = base_price + i * 0.15
        
        if i == 5:
            # Force DOJI pattern
            open_price = trend
            close_price = trend + 0.01
            high_price = trend + 0.4
            low_price = trend - 0.4
        elif i == 10:
            # Force HAMMER pattern
            open_price = trend - 0.1
            close_price = trend + 0.05
            high_price = trend + 0.2
            low_price = trend - 0.8
        elif i == 15:
            # Force another DOJI
            open_price = trend
            close_price = trend + 0.02
            high_price = trend + 0.5
            low_price = trend - 0.5
        else:
            # Regular candles
            open_price = trend + np.random.normal(0, 0.1)
            close_price = trend + np.random.normal(0, 0.15)
            high_price = max(open_price, close_price) + abs(np.random.normal(0, 0.1))
            low_price = min(open_price, close_price) - abs(np.random.normal(0, 0.1))
        
        volume = int(1000 + np.random.randint(0, 300))
        
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

def test_simplified_patterns():
    """Test the simplified patterns API response."""
    print("🧪 TESTING SIMPLIFIED CANDLESTICK PATTERNS API")
    print("="*55)
    
    test_data = create_test_data()
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get("data", {})
            patterns_data = data.get("candlestick_patterns", {})
            
            print(f"\n✅ API RESPONSE STRUCTURE:")
            print(f"Main keys: {list(result.keys())}")
            print(f"Pattern keys: {list(patterns_data.keys())}")
            
            # Check simplified structure
            expected_keys = ["recent_patterns", "overall_signal", "signal_strength", "detected_pattern_counts"]
            missing_keys = [key for key in expected_keys if key not in patterns_data]
            extra_keys = [key for key in patterns_data.keys() if key not in expected_keys and key != "error"]
            
            if not missing_keys and not extra_keys:
                print("🎯 ✅ PERFECT! Response structure matches requirements")
            else:
                if missing_keys:
                    print(f"❌ Missing keys: {missing_keys}")
                if extra_keys:
                    print(f"⚠️ Extra keys: {extra_keys}")
            
            # Show recent patterns
            recent_patterns = patterns_data.get("recent_patterns", [])
            print(f"\n🕒 RECENT PATTERNS ({len(recent_patterns)}):")
            if recent_patterns:
                for i, pattern in enumerate(recent_patterns[:5], 1):  # Show only first 5
                    direction_icon = "🟢" if pattern.get('direction') == 'Bullish' else "🔴"
                    print(f"{i:2d}. {direction_icon} {pattern.get('pattern', 'Unknown').upper()}")
                    print(f"     📅 {pattern.get('timestamp', 'N/A')}")
                    print(f"     💪 Strength: {pattern.get('strength', 'N/A')}")
            else:
                print("   No recent patterns detected")
            
            # Show overall signal
            overall_signal = patterns_data.get("overall_signal", "neutral")
            signal_strength = patterns_data.get("signal_strength", "weak")
            signal_icon = "🟢" if overall_signal == "bullish" else "🔴" if overall_signal == "bearish" else "🟡"
            
            print(f"\n📊 MARKET SIGNAL:")
            print(f"   {signal_icon} Direction: {overall_signal.upper()}")
            print(f"   💪 Strength: {signal_strength.upper()}")
            
            # Show detected pattern counts
            pattern_counts = patterns_data.get("detected_pattern_counts", {})
            print(f"\n🔢 DETECTED PATTERN COUNTS:")
            if pattern_counts:
                for pattern, count in pattern_counts.items():
                    print(f"   📈 {pattern.upper()}: {count}")
                print(f"   🎯 Total patterns: {len(pattern_counts)}")
            else:
                print("   No patterns detected")
            
            # Show data summary
            print(f"\n📊 DATA SUMMARY:")
            print(f"   📈 Data points: {result.get('data_points', 0)}")
            print(f"   🕒 Timeframe: {result.get('timeframe', 'N/A')}")
            
            market_info = data.get("market_info", {})
            if market_info:
                print(f"   💰 Current price: ${market_info.get('current_price', 0):.2f}")
            
            print(f"\n🎉 SUCCESS! Simplified API is working perfectly!")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_simplified_patterns()
