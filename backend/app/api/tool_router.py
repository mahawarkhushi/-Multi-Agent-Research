from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.tool import ToolCreate, ToolRead
from app.db.tool import Tool
from app.dependencies import get_db

router = APIRouter(prefix="/tools", tags=["Tools"])

@router.post("/", response_model=ToolRead)
def create_tool(data: ToolCreate, db: Session = Depends(get_db)):
    new_tool = Tool(**data.dict())
    db.add(new_tool)
    db.commit()
    db.refresh(new_tool)
    return new_tool


@router.get("/", response_model=list[ToolRead])
def list_tools(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    return db.query(Tool).offset(skip).limit(limit).all()

@router.get("/{tool_id}", response_model=ToolRead)
def get_tool(tool_id: str, db: Session = Depends(get_db)):
    tool = db.query(Tool).get(tool_id)
    if not tool:
        raise HTTPException(404, "Tool not found")
    return tool

@router.delete("/{tool_id}")
def delete_tool(tool_id: str, db: Session = Depends(get_db)):
    tool = db.query(Tool).get(tool_id)
    if not tool:
        raise HTTPException(404, "Tool not found")
    db.delete(tool)
    db.commit()
    return {"message": "Tool deleted"}
