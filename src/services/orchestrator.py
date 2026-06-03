import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.services.retrieval import retrieve_hybrid_context, identify_target_scheme
from src.services.llm import LLMClient
from src.config import MUTUAL_FUND_URLS

logger = logging.getLogger(__name__)

# Core compliance keywords indicating advisory requests
ADVISORY_KEYWORDS = [
    "should i", "should we", "should one", "recommend", "recommendation", "recommendations",
    "better", "best", "compare", "performance comparison", "suggest", "suitability",
    "suitable", "invest in", "buy", "sell", "is good", "is it good", "advise", "advice",
    "which fund", "which one", "suggest me"
]

# Educational links for refusals
AMFI_EDUCATION_URL = "https://www.amfiindia.com/investor-corner/education/interest-rates.html"
SEBI_INVESTOR_URL = "https://investor.sebi.gov.in/"

def classify_query(query: str) -> str:
    """
    Classifies user queries into:
    - 'advisory': Queries seeking investment advice or comparisons.
    - 'factual': Factual, objective inquiries.
    """
    query_lower = query.lower()
    for kw in ADVISORY_KEYWORDS:
        if kw in query_lower:
            return "advisory"
    return "factual"

def get_refusal_payload(reason: str) -> Dict[str, Any]:
    """Returns compliance refusal answers based on the trigger reason."""
    last_updated = datetime.now().strftime("%d-%b-%Y")
    
    if reason == "advisory":
        answer = (
            "I am a facts-only assistant and cannot provide investment advice, suggestions, or fund comparisons. "
            f"For educational materials on investing, please refer to the AMFI Investor Education Corner: {AMFI_EDUCATION_URL}"
        )
        return {
            "answer": answer,
            "source_url": AMFI_EDUCATION_URL,
            "last_updated": last_updated,
            "status": "refused_advisory"
        }
    else:  # out_of_scope
        answer = (
            "I can only answer factual questions about the 5 HDFC mutual fund schemes in our database. "
            f"For general guidelines on investing, please visit the SEBI Investor Education Portal: {SEBI_INVESTOR_URL}"
        )
        return {
            "answer": answer,
            "source_url": SEBI_INVESTOR_URL,
            "last_updated": last_updated,
            "status": "refused_out_of_scope"
        }

def ask_question(query: str, client: Optional[LLMClient] = None) -> Dict[str, Any]:
    """
    Main orchestrator for answering user questions:
    1. Classifier check (blocks advisory queries).
    2. Context Retrieval (SQL or Vector search).
    3. Scope Enforcement (filters completely out-of-scope vector lookups).
    4. Prompt execution & answer aggregation.
    """
    # 1. Pre-processing: Classify for advisory requests
    if classify_query(query) == "advisory":
        logger.info("Query flagged as ADVISORY. Routing to refusal handler.")
        return get_refusal_payload("advisory")
        
    # 2. Context Retrieval
    retrieval = retrieve_hybrid_context(query)
    context = retrieval["context"]
    source_url = retrieval["source_url"]
    last_updated = retrieval["last_updated"]
    retrieval_type = retrieval["retrieval_type"]
    
    # 3. Scope Enforcement: check if vector query is too far from our corpus
    scheme_matched = identify_target_scheme(query)
    distance = retrieval.get("distance", 0.0)
    
    # If no scheme keyword matched and the vector search distance is too high, it's out of scope
    if retrieval_type == "none" or (not scheme_matched and distance > 0.48):
        logger.info(f"Query flagged as OUT-OF-SCOPE (distance={distance:.3f}). Routing to refusal handler.")
        return get_refusal_payload("out_of_scope")
        
    # 4. Construct System Prompt and User Prompt
    system_prompt = (
        "You are a facts-only Mutual Fund FAQ Assistant.\n"
        "Answer the user's query using ONLY the verified facts provided in the context below.\n"
        "If the context does not contain the answer, politely state that you do not have that information.\n"
        "Do NOT give investment opinions, advice, or recommendations.\n"
        "Do NOT compare fund performances or recommend any action.\n"
        "Limit your response to a maximum of 3 sentences.\n"
        f"You must include exactly one citation link in your response: {source_url}."
    )
    
    user_prompt = (
        f"Context:\n{context}\n\n"
        f"Query: {query}"
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    # 5. Call LLM for completion
    llm_client = client or LLMClient()
    try:
        raw_answer = llm_client.complete(messages)
        from src.services.guardrails import enforce_guardrails
        answer = enforce_guardrails(query, raw_answer, source_url, context, llm_client)
    except Exception as e:
        logger.error(f"LLM completed with error: {e}")
        from src.services.guardrails import enforce_guardrails
        answer = enforce_guardrails(query, "", source_url, context, llm_client)
        
    return {
        "answer": answer,
        "source_url": source_url,
        "last_updated": last_updated,
        "status": "success"
    }
