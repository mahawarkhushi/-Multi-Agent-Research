# app/services/agent_orchestrator.py

from app.services.mcp.registry import tool_registry
from app.services.mcp.ingestion import IngestionInput
from app.services.mcp.research import ResearchInput
from app.services.mcp.citation import CitationInput
from app.services.mcp.formatter import FormatterInput
from app.services.mcp.compliance import ComplianceInput

class AgentOrchestrator:

    # NEW: Run single step
    def run_single(self, tool_name: str, text: str):
        tool = tool_registry.get(tool_name)

        input_map = {
            "ingestion": IngestionInput(text=text),
            "research": ResearchInput(text=text),
            "citation": CitationInput(text=text),
            "formatting": FormatterInput(text=text),
            "compliance": ComplianceInput(text=text),
        }

        result = tool.run(input_map[tool_name])

        # Each result returns different output field
        return list(result.dict().values())[0]

    # Full pipeline (used in /agent/run API)
    def run(self, text: str):
        ingestion = tool_registry.get("ingestion").run(IngestionInput(text=text))
        research = tool_registry.get("research").run(ResearchInput(text=ingestion.content))
        citation = tool_registry.get("citation").run(CitationInput(text=research.notes))
        formatted = tool_registry.get("formatter").run(FormatterInput(text=citation.cited_text))
        compliance = tool_registry.get("compliance").run(ComplianceInput(text=formatted.formatted))

        return {
            "status": "success",
            "output": compliance.safe_text
        }
