"""
Complete Technical Analysis API Demo

This script demonstrates all features of the Technical Analysis API:
1. Technical Indicators Analysis
2. Candlestick Pattern Recognition  
3. Binary Options Prediction
"""

import requests
import json
import random
from datetime import datetime, timedelta

API_URL = "http://localhost:8001"

def generate_comprehensive_market_data():
    """Generate realistic market data for comprehensive testing"""
    base_date = datetime.now() - timedelta(hours=48)
    data = []
    base_price = 1.2500
    
    for i in range(100):  # 100 data points for comprehensive analysis
        current_time = base_date + timedelta(minutes=i*30)  # 30-minute intervals
        
        # Add realistic price movement
        volatility = 0.001 + random.uniform(0, 0.001)  # Variable volatility
        trend = 0.0002 if i < 50 else -0.0001  # Trend change halfway
        
        price_change = trend + random.uniform(-volatility, volatility)
        new_price = base_price * (1 + price_change)
        
        # Generate OHLC
        open_price = base_price
        close_price = new_price
        
        # Realistic high/low based on volatility
        range_factor = volatility * 1.5
        high_price = max(open_price, close_price) + (base_price * random.uniform(0, range_factor))
        low_price = min(open_price, close_price) - (base_price * random.uniform(0, range_factor))
        
        # Volume correlation with price movement
        price_move_pct = abs(close_price - open_price) / open_price
        base_volume = 1500
        volume = int(base_volume * (1 + price_move_pct * 5) * random.uniform(0.7, 1.3))
        
        data.append({
            "time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "open": round(open_price, 5),
            "high": round(high_price, 5),
            "low": round(low_price, 5),
            "close": round(close_price, 5),
            "volume": volume
        })
        
        base_price = close_price
    
    return data

def test_technical_indicators():
    """Test technical indicators analysis"""
    print("📊 TECHNICAL INDICATORS ANALYSIS")
    print("="*50)
    
    market_data = generate_comprehensive_market_data()
    
    request_data = {
        "indicators": {
            "rsi": [14],
            "macd": [12, 26, 9],
            "sma": [20],
            "ema": [12],
            "bb": [20, 2.0],
            "stoch": [14, 3, 3]
        },
        "ohlc_data": market_data
    }
    
    response = requests.post(f"{API_URL}/analyze", json=request_data)
    
    if response.status_code == 200:
        results = response.json()
        
        print(f"📈 Current Price: ${market_data[-1]['close']}")
        print(f"📊 Data Points: {len(market_data)}")
        print("\n🔍 Technical Indicators:")
        
        for indicator, value in results.items():
            print(f"   {indicator.upper()}: {value}")
            
        return market_data, results
    else:
        print(f"❌ Error: {response.text}")
        return None, None

def test_candlestick_patterns(market_data):
    """Test candlestick pattern recognition"""
    print("\n🕯️  CANDLESTICK PATTERN ANALYSIS")
    print("="*50)
    
    request_data = {
        "indicators": {"sma": [10]},  # Minimal indicator
        "candlestick_patterns": [
            "doji", "hammer", "shooting_star", "engulfing",
            "harami", "morning_star", "evening_star", "inside",
            "marubozu", "spinning_top", "three_white_soldiers",
            "three_black_crows", "dragonfly_doji", "gravestone_doji"
        ],
        "ohlc_data": market_data
    }
    
    response = requests.post(f"{API_URL}/analyze", json=request_data)
    
    if response.status_code == 200:
        results = response.json()
        
        # Separate patterns from indicators
        patterns = {k: v for k, v in results.items() if k not in ['sma']}
        
        print("🔍 Detected Patterns:")
        detected_patterns = {k: v for k, v in patterns.items() if v != "Not Detected"}
        
        if detected_patterns:
            for pattern, signal in detected_patterns.items():
                emoji = "🟢" if signal == "Bullish" else "🔴" if signal == "Bearish" else "⚪"
                print(f"   {emoji} {pattern.replace('_', ' ').title()}: {signal}")
        else:
            print("   ⚫ No significant patterns detected")
            
        return patterns
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_binary_options_prediction(market_data):
    """Test binary options prediction"""
    print("\n🎯 BINARY OPTIONS PREDICTION")
    print("="*50)
    
    request_data = {
        "ohlc_data": market_data,
        "prediction_timeframe": 2,
        "confidence_threshold": 0.6
    }
    
    response = requests.post(f"{API_URL}/predict-binary-options", json=request_data)
    
    if response.status_code == 200:
        result = response.json()
        
        # Extract key information
        prediction = result["prediction"]
        signals = result["signal_breakdown"]
        advice = result["trading_advice"]
        
        print(f"🎯 Prediction: {prediction['direction']}")
        print(f"📊 Confidence: {prediction['confidence']:.1%}")
        print(f"⚠️  Risk Level: {prediction['risk_level']}")
        print(f"💡 Recommendation: {advice['recommended_action']}")
        
        print(f"\n📊 Signal Analysis:")
        print(f"   🟢 Bullish: {signals['bullish_signals']} signals (Weight: {signals['bullish_weight']})")
        print(f"   🔴 Bearish: {signals['bearish_signals']} signals (Weight: {signals['bearish_weight']})")
        
        # Show top signals
        print(f"\n🔍 Key Signals:")
        for signal in sorted(result["detailed_signals"], key=lambda x: x['weight'], reverse=True)[:5]:
            emoji = "🟢" if signal['direction'] == 'bullish' else "🔴"
            print(f"   {emoji} {signal['indicator'].upper()}: {signal['reason']} ({signal['weight']})")
        
        # Technical summary
        ta = result["technical_analysis"]
        print(f"\n📉 Technical Summary:")
        if 'rsi' in ta:
            status = "Overbought" if ta['rsi'] > 70 else "Oversold" if ta['rsi'] < 30 else "Neutral"
            print(f"   RSI: {ta['rsi']:.1f} ({status})")
        if 'moving_averages' in ta:
            ma = ta['moving_averages']
            trend = "Bullish" if ma['price'] > ma['sma_20'] else "Bearish"
            print(f"   Trend: {trend} (Price: {ma['price']}, SMA20: {ma['sma_20']})")
        
        return result
    else:
        print(f"❌ Error: {response.text}")
        return None

def comprehensive_analysis():
    """Perform comprehensive analysis combining all features"""
    print("\n" + "="*60)
    print("🚀 COMPREHENSIVE MARKET ANALYSIS")
    print("="*60)
    
    # 1. Technical Indicators
    market_data, indicators = test_technical_indicators()
    if not market_data:
        return
    
    # 2. Candlestick Patterns
    patterns = test_candlestick_patterns(market_data)
    
    # 3. Binary Options Prediction
    prediction = test_binary_options_prediction(market_data)
    
    # 4. Combined Analysis Summary
    if indicators and patterns and prediction:
        print("\n" + "="*60)
        print("📋 TRADING DECISION MATRIX")
        print("="*60)
        
        # Market condition assessment
        rsi = indicators.get('rsi', 50)
        macd = indicators.get('macd', 0)
        prediction_dir = prediction['prediction']['direction']
        confidence = prediction['prediction']['confidence']
        risk = prediction['prediction']['risk_level']
        
        print(f"📊 Market Condition Assessment:")
        print(f"   Current Price: ${market_data[-1]['close']}")
        print(f"   RSI Level: {rsi:.1f}")
        print(f"   MACD: {macd}")
        print(f"   Trend Prediction: {prediction_dir}")
        print(f"   Confidence: {confidence:.1%}")
        print(f"   Risk Level: {risk}")
        
        # Trading recommendation matrix
        print(f"\n🎯 Trading Recommendation:")
        
        if confidence >= 0.75 and risk == "LOW":
            action = "🟢 STRONG TRADE SIGNAL"
            position_size = "Medium (3-5% of capital)"
        elif confidence >= 0.65 and risk in ["LOW", "MEDIUM"]:
            action = "🟡 MODERATE TRADE SIGNAL"
            position_size = "Small (1-3% of capital)"
        elif confidence >= 0.55:
            action = "⚪ WEAK SIGNAL - CONSIDER WAITING"
            position_size = "Very Small (1% of capital)"
        else:
            action = "🔴 NO TRADE - WAIT FOR BETTER SETUP"
            position_size = "None"
        
        print(f"   Action: {action}")
        print(f"   Position Size: {position_size}")
        print(f"   Direction: {prediction_dir if confidence >= 0.55 else 'N/A'}")
        
        # Risk management
        print(f"\n⚠️  Risk Management:")
        current_price = market_data[-1]['close']
        if prediction_dir == "BULLISH":
            stop_loss = current_price * 0.995  # 0.5% stop loss
            take_profit = current_price * 1.01  # 1% take profit
        else:
            stop_loss = current_price * 1.005
            take_profit = current_price * 0.99
            
        print(f"   Stop Loss: ${stop_loss:.5f}")
        print(f"   Take Profit: ${take_profit:.5f}")
        print(f"   Risk/Reward Ratio: 1:2")
        
        # Pattern confirmation
        bullish_patterns = [k for k, v in patterns.items() if v == "Bullish"]
        bearish_patterns = [k for k, v in patterns.items() if v == "Bearish"]
        
        if bullish_patterns and prediction_dir == "BULLISH":
            print(f"   ✅ Pattern Confirmation: {', '.join(bullish_patterns)}")
        elif bearish_patterns and prediction_dir == "BEARISH":
            print(f"   ✅ Pattern Confirmation: {', '.join(bearish_patterns)}")
        else:
            print(f"   ⚠️  No pattern confirmation")

def main():
    """Main demo function"""
    print("🚀 COMPLETE TECHNICAL ANALYSIS API DEMO")
    print("=" * 80)
    
    # Check API status
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code != 200:
            print("❌ API is not responding correctly")
            return
    except:
        print("❌ Cannot connect to API. Start server with: uvicorn main:app --reload --port 8001")
        return
    
    print("✅ API is running - Starting comprehensive analysis...\n")
    
    # Run comprehensive analysis
    comprehensive_analysis()
    
    print("\n" + "="*80)
    print("🎉 DEMO COMPLETED!")
    print("="*80)
    
    print("""
💡 API Features Demonstrated:

✅ Technical Indicators:
   • RSI, MACD, SMA, EMA, Bollinger Bands, Stochastic

✅ Candlestick Patterns:
   • 60+ patterns including Doji, Hammer, Engulfing, etc.

✅ Binary Options Prediction:
   • Multi-indicator analysis with confidence scoring
   • Risk assessment and trading recommendations
   • Detailed signal breakdown and reasoning

🌐 API Endpoints:
   • POST /analyze - Technical indicators & patterns
   • POST /predict-binary-options - Price direction prediction
   • GET /candlestick-patterns - Pattern information
   • GET /docs - Interactive documentation

⚠️  Important: This is for educational purposes only.
    Always use proper risk management in real trading!
    """)

if __name__ == "__main__":
    main()
