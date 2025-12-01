# app/services/mcp/citation.py
from pydantic import BaseModel
from app.services.mcp.base import MCPTool
from app.services.hf_client import hf_generate
from app.services.mcp.registry import tool_registry

MODEL = "google/flan-t5-large"

class CitationInput(BaseModel):
    text: str

class CitationOutput(BaseModel):
    cited_text: str

class CitationTool(MCPTool):
    name = "citation"
    description = "Rewrite text with citation markers"
    InputSchema = CitationInput
    OutputSchema = CitationOutput

    def run(self, input_data: CitationInput):
        prompt = f"Add citation markers:\n{input_data.text}"
        output = hf_generate(MODEL, prompt)
        return CitationOutput(cited_text=output)

tool_registry.register(CitationTool())
