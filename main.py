import warnings
import os

# Suppress all pandas_ta related warnings including pkg_resources deprecation
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", category=UserWarning, module="pandas_ta")

# Also suppress via environment variable for pandas_ta
os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning:pandas_ta'

from fastapi import FastAPI
from app.routes import router
from app import __version__


# Create FastAPI app
app = FastAPI(
    title="Gold Trader Technical Analysis API",
    description="Advanced technical analysis API with 15+ indicators, candlestick patterns, and binary options predictions",
    version=__version__
)

# Include routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)