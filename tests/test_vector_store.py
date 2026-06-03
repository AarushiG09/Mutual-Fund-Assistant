import pytest
from src.data.models import MutualFundScheme, FundManager
from src.data.vector_store import create_chunks, index_schemes_in_vector_store, query_vector_store, get_chroma_client

def test_create_chunks():
    scheme = MutualFundScheme(
        scheme_name="HDFC Vector Test Scheme Direct Growth",
        expense_ratio=0.75,
        exit_load="1% if redeemed within 1 year.",
        benchmark_name="NIFTY 100 TRI",
        nav=100.50,
        nav_date="01-Jun-2026",
        launch_date="01-Jan-2015",
        min_sip_amount=500.0,
        riskometer="High",
        url="https://groww.in/mutual-funds/hdfc-vector-test-scheme",
        managers=[
            FundManager(name="Manager A", experience="10y", education="MBA", date_from="2020-01-01"),
            FundManager(name="Manager B", experience="5y", education="CA", date_from="2022-01-01")
        ]
    )
    
    chunks = create_chunks(scheme)
    
    # Expected chunks count = 1 (summary) + 2 (managers) + 1 (tax) = 4
    assert len(chunks) == 4
    
    summary_chunk = next(c for c in chunks if c["metadata"]["chunk_type"] == "scheme_summary")
    assert "HDFC Vector Test Scheme Direct Growth" in summary_chunk["text"]
    assert "NAV" in summary_chunk["text"]
    assert "0.75%" in summary_chunk["text"]
    
    manager_chunks = [c for c in chunks if c["metadata"]["chunk_type"] == "manager_bio"]
    assert len(manager_chunks) == 2
    assert {m["metadata"]["manager_name"] for m in manager_chunks} == {"Manager A", "Manager B"}
    
    tax_chunk = next(c for c in chunks if c["metadata"]["chunk_type"] == "tax_details")
    assert "Taxation" in tax_chunk["text"]

def test_vector_indexing_and_query(monkeypatch, tmp_path):
    # Override ChromaDB path to temporary path for testing
    test_chroma = str(tmp_path / "test_chroma_db")
    monkeypatch.setattr("src.data.vector_store.CHROMA_DB_PATH", test_chroma)
    
    scheme = MutualFundScheme(
        scheme_name="HDFC Test Index Scheme Direct Growth",
        expense_ratio=0.50,
        exit_load="No exit load.",
        benchmark_name="NIFTY 50 TRI",
        nav=200.0,
        nav_date="01-Jun-2026",
        launch_date="01-Jan-2018",
        min_sip_amount=100.0,
        riskometer="Moderate",
        url="https://groww.in/mutual-funds/hdfc-test-index-scheme",
        managers=[
            FundManager(name="Manager XYZ", experience="20 years", education="PhD Finance", date_from="2018-01-01")
        ]
    )
    
    # Index schemes
    index_schemes_in_vector_store([scheme])
    
    # Query vector store for manager bio
    results = query_vector_store("Manager XYZ experience", n_results=1)
    assert len(results) == 1
    assert results[0]["metadata"]["chunk_type"] == "manager_bio"
    assert results[0]["metadata"]["manager_name"] == "Manager XYZ"
    assert "PhD Finance" in results[0]["text"]
    
    # Query vector store for summary
    results_summary = query_vector_store("HDFC Test Index Scheme NAV benchmark", n_results=1)
    assert len(results_summary) == 1
    assert "NIFTY 50 TRI" in results_summary[0]["text"]
