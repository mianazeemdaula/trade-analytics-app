"""
Simple Binary Options Prediction Example

This script shows how to use the Binary Options prediction API
for real trading scenarios.
"""

import requests
import json

# API Configuration
API_URL = "http://localhost:8001"

def simple_prediction_example():
    """Simple example of binary options prediction"""
    
    # Sample OHLC data (you would replace this with real market data)
    sample_data = [
        {"time": "2025-08-03 10:00:00", "open": 1.2500, "high": 1.2520, "low": 1.2485, "close": 1.2510, "volume": 1500},
        {"time": "2025-08-03 10:01:00", "open": 1.2510, "high": 1.2525, "low": 1.2505, "close": 1.2518, "volume": 1600},
        {"time": "2025-08-03 10:02:00", "open": 1.2518, "high": 1.2535, "low": 1.2515, "close": 1.2528, "volume": 1400},
        {"time": "2025-08-03 10:03:00", "open": 1.2528, "high": 1.2540, "low": 1.2520, "close": 1.2535, "volume": 1700},
        {"time": "2025-08-03 10:04:00", "open": 1.2535, "high": 1.2545, "low": 1.2530, "close": 1.2538, "volume": 1550},
        # Add more data points here (minimum 20 recommended)
        # ... continuing the pattern for better predictions
    ]
    
    # Add more realistic data to reach minimum requirement
    base_price = 1.2538
    for i in range(5, 25):  # Add 20 more data points
        import random
        from datetime import datetime, timedelta
        
        # Simple price evolution
        price_change = random.uniform(-0.0015, 0.0015)
        base_price = max(1.2400, min(1.2600, base_price + price_change))
        
        open_price = base_price
        high_price = open_price + random.uniform(0, 0.002)
        low_price = open_price - random.uniform(0, 0.002)
        close_price = random.uniform(low_price, high_price)
        volume = random.randint(1000, 2000)
        
        time_str = (datetime(2025, 8, 3, 10, 0) + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S")
        
        sample_data.append({
            "time": time_str,
            "open": round(open_price, 4),
            "high": round(high_price, 4),
            "low": round(low_price, 4),
            "close": round(close_price, 4),
            "volume": volume
        })
        
        base_price = close_price
    
    # Prediction request
    request_data = {
        "ohlc_data": sample_data,
        "prediction_timeframe": 2,  # Predict next 2 candles
        "confidence_threshold": 0.6  # 60% minimum confidence
    }
    
    print("🎯 Making Binary Options Prediction...")
    print(f"📊 Analyzing {len(sample_data)} data points")
    print(f"💰 Current Price: ${sample_data[-1]['close']}")
    
    try:
        response = requests.post(
            f"{API_URL}/predict-binary-options",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract key information
            prediction = result["prediction"]
            advice = result["trading_advice"]
            signals = result["signal_breakdown"]
            
            print("\n" + "="*50)
            print("📈 BINARY OPTIONS PREDICTION")
            print("="*50)
            
            print(f"🎯 Direction: {prediction['direction']}")
            print(f"📊 Confidence: {prediction['confidence']:.1%}")
            print(f"⚠️  Risk Level: {prediction['risk_level']}")
            print(f"⏰ Timeframe: Next {prediction['timeframe_candles']} candles")
            
            print(f"\n💡 Trading Recommendation: {advice['recommended_action']}")
            
            # Signal analysis
            print(f"\n📊 Signal Analysis:")
            print(f"   🟢 Bullish Signals: {signals['bullish_signals']} (Weight: {signals['bullish_weight']})")
            print(f"   🔴 Bearish Signals: {signals['bearish_signals']} (Weight: {signals['bearish_weight']})")
            
            # Top signals
            detailed_signals = result["detailed_signals"]
            if detailed_signals:
                print(f"\n🔍 Key Signals:")
                for signal in sorted(detailed_signals, key=lambda x: x['weight'], reverse=True)[:3]:
                    emoji = "🟢" if signal['direction'] == 'bullish' else "🔴"
                    print(f"   {emoji} {signal['indicator'].upper()}: {signal['reason']}")
            
            # Technical analysis summary
            if 'technical_analysis' in result:
                ta = result['technical_analysis']
                print(f"\n📉 Technical Indicators:")
                if 'rsi' in ta:
                    rsi_status = "Overbought" if ta['rsi'] > 70 else "Oversold" if ta['rsi'] < 30 else "Neutral"
                    print(f"   RSI: {ta['rsi']:.1f} ({rsi_status})")
                if 'moving_averages' in ta:
                    ma = ta['moving_averages']
                    trend = "Above" if ma['price'] > ma['sma_20'] else "Below"
                    print(f"   Price vs SMA20: {trend} (Price: {ma['price']}, SMA20: {ma['sma_20']})")
            
            print("\n" + "="*50)
            
            # Risk warning
            print("⚠️  RISK WARNING:")
            print("   • This is for educational/testing purposes only")
            print("   • Binary options trading involves significant risk")
            print("   • Never risk more than you can afford to lose")
            print("   • Always use proper risk management")
            print("   • Consider multiple confirmations before trading")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running!")
    except Exception as e:
        print(f"❌ Error: {e}")

def trading_scenario_example():
    """Example of how to use prediction in a trading scenario"""
    print("\n" + "="*60)
    print("📈 TRADING SCENARIO EXAMPLE")
    print("="*60)
    
    print("""
💡 How to use Binary Options Prediction in Trading:

1. 📊 COLLECT DATA:
   • Get recent OHLC data (at least 20-30 points)
   • Ensure data quality and completeness
   • Use appropriate timeframe (1min, 5min, etc.)

2. 🎯 MAKE PREDICTION:
   • Call /predict-binary-options endpoint
   • Set appropriate confidence threshold (0.6-0.8)
   • Choose prediction timeframe (1-5 candles)

3. 📈 ANALYZE RESULTS:
   • Check prediction confidence and risk level
   • Review detailed signals and their weights
   • Consider technical analysis summary

4. 💰 TRADING DECISION:
   • HIGH confidence (>75%) + LOW risk = Consider trade
   • MEDIUM confidence (60-75%) = Proceed with caution
   • LOW confidence (<60%) = Wait for better setup

5. ⚠️  RISK MANAGEMENT:
   • Never risk more than 2-5% of account per trade
   • Use appropriate position sizing
   • Set stop-loss levels
   • Monitor trade closely

6. 📊 EXAMPLE TRADING RULES:
   • Only trade when confidence > 70%
   • Require at least 3 bullish/bearish signals
   • Avoid trading during high volatility periods
   • Confirm with additional analysis tools
    """)

if __name__ == "__main__":
    print("🚀 Binary Options Prediction Example")
    print("====================================")
    
    # Check API status
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            print("✅ API is running")
            simple_prediction_example()
            trading_scenario_example()
        else:
            print("❌ API error")
    except:
        print("❌ API is not running. Start with: uvicorn main:app --reload --port 8001")
