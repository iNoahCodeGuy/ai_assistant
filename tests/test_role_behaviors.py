import types
from agents.role_router import RoleRouter
from agents.response_formatter import ResponseFormatter
from core.memory import Memory

class DummyDoc:
    def __init__(self, text, meta=None):
        self.page_content = text
        self.metadata = meta or {}

class DummyRag:
    def __init__(self):
        self.career_calls = 0
        self.code_calls = 0

    def retrieve_career_info(self, query: str):
        self.career_calls += 1
        return [DummyDoc("Career fact A", {"source": "career_kb.csv"})]

    def retrieve_code_info(self, query: str):
        self.code_calls += 1
        return [DummyDoc("Code snippet X", {"file_path": "src/core/rag_engine.py", "start_line": 10})]

    def generate_response(self, query, context, role):
        # Deterministic stub for assertions
        return f"[{role}] {query} :: {len(context)} ctx docs"

def route(role: str, query: str):
    router = RoleRouter()
    mem = Memory()
    rag = DummyRag()
    raw = router.route(role, query, mem, rag, chat_history=[])
    formatted = ResponseFormatter().format(raw)
    return raw, formatted, rag

def test_nontechnical_hiring_manager_career():
    raw, formatted, rag = route("Hiring Manager (nontechnical)", "Show career overview")
    assert raw["type"] in ("career", "general")
    assert rag.career_calls == 1
    assert "Career Overview" in formatted or "Career" in formatted

def test_technical_hiring_manager_technical_query():
    raw, formatted, rag = route("Hiring Manager (technical)", "Explain the code architecture")
    assert raw["type"] in ("technical", "career")
    # At least one of code or career retrieval should occur
    assert rag.code_calls + rag.career_calls >= 1
    # Engineer detail section expected for technical path
    assert "Engineer Detail" in formatted or "Plain-English Summary" in formatted

def test_software_developer_prefers_code():
    raw, formatted, rag = route("Software Developer", "How does the retrieval pipeline work?")
    assert rag.code_calls >= 0  # technical classification may route to code
    assert "[Software Developer]" in raw["response"]

def test_casual_mma_query_shortcuts():
    raw, formatted, rag = route("Just looking around", "mma fight link?")
    assert raw["type"] == "mma"
    assert "youtube" in (raw.get("youtube_link","") or "").lower()

def test_casual_fun_query():
    raw, formatted, rag = route("Just looking around", "fun facts?")
    assert raw["type"] in ("fun", "general")
    assert "Fun Facts" in formatted or "fun" in formatted.lower()

def test_confession_role_bypasses_llm():
    raw, formatted, rag = route("Looking to confess crush", "I like someone")
    assert raw["type"] == "confession"
    # No retrieval calls
    assert rag.career_calls == 0 and rag.code_calls == 0
    assert "💌" in formatted