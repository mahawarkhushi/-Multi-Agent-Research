# app/services/mcp/compliance.py
from pydantic import BaseModel
from app.services.mcp.base import MCPTool
from app.services.hf_client import hf_generate
from app.services.mcp.registry import tool_registry

MODEL = "meta-llama/Llama-3.2-1B-Instruct"

class ComplianceInput(BaseModel):
    text: str

class ComplianceOutput(BaseModel):
    safe_text: str

class ComplianceTool(MCPTool):
    name = "compliance"
    description = "Ensure neutral tone and safe-compliant content"
    InputSchema = ComplianceInput
    OutputSchema = ComplianceOutput

    def run(self, input_data: ComplianceInput):
        prompt = f"Neutralize and ensure safety compliance:\n{input_data.text}"
        output = hf_generate(MODEL, prompt)
        return ComplianceOutput(safe_text=output)

tool_registry.register(ComplianceTool())
