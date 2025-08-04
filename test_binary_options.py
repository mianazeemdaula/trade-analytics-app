"""
Binary Options Prediction Test Script

This script tests the binary options prediction functionality of the Technical Analysis API.
"""

import requests
import json
import random
from datetime import datetime, timedelta

# API endpoint
API_URL = "http://localhost:8001"

def generate_realistic_market_data(trend='mixed', volatility='medium', days=30):
    """Generate realistic market data for testing"""
    base_date = datetime.now() - timedelta(days=days)
    data = []
    
    # Starting values
    base_price = 100.0
    volume_base = 1500
    
    # Trend and volatility settings
    if trend == 'bullish':
        trend_factor = 0.002  # Slight upward bias
    elif trend == 'bearish':
        trend_factor = -0.002  # Slight downward bias
    else:
        trend_factor = 0  # No bias
    
    if volatility == 'high':
        vol_factor = 0.03
    elif volatility == 'low':
        vol_factor = 0.01
    else:
        vol_factor = 0.02
    
    for i in range(days * 24):  # Hourly data
        current_time = base_date + timedelta(hours=i)
        
        # Add trend and random walk
        price_change = trend_factor + random.uniform(-vol_factor, vol_factor)
        base_price = max(10, base_price * (1 + price_change))
        
        # Generate OHLC
        open_price = base_price
        
        # Random intraday movement
        intraday_range = base_price * random.uniform(0.005, 0.025)
        high_price = open_price + random.uniform(0, intraday_range)
        low_price = open_price - random.uniform(0, intraday_range)
        
        # Close price influenced by overall trend
        close_bias = trend_factor * 0.5
        close_price = open_price + (random.uniform(-intraday_range/2, intraday_range/2) + base_price * close_bias)
        close_price = max(low_price, min(high_price, close_price))
        
        # Ensure OHLC validity
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        # Volume with some correlation to price movement
        price_move = abs(close_price - open_price) / open_price
        volume = int(volume_base * (1 + price_move * 2) * random.uniform(0.5, 1.5))
        
        data.append({
            "time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "open": round(open_price, 4),
            "high": round(high_price, 4),
            "low": round(low_price, 4),
            "close": round(close_price, 4),
            "volume": volume
        })
        
        base_price = close_price
    
    return data

def test_binary_options_prediction():
    """Test the binary options prediction endpoint"""
    print("🎯 Testing Binary Options Prediction...")
    
    # Test different market conditions
    test_scenarios = [
        {"name": "Bullish Market", "trend": "bullish", "volatility": "medium"},
        {"name": "Bearish Market", "trend": "bearish", "volatility": "medium"},
        {"name": "Sideways Market", "trend": "mixed", "volatility": "low"},
        {"name": "Volatile Market", "trend": "mixed", "volatility": "high"}
    ]
    
    for scenario in test_scenarios:
        print(f"\n📊 Testing: {scenario['name']}")
        
        # Generate test data
        market_data = generate_realistic_market_data(
            trend=scenario['trend'], 
            volatility=scenario['volatility'],
            days=20  # Reduced for faster testing
        )
        
        # Test request
        test_request = {
            "ohlc_data": market_data,
            "prediction_timeframe": 2,
            "confidence_threshold": 0.6
        }
        
        response = requests.post(
            f"{API_URL}/predict-binary-options",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Display results
            prediction = result["prediction"]
            signals = result["signal_breakdown"]
            
            print(f"   🎯 Prediction: {prediction['direction']}")
            print(f"   📈 Confidence: {prediction['confidence']:.1%}")
            print(f"   ⚠️  Risk Level: {prediction['risk_level']}")
            print(f"   📊 Signals: {signals['bullish_signals']} Bullish, {signals['bearish_signals']} Bearish")
            
            # Show top 3 signals
            detailed_signals = result["detailed_signals"]
            if detailed_signals:
                print("   🔍 Top Signals:")
                for signal in sorted(detailed_signals, key=lambda x: x['weight'], reverse=True)[:3]:
                    direction_emoji = "🟢" if signal['direction'] == 'bullish' else "🔴"
                    print(f"      {direction_emoji} {signal['indicator'].upper()}: {signal['reason']} (Weight: {signal['weight']})")
            
            # Trading advice
            advice = result["trading_advice"]
            print(f"   💡 Recommended Action: {advice['recommended_action']}")
            
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n🧪 Testing Edge Cases...")
    
    # Test 1: Insufficient data
    print("\n1. Testing insufficient data...")
    insufficient_data = generate_realistic_market_data(days=1)[:10]  # Only 10 points
    
    response = requests.post(
        f"{API_URL}/predict-binary-options",
        json={"ohlc_data": insufficient_data, "prediction_timeframe": 2, "confidence_threshold": 0.6}
    )
    
    if response.status_code == 400:
        print("   ✅ Correctly rejected insufficient data")
    else:
        print(f"   ❌ Unexpected response: {response.status_code}")
    
    # Test 2: Invalid confidence threshold
    print("\n2. Testing invalid confidence threshold...")
    valid_data = generate_realistic_market_data(days=5)
    
    response = requests.post(
        f"{API_URL}/predict-binary-options",
        json={"ohlc_data": valid_data, "prediction_timeframe": 2, "confidence_threshold": 1.5}
    )
    
    if response.status_code == 400:
        print("   ✅ Correctly rejected invalid confidence threshold")
    else:
        print(f"   ❌ Unexpected response: {response.status_code}")
    
    # Test 3: Valid minimal data
    print("\n3. Testing valid minimal data...")
    minimal_data = generate_realistic_market_data(days=5)  # 5 days = 120 points
    
    response = requests.post(
        f"{API_URL}/predict-binary-options",
        json={"ohlc_data": minimal_data, "prediction_timeframe": 1, "confidence_threshold": 0.5}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Minimal data prediction: {result['prediction']['direction']} with {result['prediction']['confidence']:.1%} confidence")
    else:
        print(f"   ❌ Failed with minimal data: {response.status_code}")

def test_different_timeframes():
    """Test different prediction timeframes"""
    print("\n⏰ Testing Different Timeframes...")
    
    market_data = generate_realistic_market_data(trend='bullish', days=15)
    
    timeframes = [1, 2, 3, 5]
    
    for tf in timeframes:
        print(f"\n   Testing {tf} candle prediction...")
        
        response = requests.post(
            f"{API_URL}/predict-binary-options",
            json={
                "ohlc_data": market_data,
                "prediction_timeframe": tf,
                "confidence_threshold": 0.6
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            pred = result["prediction"]
            print(f"      {tf} candles: {pred['direction']} ({pred['confidence']:.1%} confidence, {pred['risk_level']} risk)")
        else:
            print(f"      ❌ Failed for {tf} candles")

def test_real_time_scenario():
    """Simulate real-time trading scenario"""
    print("\n📈 Real-Time Trading Scenario Test...")
    
    # Generate extended market data
    market_data = generate_realistic_market_data(trend='mixed', volatility='medium', days=25)
    
    # Simulate multiple predictions as new data comes in
    for i in range(3):
        # Use progressively more data (simulate real-time updates)
        data_slice = market_data[:200 + i * 50]
        
        print(f"\n   Prediction #{i+1} (using {len(data_slice)} data points):")
        
        response = requests.post(
            f"{API_URL}/predict-binary-options",
            json={
                "ohlc_data": data_slice,
                "prediction_timeframe": 2,
                "confidence_threshold": 0.65
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            pred = result["prediction"]
            meta = result["metadata"]
            
            print(f"      📊 Last Price: ${meta['last_price']}")
            print(f"      🎯 Prediction: {pred['direction']} (Confidence: {pred['confidence']:.1%})")
            print(f"      📈 Action: {result['trading_advice']['recommended_action']}")
            
            # Show market conditions
            analysis = result["technical_analysis"]
            if 'rsi' in analysis:
                rsi_status = "Overbought" if analysis['rsi'] > 70 else "Oversold" if analysis['rsi'] < 30 else "Neutral"
                print(f"      📉 RSI: {analysis['rsi']:.1f} ({rsi_status})")

def main():
    """Run all binary options tests"""
    print("🚀 Binary Options Prediction API Testing")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print("❌ API responded but with error")
            return
    except requests.exceptions.ConnectionError:
        print("❌ API is not running. Please start the server first!")
        return
    
    # Run all tests
    test_binary_options_prediction()
    test_edge_cases()
    test_different_timeframes()
    test_real_time_scenario()
    
    print("\n" + "=" * 50)
    print("🎉 Binary Options Testing Completed!")
    print(f"📚 API Documentation: {API_URL}/docs")
    print(f"🎯 Binary Options Endpoint: {API_URL}/predict-binary-options")
    
    print("\n💡 Usage Tips:")
    print("   • Use at least 20-30 data points for reliable predictions")
    print("   • Higher confidence threshold = more conservative predictions")
    print("   • Consider multiple timeframes for better accuracy")
    print("   • Always use proper risk management in real trading")

if __name__ == "__main__":
    main()
