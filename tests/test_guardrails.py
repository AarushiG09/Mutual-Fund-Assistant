import pytest
from src.services.guardrails import count_sentences, extract_urls, check_compliance, enforce_guardrails
from src.services.llm import LLMClient

def test_count_sentences():
    assert count_sentences("One sentence. Two sentences!") == 2
    assert count_sentences("This is [Mid Cap Fund](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth) page. It's direct growth. Third sentence.") == 3
    assert count_sentences("") == 0
    assert count_sentences("The minimum investment is Rs. 100. The fund is HDFC Mid Cap.") == 2
    assert count_sentences("He has managed funds for 20 years, e.g. at HDFC. This is the second sentence.") == 2

def test_extract_urls():
    text = "Check the fund at https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth."
    assert extract_urls(text) == ["https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"]
    
    text_two = "Links: https://google.com and https://yahoo.com"
    assert len(extract_urls(text_two)) == 2

def test_check_compliance_valid():
    text = (
        "HDFC Mid Cap Fund has an expense ratio of 0.73%. "
        "The minimum SIP amount is 100. "
        "Source: https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
    )
    errors = check_compliance(text, "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth")
    assert len(errors) == 0

def test_check_compliance_violations():
    # 1. Too many sentences
    text_long = "One. Two. Three. Four. Source: https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
    errors = check_compliance(text_long, "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth")
    assert any("exceeds maximum sentence limit" in err for err in errors)
    
    # 2. Wrong URL
    text_url = "The exit load is 1%. Source: https://invalid-url.com"
    errors_url = check_compliance(text_url, "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth")
    assert any("authorized Groww URLs" in err or "not in the list" in err for err in errors_url)
    
    # 3. Prohibited terms
    text_adv = (
        "I highly recommend HDFC Mid Cap Fund. "
        "It is a good choice for investors. "
        "Source: https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
    )
    errors_adv = check_compliance(text_adv, "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth")
    assert any("prohibited investment advice" in err for err in errors_adv)

def test_enforce_guardrails_failsafe_fallback():
    mock_client = LLMClient(provider="mock")
    context = "Scheme Name: HDFC Test Fund\nFactual Details: NAV is ₹50.\nSource URL: https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth"
    expected_url = "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth"
    
    # Initial answer violates sentences count and contains bad advice
    initial_answer = "One. Two. Three. Four. I highly recommend HDFC Defence Fund. Link: https://invalid.com"
    
    # Executing guardrail should reject initial and mock repair, falling back to database facts
    final_ans = enforce_guardrails(
        query="Tell me about test fund",
        initial_answer=initial_answer,
        expected_url=expected_url,
        context=context,
        client=mock_client
    )
    
    assert "Factual details retrieved: Scheme Name: HDFC Test Fund Factual Details: NAV is ₹50." in final_ans
    assert f"Source: {expected_url}" in final_ans
