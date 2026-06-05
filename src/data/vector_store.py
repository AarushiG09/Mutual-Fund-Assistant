import os
import chromadb
import logging
from typing import List, Dict, Any
from chromadb.utils import embedding_functions
from src.config import CHROMA_DB_PATH, EMBEDDING_MODEL_NAME
from src.data.models import MutualFundScheme

logger = logging.getLogger(__name__)

# Initialize local sentence-transformers embedding function lazily
_embedding_fn = None

def get_embedding_fn():
    global _embedding_fn
    if _embedding_fn is None:
        logger.info("Initializing SentenceTransformer embedding function (downloading model if not cached)...")
        _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
    return _embedding_fn

def get_chroma_client() -> chromadb.PersistentClient:
    """Returns a persistent ChromaDB client."""
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)

def get_collection(client: chromadb.PersistentClient):
    """Returns the mutual funds vector collection."""
    return client.get_or_create_collection(
        name="mutual_fund_facts",
        embedding_function=get_embedding_fn()
    )

def create_chunks(scheme: MutualFundScheme) -> List[Dict[str, Any]]:
    """
    Implements the hybrid entity-based chunking strategy:
    1. Structured summary chunk
    2. Fund manager biography chunks
    3. Category disclosure / taxation chunks
    """
    chunks = []
    
    # 1. Structured Scheme Summary Chunk
    managers_str = ", ".join([m.name for m in scheme.managers]) or "None"
    summary_text = (
        f"Scheme Name: {scheme.scheme_name}\n"
        f"Net Asset Value (NAV): {scheme.nav} (as of {scheme.nav_date})\n"
        f"Expense Ratio: {scheme.expense_ratio}%\n"
        f"Exit Load Details: {scheme.exit_load}\n"
        f"Benchmark Index: {scheme.benchmark_name}\n"
        f"Minimum SIP Amount: {scheme.min_sip_amount}\n"
        f"Launch Date: {scheme.launch_date}\n"
        f"Riskometer Classification: {scheme.riskometer}\n"
        f"Fund Managers: {managers_str}\n"
        f"Source URL: {scheme.url}"
    )
    chunks.append({
        "id": f"summary_{scheme.url.split('/')[-1]}",
        "text": summary_text,
        "metadata": {
            "scheme_name": scheme.scheme_name,
            "source_url": scheme.url,
            "chunk_type": "scheme_summary"
        }
    })
    
    # 2. Entity-Based Fund Manager Biography Chunks
    for idx, manager in enumerate(scheme.managers):
        tenure_info = f"managing since {manager.date_from}" if manager.date_from else "tenure details not specified"
        bio_text = (
            f"Fund Manager: {manager.name}\n"
            f"Scheme: {scheme.scheme_name}\n"
            f"Tenure Details: {tenure_info}\n"
            f"Education/Qualifications: {manager.education or 'Not specified'}\n"
            f"Experience & Career Background: {manager.experience or 'No detailed history available.'}\n"
            f"Source URL: {scheme.url}"
        )
        chunks.append({
            "id": f"manager_{scheme.url.split('/')[-1]}_{idx}",
            "text": bio_text,
            "metadata": {
                "scheme_name": scheme.scheme_name,
                "source_url": scheme.url,
                "chunk_type": "manager_bio",
                "manager_name": manager.name
            }
        })
        
    # 3. Category Disclosures & Taxation Chunks
    # Groww tax impact helper notes
    tax_info = "Returns are taxed as per Equity or Debt fund specifications depending on holding duration. Exit load might apply."
    if "gold" in scheme.url.lower():
        tax_info = (
            "HDFC Gold ETF FoF Taxation: Gold mutual fund returns are taxed as short-term capital gains (STCG) "
            "as per the individual investor's income tax slab rate, regardless of the holding period."
        )
    elif "defence" in scheme.url.lower() or "mid-cap" in scheme.url.lower() or "small-cap" in scheme.url.lower() or "large-cap" in scheme.url.lower():
        tax_info = (
            f"Taxation for {scheme.scheme_name} (Equity Fund): Short-term Capital Gains (STCG) are taxed at 20% "
            "if redeemed within 1 year. Long-term Capital Gains (LTCG) exceeding Rs 1.25 Lakh per financial year "
            "are taxed at 12.5% if redeemed after 1 year."
        )
        
    tax_text = (
        f"Scheme Name: {scheme.scheme_name}\n"
        f"Category Disclosures & Taxation:\n"
        f"{tax_info}\n"
        f"Source URL: {scheme.url}"
    )
    chunks.append({
        "id": f"tax_{scheme.url.split('/')[-1]}",
        "text": tax_text,
        "metadata": {
            "scheme_name": scheme.scheme_name,
            "source_url": scheme.url,
            "chunk_type": "tax_details"
        }
    })
    
    return chunks

def index_schemes_in_vector_store(schemes: List[MutualFundScheme]):
    """
    Generates chunks for all schemes and writes them into ChromaDB.
    """
    logger.info("Starting vector database ingestion...")
    client = get_chroma_client()
    collection = get_collection(client)
    
    all_chunks = []
    for scheme in schemes:
        chunks = create_chunks(scheme)
        all_chunks.extend(chunks)
        
    if not all_chunks:
        logger.warning("No chunks generated for vector database indexing.")
        return
        
    ids = [c["id"] for c in all_chunks]
    texts = [c["text"] for c in all_chunks]
    metadatas = [c["metadata"] for c in all_chunks]
    
    logger.info(f"Ingesting {len(all_chunks)} chunks into ChromaDB collection...")
    
    # Batch upsert into Chroma
    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas
    )
    logger.info("Vector database indexing complete.")

def query_vector_store(query_text: str, n_results: int = 3, filter_dict: dict = None) -> List[Dict[str, Any]]:
    """
    Queries ChromaDB for semantic search.
    """
    client = get_chroma_client()
    collection = get_collection(client)
    
    # Prepend BGE asymmetric search query prefix if BGE model is used
    processed_query = query_text
    if "bge" in EMBEDDING_MODEL_NAME.lower():
        processed_query = f"Represent this sentence for searching relevant passages: {query_text}"
        
    kwargs = {}
    if filter_dict:
        kwargs["where"] = filter_dict
        
    results = collection.query(
        query_texts=[processed_query],
        n_results=n_results,
        **kwargs
    )
    
    formatted_results = []
    if results and "documents" in results and results["documents"]:
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        ids = results["ids"][0]
        distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
        
        for doc, meta, cid, dist in zip(docs, metas, ids, distances):
            formatted_results.append({
                "id": cid,
                "text": doc,
                "metadata": meta,
                "distance": dist
            })
            
    return formatted_results
