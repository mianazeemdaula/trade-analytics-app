"""
Candlestick pattern detection module
"""

import warnings
import os

# Suppress all pandas_ta related warnings including pkg_resources deprecation
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", category=UserWarning, module="pandas_ta")
os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning:pandas_ta'

from typing import Dict, List, Any
import pandas as pd
import pandas_ta as ta


def calculate_candlestick_patterns(df: pd.DataFrame, patterns: List[str] = None) -> Dict[str, Any]:
    """
    Calculate candlestick patterns using pandas_ta, with robust error handling.
    
    Args:
        df: DataFrame with OHLC data
        patterns: List of pattern names to calculate (if None, uses default set)
        
    Returns:
        Dictionary with pattern results (last values only). Returns 'Not Detected'
        for patterns that don't match, and an error message for unsupported patterns.
    """
    from typing import List, Any
    
    result = {}

    # A dictionary to map user-friendly names to pandas_ta's official names
    # This simplifies the logic and makes it more scalable.
    pattern_name_map = {
        'hammer': 'hammer', 'doji': 'doji', 'engulfing': 'engulfing',
        'harami': 'harami', 'morning_star': 'morningstar', 'morningstar': 'morningstar',
        'evening_star': 'eveningstar', 'eveningstar': 'eveningstar',
        'shooting_star': 'shootingstar', 'shootingstar': 'shootingstar',
        'hanging_man': 'hangingman', 'hangingman': 'hangingman',
        'inverted_hammer': 'invertedhammer', 'invertedhammer': 'invertedhammer',
        'dark_cloud_cover': 'darkcloudcover', 'darkcloudcover': 'darkcloudcover',
        'piercing': 'piercing', 'marubozu': 'marubozu',
        'spinning_top': 'spinningtop', 'spinningtop': 'spinningtop',
        'three_white_soldiers': '3whitesoldiers', '3whitesoldiers': '3whitesoldiers',
        'three_black_crows': '3blackcrows', '3blackcrows': '3blackcrows',
        'inside': 'inside', 'abandoned_baby': 'abandonedbaby',
        'dragonfly_doji': 'dragonflydoji', 'dragonflydoji': 'dragonflydoji',
        'gravestone_doji': 'gravestonedoji', 'gravestonedoji': 'gravestonedoji',
        'long_legged_doji': 'longleggeddoji', 'longleggeddoji': 'longleggeddoji',
    }
    
    # Default patterns if none specified
    if patterns is None:
        patterns = [
            'doji', 'hammer', 'shootingstar', 'engulfing', 'harami',
            'morningstar', 'eveningstar', '3whitesoldiers', '3blackcrows',
            'darkcloudcover', 'piercing', 'hangingman', 'invertedhammer',
            'spinningtop', 'marubozu', 'dragonflydoji', 'gravestonedoji',
            'longleggeddoji', 'inside'
        ]

    try:
        for pattern_name in patterns:
            pattern_lower = pattern_name.lower().replace(" ", "_")
            ta_pattern_name = pattern_name_map.get(pattern_lower)

            if not ta_pattern_name:
                result[pattern_name] = "Pattern Not Supported"
                continue

            pattern_result = None

            # Special case for Doji and Inside patterns which have dedicated functions.
            if ta_pattern_name == 'doji':
                pattern_result = ta.cdl_doji(df['open'], df['high'], df['low'], df['close'])
            elif ta_pattern_name == 'inside':
                pattern_result = ta.cdl_inside(df['open'], df['high'], df['low'], df['close'])
            else:
                # Use the general cdl_pattern function for all others.
                # This is more efficient and avoids a large if/elif block.
                try:
                    pattern_result = ta.cdl_pattern(
                        open_=df['open'], 
                        high=df['high'], 
                        low=df['low'], 
                        close=df['close'], 
                        name=ta_pattern_name
                    )
                except Exception as e:
                    result[pattern_name] = f"Error: {str(e)}"
                    continue

            # ---- The core fix for pattern detection ----
            # Handle both Series and DataFrame results from pandas_ta
            if pattern_result is not None:
                # Extract the data series
                if isinstance(pattern_result, pd.DataFrame):
                    if not pattern_result.empty and len(pattern_result.columns) > 0:
                        first_col = pattern_result.columns[0]
                        data_series = pattern_result[first_col]
                    else:
                        result[pattern_name] = "Not Detected"
                        continue
                elif isinstance(pattern_result, pd.Series):
                    if not pattern_result.empty:
                        data_series = pattern_result
                    else:
                        result[pattern_name] = "Not Detected"
                        continue
                else:
                    result[pattern_name] = "Not Detected"
                    continue

                # Look for ANY non-zero values in the entire series, not just the last one
                non_zero_values = data_series[data_series != 0].dropna()

                if not non_zero_values.empty:
                    # Count detections by type
                    bullish_signals = non_zero_values[non_zero_values > 0]
                    bearish_signals = non_zero_values[non_zero_values < 0]

                    bullish_count = len(bullish_signals)
                    bearish_count = len(bearish_signals)

                    # Determine overall signal based on pattern counts and strength
                    if bullish_count > bearish_count:
                        # More bullish signals
                        strongest_signal = bullish_signals.abs().max()
                        result[pattern_name] = f"Bullish ({bullish_count} signals)"
                    elif bearish_count > bullish_count:
                        # More bearish signals  
                        strongest_signal = bearish_signals.abs().max()
                        result[pattern_name] = f"Bearish ({bearish_count} signals)"
                    elif bullish_count == bearish_count and bullish_count > 0:
                        # Equal signals, use the most recent or strongest
                        last_signal = non_zero_values.iloc[-1]
                        if last_signal > 0:
                            result[pattern_name] = f"Bullish ({bullish_count} signals)"
                        else:
                            result[pattern_name] = f"Bearish ({bearish_count} signals)"
                    else:
                        result[pattern_name] = "Not Detected"
                else:
                    # No non-zero values found
                    result[pattern_name] = "Not Detected"
            else:
                # If the result is None, the pattern was not detected.
                result[pattern_name] = "Not Detected"

    except Exception as e:
        # A broader catch for any other unexpected errors.
        result["patterns_error"] = f"A general error occurred: {str(e)}"

    return result


def get_pattern_interpretation(patterns: Dict[str, str]) -> Dict[str, str]:
    """
    Get interpretations for detected patterns
    
    Args:
        patterns: Dictionary of pattern names and their detection status
        
    Returns:
        Dictionary of detected patterns with their interpretations
    """
    interpretations = {}
    
    pattern_meanings = {
        'doji': 'Indecision - market uncertainty, potential reversal signal',
        'hammer': 'Bullish reversal - strong buying pressure after decline',
        'shooting_star': 'Bearish reversal - selling pressure after advance',
        'engulfing': 'Strong reversal - buyers/sellers overwhelm opposite side',
        'harami': 'Reversal - weakening pressure from current trend',
        'morning_star': 'Strong bullish reversal - three-candle pattern',
        'evening_star': 'Strong bearish reversal - three-candle pattern',
        'three_white_soldiers': 'Strong bullish continuation - sustained buying',
        'three_black_crows': 'Strong bearish continuation - sustained selling',
        'dark_cloud_cover': 'Bearish reversal - selling pressure emerges',
        'piercing': 'Bullish reversal - buying pressure emerges',
        'hanging_man': 'Bearish reversal - selling pressure after advance',
        'inverted_hammer': 'Bullish reversal - potential buying interest',
        'spinning_top': 'Indecision - small body with long wicks',
        'marubozu': 'Strong sentiment - no wicks, strong directional pressure',
        'dragonfly_doji': 'Bullish reversal - long lower wick, buying support',
        'gravestone_doji': 'Bearish reversal - long upper wick, selling pressure',
        'long_legged_doji': 'High indecision - long wicks both sides',
        'inside': 'Consolidation - contained within previous candle range'
    }
    
    for pattern, status in patterns.items():
        if pattern in pattern_meanings and status != "Not Detected" and not status.startswith("Error"):
            interpretations[pattern] = f"{pattern_meanings[pattern]} - {status}"
    
    return interpretations


def get_pattern_signals(patterns: Dict[str, str]) -> Dict[str, Any]:
    """
    Get trading signals based on detected patterns
    
    Args:
        patterns: Dictionary of pattern names and their detection status
        
    Returns:
        Dictionary with signal strength and direction
    """
    signals = {
        'overall_signal': 'neutral',
        'signal_strength': 'weak',
        'detected_patterns': [],
        'bullish_patterns': [],
        'bearish_patterns': [],
        'neutral_patterns': []
    }
    
    bullish_patterns = [
        'hammer', 'morning_star', 'three_white_soldiers', 'piercing',
        'inverted_hammer', 'dragonfly_doji'
    ]
    
    bearish_patterns = [
        'shooting_star', 'evening_star', 'three_black_crows', 
        'dark_cloud_cover', 'hanging_man', 'gravestone_doji'
    ]
    
    neutral_patterns = [
        'doji', 'spinning_top', 'long_legged_doji', 'inside'
    ]
    
    bullish_count = 0
    bearish_count = 0
    neutral_count = 0
    
    for pattern, status in patterns.items():
        if status != "Not Detected" and not status.startswith("Error") and not status.startswith("Pattern Not Supported"):
            signals['detected_patterns'].append(pattern)
            
            # Check if it's explicitly bullish or bearish in the status
            if "Bullish" in status or pattern in bullish_patterns:
                signals['bullish_patterns'].append(pattern)
                bullish_count += 1
            elif "Bearish" in status or pattern in bearish_patterns:
                signals['bearish_patterns'].append(pattern)
                bearish_count += 1
            elif pattern in neutral_patterns:
                signals['neutral_patterns'].append(pattern)
                neutral_count += 1
    
    # Determine overall signal
    if bullish_count > bearish_count:
        signals['overall_signal'] = 'bullish'
    elif bearish_count > bullish_count:
        signals['overall_signal'] = 'bearish'
    else:
        signals['overall_signal'] = 'neutral'
    
    # Determine signal strength
    total_patterns = bullish_count + bearish_count + neutral_count
    if total_patterns >= 3:
        signals['signal_strength'] = 'strong'
    elif total_patterns >= 2:
        signals['signal_strength'] = 'moderate'
    else:
        signals['signal_strength'] = 'weak'
    
    return signals
