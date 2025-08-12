"""
Candlestick pattern detection module
"""

from typing import Dict, List
import pandas as pd
import pandas_ta as ta


def calculate_candlestick_patterns(df: pd.DataFrame) -> Dict[str, bool]:
    """
    Calculate various candlestick patterns using pandas_ta
    
    Args:
        df: DataFrame with OHLC data
        
    Returns:
        Dictionary with pattern names and boolean values
    """
    patterns = {}
    
    try:
        # Doji pattern
        doji = ta.cdl_doji(df['open'], df['high'], df['low'], df['close'])
        patterns['doji'] = bool(doji.iloc[-1]) if not doji.empty else False
        
        # Hammer pattern
        hammer = ta.cdl_hammer(df['open'], df['high'], df['low'], df['close'])
        patterns['hammer'] = bool(hammer.iloc[-1]) if not hammer.empty else False
        
        # Shooting Star pattern
        shooting_star = ta.cdl_shootingstar(df['open'], df['high'], df['low'], df['close'])
        patterns['shooting_star'] = bool(shooting_star.iloc[-1]) if not shooting_star.empty else False
        
        # Engulfing patterns
        engulfing = ta.cdl_engulfing(df['open'], df['high'], df['low'], df['close'])
        if not engulfing.empty:
            last_engulfing = engulfing.iloc[-1]
            patterns['bullish_engulfing'] = bool(last_engulfing > 0)
            patterns['bearish_engulfing'] = bool(last_engulfing < 0)
        else:
            patterns['bullish_engulfing'] = False
            patterns['bearish_engulfing'] = False
        
        # Harami patterns
        harami = ta.cdl_harami(df['open'], df['high'], df['low'], df['close'])
        if not harami.empty:
            last_harami = harami.iloc[-1]
            patterns['bullish_harami'] = bool(last_harami > 0)
            patterns['bearish_harami'] = bool(last_harami < 0)
        else:
            patterns['bullish_harami'] = False
            patterns['bearish_harami'] = False
        
        # Morning Star pattern
        morning_star = ta.cdl_morningstar(df['open'], df['high'], df['low'], df['close'])
        patterns['morning_star'] = bool(morning_star.iloc[-1]) if not morning_star.empty else False
        
        # Evening Star pattern
        evening_star = ta.cdl_eveningstar(df['open'], df['high'], df['low'], df['close'])
        patterns['evening_star'] = bool(evening_star.iloc[-1]) if not evening_star.empty else False
        
        # Three White Soldiers pattern
        three_white_soldiers = ta.cdl_3whitesoldiers(df['open'], df['high'], df['low'], df['close'])
        patterns['three_white_soldiers'] = bool(three_white_soldiers.iloc[-1]) if not three_white_soldiers.empty else False
        
        # Three Black Crows pattern
        three_black_crows = ta.cdl_3blackcrows(df['open'], df['high'], df['low'], df['close'])
        patterns['three_black_crows'] = bool(three_black_crows.iloc[-1]) if not three_black_crows.empty else False
        
        # Dark Cloud Cover pattern
        dark_cloud_cover = ta.cdl_darkcloudcover(df['open'], df['high'], df['low'], df['close'])
        patterns['dark_cloud_cover'] = bool(dark_cloud_cover.iloc[-1]) if not dark_cloud_cover.empty else False
        
        # Piercing Line pattern
        piercing = ta.cdl_piercing(df['open'], df['high'], df['low'], df['close'])
        patterns['piercing_line'] = bool(piercing.iloc[-1]) if not piercing.empty else False
        
        # Hanging Man pattern
        hanging_man = ta.cdl_hangingman(df['open'], df['high'], df['low'], df['close'])
        patterns['hanging_man'] = bool(hanging_man.iloc[-1]) if not hanging_man.empty else False
        
        # Inverted Hammer pattern
        inverted_hammer = ta.cdl_invertedhammer(df['open'], df['high'], df['low'], df['close'])
        patterns['inverted_hammer'] = bool(inverted_hammer.iloc[-1]) if not inverted_hammer.empty else False
        
        # Spinning Top pattern
        spinning_top = ta.cdl_spinningtop(df['open'], df['high'], df['low'], df['close'])
        patterns['spinning_top'] = bool(spinning_top.iloc[-1]) if not spinning_top.empty else False
        
        # Marubozu patterns
        marubozu = ta.cdl_marubozu(df['open'], df['high'], df['low'], df['close'])
        if not marubozu.empty:
            last_marubozu = marubozu.iloc[-1]
            patterns['bullish_marubozu'] = bool(last_marubozu > 0)
            patterns['bearish_marubozu'] = bool(last_marubozu < 0)
        else:
            patterns['bullish_marubozu'] = False
            patterns['bearish_marubozu'] = False
        
        # Dragonfly Doji pattern
        dragonfly_doji = ta.cdl_dragonflydoji(df['open'], df['high'], df['low'], df['close'])
        patterns['dragonfly_doji'] = bool(dragonfly_doji.iloc[-1]) if not dragonfly_doji.empty else False
        
        # Gravestone Doji pattern
        gravestone_doji = ta.cdl_gravestonedoji(df['open'], df['high'], df['low'], df['close'])
        patterns['gravestone_doji'] = bool(gravestone_doji.iloc[-1]) if not gravestone_doji.empty else False
        
        # Long Legged Doji pattern
        long_legged_doji = ta.cdl_longleggeddoji(df['open'], df['high'], df['low'], df['close'])
        patterns['long_legged_doji'] = bool(long_legged_doji.iloc[-1]) if not long_legged_doji.empty else False
        
        # Four Price Doji pattern (all prices equal)
        four_price_doji = ta.cdl_4price(df['open'], df['high'], df['low'], df['close'])
        patterns['four_price_doji'] = bool(four_price_doji.iloc[-1]) if not four_price_doji.empty else False
        
    except Exception as e:
        # If any pattern calculation fails, return empty patterns dict
        print(f"Error calculating candlestick patterns: {str(e)}")
        patterns = {}
    
    return patterns


def get_pattern_interpretation(patterns: Dict[str, bool]) -> Dict[str, str]:
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
        'bullish_engulfing': 'Strong bullish reversal - buyers overwhelm sellers',
        'bearish_engulfing': 'Strong bearish reversal - sellers overwhelm buyers',
        'bullish_harami': 'Bullish reversal - weakening selling pressure',
        'bearish_harami': 'Bearish reversal - weakening buying pressure',
        'morning_star': 'Strong bullish reversal - three-candle pattern',
        'evening_star': 'Strong bearish reversal - three-candle pattern',
        'three_white_soldiers': 'Strong bullish continuation - sustained buying',
        'three_black_crows': 'Strong bearish continuation - sustained selling',
        'dark_cloud_cover': 'Bearish reversal - selling pressure emerges',
        'piercing_line': 'Bullish reversal - buying pressure emerges',
        'hanging_man': 'Bearish reversal - selling pressure after advance',
        'inverted_hammer': 'Bullish reversal - potential buying interest',
        'spinning_top': 'Indecision - small body with long wicks',
        'bullish_marubozu': 'Strong bullish sentiment - no wicks, strong buying',
        'bearish_marubozu': 'Strong bearish sentiment - no wicks, strong selling',
        'dragonfly_doji': 'Bullish reversal - long lower wick, buying support',
        'gravestone_doji': 'Bearish reversal - long upper wick, selling pressure',
        'long_legged_doji': 'High indecision - long wicks both sides',
        'four_price_doji': 'Extreme indecision - all prices equal'
    }
    
    for pattern, detected in patterns.items():
        if detected and pattern in pattern_meanings:
            interpretations[pattern] = pattern_meanings[pattern]
    
    return interpretations


def get_pattern_signals(patterns: Dict[str, bool]) -> Dict[str, str]:
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
        'hammer', 'bullish_engulfing', 'bullish_harami', 'morning_star',
        'three_white_soldiers', 'piercing_line', 'inverted_hammer',
        'bullish_marubozu', 'dragonfly_doji'
    ]
    
    bearish_patterns = [
        'shooting_star', 'bearish_engulfing', 'bearish_harami', 'evening_star',
        'three_black_crows', 'dark_cloud_cover', 'hanging_man',
        'bearish_marubozu', 'gravestone_doji'
    ]
    
    neutral_patterns = [
        'doji', 'spinning_top', 'long_legged_doji', 'four_price_doji'
    ]
    
    bullish_count = 0
    bearish_count = 0
    neutral_count = 0
    
    for pattern, detected in patterns.items():
        if detected:
            signals['detected_patterns'].append(pattern)
            
            if pattern in bullish_patterns:
                signals['bullish_patterns'].append(pattern)
                bullish_count += 1
            elif pattern in bearish_patterns:
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
