# budget_routes.py

from fastapi import APIRouter, HTTPException, Query
from ...schemas import *
from ...core import manager

router = APIRouter(prefix="/budget", tags=["budget"])

@router.post("/start")
def api_start(req: StartRequest):
    try:
        manager.start(req.income)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "started"}

@router.put("/income")
def api_edit_income(req: StartRequest):
    try:
        manager.edit_income(req.income)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "updated"}

@router.get("/data")
def api_data(projection_months: int = Query(0)):
    try:
        return manager.get_visualization_data(projection_months)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

legacy_router = APIRouter(tags=["budget-legacy"])

@legacy_router.post("/start")
def legacy_start(req: StartRequest):
    return api_start(req)

@legacy_router.put("/income")
def legacy_income(req: StartRequest):
    return api_edit_income(req)

@legacy_router.get("/data")
def legacy_data(projection_months: int = Query(0)):
    return api_data(projection_months)
