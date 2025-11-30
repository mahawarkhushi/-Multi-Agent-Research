from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.agent import AgentCreate, AgentRead
from app.db.agent import Agent
from app.dependencies import get_db

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.post("/", response_model=AgentRead)
def create_agent(data: AgentCreate, db: Session = Depends(get_db)):
    new_agent = Agent(**data.dict())
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return new_agent

@router.get("/", response_model=list[AgentRead])
def list_agents(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    return db.query(Agent).offset(skip).limit(limit).all()

@router.get("/{agent_id}", response_model=AgentRead)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).get(agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    return agent

@router.delete("/{agent_id}")
def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).get(agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    db.delete(agent)
    db.commit()
    return {"message": "Agent deleted"}
