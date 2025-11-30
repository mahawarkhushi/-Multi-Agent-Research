# app/main.py
from fastapi import FastAPI
from app.api.user_router import router as users_router
from app.api.auth_router import router as auth_router
from app.api.agent_router import router as agent_router
from app.api.report_router import router as report_router
from app.api.tool_router import router as tool_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(agent_router)
app.include_router(report_router)
app.include_router(tool_router)