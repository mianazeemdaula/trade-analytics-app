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
