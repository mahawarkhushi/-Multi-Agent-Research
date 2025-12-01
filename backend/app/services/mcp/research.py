# app/services/mcp/research.py
from pydantic import BaseModel
from app.services.mcp.base import MCPTool
from app.services.hf_client import hf_generate
from app.services.mcp.registry import tool_registry

MODEL = "microsoft/Phi-3-mini-4k-instruct"

class ResearchInput(BaseModel):
    text: str

class ResearchOutput(BaseModel):
    notes: str

class ResearchTool(MCPTool):
    name = "research"
    description = "Generate detailed factual notes"
    InputSchema = ResearchInput
    OutputSchema = ResearchOutput

    def run(self, input_data: ResearchInput):
        prompt = f"Research this topic:\n{input_data.text}"
        output = hf_generate(MODEL, prompt)
        return ResearchOutput(notes=output)

tool_registry.register(ResearchTool())
