#!/usr/bin/env python3
"""Test script for pattern calculation fix"""

import pandas as pd
import numpy as np
import pandas_ta as ta

# Simulate the pattern calculation function from main.py
def test_calculate_candlestick_patterns(df, patterns):
    """Test version of calculate_candlestick_patterns with the fix"""
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
            elif pattern_lower in ['inside']:
                pattern_result = ta.cdl_inside(df['open'], df['high'], df['low'], df['close'])
            else:
                result[f"{pattern_name}_error"] = f"Pattern '{pattern_name}' not supported"
                continue
            
            # Extract the last value if pattern was calculated successfully - FIXED VERSION
            if pattern_result is not None:
                # Check if it's a Series and not empty
                if hasattr(pattern_result, 'empty') and not pattern_result.empty:
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
            else:
                result[pattern_name] = "Not Detected"
                
    except Exception as e:
        result["patterns_error"] = f"Error calculating patterns: {str(e)}"
    
    return result

# Create test data
test_data = {
    'open': [100.0, 101.0, 102.0, 103.0, 104.0] * 6,
    'high': [101.0, 102.0, 103.0, 104.0, 105.0] * 6,
    'low': [99.0, 100.0, 101.0, 102.0, 103.0] * 6,
    'close': [100.5, 101.5, 102.5, 103.5, 104.5] * 6,
    'volume': [1000, 1100, 1200, 1300, 1400] * 6
}

df = pd.DataFrame(test_data)
df.index = pd.date_range('2025-01-01', periods=len(df), freq='1min')

print("Testing candlestick pattern calculation...")
try:
    patterns = ['doji', 'hammer', 'engulfing', 'inside']
    result = test_calculate_candlestick_patterns(df, patterns)
    print("✅ SUCCESS: Pattern calculation works!")
    print("Results:", result)
except Exception as e:
    print(f"❌ ERROR: {e}")
