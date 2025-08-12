# Gold Trader Technical Analysis API

A comprehensive FastAPI-based technical analysis API with 15+ indicators, candlestick pattern detection, and binary options prediction capabilities.

## Features

- **15+ Technical Indicators**: RSI, MACD, EMA, SMA, Bollinger Bands, Stochastic, ATR, and more
- **Advanced Analysis**: Volume Profile, Support/Resistance, Market Structure, Price Action
- **Pattern Recognition**: 19+ candlestick patterns with interpretations
- **Binary Options Prediction**: ML-based direction prediction with confidence scores
- **Modular Architecture**: Clean, maintainable code structure
- **Health Monitoring**: Built-in health check endpoints

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test Installation**:
   ```bash
   python start.py
   ```

3. **Start the API Server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

4. **Access API Documentation**:
   - Open http://localhost:8000/docs in your browser

## API Endpoints

- `GET /health` - Health check
- `POST /analyze` - Technical indicator analysis
- `POST /predict` - Binary options prediction
- `GET /indicators/list` - List available indicators
- `GET /patterns/list` - List candlestick patterns

## Warning Suppression

This application includes automatic suppression of pandas_ta deprecation warnings related to pkg_resources. The warnings are handled in the startup modules to ensure clean console output.

## Project Structure

```
├── main.py              # FastAPI application entry point
├── start.py             # Startup script with testing
├── requirements.txt     # Python dependencies
├── app/
│   ├── __init__.py      # Package initialization
│   ├── models.py        # Pydantic data models
│   ├── utils.py         # Utility functions
│   ├── indicators.py    # Technical indicators
│   ├── patterns.py      # Candlestick patterns
│   ├── predictions.py   # Binary options prediction
│   └── routes.py        # FastAPI routes
```

## Usage Example

```python
import requests

# Analyze indicators
response = requests.post("http://localhost:8000/analyze", json={
    "data": [
        {
            "timestamp": "2024-01-01T00:00:00",
            "open": 2000.0,
            "high": 2010.0,
            "low": 1995.0,
            "close": 2005.0,
            "volume": 1000.0
        }
        # ... more data points
    ],
    "indicators": [
        {"name": "RSI", "params": [14]},
        {"name": "MACD", "params": [12, 26, 9]}
    ],
    "include_patterns": true
})

print(response.json())
```

## License

This project is for educational and research purposes.
