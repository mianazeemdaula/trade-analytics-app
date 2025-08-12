"""
Binary options prediction module
"""

from typing import Dict, List, Any
import pandas as pd
import numpy as np
from .indicators import calculate_indicator
from .patterns import calculate_candlestick_patterns, get_pattern_signals


def predict_binary_options(df: pd.DataFrame, timeframe_minutes: int = 5) -> Dict[str, Any]:
    """
    Predict binary options direction using multiple indicators and patterns
    
    Args:
        df: DataFrame with OHLC data
        timeframe_minutes: Prediction timeframe in minutes
        
    Returns:
        Dictionary with prediction details
    """
    prediction = {
        'prediction': 'neutral',
        'confidence': 0.0,
        'timeframe_minutes': timeframe_minutes,
        'signals': {},
        'indicator_scores': {},
        'pattern_analysis': {},
        'risk_assessment': 'medium'
    }
    
    try:
        current_price = float(df['close'].iloc[-1])
        
        # Calculate multiple indicators for prediction
        indicators_config = [
            ('rsi', [14]),
            ('macd', [12, 26, 9]),
            ('ema', [20]),
            ('bb', [20, 2]),
            ('stoch', [14, 3, 3]),
            ('atr', [14]),
            ('stoch_rsi', [14, 14, 3]),
            ('vwap', []),
            ('supertrend', [10, 3])
        ]
        
        bullish_signals = 0
        bearish_signals = 0
        total_signals = 0
        signal_weights = {}
        
        # Analyze each indicator
        for indicator_name, params in indicators_config:
            try:
                result = calculate_indicator(df, indicator_name, params)
                prediction['indicator_scores'][indicator_name] = result
                
                # Analyze signals from each indicator
                signal, weight = _analyze_indicator_signal(indicator_name, result, current_price)
                signal_weights[indicator_name] = {'signal': signal, 'weight': weight}
                
                if signal == 'bullish':
                    bullish_signals += weight
                elif signal == 'bearish':
                    bearish_signals += weight
                
                total_signals += weight
                
            except Exception as e:
                print(f"Error calculating {indicator_name}: {str(e)}")
                continue
        
        # Calculate candlestick patterns
        try:
            patterns = calculate_candlestick_patterns(df)
            pattern_signals = get_pattern_signals(patterns)
            prediction['pattern_analysis'] = pattern_signals
            
            # Add pattern signals to prediction
            if pattern_signals['overall_signal'] == 'bullish':
                pattern_weight = 2 if pattern_signals['signal_strength'] == 'strong' else 1
                bullish_signals += pattern_weight
                total_signals += pattern_weight
            elif pattern_signals['overall_signal'] == 'bearish':
                pattern_weight = 2 if pattern_signals['signal_strength'] == 'strong' else 1
                bearish_signals += pattern_weight
                total_signals += pattern_weight
                
        except Exception as e:
            print(f"Error calculating patterns: {str(e)}")
        
        # Calculate overall prediction
        if total_signals > 0:
            bullish_ratio = bullish_signals / total_signals
            bearish_ratio = bearish_signals / total_signals
            
            if bullish_ratio > 0.6:
                prediction['prediction'] = 'call'
                prediction['confidence'] = min(bullish_ratio, 0.95)
            elif bearish_ratio > 0.6:
                prediction['prediction'] = 'put'
                prediction['confidence'] = min(bearish_ratio, 0.95)
            else:
                prediction['prediction'] = 'neutral'
                prediction['confidence'] = 1 - abs(bullish_ratio - bearish_ratio)
        
        # Add detailed signal analysis
        prediction['signals'] = {
            'bullish_signals': bullish_signals,
            'bearish_signals': bearish_signals,
            'total_signals': total_signals,
            'bullish_ratio': bullish_signals / max(total_signals, 1),
            'bearish_ratio': bearish_signals / max(total_signals, 1),
            'signal_breakdown': signal_weights
        }
        
        # Risk assessment
        prediction['risk_assessment'] = _assess_risk(df, prediction['confidence'])
        
        # Add market conditions
        prediction['market_conditions'] = _analyze_market_conditions(df)
        
        # Add entry suggestions
        prediction['entry_suggestions'] = _generate_entry_suggestions(df, prediction)
        
    except Exception as e:
        prediction['error'] = f"Prediction error: {str(e)}"
        prediction['prediction'] = 'neutral'
        prediction['confidence'] = 0.0
    
    return prediction


def _analyze_indicator_signal(indicator_name: str, result: Dict[str, Any], current_price: float) -> tuple[str, float]:
    """
    Analyze signal from individual indicator
    
    Args:
        indicator_name: Name of the indicator
        result: Indicator calculation result
        current_price: Current price
        
    Returns:
        Tuple of (signal_direction, signal_weight)
    """
    signal = 'neutral'
    weight = 1.0
    
    try:
        if indicator_name == 'rsi':
            rsi_value = result.get('rsi', 50)
            if rsi_value < 30:
                signal = 'bullish'  # Oversold
                weight = 1.5
            elif rsi_value > 70:
                signal = 'bearish'  # Overbought
                weight = 1.5
            elif rsi_value < 40:
                signal = 'bullish'
                weight = 0.8
            elif rsi_value > 60:
                signal = 'bearish'
                weight = 0.8
        
        elif indicator_name == 'macd':
            macd = result.get('macd', 0)
            macd_signal = result.get('macd_signal', 0)
            if macd > macd_signal:
                signal = 'bullish'
                weight = 1.2
            elif macd < macd_signal:
                signal = 'bearish'
                weight = 1.2
        
        elif indicator_name == 'ema':
            ema_value = result.get('ema', current_price)
            if current_price > ema_value:
                signal = 'bullish'
                weight = 1.0
            elif current_price < ema_value:
                signal = 'bearish'
                weight = 1.0
        
        elif indicator_name == 'bb':
            bb_upper = result.get('bb_upper', current_price)
            bb_lower = result.get('bb_lower', current_price)
            bb_middle = result.get('bb_middle', current_price)
            
            if current_price <= bb_lower:
                signal = 'bullish'  # Price at lower band - potential bounce
                weight = 1.3
            elif current_price >= bb_upper:
                signal = 'bearish'  # Price at upper band - potential reversal
                weight = 1.3
            elif current_price > bb_middle:
                signal = 'bullish'
                weight = 0.7
            elif current_price < bb_middle:
                signal = 'bearish'
                weight = 0.7
        
        elif indicator_name == 'stoch':
            stoch_k = result.get('stoch_k', 50)
            stoch_d = result.get('stoch_d', 50)
            if stoch_k < 20 and stoch_d < 20:
                signal = 'bullish'  # Oversold
                weight = 1.4
            elif stoch_k > 80 and stoch_d > 80:
                signal = 'bearish'  # Overbought
                weight = 1.4
            elif stoch_k > stoch_d:
                signal = 'bullish'
                weight = 0.8
            elif stoch_k < stoch_d:
                signal = 'bearish'
                weight = 0.8
        
        elif indicator_name == 'stoch_rsi':
            stoch_rsi_k = result.get('stoch_rsi_k', 50)
            stoch_rsi_d = result.get('stoch_rsi_d', 50)
            if stoch_rsi_k < 20 and stoch_rsi_d < 20:
                signal = 'bullish'
                weight = 1.3
            elif stoch_rsi_k > 80 and stoch_rsi_d > 80:
                signal = 'bearish'
                weight = 1.3
        
        elif indicator_name == 'vwap':
            vwap_value = result.get('vwap', current_price)
            price_vs_vwap = result.get('price_vs_vwap', 'neutral')
            if price_vs_vwap == 'above':
                signal = 'bullish'
                weight = 1.1
            elif price_vs_vwap == 'below':
                signal = 'bearish'
                weight = 1.1
        
        elif indicator_name == 'supertrend':
            supertrend_direction = result.get('supertrend_direction', 'neutral')
            price_vs_supertrend = result.get('price_vs_supertrend', 'neutral')
            if supertrend_direction == 'bullish' and price_vs_supertrend == 'above':
                signal = 'bullish'
                weight = 1.5
            elif supertrend_direction == 'bearish' and price_vs_supertrend == 'below':
                signal = 'bearish'
                weight = 1.5
        
    except Exception as e:
        print(f"Error analyzing {indicator_name} signal: {str(e)}")
        signal = 'neutral'
        weight = 0.0
    
    return signal, weight


def _assess_risk(df: pd.DataFrame, confidence: float) -> str:
    """
    Assess risk level based on market conditions and confidence
    
    Args:
        df: DataFrame with OHLC data
        confidence: Prediction confidence
        
    Returns:
        Risk level string
    """
    try:
        # Calculate volatility
        returns = df['close'].pct_change().dropna()
        volatility = returns.std()
        
        # Calculate volume consistency
        volume_cv = df['volume'].tail(10).std() / df['volume'].tail(10).mean()
        
        # Assess risk
        if confidence > 0.8 and volatility < 0.02 and volume_cv < 1.0:
            return 'low'
        elif confidence > 0.6 and volatility < 0.05:
            return 'medium'
        elif volatility > 0.08 or volume_cv > 2.0:
            return 'high'
        else:
            return 'medium'
            
    except Exception:
        return 'medium'


def _analyze_market_conditions(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze current market conditions
    
    Args:
        df: DataFrame with OHLC data
        
    Returns:
        Dictionary with market condition analysis
    """
    conditions = {}
    
    try:
        # Trend analysis
        ema_short = df['close'].ewm(span=10).mean()
        ema_long = df['close'].ewm(span=20).mean()
        
        if ema_short.iloc[-1] > ema_long.iloc[-1]:
            conditions['trend'] = 'bullish'
        elif ema_short.iloc[-1] < ema_long.iloc[-1]:
            conditions['trend'] = 'bearish'
        else:
            conditions['trend'] = 'sideways'
        
        # Volatility
        returns = df['close'].pct_change().dropna()
        volatility = returns.tail(10).std()
        
        if volatility > 0.05:
            conditions['volatility'] = 'high'
        elif volatility > 0.02:
            conditions['volatility'] = 'medium'
        else:
            conditions['volatility'] = 'low'
        
        # Volume trend
        volume_ma = df['volume'].rolling(window=10).mean()
        recent_volume = df['volume'].tail(3).mean()
        
        if recent_volume > volume_ma.iloc[-1] * 1.2:
            conditions['volume'] = 'increasing'
        elif recent_volume < volume_ma.iloc[-1] * 0.8:
            conditions['volume'] = 'decreasing'
        else:
            conditions['volume'] = 'stable'
        
        # Price momentum
        price_change = (df['close'].iloc[-1] - df['close'].iloc[-5]) / df['close'].iloc[-5]
        
        if price_change > 0.02:
            conditions['momentum'] = 'strong_bullish'
        elif price_change > 0.005:
            conditions['momentum'] = 'bullish'
        elif price_change < -0.02:
            conditions['momentum'] = 'strong_bearish'
        elif price_change < -0.005:
            conditions['momentum'] = 'bearish'
        else:
            conditions['momentum'] = 'neutral'
            
    except Exception as e:
        conditions['error'] = f"Error analyzing market conditions: {str(e)}"
    
    return conditions


def _generate_entry_suggestions(df: pd.DataFrame, prediction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate entry suggestions based on prediction
    
    Args:
        df: DataFrame with OHLC data
        prediction: Prediction dictionary
        
    Returns:
        Dictionary with entry suggestions
    """
    suggestions = {}
    
    try:
        current_price = float(df['close'].iloc[-1])
        atr_values = df['high'].rolling(14).max() - df['low'].rolling(14).min()
        avg_atr = atr_values.mean()
        
        if prediction['prediction'] in ['call', 'put']:
            # Entry timing suggestions
            if prediction['confidence'] > 0.8:
                suggestions['entry_timing'] = 'immediate'
            elif prediction['confidence'] > 0.6:
                suggestions['entry_timing'] = 'wait_for_confirmation'
            else:
                suggestions['entry_timing'] = 'avoid'
            
            # Risk management
            suggestions['position_size'] = 'small' if prediction['risk_assessment'] == 'high' else 'normal'
            
            # Stop loss suggestions (for longer timeframes)
            if prediction['prediction'] == 'call':
                suggestions['stop_loss'] = round(current_price - avg_atr * 0.5, 4)
                suggestions['take_profit'] = round(current_price + avg_atr * 1.0, 4)
            else:  # put
                suggestions['stop_loss'] = round(current_price + avg_atr * 0.5, 4)
                suggestions['take_profit'] = round(current_price - avg_atr * 1.0, 4)
            
            # Timeframe suggestions
            if prediction['confidence'] > 0.7:
                suggestions['recommended_timeframes'] = ['5m', '15m']
            else:
                suggestions['recommended_timeframes'] = ['1m', '5m']
        
        else:
            suggestions['entry_timing'] = 'avoid'
            suggestions['reason'] = 'No clear directional bias detected'
    
    except Exception as e:
        suggestions['error'] = f"Error generating suggestions: {str(e)}"
    
    return suggestions
