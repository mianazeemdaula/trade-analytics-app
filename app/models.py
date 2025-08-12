"""
Pydantic models for request validation
"""

from pydantic import BaseModel, field_validator
from typing import Dict, List, Any, Union, Optional
import pandas as pd


class OHLCData(BaseModel):
    """Model for individual OHLC candle data"""
    time: Optional[str] = None
    datetime: Optional[str] = None  # Alternative time field name
    open: Union[float, str]
    high: Union[float, str]
    low: Union[float, str]
    close: Union[float, str]
    volume: Optional[Union[float, str]] = None  # Make volume optional
    
    @field_validator('open', 'high', 'low', 'close', 'volume')
    def convert_to_float(cls, v):
        """Convert string numbers to float, handle None for volume"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                raise ValueError(f"Cannot convert '{v}' to float")
        return float(v)
    
    @field_validator('time', 'datetime')
    def validate_time_fields(cls, v):
        """Validate time format"""
        if v is None:
            return None
        try:
            pd.to_datetime(v)
            return v
        except Exception:
            raise ValueError(f"Invalid time format: '{v}'. Use formats like '2025-07-01 07:45:25'")
    
    def get_time(self) -> str:
        """Get the time value, preferring 'time' over 'datetime'"""
        if self.time is not None:
            return self.time
        elif self.datetime is not None:
            return self.datetime
        else:
            raise ValueError("Either 'time' or 'datetime' field must be provided")
    
    def get_volume(self) -> float:
        """Get volume, return default if not provided"""
        return self.volume if self.volume is not None else 1000.0


class AnalysisRequest(BaseModel):
    """Model for the main request containing indicators and OHLC data"""
    indicators: Dict[str, List[Union[int, float]]]
    ohlc_data: List[OHLCData]
    include_patterns: Optional[bool] = True


class BinaryOptionsRequest(BaseModel):
    """Model for binary options prediction request"""
    ohlc_data: List[OHLCData]
    prediction_timeframe: Optional[int] = 2  # Number of candles to predict (default 2)
    confidence_threshold: Optional[float] = 0.6  # Minimum confidence level (0.5-1.0)
