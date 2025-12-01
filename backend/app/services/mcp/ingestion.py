# app/services/mcp/ingestion.py

from pydantic import BaseModel
from app.services.mcp.base import MCPTool
from app.services.hf_client import hf_generate
from app.services.mcp.registry import tool_registry

MODEL = "meta-llama/Llama-3.2-1B-Instruct"

class IngestionInput(BaseModel):
    text: str

class IngestionOutput(BaseModel):
    content: str

class IngestionTool(MCPTool):
    name = "ingestion"
    description = "Extract clean structured content from raw input"
    InputSchema = IngestionInput
    OutputSchema = IngestionOutput

    def run(self, input_data: IngestionInput):
        prompt = f"Extract clean structured content:\n\n{input_data.text}"
        output = hf_generate(MODEL, prompt)
        return IngestionOutput(content=output)

tool_registry.register(IngestionTool())
