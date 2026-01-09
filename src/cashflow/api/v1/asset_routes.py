# asset_routes.py

from fastapi import APIRouter, HTTPException, Path
from ...schemas import *
from ...core import manager

router = APIRouter(prefix="/assets", tags=["assets"])

@router.post("/")
def api_add_asset(req: AssetRequest):
    if any(a["name"] == req.name for a in manager.assets):
        raise HTTPException(status_code=400, detail="Asset name exists")
    manager.assets.append({"name": req.name, "value": req.value})
    return {"status": "added"}

@router.delete("/{name}")
def api_remove_asset(name: str = Path(...)):
    manager.assets = [a for a in manager.assets if a["name"] != name]
    return {"status": "removed"}

@router.get("/")
def api_list_assets():
    return manager.assets