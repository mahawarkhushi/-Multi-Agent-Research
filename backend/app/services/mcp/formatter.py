# app/services/mcp/formatter.py
from pydantic import BaseModel
from app.services.mcp.base import MCPTool
from app.services.hf_client import hf_generate
from app.services.mcp.registry import tool_registry

MODEL = "facebook/bart-large-cnn"

class FormatterInput(BaseModel):
    text: str

class FormatterOutput(BaseModel):
    formatted: str

class FormatterTool(MCPTool):
    name = "formatter"
    description = "Format text into a structured report"
    InputSchema = FormatterInput
    OutputSchema = FormatterOutput

    def run(self, input_data: FormatterInput):
        prompt = f"Format professionally:\n{input_data.text}"
        output = hf_generate(MODEL, prompt)
        return FormatterOutput(formatted=output)

tool_registry.register(FormatterTool())
