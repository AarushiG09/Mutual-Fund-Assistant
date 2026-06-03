import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from src.data.db import get_connection, get_all_schemes
from src.data.vector_store import query_vector_store
from src.config import MUTUAL_FUND_URLS

logger = logging.getLogger(__name__)

# Keywords mapping to scheme URLs
SCHEME_MAPPING = {
    "mid": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "large": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "top": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "small": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "gold": "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "defence": "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth",
    "defense": "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth"
}

# Structured fields keyword mapping
STRUCTURED_FIELDS = {
    "nav": ("nav", "Net Asset Value (NAV)"),
    "net asset value": ("nav", "Net Asset Value (NAV)"),
    "exit load": ("exit_load", "Exit Load Details"),
    "exit fee": ("exit_load", "Exit Load Details"),
    "exit penalty": ("exit_load", "Exit Load Details"),
    "expense ratio": ("expense_ratio", "Expense Ratio"),
    "expense percentage": ("expense_ratio", "Expense Ratio"),
    "charge": ("expense_ratio", "Expense Ratio"),
    "benchmark": ("benchmark_name", "Benchmark Index"),
    "index": ("benchmark_name", "Benchmark Index"),
    "sip": ("min_sip_amount", "Minimum SIP Amount"),
    "min sip": ("min_sip_amount", "Minimum SIP Amount"),
    "minimum sip": ("min_sip_amount", "Minimum SIP Amount"),
    "launch": ("launch_date", "Launch Date"),
    "started": ("launch_date", "Launch Date"),
    "date": ("launch_date", "Launch Date")
}

def identify_target_scheme(query: str) -> Optional[str]:
    """Identifies the scheme URL from keywords in the query."""
    query_lower = query.lower()
    for key, url in SCHEME_MAPPING.items():
        if key in query_lower:
            return url
    return None

def identify_structured_field(query: str) -> Optional[tuple]:
    """Identifies if the query is asking for a specific structured field."""
    query_lower = query.lower()
    for key, (field_name, display_name) in STRUCTURED_FIELDS.items():
        if key in query_lower:
            return field_name, display_name
    return None

def retrieve_from_sqlite(scheme_url: str, field_name: str, display_name: str) -> Optional[Dict[str, Any]]:
    """Retrieves a specific field value directly from the SQLite database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get scheme details
        cursor.execute("SELECT * FROM schemes WHERE url = ?", (scheme_url,))
        scheme_row = cursor.fetchone()
        if not scheme_row:
            return None
            
        value = scheme_row[field_name]
        scheme_name = scheme_row["scheme_name"]
        last_updated_raw = scheme_row["last_updated"]
        
        # Format last updated date
        try:
            dt = datetime.fromisoformat(last_updated_raw)
            last_updated = dt.strftime("%d-%b-%Y")
        except (ValueError, TypeError):
            last_updated = "Unknown Date"
            
        # Format the value nicely
        if field_name == "nav":
            formatted_val = f"₹{value}"
        elif field_name == "expense_ratio":
            formatted_val = f"{value}%"
        elif field_name == "min_sip_amount":
            formatted_val = f"₹{value}"
        else:
            formatted_val = str(value)
            
        context_str = (
            f"Scheme Name: {scheme_name}\n"
            f"Factual Details: The {display_name} is {formatted_val}.\n"
            f"Source URL: {scheme_url}"
        )
        
        return {
            "context": context_str,
            "source_url": scheme_url,
            "last_updated": last_updated,
            "retrieval_type": "sqlite",
            "distance": 0.0
        }
    except Exception as e:
        logger.error(f"Error retrieving from SQLite: {e}")
        return None
    finally:
        conn.close()

def retrieve_hybrid_context(query: str) -> Dict[str, Any]:
    """
    Main entry point for context retrieval:
    1. Direct SQLite lookup for specific structured metrics (NAV, expense ratio, etc.) if matched.
    2. Fallback to semantic search on ChromaDB.
    """
    # 1. Check if direct SQLite lookup is possible
    scheme_url = identify_target_scheme(query)
    field_info = identify_structured_field(query)
    
    if scheme_url and field_info:
        field_name, display_name = field_info
        # Avoid direct lookup if query asks about manager background or details (needs vector search)
        if "manager" not in query.lower() and "who" not in query.lower():
            sqlite_result = retrieve_from_sqlite(scheme_url, field_name, display_name)
            if sqlite_result:
                logger.info(f"Factual query resolved via SQLite for field {field_name}")
                return sqlite_result
                
    # 2. Fallback to Semantic Search in ChromaDB
    logger.info("Factual query routing to ChromaDB semantic search...")
    filter_dict = None
    if scheme_url:
        # Pre-filter by scheme URL to improve context accuracy
        filter_dict = {"source_url": scheme_url}
        
    results = query_vector_store(query, n_results=2, filter_dict=filter_dict)
    
    if not results:
        # If no results found, fallback to searching all schemes
        results = query_vector_store(query, n_results=2)
        
    if not results:
        return {
            "context": "No verified facts found in database for the given query.",
            "source_url": MUTUAL_FUND_URLS[0], # fallback citation
            "last_updated": datetime.now().strftime("%d-%b-%Y"),
            "retrieval_type": "none"
        }
        
    # Aggregate contexts and select citation URL
    context_chunks = []
    citation_url = results[0]["metadata"]["source_url"]
    
    for r in results:
        context_chunks.append(r["text"])
        
    unified_context = "\n\n---\n\n".join(context_chunks)
    
    # Get last updated date from database (defaulting to today)
    last_updated = datetime.now().strftime("%d-%b-%Y")
    if scheme_url:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT last_updated FROM schemes WHERE url = ?", (scheme_url,))
        row = cursor.fetchone()
        if row:
            try:
                dt = datetime.fromisoformat(row["last_updated"])
                last_updated = dt.strftime("%d-%b-%Y")
            except Exception:
                pass
        conn.close()
        
    return {
        "context": unified_context,
        "source_url": citation_url,
        "last_updated": last_updated,
        "retrieval_type": "vector",
        "distance": results[0]["distance"] if results else 2.0
    }
