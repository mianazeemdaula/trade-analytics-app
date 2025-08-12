#!/usr/bin/env python3
"""Test the API recent_patterns_with_timestamps feature."""

import requests
import json

def test_recent_patterns_key():
    print("🧪 Testing recent_patterns_with_timestamps API Feature")
    print("="*55)
    
    # Create test data with multiple patterns
    test_data = {
        "ohlc_data": [
            {"time": "2025-01-01T09:00:00", "open": 100.0, "high": 101.5, "low": 99.5, "close": 101.0, "volume": 1000},
            {"time": "2025-01-01T10:00:00", "open": 101.0, "high": 102.5, "low": 100.2, "close": 102.0, "volume": 1100},
            {"time": "2025-01-01T11:00:00", "open": 102.0, "high": 103.8, "low": 101.0, "close": 103.0, "volume": 1200},
            {"time": "2025-01-01T12:00:00", "open": 103.0, "high": 104.2, "low": 102.5, "close": 104.0, "volume": 1300},
            {"time": "2025-01-01T13:00:00", "open": 104.0, "high": 105.8, "low": 103.2, "close": 105.0, "volume": 1400},
            {"time": "2025-01-01T14:00:00", "open": 105.0, "high": 106.2, "low": 104.5, "close": 106.0, "volume": 1500},
            {"time": "2025-01-01T15:00:00", "open": 106.0, "high": 107.5, "low": 105.8, "close": 107.0, "volume": 1600},
            {"time": "2025-01-01T16:00:00", "open": 107.0, "high": 108.0, "low": 106.5, "close": 107.05, "volume": 1700},
            {"time": "2025-01-01T17:00:00", "open": 107.05, "high": 108.2, "low": 106.8, "close": 107.8, "volume": 1800},
            {"time": "2025-01-01T18:00:00", "open": 107.8, "high": 109.0, "low": 107.2, "close": 108.5, "volume": 1900}
        ],
        "indicators": {
            "EMA": [12]
        },
        "include_patterns": True
    }
    
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
            
            print(f"\n📋 API Response Structure:")
            print(f"✅ Candlestick patterns keys: {list(patterns_data.keys())}")
            
            # Check for the new key
            if "recent_patterns_with_timestamps" in patterns_data:
                recent_patterns = patterns_data["recent_patterns_with_timestamps"]
                print(f"\n🎯 SUCCESS! recent_patterns_with_timestamps found!")
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
                    print("   ℹ️ Empty recent patterns list (no patterns detected)")
            else:
                print("❌ recent_patterns_with_timestamps key NOT found!")
            
            # Show general stats
            detected_patterns = patterns_data.get("detected_patterns", {})
            pattern_count = 0
            for name, data_info in detected_patterns.items():
                if isinstance(data_info, dict) and 'status' in data_info:
                    if data_info['status'] != "Not Detected":
                        pattern_count += 1
                elif isinstance(data_info, str) and data_info != "Not Detected":
                    pattern_count += 1
            
            print(f"📈 Pattern Summary: {pattern_count} patterns detected out of {len(detected_patterns)} checked")
            
            # Show signals summary
            signals = patterns_data.get("signals", {})
            if signals:
                print(f"📡 Market Signal: {signals.get('overall_signal', 'N/A').upper()} ({signals.get('signal_strength', 'N/A')})")
                print(f"📊 Total occurrences: {signals.get('total_occurrences', 0)}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response text: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_recent_patterns_key()
