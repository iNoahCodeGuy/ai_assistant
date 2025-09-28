from typing import Any, Dict, Tuple

class ResponseFormatter:
    def __init__(self):
        pass

    def format_response(self, response: Dict[str, Any], role: str) -> Tuple[str, str]:
        """
        Formats the response based on the user role.

        Args:
            response (Dict[str, Any]): The response data containing technical details and summaries.
            role (str): The role of the user (e.g., 'Hiring Manager (nontechnical)', 'Software Developer').

        Returns:
            Tuple[str, str]: A tuple containing the formatted response for the user.
        """
        if role == 'Hiring Manager (nontechnical)':
            return self._format_nontechnical(response)
        elif role in ['Hiring Manager (technical)', 'Software Developer']:
            return self._format_technical(response)
        elif role == 'Just looking around':
            return self._format_fun_facts(response)
        elif role == 'Looking to confess crush':
            return self._format_crush_confession(response)
        else:
            return "Role not recognized", ""

    def _format_nontechnical(self, response: Dict[str, Any]) -> Tuple[str, str]:
        summary = response.get('summary', 'No summary available.')
        return summary, ""

    def _format_technical(self, response: Dict[str, Any]) -> Tuple[str, str]:
        technical_details = response.get('technical_details', 'No technical details available.')
        summary = response.get('summary', 'No summary available.')
        return technical_details, summary

    def _format_fun_facts(self, response: Dict[str, Any]) -> Tuple[str, str]:
        fun_facts = response.get('fun_facts', 'No fun facts available.')
        video_link = response.get('video_link', '')
        return fun_facts, video_link

    def _format_crush_confession(self, response: Dict[str, Any]) -> Tuple[str, str]:
        confession = response.get('confession', 'No confession made.')
        return confession, ""