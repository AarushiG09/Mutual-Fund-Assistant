import pytest
import sqlite3
from src.data.models import MutualFundScheme, FundManager
from src.data.scraper import parse_groww_html
from src.data.db import init_db, save_scheme, get_all_schemes, get_connection

MOCK_NEXT_DATA_HTML = """
<html>
  <body>
    <script id="__NEXT_DATA__" type="application/json">
    {
      "props": {
        "pageProps": {
          "mfServerSideData": {
            "scheme_name": "HDFC Test Fund Direct Growth",
            "expense_ratio": "0.55",
            "exit_load": "Exit load of 1% within 365 days.",
            "benchmark_name": "NIFTY 50 TRI",
            "nav": 123.45,
            "nav_date": "01-Jun-2026",
            "launch_date": "01-Jan-2015",
            "min_sip_investment": 500,
            "nfo_risk": "High",
            "fund_manager_details": [
              {
                "person_name": "Test Manager A",
                "experience": "10 years experience",
                "education": "MBA Finance",
                "date_from": "2018-05-10"
              }
            ]
          }
        }
      }
    }
    </script>
  </body>
</html>
"""

def test_parse_groww_html():
    url = "https://groww.in/mutual-funds/hdfc-test-fund"
    scheme = parse_groww_html(MOCK_NEXT_DATA_HTML, url)
    
    assert scheme.scheme_name == "HDFC Test Fund Direct Growth"
    assert scheme.expense_ratio == 0.55
    assert scheme.exit_load == "Exit load of 1% within 365 days."
    assert scheme.benchmark_name == "NIFTY 50 TRI"
    assert scheme.nav == 123.45
    assert scheme.nav_date == "01-Jun-2026"
    assert scheme.launch_date == "01-Jan-2015"
    assert scheme.min_sip_amount == 500.0
    assert scheme.riskometer == "High"
    assert scheme.url == url
    assert len(scheme.managers) == 1
    assert scheme.managers[0].name == "Test Manager A"
    assert scheme.managers[0].experience == "10 years experience"
    assert scheme.managers[0].education == "MBA Finance"
    assert scheme.managers[0].date_from == "2018-05-10"

def test_db_operations(monkeypatch, tmp_path):
    # Override database path for testing to use a temporary DB
    test_db = str(tmp_path / "test_mutual_funds.db")
    monkeypatch.setattr("src.data.db.SQLITE_DB_PATH", test_db)
    
    # Initialize the database
    init_db()
    
    # Verify tables created
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    assert "schemes" in tables
    assert "managers" in tables
    conn.close()
    
    # Create mock scheme
    scheme = MutualFundScheme(
        scheme_name="HDFC DB Test Scheme Direct Growth",
        expense_ratio=0.15,
        exit_load="No exit load",
        benchmark_name="NIFTY 500 TRI",
        nav=50.0,
        nav_date="02-Jun-2026",
        launch_date="12-Dec-2020",
        min_sip_amount=100.0,
        riskometer="Moderate",
        url="https://groww.in/mutual-funds/hdfc-db-test-scheme",
        managers=[
            FundManager(name="Mgr X", experience="5 years", education="BTech", date_from="2021-01-01"),
            FundManager(name="Mgr Y", experience="2 years", education="MTech", date_from="2023-01-01")
        ]
    )
    
    # Save scheme
    save_scheme(scheme)
    
    # Retrieve all schemes
    all_schemes = get_all_schemes()
    assert len(all_schemes) == 1
    retrieved = all_schemes[0]
    assert retrieved.scheme_name == "HDFC DB Test Scheme Direct Growth"
    assert retrieved.expense_ratio == 0.15
    assert retrieved.nav == 50.0
    assert len(retrieved.managers) == 2
    
    manager_names = {m.name for m in retrieved.managers}
    assert manager_names == {"Mgr X", "Mgr Y"}
