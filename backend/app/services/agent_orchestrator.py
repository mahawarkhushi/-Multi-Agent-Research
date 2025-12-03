from app.services.mcp.registry import tool_registry
from app.services.mcp.ingestion import IngestionInput
from app.services.mcp.research import ResearchInput
from app.services.mcp.citation import CitationInput
from app.services.mcp.formatter import FormatterInput
from app.services.mcp.compliance import ComplianceInput

class AgentOrchestrator:

    # Run a single tool for debugging
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

        # Return the one output field
        return next(iter(result.dict().values()))

    # -----------------------------
    # FULL ORCHESTRATION PIPELINE
    # -----------------------------
    def run(self, raw_text: str) -> str:
        """
        Runs the full 5-step LLM pipeline and returns ONLY
        the final safe report text (string).
        This ensures job_runner can save the report properly.
        """

        # 1. INGESTION
        ingestion = tool_registry.get("ingestion").run(
            IngestionInput(text=raw_text)
        )
        if not ingestion or not ingestion.content:
            raise ValueError("Ingestion tool produced no content")

        # 2. RESEARCH
        research = tool_registry.get("research").run(
            ResearchInput(text=ingestion.content)
        )
        if not research or not research.notes:
            raise ValueError("Research tool failed to generate notes")

        # 3. CITATION CHECKING
        citation = tool_registry.get("citation").run(
            CitationInput(text=research.notes)
        )
        if not citation or not citation.cited_text:
            raise ValueError("Citation tool failed to generate cited text")

        # 4. FORMATTING
        formatted = tool_registry.get("formatter").run(
            FormatterInput(text=citation.cited_text)
        )
        if not formatted or not formatted.formatted:
            raise ValueError("Formatter tool failed to format text")

        # 5. COMPLIANCE (PII removal, safe output)
        compliance = tool_registry.get("compliance").run(
            ComplianceInput(text=formatted.formatted)
        )
        if not compliance or not compliance.safe_text:
            raise ValueError("Compliance tool failed to produce safe text")

        # Return ONLY the final safe text so DB can store it
        return compliance.safe_text
