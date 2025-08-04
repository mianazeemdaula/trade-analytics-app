"""
FastAPI-based Technical Analysis API

This API provides a single endpoint to calculate technical indicators
on financial OHLC data using pandas_ta library.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Union, Optional
import pandas as pd
import pandas_ta as ta
import json
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Technical Analysis API",
    description="API for calculating technical indicators on financial data",
    version="1.0.0"
)

# Pydantic models for request validation
class OHLCData(BaseModel):
    """Model for individual OHLC candle data"""
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class AnalysisRequest(BaseModel):
    """Model for the main request containing indicators and OHLC data"""
    indicators: Dict[str, List[Union[int, float]]]
    ohlc_data: List[OHLCData]
    candlestick_patterns: Optional[List[str]] = None  # Optional list of candlestick patterns to calculate

class BinaryOptionsRequest(BaseModel):
    """Model for binary options prediction request"""
    ohlc_data: List[OHLCData]
    prediction_timeframe: Optional[int] = 2  # Number of candles to predict (default 2)
    confidence_threshold: Optional[float] = 0.6  # M                                                                                                       inimum confidence level (0.5-1.0)

def convert_ohlc_to_dataframe(ohlc_data: List[OHLCData]) -> pd.DataFrame:
    """
    Convert OHLC data list to pandas DataFrame
    
    Args:
        ohlc_data: List of OHLC data objects
        
    Returns:
        pandas DataFrame with OHLC data
    """
    # Convert to list of dictionaries
    data_dicts = [candle.dict() for candle in ohlc_data]
    
    # Create DataFrame
    df = pd.DataFrame(data_dicts)
    
    # Convert time column to datetime
    df['time'] = pd.to_datetime(df['time'])
    
    # Set time as index for better compatibility with pandas_ta
    df.set_index('time', inplace=True)
    
    # Ensure columns are in the right order and type
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    
    return df

def calculate_indicator(df: pd.DataFrame, indicator_name: str, params: List[Union[int, float]]) -> Dict[str, float]:
    """
    Calculate a specific technical indicator using pandas_ta
    
    Args:
        df: DataFrame with OHLC data
        indicator_name: Name of the indicator to calculate
        params: Parameters for the indicator
        
    Returns:
        Dictionary with indicator values (last values only)
    """
    result = {}
    
    try:
        if indicator_name.lower() == 'rsi':
            # RSI - Relative Strength Index
            if len(params) != 1:
                raise ValueError("RSI requires exactly 1 parameter (period)")
            period = int(params[0])
            rsi_values = ta.rsi(df['close'], length=period)
            if not rsi_values.empty:
                result['rsi'] = round(float(rsi_values.iloc[-1]), 2)
        
        elif indicator_name.lower() == 'macd':
            # MACD - Moving Average Convergence Divergence
            if len(params) != 3:
                raise ValueError("MACD requires exactly 3 parameters (fast, slow, signal)")
            fast, slow, signal = int(params[0]), int(params[1]), int(params[2])
            macd_data = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
            if macd_data is not None and not macd_data.empty:
                # MACD returns a DataFrame with MACD_fast_slow_signal, MACDh_fast_slow_signal, MACDs_fast_slow_signal
                macd_col = f'MACD_{fast}_{slow}_{signal}'
                signal_col = f'MACDs_{fast}_{slow}_{signal}'
                
                if macd_col in macd_data.columns:
                    result['macd'] = round(float(macd_data[macd_col].iloc[-1]), 2)
                if signal_col in macd_data.columns:
                    result['macd_signal'] = round(float(macd_data[signal_col].iloc[-1]), 2)
        
        elif indicator_name.lower() == 'sma':
            # SMA - Simple Moving Average
            if len(params) != 1:
                raise ValueError("SMA requires exactly 1 parameter (period)")
            period = int(params[0])
            sma_values = ta.sma(df['close'], length=period)
            if not sma_values.empty:
                result['sma'] = round(float(sma_values.iloc[-1]), 2)
        
        elif indicator_name.lower() == 'ema':
            # EMA - Exponential Moving Average
            if len(params) != 1:
                raise ValueError("EMA requires exactly 1 parameter (period)")
            period = int(params[0])
            ema_values = ta.ema(df['close'], length=period)
            if not ema_values.empty:
                result['ema'] = round(float(ema_values.iloc[-1]), 2)
        
        elif indicator_name.lower() == 'bb' or indicator_name.lower() == 'bollinger':
            # Bollinger Bands
            if len(params) != 2:
                raise ValueError("Bollinger Bands requires exactly 2 parameters (period, std)")
            period, std = int(params[0]), float(params[1])
            bb_data = ta.bbands(df['close'], length=period, std=std)
            if bb_data is not None and not bb_data.empty:
                # Bollinger Bands returns DataFrame with multiple columns
                upper_col = f'BBU_{period}_{std}'
                middle_col = f'BBM_{period}_{std}'
                lower_col = f'BBL_{period}_{std}'
                
                if upper_col in bb_data.columns:
                    result['bb_upper'] = round(float(bb_data[upper_col].iloc[-1]), 2)
                if middle_col in bb_data.columns:
                    result['bb_middle'] = round(float(bb_data[middle_col].iloc[-1]), 2)
                if lower_col in bb_data.columns:
                    result['bb_lower'] = round(float(bb_data[lower_col].iloc[-1]), 2)
        
        elif indicator_name.lower() == 'stoch' or indicator_name.lower() == 'stochastic':
            # Stochastic Oscillator
            if len(params) != 3:
                raise ValueError("Stochastic requires exactly 3 parameters (k, d, smooth_k)")
            k, d, smooth_k = int(params[0]), int(params[1]), int(params[2])
            stoch_data = ta.stoch(df['high'], df['low'], df['close'], k=k, d=d, smooth_k=smooth_k)
            if stoch_data is not None and not stoch_data.empty:
                k_col = f'STOCHk_{k}_{d}_{smooth_k}'
                d_col = f'STOCHd_{k}_{d}_{smooth_k}'
                
                if k_col in stoch_data.columns:
                    result['stoch_k'] = round(float(stoch_data[k_col].iloc[-1]), 2)
                if d_col in stoch_data.columns:
                    result['stoch_d'] = round(float(stoch_data[d_col].iloc[-1]), 2)
        
        else:
            raise ValueError(f"Unsupported indicator: {indicator_name}")
            
    except Exception as e:
        raise ValueError(f"Error calculating {indicator_name}: {str(e)}")
    
    return result

def calculate_candlestick_patterns(df: pd.DataFrame, patterns: List[str]) -> Dict[str, Any]:
    """
    Calculate candlestick patterns using pandas_ta
    
    Args:
        df: DataFrame with OHLC data
        patterns: List of pattern names to calculate
        
    Returns:
        Dictionary with pattern results (last values only)
    """
    result = {}
    
    try:
        for pattern_name in patterns:
            pattern_lower = pattern_name.lower()
            
            # Handle common pattern name variations
            if pattern_lower in ['hammer']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='hammer')
            elif pattern_lower in ['doji']:
                pattern_result = ta.cdl_doji(df['open'], df['high'], df['low'], df['close'])
            elif pattern_lower in ['engulfing']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='engulfing')
            elif pattern_lower in ['harami']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='harami')
            elif pattern_lower in ['morning_star', 'morningstar']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='morningstar')
            elif pattern_lower in ['evening_star', 'eveningstar']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='eveningstar')
            elif pattern_lower in ['shooting_star', 'shootingstar']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='shootingstar')
            elif pattern_lower in ['hanging_man', 'hangingman']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='hangingman')
            elif pattern_lower in ['inverted_hammer', 'invertedhammer']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='invertedhammer')
            elif pattern_lower in ['dark_cloud_cover', 'darkcloudcover']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='darkcloudcover')
            elif pattern_lower in ['piercing']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='piercing')
            elif pattern_lower in ['marubozu']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='marubozu')
            elif pattern_lower in ['spinning_top', 'spinningtop']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='spinningtop')
            elif pattern_lower in ['three_white_soldiers', '3whitesoldiers']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='3whitesoldiers')
            elif pattern_lower in ['three_black_crows', '3blackcrows']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='3blackcrows')
            elif pattern_lower in ['inside']:
                pattern_result = ta.cdl_inside(df['open'], df['high'], df['low'], df['close'])
            elif pattern_lower in ['dragonfly_doji', 'dragonflydoji']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='dragonflydoji')
            elif pattern_lower in ['gravestone_doji', 'gravestonedoji']:
                pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name='gravestonedoji')
            else:
                # Try to use the pattern name directly with cdl_pattern
                if pattern_lower in ta.CDL_PATTERN_NAMES:
                    pattern_result = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name=pattern_lower)
                else:
                    result[f"{pattern_name}_error"] = f"Pattern '{pattern_name}' not supported"
                    continue
            
            # Extract the last value if pattern was calculated successfully
            if pattern_result is not None and not pattern_result.empty:
                last_value = pattern_result.iloc[-1]
                if pd.notna(last_value):
                    # Convert pattern signal to readable format
                    if last_value > 0:
                        result[pattern_name] = "Bullish"
                    elif last_value < 0:
                        result[pattern_name] = "Bearish"
                    else:
                        result[pattern_name] = "Neutral"
                else:
                    result[pattern_name] = "Not Detected"
            else:
                result[pattern_name] = "Not Detected"
                
    except Exception as e:
        result["patterns_error"] = f"Error calculating patterns: {str(e)}"
    
    return result

def predict_binary_options(df: pd.DataFrame, prediction_timeframe: int = 2, confidence_threshold: float = 0.6) -> Dict[str, Any]:
    """
    Predict binary options direction using multiple technical indicators and patterns
    
    Args:
        df: DataFrame with OHLC data
        prediction_timeframe: Number of candles to predict (default 2)
        confidence_threshold: Minimum confidence level (0.5-1.0)
        
    Returns:
        Dictionary with prediction results and analysis
    """
    try:
        signals = []
        analysis = {}
        
        # 1. RSI Analysis (14 period)
        if len(df) >= 14:
            rsi = ta.rsi(df['close'], length=14)
            if not rsi.empty:
                current_rsi = float(rsi.iloc[-1])
                analysis['rsi'] = current_rsi
                
                if current_rsi < 30:
                    signals.append(('rsi', 'bullish', 0.8, 'RSI oversold - likely reversal up'))
                elif current_rsi > 70:
                    signals.append(('rsi', 'bearish', 0.8, 'RSI overbought - likely reversal down'))
                elif current_rsi < 45:
                    signals.append(('rsi', 'bullish', 0.4, 'RSI below midpoint - slight bullish bias'))
                elif current_rsi > 55:
                    signals.append(('rsi', 'bearish', 0.4, 'RSI above midpoint - slight bearish bias'))
        
        # 2. MACD Analysis
        if len(df) >= 26:
            macd_data = ta.macd(df['close'], fast=12, slow=26, signal=9)
            if macd_data is not None and not macd_data.empty:
                macd_line = macd_data['MACD_12_26_9'].iloc[-1]
                signal_line = macd_data['MACDs_12_26_9'].iloc[-1]
                histogram = macd_data['MACDh_12_26_9'].iloc[-1]
                
                analysis['macd'] = {'line': round(float(macd_line), 4), 'signal': round(float(signal_line), 4)}
                
                if macd_line > signal_line and histogram > 0:
                    signals.append(('macd', 'bullish', 0.7, 'MACD bullish crossover'))
                elif macd_line < signal_line and histogram < 0:
                    signals.append(('macd', 'bearish', 0.7, 'MACD bearish crossover'))
        
        # 3. Moving Average Analysis
        if len(df) >= 20:
            sma_20 = ta.sma(df['close'], length=20)
            ema_12 = ta.ema(df['close'], length=12)
            
            if not sma_20.empty and not ema_12.empty:
                current_price = float(df['close'].iloc[-1])
                sma_20_val = float(sma_20.iloc[-1])
                ema_12_val = float(ema_12.iloc[-1])
                
                analysis['moving_averages'] = {
                    'price': current_price,
                    'sma_20': round(sma_20_val, 2),
                    'ema_12': round(ema_12_val, 2)
                }
                
                if current_price > sma_20_val and ema_12_val > sma_20_val:
                    signals.append(('ma', 'bullish', 0.6, 'Price above SMA20 and EMA12 > SMA20'))
                elif current_price < sma_20_val and ema_12_val < sma_20_val:
                    signals.append(('ma', 'bearish', 0.6, 'Price below SMA20 and EMA12 < SMA20'))
        
        # 4. Bollinger Bands Analysis
        if len(df) >= 20:
            bb_data = ta.bbands(df['close'], length=20, std=2)
            if bb_data is not None and not bb_data.empty:
                current_price = float(df['close'].iloc[-1])
                bb_upper = float(bb_data['BBU_20_2.0'].iloc[-1])
                bb_lower = float(bb_data['BBL_20_2.0'].iloc[-1])
                bb_middle = float(bb_data['BBM_20_2.0'].iloc[-1])
                
                analysis['bollinger_bands'] = {
                    'upper': round(bb_upper, 2),
                    'middle': round(bb_middle, 2),
                    'lower': round(bb_lower, 2),
                    'price_position': round((current_price - bb_lower) / (bb_upper - bb_lower), 2)
                }
                
                if current_price <= bb_lower:
                    signals.append(('bb', 'bullish', 0.75, 'Price at/below lower Bollinger Band - oversold'))
                elif current_price >= bb_upper:
                    signals.append(('bb', 'bearish', 0.75, 'Price at/above upper Bollinger Band - overbought'))
        
        # 5. Stochastic Analysis
        if len(df) >= 14:
            stoch_data = ta.stoch(df['high'], df['low'], df['close'], k=14, d=3, smooth_k=3)
            if stoch_data is not None and not stoch_data.empty:
                stoch_k = float(stoch_data['STOCHk_14_3_3'].iloc[-1])
                stoch_d = float(stoch_data['STOCHd_14_3_3'].iloc[-1])
                
                analysis['stochastic'] = {'k': round(stoch_k, 2), 'd': round(stoch_d, 2)}
                
                if stoch_k < 20 and stoch_d < 20:
                    signals.append(('stoch', 'bullish', 0.7, 'Stochastic oversold - likely reversal up'))
                elif stoch_k > 80 and stoch_d > 80:
                    signals.append(('stoch', 'bearish', 0.7, 'Stochastic overbought - likely reversal down'))
                elif stoch_k > stoch_d and stoch_k < 80:
                    signals.append(('stoch', 'bullish', 0.5, 'Stochastic K above D - bullish momentum'))
                elif stoch_k < stoch_d and stoch_k > 20:
                    signals.append(('stoch', 'bearish', 0.5, 'Stochastic K below D - bearish momentum'))
        
        # 6. Price Action Analysis
        if len(df) >= 3:
            recent_closes = df['close'].tail(3).values
            recent_highs = df['high'].tail(3).values
            recent_lows = df['low'].tail(3).values
            
            # Check for higher highs/lows or lower highs/lows
            if recent_highs[-1] > recent_highs[-2] > recent_highs[-3] and recent_lows[-1] > recent_lows[-2]:
                signals.append(('price_action', 'bullish', 0.6, 'Higher highs and higher lows pattern'))
            elif recent_highs[-1] < recent_highs[-2] < recent_highs[-3] and recent_lows[-1] < recent_lows[-2]:
                signals.append(('price_action', 'bearish', 0.6, 'Lower highs and lower lows pattern'))
        
        # 7. Volume Analysis (if available)
        if 'volume' in df.columns and len(df) >= 10:
            recent_volumes = df['volume'].tail(3).values
            avg_volume = df['volume'].tail(10).mean()
            current_volume = recent_volumes[-1]
            
            analysis['volume'] = {
                'current': int(current_volume),
                'average_10': int(avg_volume),
                'volume_ratio': round(current_volume / avg_volume, 2)
            }
            
            # High volume confirms the direction
            if current_volume > avg_volume * 1.5:
                # Volume confirmation signal will be added based on price movement
                price_change = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]
                if price_change > 0:
                    signals.append(('volume', 'bullish', 0.3, 'High volume confirming upward movement'))
                else:
                    signals.append(('volume', 'bearish', 0.3, 'High volume confirming downward movement'))
        
        # 8. Simple Candlestick Pattern Analysis
        key_patterns = ['doji', 'hammer', 'shooting_star', 'engulfing', 'inside']
        pattern_signals = calculate_candlestick_patterns(df, key_patterns)
        
        pattern_analysis = {}
        for pattern, signal in pattern_signals.items():
            if signal != "Not Detected" and not pattern.endswith('_error'):
                pattern_analysis[pattern] = signal
                if signal == "Bullish":
                    signals.append(('pattern', 'bullish', 0.5, f'{pattern.title()} pattern detected'))
                elif signal == "Bearish":
                    signals.append(('pattern', 'bearish', 0.5, f'{pattern.title()} pattern detected'))
        
        analysis['patterns'] = pattern_analysis
        
        # Calculate overall prediction
        bullish_signals = [s for s in signals if s[1] == 'bullish']
        bearish_signals = [s for s in signals if s[1] == 'bearish']
        
        bullish_weight = sum(s[2] for s in bullish_signals)
        bearish_weight = sum(s[2] for s in bearish_signals)
        
        total_weight = bullish_weight + bearish_weight
        
        if total_weight > 0:
            bullish_confidence = bullish_weight / total_weight
            bearish_confidence = bearish_weight / total_weight
        else:
            bullish_confidence = bearish_confidence = 0.5
        
        # Determine prediction
        if bullish_confidence >= confidence_threshold:
            prediction = "BULLISH"
            confidence = bullish_confidence
        elif bearish_confidence >= confidence_threshold:
            prediction = "BEARISH"  
            confidence = bearish_confidence
        else:
            prediction = "NEUTRAL"
            confidence = max(bullish_confidence, bearish_confidence)
        
        # Risk assessment
        risk_level = "LOW"
        if confidence < 0.6:
            risk_level = "HIGH"
        elif confidence < 0.75:
            risk_level = "MEDIUM"
        
        return {
            "prediction": {
                "direction": prediction,
                "confidence": round(confidence, 3),
                "timeframe_candles": prediction_timeframe,
                "risk_level": risk_level
            },
            "signal_breakdown": {
                "bullish_signals": len(bullish_signals),
                "bearish_signals": len(bearish_signals),
                "bullish_weight": round(bullish_weight, 2),
                "bearish_weight": round(bearish_weight, 2)
            },
            "detailed_signals": [
                {
                    "indicator": signal[0],
                    "direction": signal[1],
                    "weight": signal[2],
                    "reason": signal[3]
                } for signal in signals
            ],
            "technical_analysis": analysis,
            "trading_advice": {
                "recommended_action": "BUY" if prediction == "BULLISH" else "SELL" if prediction == "BEARISH" else "WAIT",
                "stop_loss_suggestion": "Set stop-loss at recent support/resistance levels",
                "notes": f"Prediction based on {len(signals)} technical signals with {confidence:.1%} confidence"
            }
        }
        
    except Exception as e:
        return {
            "error": f"Prediction failed: {str(e)}",
            "prediction": {"direction": "NEUTRAL", "confidence": 0.5, "risk_level": "HIGH"}
        }

@app.get("/candlestick-patterns")
async def get_candlestick_patterns():
    """
    Get comprehensive list of supported candlestick patterns
    
    Returns:
        JSON object with all available candlestick patterns, their descriptions, and types
    """
    # Comprehensive candlestick patterns with descriptions
    patterns = {
        "reversal_patterns": {
            "hammer": {
                "name": "Hammer",
                "type": "Bullish Reversal",
                "description": "Small body at the top with a long lower shadow, indicates potential bullish reversal at bottom of downtrend",
                "reliability": "Medium",
                "confirmation_needed": True
            },
            "hanging_man": {
                "name": "Hanging Man", 
                "type": "Bearish Reversal",
                "description": "Small body at the top with a long lower shadow, indicates potential bearish reversal at top of uptrend",
                "reliability": "Medium",
                "confirmation_needed": True
            },
            "inverted_hammer": {
                "name": "Inverted Hammer",
                "type": "Bullish Reversal", 
                "description": "Small body at the bottom with a long upper shadow, potential bullish reversal",
                "reliability": "Medium",
                "confirmation_needed": True
            },
            "shooting_star": {
                "name": "Shooting Star",
                "type": "Bearish Reversal",
                "description": "Small body at the bottom with a long upper shadow, potential bearish reversal at top of uptrend",
                "reliability": "Medium", 
                "confirmation_needed": True
            },
            "doji": {
                "name": "Doji",
                "type": "Neutral/Reversal",
                "description": "Open and close prices are virtually equal, indicates indecision and potential reversal",
                "reliability": "Low-Medium",
                "confirmation_needed": True
            },
            "dragonfly_doji": {
                "name": "Dragonfly Doji",
                "type": "Bullish Reversal",
                "description": "Doji with long lower shadow and no upper shadow, potential bullish reversal",
                "reliability": "Medium",
                "confirmation_needed": True
            },
            "gravestone_doji": {
                "name": "Gravestone Doji", 
                "type": "Bearish Reversal",
                "description": "Doji with long upper shadow and no lower shadow, potential bearish reversal",
                "reliability": "Medium",
                "confirmation_needed": True
            },
            "engulfing": {
                "name": "Engulfing Pattern",
                "type": "Reversal (Bullish/Bearish)",
                "description": "Second candle completely engulfs the first candle's body, strong reversal signal",
                "reliability": "High",
                "confirmation_needed": False
            },
            "harami": {
                "name": "Harami",
                "type": "Reversal (Bullish/Bearish)", 
                "description": "Small candle contained within the previous large candle's body, potential reversal",
                "reliability": "Medium",
                "confirmation_needed": True
            },
            "dark_cloud_cover": {
                "name": "Dark Cloud Cover",
                "type": "Bearish Reversal",
                "description": "Bearish candle opens above previous bullish candle's high and closes below its midpoint",
                "reliability": "High",
                "confirmation_needed": False
            },
            "piercing": {
                "name": "Piercing Pattern",
                "type": "Bullish Reversal", 
                "description": "Bullish candle opens below previous bearish candle's low and closes above its midpoint",
                "reliability": "High",
                "confirmation_needed": False
            },
            "morning_star": {
                "name": "Morning Star",
                "type": "Bullish Reversal",
                "description": "Three-candle pattern: large bearish, small body (gap down), large bullish (gap up)",
                "reliability": "Very High",
                "confirmation_needed": False
            },
            "evening_star": {
                "name": "Evening Star", 
                "type": "Bearish Reversal",
                "description": "Three-candle pattern: large bullish, small body (gap up), large bearish (gap down)",
                "reliability": "Very High", 
                "confirmation_needed": False
            },
            "morning_doji_star": {
                "name": "Morning Doji Star",
                "type": "Bullish Reversal",
                "description": "Like morning star but with doji in the middle, stronger bullish reversal signal",
                "reliability": "Very High",
                "confirmation_needed": False
            },
            "evening_doji_star": {
                "name": "Evening Doji Star",
                "type": "Bearish Reversal", 
                "description": "Like evening star but with doji in the middle, stronger bearish reversal signal",
                "reliability": "Very High",
                "confirmation_needed": False
            }
        },
        "continuation_patterns": {
            "spinning_top": {
                "name": "Spinning Top",
                "type": "Continuation/Indecision",
                "description": "Small body with long upper and lower shadows, indicates indecision",
                "reliability": "Low",
                "confirmation_needed": True
            },
            "marubozu": {
                "name": "Marubozu", 
                "type": "Continuation",
                "description": "No upper or lower shadows, strong continuation signal in direction of candle",
                "reliability": "High",
                "confirmation_needed": False
            },
            "long_line": {
                "name": "Long Line",
                "type": "Continuation",
                "description": "Large candle body with minimal shadows, strong continuation signal",
                "reliability": "Medium-High", 
                "confirmation_needed": False
            },
            "short_line": {
                "name": "Short Line",
                "type": "Consolidation",
                "description": "Small candle body, indicates consolidation or indecision",
                "reliability": "Low",
                "confirmation_needed": True
            }
        },
        "multi_candle_patterns": {
            "three_white_soldiers": {
                "name": "Three White Soldiers",
                "type": "Bullish Continuation/Reversal",
                "description": "Three consecutive bullish candles with progressively higher closes",
                "reliability": "Very High", 
                "confirmation_needed": False
            },
            "three_black_crows": {
                "name": "Three Black Crows",
                "type": "Bearish Continuation/Reversal", 
                "description": "Three consecutive bearish candles with progressively lower closes",
                "reliability": "Very High",
                "confirmation_needed": False
            },
            "inside": {
                "name": "Inside Bar",
                "type": "Consolidation",
                "description": "Current candle's high and low are within the previous candle's range",
                "reliability": "Medium",
                "confirmation_needed": True
            },
            "abandoned_baby": {
                "name": "Abandoned Baby",
                "type": "Reversal (Bullish/Bearish)",
                "description": "Rare three-candle pattern with gaps, very strong reversal signal",
                "reliability": "Very High",
                "confirmation_needed": False
            }
        },
        "gap_patterns": {
            "upside_gap_two_crows": {
                "name": "Upside Gap Two Crows",
                "type": "Bearish Reversal",
                "description": "Bullish gap followed by two bearish candles, bearish reversal signal",
                "reliability": "Medium",
                "confirmation_needed": True
            },
            "gap_side_side_white": {
                "name": "Gap Side-by-Side White Lines", 
                "type": "Bullish Continuation",
                "description": "Two white candles with a gap between them, bullish continuation",
                "reliability": "Medium",
                "confirmation_needed": False
            }
        }
    }
    
    # Get all available patterns from pandas_ta
    available_ta_patterns = []
    if hasattr(ta, 'CDL_PATTERN_NAMES'):
        available_ta_patterns = sorted(ta.CDL_PATTERN_NAMES)
    
    return {
        "patterns_by_category": patterns,
        "available_ta_lib_patterns": available_ta_patterns,
        "pattern_count": {
            "reversal_patterns": len(patterns["reversal_patterns"]),
            "continuation_patterns": len(patterns["continuation_patterns"]), 
            "multi_candle_patterns": len(patterns["multi_candle_patterns"]),
            "gap_patterns": len(patterns["gap_patterns"]),
            "total_categorized": sum(len(cat) for cat in patterns.values()),
            "total_ta_lib_available": len(available_ta_patterns)
        },
        "usage_notes": {
            "reliability_levels": ["Low", "Medium", "High", "Very High"],
            "confirmation_needed": "Indicates whether the pattern should be confirmed by subsequent price action",
            "pattern_types": ["Bullish Reversal", "Bearish Reversal", "Continuation", "Consolidation", "Neutral/Reversal"]
        }
    }

@app.post("/predict-binary-options")
async def predict_binary_options_endpoint(request: BinaryOptionsRequest):
    """
    Predict binary options direction for next 2 candles using technical analysis
    
    Args:
        request: BinaryOptionsRequest containing OHLC data and prediction parameters
        
    Returns:
        JSON object with prediction, confidence, analysis and trading advice
    """
    try:
        # Validate input
        if not request.ohlc_data:
            raise HTTPException(status_code=400, detail="OHLC data cannot be empty")
        
        if len(request.ohlc_data) < 20:
            raise HTTPException(status_code=400, detail="Need at least 20 data points for reliable binary options prediction")
        
        if not (0.5 <= request.confidence_threshold <= 1.0):
            raise HTTPException(status_code=400, detail="Confidence threshold must be between 0.5 and 1.0")
        
        # Convert OHLC data to DataFrame
        df = convert_ohlc_to_dataframe(request.ohlc_data)
        
        # Generate prediction
        prediction_result = predict_binary_options(
            df, 
            request.prediction_timeframe, 
            request.confidence_threshold
        )
        
        # Add metadata
        prediction_result["metadata"] = {
            "data_points_analyzed": len(df),
            "last_price": round(float(df['close'].iloc[-1]), 4),
            "prediction_timestamp": datetime.now().isoformat(),
            "timeframe": f"Next {request.prediction_timeframe} candles"
        }
        
        return prediction_result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint providing API information"""
    return {
        "message": "Technical Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "POST - Calculate technical indicators and candlestick patterns",
            "/predict-binary-options": "POST - Predict next 2 candles direction for binary options",
            "/candlestick-patterns": "GET - Get comprehensive list of candlestick patterns",
            "/supported-indicators": "GET - Get list of supported technical indicators",
            "/docs": "GET - API documentation"
        }
    }

@app.post("/analyze")
async def analyze_technical_indicators(request: AnalysisRequest):
    """
    Calculate technical indicators on OHLC data
    
    Args:
        request: AnalysisRequest containing indicators and OHLC data
        
    Returns:
        JSON object with calculated indicator values (last values only)
    """
    try:
        # Validate input
        if not request.ohlc_data:
            raise HTTPException(status_code=400, detail="OHLC data cannot be empty")
        
        if not request.indicators:
            raise HTTPException(status_code=400, detail="Indicators cannot be empty")
        
        # Convert OHLC data to DataFrame
        df = convert_ohlc_to_dataframe(request.ohlc_data)
        
        # Check if we have enough data
        if len(df) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 data points for analysis")
        
        # Calculate indicators
        results = {}
        
        for indicator_name, params in request.indicators.items():
            try:
                indicator_results = calculate_indicator(df, indicator_name, params)
                results.update(indicator_results)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # Calculate candlestick patterns if requested
        if request.candlestick_patterns:
            try:
                pattern_results = calculate_candlestick_patterns(df, request.candlestick_patterns)
                results.update(pattern_results)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error calculating patterns: {str(e)}")
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/supported-indicators")
async def get_supported_indicators():
    """
    Get list of supported technical indicators and their parameter requirements
    """
    return {
        "supported_indicators": {
            "rsi": {
                "name": "Relative Strength Index",
                "parameters": ["period (int)"],
                "example": [14]
            },
            "macd": {
                "name": "Moving Average Convergence Divergence",
                "parameters": ["fast (int)", "slow (int)", "signal (int)"],
                "example": [12, 26, 9]
            },
            "sma": {
                "name": "Simple Moving Average",
                "parameters": ["period (int)"],
                "example": [20]
            },
            "ema": {
                "name": "Exponential Moving Average",
                "parameters": ["period (int)"],
                "example": [20]
            },
            "bb": {
                "name": "Bollinger Bands",
                "parameters": ["period (int)", "standard_deviation (float)"],
                "example": [20, 2.0]
            },
            "stoch": {
                "name": "Stochastic Oscillator",
                "parameters": ["k (int)", "d (int)", "smooth_k (int)"],
                "example": [14, 3, 3]
            }
        },
        "note": "For candlestick patterns, use the /candlestick-patterns endpoint to see available patterns, then include them in the 'candlestick_patterns' field of your analysis request."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
