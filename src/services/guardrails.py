import re
import logging
from typing import List, Dict, Any, Optional
from src.services.llm import LLMClient
from src.config import MUTUAL_FUND_URLS

logger = logging.getLogger(__name__)

# Strict prohibited terms in final answers
PROHIBITED_ADVISORY_TERMS = [
    "highly recommend", "suggest investing", "recommend", "better return",
    "should invest", "you should", "investment advice", "good choice", "best fund"
]

def count_sentences(text: str) -> int:
    """Counts the number of sentences in a given text string."""
    # Clean up markdown link brackets before splitting to avoid period issues inside URLs
    clean_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', text)
    
    # Temporary placeholder cleanup for common abbreviations to prevent splitting on them
    abbrevs = ["e.g.", "i.e.", "etc.", "mr.", "ms.", "dr.", "rs.", "a.m.", "p.m."]
    for abbrev in abbrevs:
        pattern = re.compile(re.escape(abbrev), re.IGNORECASE)
        clean_text = pattern.sub(abbrev.replace(".", ""), clean_text)
        
    # Split by periods, exclamation marks, or question marks followed by space or end-of-string
    sentences = re.split(r'(?<=[.!?])\s+|(?<=[.!?])$', clean_text.strip())
    # Filter out empty strings
    sentences = [s for s in sentences if s.strip()]
    return len(sentences)

def extract_urls(text: str) -> List[str]:
    """Extracts all URLs found in the text."""
    # Matches markdown links [name](url) or naked URLs
    markdown_urls = re.findall(r'https?://[^\s)]+', text)
    # Strip trailing periods/brackets if any
    cleaned_urls = []
    for url in markdown_urls:
        url_clean = url.rstrip('.)]')
        cleaned_urls.append(url_clean)
    return cleaned_urls

def audit_advisory_terms(text: str) -> bool:
    """
    Returns True if the text contains prohibited advisory words,
    indicating a compliance violation.
    """
    text_lower = text.lower()
    for term in PROHIBITED_ADVISORY_TERMS:
        if term in text_lower:
            logger.warning(f"Response contains prohibited advisory term: '{term}'")
            return True
    return False

def check_compliance(text: str, expected_url: str) -> List[str]:
    """
    Validates all compliance constraints for the generated text.
    Returns a list of error strings if any violations are found.
    """
    errors = []
    
    # 1. Sentence limit check (<= 3 sentences)
    sentence_count = count_sentences(text)
    if sentence_count > 3:
        errors.append(f"Response exceeds maximum sentence limit (has {sentence_count} sentences, max is 3).")
        
    # 2. Citation check (exactly 1 URL matching Groww target URLs)
    urls = extract_urls(text)
    if len(urls) != 1:
        errors.append(f"Response must contain exactly one citation link (has {len(urls)}).")
    else:
        citation_url = urls[0]
        if citation_url != expected_url:
            errors.append(f"Citation URL '{citation_url}' does not match expected URL '{expected_url}'.")
        if citation_url not in MUTUAL_FUND_URLS:
            errors.append(f"Citation URL '{citation_url}' is not in the list of authorized Groww URLs.")
            
    # 3. Advisory terms check
    if audit_advisory_terms(text):
        errors.append("Response contains prohibited investment advice or advisory phrasing.")
        
    return errors

def run_self_correction_loop(
    query: str, 
    answer: str, 
    expected_url: str, 
    errors: List[str], 
    client: LLMClient
) -> Optional[str]:
    """
    Queries the LLM (Groq) with a repair prompt to self-correct
    a response that failed compliance checks.
    """
    logger.info("Triggering self-correction repair loop via Groq...")
    
    errors_str = "\n".join([f"- {err}" for err in errors])
    
    system_prompt = (
        "You are a strict compliance auditor. Your job is to rewrite the provided draft response "
        "to fix all specified compliance errors.\n"
        "You must strictly adhere to these compliance rules:\n"
        "1. Do not exceed a maximum of 3 sentences.\n"
        "2. Do not offer opinions, suggestions, or investment advice.\n"
        f"3. You must include exactly one citation link, which must be: {expected_url}."
    )
    
    user_prompt = (
        f"Original User Query: {query}\n\n"
        f"Draft Response to Repair:\n{answer}\n\n"
        f"Compliance Violations to Fix:\n{errors_str}\n\n"
        "Please output the corrected response now."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        repaired_answer = client.complete(messages, temperature=0.0)
        return repaired_answer
    except Exception as e:
        logger.error(f"Compliance repair call failed: {e}")
        return None

def enforce_guardrails(
    query: str, 
    initial_answer: str, 
    expected_url: str, 
    context: str, 
    client: LLMClient
) -> str:
    """
    Runs the full compliance guardrail pipeline:
    1. Runs checks on the initial response.
    2. If violations occur, triggers a Groq self-correction loop.
    3. If self-correction fails, falls back to a deterministic SQLite-based response.
    """
    errors = check_compliance(initial_answer, expected_url)
    
    if not errors:
        logger.info("Initial LLM response passed all compliance checks.")
        return initial_answer
        
    logger.warning(f"Compliance checks failed. Violations:\n{errors}")
    
    # Attempt self-correction
    repaired_answer = run_self_correction_loop(query, initial_answer, expected_url, errors, client)
    
    if repaired_answer:
        # Re-check the repaired response
        repair_errors = check_compliance(repaired_answer, expected_url)
        if not repair_errors:
            logger.info("Repaired response successfully passed compliance checks.")
            return repaired_answer
        logger.warning(f"Repaired response still failed compliance checks: {repair_errors}")
        
    # Failsafe fallback: Construct deterministic card from SQLite context
    logger.error("Guardrails and repair failed. Triggering deterministic fallback response.")
    clean_facts = context.split("Source URL:")[0].strip()
    # Normalize spacing
    clean_facts = re.sub(r'\s+', ' ', clean_facts)
    
    # Ensure the fallback facts don't exceed 2 sentences (leaving room for the source citation sentence)
    fact_sentences = re.split(r'(?<=[.!?])\s+|(?<=[.!?])$', clean_facts)
    fact_sentences = [s.strip() for s in fact_sentences if s.strip()]
    if len(fact_sentences) > 2:
        clean_facts = " ".join(fact_sentences[:2])
        if not clean_facts.endswith(('.', '!', '?')):
            clean_facts += "."
            
    fallback_response = (
        f"Factual details retrieved: {clean_facts} "
        f"Source: {expected_url}"
    )
    return fallback_response
