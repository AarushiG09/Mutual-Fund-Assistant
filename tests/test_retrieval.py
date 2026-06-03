import pytest
from src.services.retrieval import identify_target_scheme, identify_structured_field, retrieve_hybrid_context
from src.data.db import init_db, save_scheme
from src.data.models import MutualFundScheme, FundManager
from src.data.vector_store import index_schemes_in_vector_store

@pytest.fixture(autouse=True)
def setup_test_data(tmp_path, monkeypatch):
    # Setup temporary SQLite and Chroma DB directories for testing retrieval
    test_db = str(tmp_path / "test_funds.db")
    test_chroma = str(tmp_path / "test_chroma")
    
    monkeypatch.setattr("src.data.db.SQLITE_DB_PATH", test_db)
    monkeypatch.setattr("src.data.vector_store.CHROMA_DB_PATH", test_chroma)
    
    init_db()
    
    # Create two test schemes
    scheme_mid = MutualFundScheme(
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
            FundManager(name="Chirag Setalvad", experience="Chirag Setalvad has 20 years experience", education="MBA", date_from="2013-01-01")
        ]
    )
    
    scheme_defence = MutualFundScheme(
        scheme_name="HDFC Defence Fund Direct Growth",
        expense_ratio=0.82,
        exit_load="Exit load of 1% within 1 year.",
        benchmark_name="Nifty India Defence TRI",
        nav=28.2,
        nav_date="01-Jun-2026",
        launch_date="02-Jun-2023",
        min_sip_amount=100.0,
        riskometer="Very High",
        url="https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth",
        managers=[
            FundManager(name="Priya Ranjan", experience="Priya Ranjan has 15 years experience", education="MTech", date_from="2023-06-02")
        ]
    )
    
    # Save to SQLite
    save_scheme(scheme_mid)
    save_scheme(scheme_defence)
    
    # Save to ChromaDB
    index_schemes_in_vector_store([scheme_mid, scheme_defence])

def test_scheme_identification():
    assert identify_target_scheme("What is the NAV of HDFC Mid Cap?") == "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
    assert identify_target_scheme("Tell me about defence fund") == "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth"
    assert identify_target_scheme("Some general question") is None

def test_field_identification():
    assert identify_structured_field("What is the exit load of HDFC Mid Cap?") == ("exit_load", "Exit Load Details")
    assert identify_structured_field("What is the expense percentage?") == ("expense_ratio", "Expense Ratio")
    assert identify_structured_field("Who manages the fund?") is None

def test_hybrid_retrieval_routing():
    # 1. Structured query (should use SQLite)
    res_nav = retrieve_hybrid_context("What is the NAV of HDFC Mid Cap?")
    assert res_nav["retrieval_type"] == "sqlite"
    assert "₹218.8" in res_nav["context"]
    assert res_nav["source_url"] == "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
    
    # 2. Semantic query (should use Vector Store)
    res_mgr = retrieve_hybrid_context("Who is the manager of HDFC Defence and what is their education?")
    assert res_mgr["retrieval_type"] == "vector"
    assert "Priya Ranjan" in res_mgr["context"]
    assert "MTech" in res_mgr["context"]
    assert res_mgr["source_url"] == "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth"
