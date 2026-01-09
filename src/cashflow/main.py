# main.py

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import budget_routes, node_routes, asset_routes

app = FastAPI(
    title="Budget Cashflow Visualizer API",
    description="API for interactive budget Sankey visualization with projections",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(budget_routes.router, prefix="/api/v1")
app.include_router(node_routes.router, prefix="/api/v1")
app.include_router(asset_routes.router, prefix="/api/v1")
app.include_router(budget_routes.legacy_router, prefix="/api")
app.include_router(node_routes.router, prefix="/api")
app.include_router(asset_routes.router, prefix="/api")

static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir), html=True), name="static")

@app.get("/")
def root():
    static_dir = Path(__file__).resolve().parent / "static"
    if static_dir.exists() and (static_dir / "index.html").exists():
        return RedirectResponse(url="/static/index.html")
    return JSONResponse({"status": "ok", "message": "Budget Cashflow API running", "routes": ["/api/v1/budget", "/api/v1/nodes", "/api/v1/assets"]})
