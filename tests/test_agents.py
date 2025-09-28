import pytest
from src.agents.role_router import RoleRouter
from src.agents.response_formatter import ResponseFormatter

@pytest.fixture
def role_router():
    return RoleRouter()

@pytest.fixture
def response_formatter():
    return ResponseFormatter()

def test_role_router_initialization(role_router):
    assert role_router is not None

def test_route_nontechnical_hiring_manager(role_router):
    response = role_router.route("Hiring Manager (nontechnical)")
    assert response == "Routing to nontechnical hiring manager response handler."

def test_route_technical_hiring_manager(role_router):
    response = role_router.route("Hiring Manager (technical)")
    assert response == "Routing to technical hiring manager response handler."

def test_route_software_developer(role_router):
    response = role_router.route("Software Developer")
    assert response == "Routing to software developer response handler."

def test_route_casual_visitor(role_router):
    response = role_router.route("Just looking around")
    assert response == "Routing to casual visitor response handler."

def test_route_confess_crush(role_router):
    response = role_router.route("Looking to confess crush")
    assert response == "Routing to confess crush response handler."

def test_response_formatter_initialization(response_formatter):
    assert response_formatter is not None

def test_format_technical_response(response_formatter):
    technical_response = response_formatter.format_technical("Technical details here.")
    assert "Technical details here." in technical_response

def test_format_plain_english_response(response_formatter):
    plain_response = response_formatter.format_plain_english("Plain English summary here.")
    assert "Plain English summary here." in plain_response

def test_format_mixed_response(response_formatter):
    mixed_response = response_formatter.format_mixed("Technical details", "Plain English summary")
    assert "Technical details" in mixed_response
    assert "Plain English summary" in mixed_response