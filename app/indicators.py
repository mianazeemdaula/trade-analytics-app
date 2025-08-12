"""
Technical indicators calculation module
"""

import warnings
import os

# Suppress all pandas_ta related warnings including pkg_resources deprecation
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", category=UserWarning, module="pandas_ta")
os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning:pandas_ta'

from typing import Dict, List, Union, Any
import pandas as pd
import pandas_ta as ta
import numpy as np


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
            # EMA - Exponential Moving Average (supports multiple periods)
            if len(params) == 0:
                raise ValueError("EMA requires at least 1 parameter (period)")
            
            # Calculate EMA for each period provided
            for period in params:
                period = int(period)
                ema_values = ta.ema(df['close'], length=period)
                if not ema_values.empty:
                    result[f'ema_{period}'] = round(float(ema_values.iloc[-1]), 2)
        
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
        
        elif indicator_name.lower() == 'atr':
            # ATR - Average True Range
            if len(params) != 1:
                raise ValueError("ATR requires exactly 1 parameter (period)")
            period = int(params[0])
            atr_values = ta.atr(df['high'], df['low'], df['close'], length=period)
            if not atr_values.empty:
                result['atr'] = round(float(atr_values.iloc[-1]), 4)
        
        elif indicator_name.lower() == 'obv':
            # OBV - On-Balance Volume
            if len(params) != 0:
                raise ValueError("OBV requires no parameters")
            obv_values = ta.obv(df['close'], df['volume'])
            if not obv_values.empty:
                result['obv'] = round(float(obv_values.iloc[-1]), 2)
                # Add trend analysis
                if len(obv_values) >= 5:
                    obv_trend = "bullish" if obv_values.iloc[-1] > obv_values.iloc[-5] else "bearish"
                    result['obv_trend'] = obv_trend
        
        elif indicator_name.lower() == 'market_structure' or indicator_name.lower() == 'ms':
            # Market Structure - Higher Highs, Higher Lows, Lower Highs, Lower Lows
            result.update(_calculate_market_structure(df, params))
        
        elif indicator_name.lower() == 'support_resistance' or indicator_name.lower() == 'sr':
            # Support and Resistance Zones
            result.update(_calculate_support_resistance(df, params))
        
        elif indicator_name.lower() == 'stoch_rsi' or indicator_name.lower() == 'stochrsi':
            # Stochastic RSI
            result.update(_calculate_stoch_rsi(df, params))
        
        elif indicator_name.lower() == 'fibonacci' or indicator_name.lower() == 'fib':
            # Fibonacci Retracements
            result.update(_calculate_fibonacci(df, params))
        
        elif indicator_name.lower() == 'vwap':
            # Volume Weighted Average Price
            result.update(_calculate_vwap(df, params))
        
        elif indicator_name.lower() == 'volume_ma' or indicator_name.lower() == 'vma':
            # Volume Moving Average
            result.update(_calculate_volume_ma(df, params))
        
        elif indicator_name.lower() == 'supertrend':
            # SuperTrend
            result.update(_calculate_supertrend(df, params))
        
        elif indicator_name.lower() == 'volume_profile' or indicator_name.lower() == 'vp':
            # Volume Profile
            result.update(_calculate_volume_profile(df, params))
        
        elif indicator_name.lower() == 'price_action' or indicator_name.lower() == 'pa':
            # Price Action Analysis
            result.update(_calculate_price_action(df, params))
        
        elif indicator_name.lower() == 'order_flow' or indicator_name.lower() == 'of':
            # Order Flow Analysis
            result.update(_calculate_order_flow(df, params))
        
        elif indicator_name.lower() == 'supply_demand' or indicator_name.lower() == 'sd':
            # Supply and Demand Zones
            result.update(_calculate_supply_demand(df, params))
        
        else:
            raise ValueError(f"Unsupported indicator: {indicator_name}")
            
    except Exception as e:
        raise ValueError(f"Error calculating {indicator_name}: {str(e)}")
    
    return result


def _calculate_market_structure(df: pd.DataFrame, params: List[Union[int, float]]) -> Dict[str, Any]:
    """Calculate market structure analysis"""
    if len(params) != 1:
        raise ValueError("Market Structure requires exactly 1 parameter (lookback_period)")
    lookback = int(params[0])
    
    result = {}
    if len(df) >= lookback * 2:
        # Get recent highs and lows
        recent_highs = df['high'].tail(lookback * 2)
        recent_lows = df['low'].tail(lookback * 2)
        
        # Find swing highs and lows
        swing_highs = []
        swing_lows = []
        
        for i in range(lookback, len(recent_highs) - lookback):
            # Check for swing high
            if (recent_highs.iloc[i] == recent_highs.iloc[i-lookback:i+lookback+1].max()):
                swing_highs.append(recent_highs.iloc[i])
            
            # Check for swing low
            if (recent_lows.iloc[i] == recent_lows.iloc[i-lookback:i+lookback+1].min()):
                swing_lows.append(recent_lows.iloc[i])
        
        # Analyze market structure
        structure = "sideways"
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            if swing_highs[-1] > swing_highs[-2] and swing_lows[-1] > swing_lows[-2]:
                structure = "uptrend_hh_hl"  # Higher Highs, Higher Lows
            elif swing_highs[-1] < swing_highs[-2] and swing_lows[-1] < swing_lows[-2]:
                structure = "downtrend_lh_ll"  # Lower Highs, Lower Lows
            elif swing_highs[-1] > swing_highs[-2] and swing_lows[-1] < swing_lows[-2]:
                structure = "expanding_hh_ll"  # Higher Highs, Lower Lows (expanding)
            elif swing_highs[-1] < swing_highs[-2] and swing_lows[-1] > swing_lows[-2]:
                structure = "contracting_lh_hl"  # Lower Highs, Higher Lows (contracting)
        
        result['market_structure'] = structure
        if swing_highs:
            result['last_swing_high'] = round(float(swing_highs[-1]), 4)
        if swing_lows:
            result['last_swing_low'] = round(float(swing_lows[-1]), 4)
    
    return result


def _calculate_support_resistance(df: pd.DataFrame, params: List[Union[int, float]]) -> Dict[str, Any]:
    """Calculate support and resistance zones"""
    if len(params) != 2:
        raise ValueError("Support/Resistance requires exactly 2 parameters (lookback_period, zone_strength)")
    lookback, strength_threshold = int(params[0]), int(params[1])
    
    result = {}
    if len(df) >= lookback * 2:
        current_price = float(df['close'].iloc[-1])
        
        # Find potential support and resistance levels
        resistance_levels = []
        support_levels = []
        
        # Get recent significant highs and lows
        recent_data = df.tail(lookback * 3)
        
        # Find resistance levels (areas where price struggled to break above)
        for i in range(len(recent_data) - lookback):
            high_level = recent_data['high'].iloc[i:i+lookback].max()
            touches = sum(1 for h in recent_data['high'].iloc[i:] if abs(h - high_level) <= current_price * 0.002)  # 0.2% tolerance
            
            if touches >= strength_threshold and high_level not in [r['level'] for r in resistance_levels]:
                resistance_levels.append({
                    'level': round(high_level, 4),
                    'touches': touches,
                    'strength': 'strong' if touches >= strength_threshold * 1.5 else 'moderate'
                })
        
        # Find support levels (areas where price found support)
        for i in range(len(recent_data) - lookback):
            low_level = recent_data['low'].iloc[i:i+lookback].min()
            touches = sum(1 for l in recent_data['low'].iloc[i:] if abs(l - low_level) <= current_price * 0.002)  # 0.2% tolerance
            
            if touches >= strength_threshold and low_level not in [s['level'] for s in support_levels]:
                support_levels.append({
                    'level': round(low_level, 4),
                    'touches': touches,
                    'strength': 'strong' if touches >= strength_threshold * 1.5 else 'moderate'
                })
        
        # Sort and get closest levels
        resistance_levels.sort(key=lambda x: abs(x['level'] - current_price))
        support_levels.sort(key=lambda x: abs(x['level'] - current_price))
        
        result['current_price'] = round(current_price, 4)
        result['nearest_resistance'] = resistance_levels[0] if resistance_levels else None
        result['nearest_support'] = support_levels[0] if support_levels else None
        result['all_resistance_levels'] = resistance_levels[:3]  # Top 3 closest
        result['all_support_levels'] = support_levels[:3]  # Top 3 closest
    
    return result


def _calculate_stoch_rsi(df: pd.DataFrame, params: List[Union[int, float]]) -> Dict[str, Any]:
    """Calculate Stochastic RSI"""
    if len(params) != 3:
        raise ValueError("Stochastic RSI requires exactly 3 parameters (rsi_length, stoch_length, k)")
    rsi_length, stoch_length, k = int(params[0]), int(params[1]), int(params[2])
    
    result = {}
    stoch_rsi_data = ta.stochrsi(df['close'], length=rsi_length, rsi_length=rsi_length, k=k, d=3)
    if stoch_rsi_data is not None and not stoch_rsi_data.empty:
        stoch_rsi_k_col = f'STOCHRSIk_{rsi_length}_{stoch_length}_{k}_3'
        stoch_rsi_d_col = f'STOCHRSId_{rsi_length}_{stoch_length}_{k}_3'
        
        if stoch_rsi_k_col in stoch_rsi_data.columns:
            result['stoch_rsi_k'] = round(float(stoch_rsi_data[stoch_rsi_k_col].iloc[-1]), 2)
        if stoch_rsi_d_col in stoch_rsi_data.columns:
            result['stoch_rsi_d'] = round(float(stoch_rsi_data[stoch_rsi_d_col].iloc[-1]), 2)
    
    return result


def _calculate_fibonacci(df: pd.DataFrame, params: List[Union[int, float]]) -> Dict[str, Any]:
    """Calculate Fibonacci retracements"""
    if len(params) != 1:
        raise ValueError("Fibonacci requires exactly 1 parameter (lookback_period)")
    lookback = int(params[0])
    
    result = {}
    if len(df) >= lookback:
        recent_data = df.tail(lookback)
        high_price = recent_data['high'].max()
        low_price = recent_data['low'].min()
        current_price = float(df['close'].iloc[-1])
        
        # Calculate Fibonacci levels
        diff = high_price - low_price
        fib_levels = {
            'high': round(high_price, 4),
            'low': round(low_price, 4),
            'fib_0': round(high_price, 4),  # 0% (high)
            'fib_236': round(high_price - 0.236 * diff, 4),  # 23.6%
            'fib_382': round(high_price - 0.382 * diff, 4),  # 38.2%
            'fib_500': round(high_price - 0.500 * diff, 4),  # 50%
            'fib_618': round(high_price - 0.618 * diff, 4),  # 61.8%
            'fib_786': round(high_price - 0.786 * diff, 4),  # 78.6%
            'fib_100': round(low_price, 4),  # 100% (low)
        }
        
        # Find nearest fib level
        closest_level = min(fib_levels.items(), key=lambda x: abs(x[1] - current_price) if isinstance(x[1], (int, float)) else float('inf'))
        
        result.update(fib_levels)
        result['nearest_fib_level'] = closest_level[0]
        result['distance_to_nearest_fib'] = round(abs(current_price - closest_level[1]), 4)
    
    return result


def _calculate_vwap(df: pd.DataFrame, params: List[Union[int, float]]) -> Dict[str, Any]:
    """Calculate VWAP"""
    if len(params) != 0:
        raise ValueError("VWAP requires no parameters")
    
    result = {}
    vwap_values = ta.vwap(df['high'], df['low'], df['close'], df['volume'])
    if not vwap_values.empty:
        current_vwap = float(vwap_values.iloc[-1])
        current_price = float(df['close'].iloc[-1])
        result['vwap'] = round(current_vwap, 4)
        result['price_vs_vwap'] = "above" if current_price > current_vwap else "below"
        result['vwap_distance'] = round(abs(current_price - current_vwap), 4)
    
    return result


def _calculate_volume_ma(df: pd.DataFrame, params: List[Union[int, float]]) -> Dict[str, Any]:
    """Calculate Volume Moving Average"""
    if len(params) != 1:
        raise ValueError("Volume MA requires exactly 1 parameter (period)")
    period = int(params[0])
    
    result = {}
    volume_ma = df['volume'].rolling(window=period).mean()
    if not volume_ma.empty:
        current_volume = float(df['volume'].iloc[-1])
        current_vma = float(volume_ma.iloc[-1])
        result['volume_ma'] = round(current_vma, 2)
        result['volume_vs_ma'] = round(current_volume / current_vma, 2)
        result['volume_trend'] = "high" if current_volume > current_vma * 1.2 else "normal" if current_volume > current_vma * 0.8 else "low"
    
    return result


def _calculate_supertrend(df: pd.DataFrame, params: List[Union[int, float]]) -> Dict[str, Any]:
    """Calculate SuperTrend"""
    if len(params) != 2:
        raise ValueError("SuperTrend requires exactly 2 parameters (period, multiplier)")
    period, multiplier = int(params[0]), float(params[1])
    
    result = {}
    supertrend_data = ta.supertrend(df['high'], df['low'], df['close'], length=period, multiplier=multiplier)
    if supertrend_data is not None and not supertrend_data.empty:
        st_col = f'SUPERT_{period}_{multiplier}'
        std_col = f'SUPERTd_{period}_{multiplier}'
        
        if st_col in supertrend_data.columns:
            current_price = float(df['close'].iloc[-1])
            supertrend_value = float(supertrend_data[st_col].iloc[-1])
            supertrend_direction = int(supertrend_data[std_col].iloc[-1]) if std_col in supertrend_data.columns else 0
            
            result['supertrend_value'] = round(supertrend_value, 4)
            result['supertrend_direction'] = "bullish" if supertrend_direction == 1 else "bearish"
            result['price_vs_supertrend'] = "above" if current_price > supertrend_value else "below"
    
    return result


def _calculate_volume_profile(df: pd.DataFrame, params: List[Union[int, float]]) -> Dict[str, Any]:
    """Calculate Volume Profile"""
    if len(params) != 2:
        raise ValueError("Volume Profile requires exactly 2 parameters (lookback_period, price_bins)")
    lookback, bins = int(params[0]), int(params[1])
    
    result = {}
    if len(df) >= lookback:
        recent_data = df.tail(lookback)
        
        # Create price bins
        price_range = recent_data['high'].max() - recent_data['low'].min()
        bin_size = price_range / bins
        
        poc_volume = 0
        poc_price = 0
        
        for i in range(bins):
            bin_low = recent_data['low'].min() + i * bin_size
            bin_high = bin_low + bin_size
            
            # Calculate volume in this price range
            volume_in_bin = 0
            for _, row in recent_data.iterrows():
                if bin_low <= row['close'] <= bin_high:
                    volume_in_bin += row['volume']
            
            if volume_in_bin > poc_volume:
                poc_volume = volume_in_bin
                poc_price = (bin_low + bin_high) / 2
        
        result['volume_profile_poc'] = round(poc_price, 4)  # Point of Control
        result['poc_volume'] = round(poc_volume, 2)
        result['current_price'] = round(float(df['close'].iloc[-1]), 4)
        result['distance_from_poc'] = round(abs(float(df['close'].iloc[-1]) - poc_price), 4)
    
    return result


def _calculate_price_action(df: pd.DataFrame, params: List[Union[int, float]]) -> Dict[str, Any]:
    """Calculate Price Action Analysis"""
    if len(params) != 1:
        raise ValueError("Price Action requires exactly 1 parameter (lookback_period)")
    lookback = int(params[0])
    
    result = {}
    if len(df) >= lookback:
        recent_data = df.tail(lookback)
        
        # Calculate price action metrics
        body_sizes = abs(recent_data['close'] - recent_data['open'])
        wick_sizes_upper = recent_data['high'] - recent_data[['open', 'close']].max(axis=1)
        wick_sizes_lower = recent_data[['open', 'close']].min(axis=1) - recent_data['low']
        
        avg_body_size = body_sizes.mean()
        avg_upper_wick = wick_sizes_upper.mean()
        avg_lower_wick = wick_sizes_lower.mean()
        
        # Recent candle analysis
        last_candle = recent_data.iloc[-1]
        last_body_size = abs(last_candle['close'] - last_candle['open'])
        last_upper_wick = last_candle['high'] - max(last_candle['open'], last_candle['close'])
        last_lower_wick = min(last_candle['open'], last_candle['close']) - last_candle['low']
        
        result['avg_body_size'] = round(avg_body_size, 4)
        result['avg_upper_wick'] = round(avg_upper_wick, 4)
        result['avg_lower_wick'] = round(avg_lower_wick, 4)
        result['last_body_size'] = round(last_body_size, 4)
        result['last_upper_wick'] = round(last_upper_wick, 4)
        result['last_lower_wick'] = round(last_lower_wick, 4)
        result['candle_type'] = "bullish" if last_candle['close'] > last_candle['open'] else "bearish"
        result['body_vs_avg'] = "large" if last_body_size > avg_body_size * 1.5 else "normal" if last_body_size > avg_body_size * 0.5 else "small"
    
    return result


def _calculate_order_flow(df: pd.DataFrame, params: List[Union[int, float]]) -> Dict[str, Any]:
    """Calculate Order Flow Analysis"""
    if len(params) != 1:
        raise ValueError("Order Flow requires exactly 1 parameter (lookback_period)")
    lookback = int(params[0])
    
    result = {}
    if len(df) >= lookback:
        recent_data = df.tail(lookback)
        
        # Calculate buying vs selling pressure (simplified)
        buying_volume = 0
        selling_volume = 0
        
        for _, row in recent_data.iterrows():
            if row['close'] > row['open']:  # Bullish candle
                buying_volume += row['volume']
            else:  # Bearish candle
                selling_volume += row['volume']
        
        total_volume = buying_volume + selling_volume
        
        if total_volume > 0:
            buying_pressure = buying_volume / total_volume
            selling_pressure = selling_volume / total_volume
            
            result['buying_volume'] = round(buying_volume, 2)
            result['selling_volume'] = round(selling_volume, 2)
            result['buying_pressure'] = round(buying_pressure, 3)
            result['selling_pressure'] = round(selling_pressure, 3)
            result['order_flow_bias'] = "bullish" if buying_pressure > 0.6 else "bearish" if selling_pressure > 0.6 else "neutral"
            
            # Volume delta
            result['volume_delta'] = round(buying_volume - selling_volume, 2)
    
    return result


def _calculate_supply_demand(df: pd.DataFrame, params: List[Union[int, float]]) -> Dict[str, Any]:
    """Calculate Supply and Demand Zones with improved detection"""
    if len(params) != 2:
        raise ValueError("Supply/Demand requires exactly 2 parameters (lookback_period, zone_strength)")
    
    lookback = int(params[0]) if params[0] > 5 else 20  # Default to 20 if too small
    min_strength = int(params[1]) if params[1] > 0 else 2  # Default to 2
    
    result = {}
    
    if len(df) < lookback:
        # Not enough data - return default structure
        current_price = float(df['close'].iloc[-1])
        result = {
            'current_price': round(current_price, 2),
            'nearest_supply_zone': None,
            'nearest_demand_zone': None,
            'all_supply_zones': [],
            'all_demand_zones': []
        }
        return result
    
    current_price = float(df['close'].iloc[-1])
    supply_zones = []
    demand_zones = []
    
    # Use more data for better zone detection
    data_window = df.tail(min(len(df), lookback * 3))
    
    # Improved zone detection algorithm
    for i in range(min_strength, len(data_window) - min_strength):
        current_row = data_window.iloc[i]
        
        # Look at surrounding candles
        window_before = data_window.iloc[max(0, i-min_strength):i]
        window_after = data_window.iloc[i+1:min(len(data_window), i+min_strength+1)]
        
        current_high = current_row['high']
        current_low = current_row['low']
        current_close = current_row['close']
        current_open = current_row['open']
        current_volume = current_row['volume']
        
        # Supply Zone Detection (Resistance areas)
        # Check if current high is higher than surrounding highs
        before_highs = window_before['high'].max() if len(window_before) > 0 else 0
        after_highs = window_after['high'].max() if len(window_after) > 0 else 0
        
        # More lenient supply zone detection
        if (current_high >= before_highs and current_high >= after_highs and
            current_volume > data_window['volume'].mean() * 0.8):  # Lower volume threshold
            
            # Create supply zone
            zone_high = current_high
            zone_low = max(current_open, current_close)  # Use body as zone low
            
            # Calculate zone strength based on volume and price rejection
            rejection = (current_high - current_close) / current_high if current_high > 0 else 0
            volume_strength = current_volume / data_window['volume'].mean()
            
            strength_score = (rejection * 100) + (volume_strength * 50)
            strength_level = 'strong' if strength_score > 100 else 'moderate' if strength_score > 50 else 'weak'
            
            supply_zones.append({
                'high': round(zone_high, 2),
                'low': round(zone_low, 2),
                'volume': round(current_volume, 0),
                'strength': strength_level,
                'distance_from_current': abs(zone_low - current_price)
            })
        
        # Demand Zone Detection (Support areas)
        # Check if current low is lower than surrounding lows
        before_lows = window_before['low'].min() if len(window_before) > 0 else float('inf')
        after_lows = window_after['low'].min() if len(window_after) > 0 else float('inf')
        
        # More lenient demand zone detection
        if (current_low <= before_lows and current_low <= after_lows and
            current_volume > data_window['volume'].mean() * 0.8):  # Lower volume threshold
            
            # Create demand zone
            zone_low = current_low
            zone_high = min(current_open, current_close)  # Use body as zone high
            
            # Calculate zone strength
            bounce = (current_close - current_low) / current_close if current_close > 0 else 0
            volume_strength = current_volume / data_window['volume'].mean()
            
            strength_score = (bounce * 100) + (volume_strength * 50)
            strength_level = 'strong' if strength_score > 100 else 'moderate' if strength_score > 50 else 'weak'
            
            demand_zones.append({
                'low': round(zone_low, 2),
                'high': round(zone_high, 2),
                'volume': round(current_volume, 0),
                'strength': strength_level,
                'distance_from_current': abs(zone_high - current_price)
            })
    
    # Remove duplicate zones (zones too close to each other)
    def remove_duplicates(zones, min_distance_pct=0.01):
        if not zones:
            return zones
        
        unique_zones = []
        for zone in zones:
            is_duplicate = False
            zone_center = (zone['high'] + zone['low']) / 2
            
            for existing in unique_zones:
                existing_center = (existing['high'] + existing['low']) / 2
                distance_pct = abs(zone_center - existing_center) / existing_center
                
                if distance_pct < min_distance_pct:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_zones.append(zone)
        
        return unique_zones
    
    # Clean up zones
    supply_zones = remove_duplicates(supply_zones)
    demand_zones = remove_duplicates(demand_zones)
    
    # Sort by distance from current price
    supply_zones.sort(key=lambda x: x['distance_from_current'])
    demand_zones.sort(key=lambda x: x['distance_from_current'])
    
    # Build result
    result = {
        'current_price': round(current_price, 2),
        'nearest_supply_zone': supply_zones[0] if supply_zones else None,
        'nearest_demand_zone': demand_zones[0] if demand_zones else None,
        'all_supply_zones': supply_zones[:5],  # Top 5 zones
        'all_demand_zones': demand_zones[:5]   # Top 5 zones
    }
    
    # Remove distance field from final output (internal use only)
    for zone_list in [result['all_supply_zones'], result['all_demand_zones']]:
        for zone in zone_list:
            zone.pop('distance_from_current', None)
    
    if result['nearest_supply_zone']:
        result['nearest_supply_zone'].pop('distance_from_current', None)
    if result['nearest_demand_zone']:
        result['nearest_demand_zone'].pop('distance_from_current', None)
    
    return result
    
    return result
