"""
Utility functions for data processing and conversion
"""

from fastapi import HTTPException
from typing import List
import pandas as pd
from .models import OHLCData


def convert_ohlc_to_dataframe(ohlc_data: List[OHLCData]) -> pd.DataFrame:
    """
    Convert OHLC data list to pandas DataFrame
    
    Args:
        ohlc_data: List of OHLC data objects
        
    Returns:
        pandas DataFrame with OHLC data
    """
    # Convert to list of dictionaries
    data_dicts = []
    for candle in ohlc_data:
        try:
            record = {
                'time': candle.get_time(),
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'volume': candle.get_volume()
            }
            data_dicts.append(record)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing candle data: {str(e)}")
    
    # Create DataFrame
    df = pd.DataFrame(data_dicts)
    
    # Convert time column to datetime
    df['time'] = pd.to_datetime(df['time'])
    
    # Set time as index for better compatibility with pandas_ta
    df.set_index('time', inplace=True)
    
    # Ensure columns are in the right order and type
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df
