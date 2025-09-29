from typing import Any, Dict, Tuple, List
import re
from typing import Dict, Any, List
from langchain.schema import Document

class ResponseFormatter:
    """Formats responses based on role and content type."""

    def format(self, response_data: Dict[str, Any]) -> str:
        response = response_data.get("response", "")
        rtype = response_data.get("type", "general")
        context = response_data.get("context", [])

        if rtype == "technical":
            return self._format_technical_response(response, context)
        if rtype == "mma":
            return self._format_mma_response(response_data)
        if rtype == "career":
            return self._format_career_response(response, context)
        if rtype == "fun":
            return self._format_fun_response(response)
        if rtype == "confession":
            return "💌 " + response
        return self._format_general_response(response)

    def _format_technical_response(self, response: str, context: List[Document]) -> str:
        out = f"## Engineer Detail\n{response}\n\n"
        if context:
            out += "### Citations\n"
            for i, doc in enumerate(context[:3], 1):
                fp = doc.metadata.get("file_path") or doc.metadata.get("source", "unknown")
                line = doc.metadata.get("start_line", "?")
                out += f"{i}. `{fp}:{line}`\n"
        out += "\n## Plain-English Summary\n(High-level explanation forthcoming.)"
        return out

    def _format_mma_response(self, data: Dict[str, Any]) -> str:
        base = data.get("response", "")
        link = data.get("youtube_link")
        if link:
            return f"{base}\n\nWatch: {link}"
        return base

    def _format_career_response(self, response: str, context: List[Document]) -> str:
        sources = "\n".join(f"- {d.metadata.get('source','unknown')}" for d in context[:3]) or "- (no sources)"
        return f"## Career Overview\n{response}\n\n### Notable Outcomes\n(Derived from grounded data.)\n\n### Sources\n{sources}"

    def _format_fun_response(self, response: str) -> str:
        return f"### Fun Facts\n{response}"

    def _format_general_response(self, response: str) -> str:
        return response