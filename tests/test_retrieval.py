import pytest
from src.retrieval.career_kb import CareerKnowledgeBase
from src.retrieval.code_index import CodeIndex

@pytest.fixture
def setup_career_kb():
    return CareerKnowledgeBase('data/career_kb.csv')

@pytest.fixture
def setup_code_index():
    return CodeIndex('vector_stores/code_index')

def test_career_kb_loading(setup_career_kb):
    assert setup_career_kb.data is not None
    assert len(setup_career_kb.data) > 0

def test_career_kb_query(setup_career_kb):
    result = setup_career_kb.query('Software Engineer')
    assert result is not None
    assert 'Software Engineer' in result['title']

def test_code_index_loading(setup_code_index):
    assert setup_code_index.index is not None

def test_code_index_query(setup_code_index):
    result = setup_code_index.query('def example_function')
    assert result is not None
    assert 'example_function' in result['code']