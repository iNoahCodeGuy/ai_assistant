from typing import Any, Dict, Tuple, List
import re

class ResponseFormatter:
    def __init__(self):
        pass

    def format_response(self, response: Dict[str, Any], role: str) -> Tuple[str, str]:
        # response expected keys: answer, sources, confidence, role
        if role == 'Hiring Manager (nontechnical)':
            return self._format_nontechnical(response)
        if role in ['Hiring Manager (technical)', 'Software Developer']:
            return self._format_technical(response)
        if role == 'Just looking around':
            return self._format_fun_facts(response)
        if role == 'Looking to confess crush':
            return self._format_crush_confession(response)
        return (response.get('answer', ''), '')

    # --- Nontechnical Hiring Manager ---
    def _format_nontechnical(self, response: Dict[str, Any]) -> Tuple[str, str]:
        answer = response.get('answer', '')
        sources: List[str] = response.get('sources', [])
        overview = self._extract_overview(answer)
        outcomes = self._extract_outcomes(answer)
        if not sources:
            sources_block = "Sources: (No explicit sources retrieved – please ask for clarification if needed.)"
        else:
            sources_block = "Sources:\n" + "\n".join(f"- {s}" for s in sources[:5])
        contact_block = "Contact: noahdelacalzada@gmail.com | LinkedIn: https://www.linkedin.com/in/noah-de-la-calzada-250412358/"
        formatted = (
            "Career Overview:\n" + overview + "\n\n" +
            "Notable Outcomes:\n" + ("\n".join(f"- {o}" for o in outcomes) if outcomes else "- Impact narratives available on request.") + "\n\n" +
            sources_block + "\n\n" +
            contact_block
        )
        return formatted, ''

    def _extract_overview(self, text: str) -> str:
        # First paragraph or first 3 sentences
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return ' '.join(sentences[:3]).strip()

    def _extract_outcomes(self, text: str) -> List[str]:
        # Heuristic: lines/sentences containing verbs and numbers or key action words
        keywords = ['improv', 'build', 'develop', 'launch', 'deliver', 'rank', 'close', 'prototype']
        sentences = re.split(r'(?<=[.!?])\s+', text)
        picked = []
        for s in sentences:
            lower = s.lower()
            if any(k in lower for k in keywords):
                picked.append(s.strip())
        # dedupe
        seen = set()
        uniq = []
        for p in picked:
            if p not in seen and len(p) > 25:
                seen.add(p)
                uniq.append(p)
        return uniq[:6]

    # --- Technical / Developer ---
    def _format_technical(self, response: Dict[str, Any]) -> Tuple[str, str]:
        answer = response.get('answer', '')
        sources = response.get('sources', [])
        detail_block = answer
        source_block = '' if not sources else ('\n\nSources:\n' + '\n'.join(f'- {s}' for s in sources[:5]))
        return detail_block + source_block, ''

    def _format_fun_facts(self, response: Dict[str, Any]) -> Tuple[str, str]:
        return response.get('answer', ''), ''

    def _format_crush_confession(self, response: Dict[str, Any]) -> Tuple[str, str]:
        return response.get('answer', ''), ''