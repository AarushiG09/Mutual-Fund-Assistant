import pytest
from src.services.orchestrator import classify_query, ask_question
from src.services.llm import LLMClient
from src.data.db import init_db, save_scheme
from src.data.models import MutualFundScheme, FundManager
from src.data.vector_store import index_schemes_in_vector_store

@pytest.fixture(autouse=True)
def setup_orchestrator_data(tmp_path, monkeypatch):
    # Setup temporary SQLite and Chroma DB directories for testing orchestrator
    test_db = str(tmp_path / "test_funds.db")
    test_chroma = str(tmp_path / "test_chroma")
    
    monkeypatch.setattr("src.data.db.SQLITE_DB_PATH", test_db)
    monkeypatch.setattr("src.data.vector_store.CHROMA_DB_PATH", test_chroma)
    
    init_db()
    
    scheme = MutualFundScheme(
        scheme_name="HDFC Mid Cap Fund Direct Growth",
        expense_ratio=0.73,
        exit_load="Exit load of 1% within 1 year.",
        benchmark_name="NIFTY Midcap 150 TRI",
        nav=218.8,
        nav_date="01-Jun-2026",
        launch_date="01-Jan-2013",
        min_sip_amount=100.0,
        riskometer="Very High",
        url="https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        managers=[
            FundManager(name="Chirag Setalvad", experience="Chirag has 20 years experience", education="MBA", date_from="2013-01-01")
        ]
    )
    
    save_scheme(scheme)
    index_schemes_in_vector_store([scheme])

def test_classify_query():
    assert classify_query("What is the NAV of HDFC Mid Cap?") == "factual"
    assert classify_query("Should I invest in HDFC Mid Cap?") == "advisory"
    assert classify_query("Which fund is better between Mid Cap and Small Cap?") == "advisory"

def test_ask_factual_question():
    # Use mock client to verify flow
    mock_client = LLMClient(provider="mock")
    res = ask_question("Who manages the HDFC Mid Cap Fund?", client=mock_client)
    
    assert res["status"] == "success"
    assert "Chirag Setalvad" in res["answer"]
    assert res["source_url"] == "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"

def test_ask_advisory_question():
    res = ask_question("Should I invest in HDFC Mid Cap Fund?")
    assert res["status"] == "refused_advisory"
    assert "amfiindia.com" in res["source_url"]
    assert "cannot provide investment advice" in res["answer"]

def test_ask_out_of_scope_question():
    res = ask_question("What is the capital of Spain?")
    assert res["status"] == "refused_out_of_scope"
    assert "sebi.gov.in" in res["source_url"]
    assert "only answer factual questions" in res["answer"]
