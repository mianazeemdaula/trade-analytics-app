"""
FastAPI routes module
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Union
import pandas as pd

from .models import OHLCData, AnalysisRequest, BinaryOptionsRequest
from .utils import convert_ohlc_to_dataframe
from .indicators import calculate_indicator
from .patterns import calculate_candlestick_patterns, get_pattern_interpretation, get_pattern_signals
from .predictions import predict_binary_options

# Create API router
router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "Gold Trader Technical Analysis API",
        "version": "1.0.0"
    }


@router.post("/analyze")
async def analyze_indicators(request: AnalysisRequest) -> Dict[str, Any]:
    """
    Analyze technical indicators for given OHLC data
    
    Args:
        request: Analysis request with OHLC data and indicators
        
    Returns:
        Dictionary with analysis results
    """
    try:
        # Convert OHLC data to DataFrame
        df = convert_ohlc_to_dataframe(request.data)
        
        results = {}
        
        # Calculate each requested indicator
        for indicator_request in request.indicators:
            indicator_name = indicator_request.name.lower()
            params = indicator_request.params
            
            try:
                # Handle indicator aliases
                if indicator_name in ['bollinger', 'bollinger_bands']:
                    indicator_name = 'bb'
                elif indicator_name in ['stochastic']:
                    indicator_name = 'stoch'
                elif indicator_name in ['stochastic_rsi']:
                    indicator_name = 'stoch_rsi'
                elif indicator_name in ['fibonacci', 'fib_retracements']:
                    indicator_name = 'fibonacci'
                elif indicator_name in ['volume_ma', 'volume_moving_average']:
                    indicator_name = 'volume_ma'
                elif indicator_name in ['volume_profile', 'vp']:
                    indicator_name = 'volume_profile'
                elif indicator_name in ['price_action', 'pa']:
                    indicator_name = 'price_action'
                elif indicator_name in ['order_flow', 'of']:
                    indicator_name = 'order_flow'
                elif indicator_name in ['supply_demand', 'sd']:
                    indicator_name = 'supply_demand'
                elif indicator_name in ['support_resistance', 'sr']:
                    indicator_name = 'support_resistance'
                elif indicator_name in ['market_structure', 'ms']:
                    indicator_name = 'market_structure'
                
                result = calculate_indicator(df, indicator_name, params)
                results[indicator_request.name] = result
                
            except Exception as e:
                results[indicator_request.name] = {"error": str(e)}
        
        # Add candlestick patterns if requested
        if request.include_patterns:
            try:
                patterns = calculate_candlestick_patterns(df)
                pattern_interpretations = get_pattern_interpretation(patterns)
                pattern_signals = get_pattern_signals(patterns)
                
                results["candlestick_patterns"] = {
                    "detected_patterns": patterns,
                    "interpretations": pattern_interpretations,
                    "signals": pattern_signals
                }
            except Exception as e:
                results["candlestick_patterns"] = {"error": str(e)}
        
        # Add basic market info
        results["market_info"] = {
            "current_price": float(df['close'].iloc[-1]),
            "price_change": float(df['close'].iloc[-1] - df['close'].iloc[-2]) if len(df) > 1 else 0.0,
            "volume": float(df['volume'].iloc[-1]),
            "timestamp": str(df.index[-1]) if hasattr(df.index[-1], 'strftime') else str(df.index[-1])
        }
        
        return {
            "status": "success",
            "data": results,
            "data_points": len(df),
            "timeframe": f"{len(df)} periods"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis error: {str(e)}")


@router.post("/predict")
async def predict_binary_options_direction(request: BinaryOptionsRequest) -> Dict[str, Any]:
    """
    Predict binary options direction using multiple indicators
    
    Args:
        request: Binary options prediction request
        
    Returns:
        Dictionary with prediction results
    """
    try:
        # Convert OHLC data to DataFrame
        df = convert_ohlc_to_dataframe(request.data)
        
        # Validate minimum data points
        if len(df) < 30:
            raise HTTPException(
                status_code=400, 
                detail="Insufficient data. At least 30 data points required for accurate prediction."
            )
        
        # Generate prediction
        prediction = predict_binary_options(df, request.timeframe_minutes)
        
        # Add request info
        prediction["request_info"] = {
            "timeframe_minutes": request.timeframe_minutes,
            "data_points": len(df),
            "current_price": float(df['close'].iloc[-1])
        }
        
        return {
            "status": "success",
            "prediction": prediction
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")


@router.get("/indicators/list")
async def list_available_indicators():
    """
    List all available technical indicators with their parameters
    
    Returns:
        Dictionary with available indicators and their descriptions
    """
    indicators = {
        "trend_indicators": {
            "SMA": {
                "name": "Simple Moving Average",
                "params": ["period"],
                "example": {"name": "SMA", "params": [20]}
            },
            "EMA": {
                "name": "Exponential Moving Average", 
                "params": ["period"],
                "example": {"name": "EMA", "params": [20]}
            },
            "MACD": {
                "name": "Moving Average Convergence Divergence",
                "params": ["fast_period", "slow_period", "signal_period"],
                "example": {"name": "MACD", "params": [12, 26, 9]}
            },
            "SuperTrend": {
                "name": "SuperTrend",
                "params": ["period", "multiplier"],
                "example": {"name": "SuperTrend", "params": [10, 3]}
            }
        },
        "momentum_indicators": {
            "RSI": {
                "name": "Relative Strength Index",
                "params": ["period"],
                "example": {"name": "RSI", "params": [14]}
            },
            "Stochastic": {
                "name": "Stochastic Oscillator",
                "params": ["k_period", "d_period", "smooth_k"],
                "example": {"name": "Stochastic", "params": [14, 3, 3]}
            },
            "Stochastic_RSI": {
                "name": "Stochastic RSI",
                "params": ["rsi_length", "stoch_length", "k"],
                "example": {"name": "Stochastic_RSI", "params": [14, 14, 3]}
            }
        },
        "volatility_indicators": {
            "ATR": {
                "name": "Average True Range",
                "params": ["period"],
                "example": {"name": "ATR", "params": [14]}
            },
            "Bollinger_Bands": {
                "name": "Bollinger Bands",
                "params": ["period", "standard_deviation"],
                "example": {"name": "Bollinger_Bands", "params": [20, 2]}
            }
        },
        "volume_indicators": {
            "OBV": {
                "name": "On-Balance Volume",
                "params": [],
                "example": {"name": "OBV", "params": []}
            },
            "VWAP": {
                "name": "Volume Weighted Average Price",
                "params": [],
                "example": {"name": "VWAP", "params": []}
            },
            "Volume_MA": {
                "name": "Volume Moving Average",
                "params": ["period"],
                "example": {"name": "Volume_MA", "params": [20]}
            },
            "Volume_Profile": {
                "name": "Volume Profile",
                "params": ["lookback_period", "price_bins"],
                "example": {"name": "Volume_Profile", "params": [100, 20]}
            }
        },
        "advanced_indicators": {
            "Market_Structure": {
                "name": "Market Structure Analysis",
                "params": ["lookback_period"],
                "example": {"name": "Market_Structure", "params": [20]}
            },
            "Support_Resistance": {
                "name": "Support and Resistance Zones",
                "params": ["lookback_period", "zone_strength"],
                "example": {"name": "Support_Resistance", "params": [50, 3]}
            },
            "Fibonacci": {
                "name": "Fibonacci Retracements",
                "params": ["lookback_period"],
                "example": {"name": "Fibonacci", "params": [50]}
            },
            "Supply_Demand": {
                "name": "Supply and Demand Zones",
                "params": ["lookback_period", "zone_strength"],
                "example": {"name": "Supply_Demand", "params": [50, 3]}
            },
            "Price_Action": {
                "name": "Price Action Analysis",
                "params": ["lookback_period"],
                "example": {"name": "Price_Action", "params": [20]}
            },
            "Order_Flow": {
                "name": "Order Flow Analysis",
                "params": ["lookback_period"],
                "example": {"name": "Order_Flow", "params": [20]}
            }
        }
    }
    
    return {
        "status": "success",
        "indicators": indicators,
        "total_indicators": sum(len(category) for category in indicators.values()),
        "categories": list(indicators.keys())
    }


@router.get("/patterns/list")
async def list_candlestick_patterns():
    """
    List all available candlestick patterns with their interpretations
    
    Returns:
        Dictionary with available patterns and their meanings
    """
    patterns = {
        "reversal_patterns": {
            "hammer": "Bullish reversal - strong buying pressure after decline",
            "shooting_star": "Bearish reversal - selling pressure after advance",
            "bullish_engulfing": "Strong bullish reversal - buyers overwhelm sellers",
            "bearish_engulfing": "Strong bearish reversal - sellers overwhelm buyers",
            "bullish_harami": "Bullish reversal - weakening selling pressure",
            "bearish_harami": "Bearish reversal - weakening buying pressure",
            "morning_star": "Strong bullish reversal - three-candle pattern",
            "evening_star": "Strong bearish reversal - three-candle pattern",
            "dark_cloud_cover": "Bearish reversal - selling pressure emerges",
            "piercing_line": "Bullish reversal - buying pressure emerges",
            "hanging_man": "Bearish reversal - selling pressure after advance",
            "inverted_hammer": "Bullish reversal - potential buying interest",
            "dragonfly_doji": "Bullish reversal - long lower wick, buying support",
            "gravestone_doji": "Bearish reversal - long upper wick, selling pressure"
        },
        "continuation_patterns": {
            "three_white_soldiers": "Strong bullish continuation - sustained buying",
            "three_black_crows": "Strong bearish continuation - sustained selling"
        },
        "indecision_patterns": {
            "doji": "Indecision - market uncertainty, potential reversal signal",
            "spinning_top": "Indecision - small body with long wicks",
            "long_legged_doji": "High indecision - long wicks both sides",
            "four_price_doji": "Extreme indecision - all prices equal"
        },
        "momentum_patterns": {
            "bullish_marubozu": "Strong bullish sentiment - no wicks, strong buying",
            "bearish_marubozu": "Strong bearish sentiment - no wicks, strong selling"
        }
    }
    
    return {
        "status": "success",
        "patterns": patterns,
        "total_patterns": sum(len(category) for category in patterns.values()),
        "categories": list(patterns.keys())
    }


@router.get("/")
async def root():
    """
    Root endpoint with API information
    
    Returns:
        API information and available endpoints
    """
    return {
        "service": "Gold Trader Technical Analysis API",
        "version": "1.0.0",
        "description": "Advanced technical analysis API for trading with 15+ indicators, candlestick patterns, and binary options predictions",
        "endpoints": {
            "/": "API information",
            "/health": "Health check",
            "/analyze": "Technical indicator analysis",
            "/predict": "Binary options prediction",
            "/indicators/list": "List available indicators",
            "/patterns/list": "List candlestick patterns",
            "/docs": "API documentation"
        },
        "features": [
            "15+ Technical Indicators",
            "Candlestick Pattern Recognition", 
            "Binary Options Prediction",
            "Market Structure Analysis",
            "Support/Resistance Detection",
            "Volume Profile Analysis",
            "Price Action Analysis",
            "Order Flow Analysis"
        ]
    }
