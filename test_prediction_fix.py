#!/usr/bin/env python3
"""Simple test for the prediction function fix"""

import pandas as pd
import numpy as np
from main import predict_binary_options

# Create test data with some NaN values to simulate the issue
test_data = {
    'open': [100.0, 101.0, 102.0, 103.0, 104.0] * 6,
    'high': [101.0, 102.0, 103.0, 104.0, 105.0] * 6,
    'low': [99.0, 100.0, 101.0, 102.0, 103.0] * 6,
    'close': [100.5, 101.5, 102.5, 103.5, 104.5] * 6,
    'volume': [1000, 1100, 1200, 1300, 1400] * 6
}

# Add some NaN values to test robustness
test_data['volume'][10] = None
test_data['close'][5] = None

df = pd.DataFrame(test_data)
df.index = pd.date_range('2025-01-01', periods=len(df), freq='1min')

print("Testing prediction function with problematic data...")
try:
    result = predict_binary_options(df, prediction_timeframe=2, confidence_threshold=0.6)
    print("✅ SUCCESS: Prediction function works!")
    print(f"Prediction: {result['prediction']['direction']}")
    print(f"Confidence: {result['prediction']['confidence']}")
    if 'error' in result:
        print(f"⚠️  Warning: {result['error']}")
except Exception as e:
    print(f"❌ ERROR: {e}")
