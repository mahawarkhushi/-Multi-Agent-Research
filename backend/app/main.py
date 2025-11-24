from fastapi import FastAPI
from app.api import users, agents, tools, reports

app = FastAPI()

app.include_router(users.router)
app.include_router(agents.router)
app.include_router(tools.router)
app.include_router(reports.router)
