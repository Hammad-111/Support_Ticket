from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.auth import router as auth_router
from app.api.tickets import router as tickets_router
from app.api.websocket import router as ws_router
from app.core.rate_limit import limiter

app = FastAPI(
    title="Support System API",
    description="Customer support ticket system",
    version="0.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(ws_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/ui")
def test_ui():
    return FileResponse("static/index.html")


@app.get("/")
def root():
    return {"status": "ok"}
