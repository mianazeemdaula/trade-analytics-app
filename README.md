# Technical Analysis API

A FastAPI-based REST API for calculating technical indicators on financial OHLC (Open, High, Low, Close) data using the pandas_ta library.

## Features

- **Single Endpoint Analysis**: Send OHLC data and get technical indicators calculated
- **Multiple Indicators**: Supports RSI, MACD, SMA, EMA, Bollinger Bands, and Stochastic Oscillator
- **Candlestick Pattern Recognition**: Comprehensive support for 60+ candlestick patterns
- **Binary Options Prediction**: AI-powered prediction for next 2 candles direction
- **Flexible Parameters**: Each indicator can be configured with custom parameters
- **Clean Output**: Returns only the last calculated values for each indicator and pattern signals
- **Well-Documented**: Automatic API documentation with FastAPI

## Supported Technical Indicators

| Indicator | Parameters | Example |
|-----------|------------|---------|
| RSI | period | `[14]` |
| MACD | fast, slow, signal | `[12, 26, 9]` |
| SMA | period | `[20]` |
| EMA | period | `[20]` |
| Bollinger Bands | period, std deviation | `[20, 2.0]` |
| Stochastic | k, d, smooth_k | `[14, 3, 3]` |

## Supported Candlestick Patterns

The API supports 60+ candlestick patterns including:

### Reversal Patterns
- **Hammer/Hanging Man** - Small body with long lower shadow
- **Doji** - Open and close prices nearly equal
- **Engulfing** - One candle completely engulfs the previous
- **Harami** - Small candle within previous large candle
- **Morning/Evening Star** - Three-candle reversal patterns
- **Shooting Star** - Small body with long upper shadow
- **Dark Cloud Cover/Piercing** - Two-candle reversal patterns

### Continuation Patterns  
- **Marubozu** - No shadows, strong directional move
- **Spinning Top** - Small body with long shadows
- **Inside Bar** - Current candle within previous range

### Multi-Candle Patterns
- **Three White Soldiers/Black Crows** - Three consecutive same-direction candles
- **Abandoned Baby** - Rare gap-based reversal pattern

*View complete list at: `GET /candlestick-patterns`*

## Binary Options Prediction

The API includes an advanced binary options prediction system that analyzes multiple technical indicators to predict whether the next 1-5 candles will be bullish or bearish.

### Prediction Algorithm
- **RSI Analysis**: Overbought/oversold conditions and momentum
- **MACD**: Trend direction and crossover signals  
- **Moving Averages**: Price position relative to SMA20 and EMA12
- **Bollinger Bands**: Price squeeze and breakout detection
- **Stochastic**: Momentum and reversal signals
- **Price Action**: Higher highs/lows pattern recognition
- **Volume**: Confirmation of price movements
- **Candlestick Patterns**: Key reversal and continuation patterns

### Confidence Levels
- **HIGH (>75%)**: Strong signals across multiple indicators
- **MEDIUM (60-75%)**: Moderate agreement between indicators  
- **LOW (<60%)**: Conflicting signals, recommend waiting

### Risk Assessment
- **LOW**: High confidence prediction with strong signal alignment
- **MEDIUM**: Moderate confidence with some conflicting signals
- **HIGH**: Low confidence or insufficient data for reliable prediction

## Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd d:\py\goldtrader
   ```

2. **Activate the virtual environment** (if not already activated)
   ```bash
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

1. **Start the server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```
   
   The API will be available at: `http://localhost:8001`

2. **View API Documentation**
   - Swagger UI: `http://localhost:8001/docs`
   - ReDoc: `http://localhost:8001/redoc`

## Important Notes

- **Numpy Compatibility**: This project requires numpy < 2.0.0 for compatibility with pandas_ta
- **Minimum Data**: MACD requires at least 26+ data points for calculation
- **Port**: The default port is 8001 (you can change this if needed)

## API Usage

### Endpoint: `POST /analyze`

**Request Format:**
```json
{
  "indicators": {
    "rsi": [14],
    "macd": [12, 26, 9],
    "sma": [20]
  },
  "candlestick_patterns": [
    "doji", "hammer", "engulfing", "shooting_star"
  ],
  "ohlc_data": [
    {
      "time": "2025-07-01 07:45:25",
      "open": 100,
      "high": 105,
      "low": 98,
      "close": 103,
      "volume": 1000
    },
    {
      "time": "2025-07-01 07:50:00",
      "open": 103,
      "high": 108,
      "low": 102,
      "close": 107,
      "volume": 1200
    }
  ]
}
```

**Response Format:**
```json
{
  "rsi": 65.43,
  "macd": 2.15,
  "macd_signal": 1.88,
  "sma": 105.5,
  "doji": "Neutral",
  "hammer": "Not Detected",
  "engulfing": "Bullish",
  "shooting_star": "Not Detected"
}
```

### Endpoint: `GET /candlestick-patterns`

Returns comprehensive information about all supported candlestick patterns, including:
- Pattern categories (reversal, continuation, multi-candle, gap patterns)
- Pattern descriptions and reliability levels
- Complete list of 60+ available TA-Lib patterns

### Endpoint: `POST /predict-binary-options`

**Request Format:**
```json
{
  "ohlc_data": [
    {
      "time": "2025-07-01 07:45:25",
      "open": 100,
      "high": 105,
      "low": 98,
      "close": 103,
      "volume": 1000
    }
  ],
  "prediction_timeframe": 2,
  "confidence_threshold": 0.6
}
```

**Response Format:**
```json
{
  "prediction": {
    "direction": "BULLISH",
    "confidence": 0.758,
    "timeframe_candles": 2,
    "risk_level": "MEDIUM"
  },
  "signal_breakdown": {
    "bullish_signals": 4,
    "bearish_signals": 1,
    "bullish_weight": 2.3,
    "bearish_weight": 0.7
  },
  "detailed_signals": [
    {
      "indicator": "macd",
      "direction": "bullish",
      "weight": 0.7,
      "reason": "MACD bullish crossover"
    }
  ],
  "technical_analysis": {
    "rsi": 45.2,
    "macd": {"line": 0.023, "signal": 0.018},
    "moving_averages": {"price": 103, "sma_20": 101.5, "ema_12": 102.1}
  },
  "trading_advice": {
    "recommended_action": "BUY",
    "stop_loss_suggestion": "Set stop-loss at recent support/resistance levels",
    "notes": "Prediction based on 5 technical signals with 75.8% confidence"
  }
}
```

### Other Endpoints

- `GET /` - API information
- `GET /supported-indicators` - List of supported indicators and their parameters

## Testing

Run the test script to verify the API is working:

```bash
python test_api.py
```

Make sure the API server is running before executing the test script.

## Example Usage with Python

```python
import requests
import json

# Sample request
data = {
    "indicators": {
        "rsi": [14],
        "macd": [12, 26, 9],
        "sma": [20]
    },
    "candlestick_patterns": [
        "doji", "hammer", "engulfing"
    ],
    "ohlc_data": [
        # Your OHLC data here
    ]
}

response = requests.post(
    "http://localhost:8001/analyze",
    json=data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    results = response.json()
    print("Analysis Results:", results)
else:
    print("Error:", response.text)
```

## Example Usage with cURL

```bash
curl -X POST "http://localhost:8001/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "indicators": {
         "rsi": [14],
         "sma": [20]
       },
       "candlestick_patterns": ["doji", "hammer"],
       "ohlc_data": [
         {
           "time": "2025-07-01 07:45:25",
           "open": 100,
           "high": 105,
           "low": 98,
           "close": 103,
           "volume": 1000
         }
       ]
     }'
```

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input data or parameters
- **500 Internal Server Error**: Unexpected server errors

All errors include descriptive messages to help diagnose issues.

## Technical Details

- **Framework**: FastAPI
- **Technical Analysis Library**: pandas_ta
- **Data Processing**: pandas
- **Validation**: Pydantic
- **Server**: Uvicorn

## Notes

- The API returns only the **last calculated value** for each indicator
- Minimum 2 data points required for analysis
- All timestamp formats should be parseable by pandas `pd.to_datetime()`
- Results are rounded to 2 decimal places for readability

## Dependencies

- fastapi==0.104.1
- uvicorn==0.24.0
- pandas==2.1.4
- pandas-ta==0.3.14b0
- pydantic==2.5.2
- python-multipart==0.0.6
#   t r a d e - a n a l y t i c s - a p p  
 