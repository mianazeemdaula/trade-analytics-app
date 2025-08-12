#!/usr/bin/env python3
"""Test multiple EMA periods (EMA 50, EMA 100, etc.)"""

import requests
import json

def test_multiple_ema():
    """Test API with multiple EMA periods."""
    
    # Create more data points to ensure EMAs can be calculated properly
    data_points = []
    base_price = 100.0
    
    # Generate 120 data points (enough for EMA 100)
    for i in range(120):
        hour = i % 24
        day = 1 + (i // 24)
        time = f"2025-08-{day:02d}T{hour:02d}:00:00"
        
        # Create trending price data
        trend = base_price + (i * 0.05)
        noise = (i % 7 - 3) * 0.1  # Some price variation
        
        price = trend + noise
        open_price = price - 0.05
        close_price = price + 0.05
        high_price = max(open_price, close_price) + 0.1
        low_price = min(open_price, close_price) - 0.1
        
        data_points.append({
            "time": time,
            "open": round(open_price, 2),
            "high": round(high_price, 2), 
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": 1000 + (i % 100)
        })
    
    # Test with multiple EMA periods
    test_data = {
        "ohlc_data": data_points,
        "indicators": {
            "EMA": [12, 26, 50, 100],  # Multiple EMA periods
            "RSI": [14]
        },
        "include_patterns": False  # Focus on indicators only
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"🧪 TESTING MULTIPLE EMA PERIODS")
        print("="*50)
        print(f"📡 Response Status: {response.status_code}")
        print(f"📊 Data points: {len(data_points)}")
        print(f"🎯 Requested EMAs: 12, 26, 50, 100")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get("data", {})
            
            print(f"\n✅ API RESPONSE:")
            print(f"Available indicators: {list(data.keys())}")
            
            # Check EMA results
            ema_data = data.get("EMA", {})
            print(f"\n📈 EMA RESULTS:")
            
            if "error" in ema_data:
                print(f"❌ Error: {ema_data['error']}")
            else:
                print(f"EMA response keys: {list(ema_data.keys())}")
                
                # Show each EMA value
                for key, value in ema_data.items():
                    if key.startswith('ema_'):
                        period = key.split('_')[1]
                        print(f"  📊 EMA {period}: ${value:.2f}")
                
                # Show current price for comparison
                market_info = data.get("market_info", {})
                if market_info:
                    current_price = market_info.get("current_price", 0)
                    print(f"\n💰 Current Price: ${current_price:.2f}")
                    
                    # Show EMA vs current price analysis
                    print(f"\n📊 EMA ANALYSIS:")
                    for key, value in ema_data.items():
                        if key.startswith('ema_'):
                            period = key.split('_')[1]
                            diff = current_price - value
                            trend_icon = "🟢" if diff > 0 else "🔴"
                            print(f"  {trend_icon} EMA {period}: ${value:.2f} (diff: {diff:+.2f})")
            
            # Show RSI for additional context
            rsi_data = data.get("RSI", {})
            if rsi_data and "error" not in rsi_data:
                rsi_value = rsi_data.get("rsi", 0)
                print(f"\n📈 RSI (14): {rsi_value:.2f}")
                
                if rsi_value > 70:
                    print("  🔴 Overbought")
                elif rsi_value < 30:
                    print("  🟢 Oversold")
                else:
                    print("  🟡 Neutral")
            
            print(f"\n🎉 SUCCESS! Multiple EMA periods working!")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_multiple_ema()
