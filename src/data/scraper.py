import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import List, Optional
from src.config import REQUEST_HEADERS
from src.data.models import MutualFundScheme, FundManager

logger = logging.getLogger(__name__)

def parse_groww_html(html_content: str, url: str) -> MutualFundScheme:
    """
    Parses the Groww scheme page HTML content by extracting the __NEXT_DATA__ JSON state.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    next_data_script = soup.find("script", id="__NEXT_DATA__")
    
    if not next_data_script:
        raise ValueError("Could not find __NEXT_DATA__ script tag in the page.")
        
    try:
        data = json.loads(next_data_script.string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse __NEXT_DATA__ JSON: {e}")
        
    try:
        page_props = data.get("props", {}).get("pageProps", {})
        mf_data = page_props.get("mfServerSideData")
        if not mf_data:
            raise ValueError("mfServerSideData is missing in pageProps.")
    except Exception as e:
        raise ValueError(f"Unexpected JSON structure in __NEXT_DATA__: {e}")
        
    # Extract basic fields with robust defaults
    scheme_name = mf_data.get("scheme_name") or "Unknown Scheme"
    
    # Parse expense ratio as float
    raw_expense = mf_data.get("expense_ratio")
    try:
        expense_ratio = float(raw_expense) if raw_expense is not None else 0.0
    except (ValueError, TypeError):
        expense_ratio = 0.0
        
    exit_load = mf_data.get("exit_load") or "No Exit Load details available."
    benchmark_name = mf_data.get("benchmark_name") or "No Benchmark details."
    
    # Parse NAV as float
    raw_nav = mf_data.get("nav")
    try:
        nav = float(raw_nav) if raw_nav is not None else 0.0
    except (ValueError, TypeError):
        nav = 0.0
        
    nav_date = mf_data.get("nav_date") or "Unknown Date"
    launch_date = mf_data.get("launch_date") or "Unknown Launch Date"
    
    # Parse Min SIP as float
    raw_min_sip = mf_data.get("min_sip_investment")
    try:
        min_sip_amount = float(raw_min_sip) if raw_min_sip is not None else 0.0
    except (ValueError, TypeError):
        min_sip_amount = 0.0
        
    # Extract riskometer (Check return_stats first, fallback to nfo_risk)
    riskometer = None
    return_stats = mf_data.get("return_stats", [])
    if return_stats and isinstance(return_stats, list) and len(return_stats) > 0:
        riskometer = return_stats[0].get("risk")
    if not riskometer:
        riskometer = mf_data.get("nfo_risk") or "Unknown Risk"

    # Extract Fund Managers
    managers: List[FundManager] = []
    fm_details = mf_data.get("fund_manager_details", [])
    if fm_details and isinstance(fm_details, list):
        for fm in fm_details:
            name = fm.get("person_name")
            if name:
                managers.append(FundManager(
                    name=name,
                    experience=fm.get("experience"),
                    education=fm.get("education"),
                    date_from=fm.get("date_from")
                ))

    return MutualFundScheme(
        scheme_name=scheme_name,
        expense_ratio=expense_ratio,
        exit_load=exit_load,
        benchmark_name=benchmark_name,
        nav=nav,
        nav_date=nav_date,
        launch_date=launch_date,
        min_sip_amount=min_sip_amount,
        riskometer=riskometer,
        url=url,
        managers=managers
    )

def fetch_scheme(url: str) -> MutualFundScheme:
    """
    Fetches a Groww mutual fund page and returns a parsed MutualFundScheme model.
    """
    logger.info(f"Fetching Groww scheme page from: {url}")
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=15)
    response.raise_for_status()
    return parse_groww_html(response.text, url)
