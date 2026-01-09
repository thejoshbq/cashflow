# node_routes.py

from fastapi import APIRouter, HTTPException, Path
from ...schemas import *
from ...core import manager

router = APIRouter(prefix="/nodes", tags=["nodes"])

@router.post("/")
def api_add_node(req: NodeRequest):
    try:
        manager.add_node(req.parent_label, req.label, req.amount, req.group, req.apr, req.current_balance)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "added"}

@router.put("/{label}")
def api_edit_node(label: str = Path(...), req: EditNodeRequest = None):
    try:
        manager.edit_node(label, req.new_label, req.new_amount, req.new_group, req.apr, req.current_balance)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "updated"}

@router.delete("/{label}")
def api_remove_node(label: str = Path(...)):
    try:
        manager.remove_node(label)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "removed"}

@router.get("/")
def api_list_nodes():
    return sorted(manager.nodes.keys())