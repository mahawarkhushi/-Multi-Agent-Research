# app/services/mcp/base.py
from pydantic import BaseModel

class MCPTool:
    """
    Base class for all MCP tools.
    Each tool should inherit from this and implement .run()
    """

    name: str
    description: str
    InputSchema: BaseModel
    OutputSchema: BaseModel

    def run(self, input_data: BaseModel):
        """
        Execute the tool logic.
        Must return an instance of OutputSchema
        """
        raise NotImplementedError("Tool must implement .run()")
