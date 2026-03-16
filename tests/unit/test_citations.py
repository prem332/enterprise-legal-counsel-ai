import pytest
from unittest.mock import MagicMock
from src.rag.citations import (
    extract_citations,
    format_citations,
    format_legal_disclaimer
)

def test_citation_extraction():
    """Test basic citation extraction from document"""
    mock_doc = MagicMock()
    mock_doc.metadata = {
        "source": "employment_contract.pdf",
        "page": 3
    }
    mock_doc.page_content = "Notice period shall be 3 months from date of resignation"

    citations = extract_citations([(mock_doc, 0.92)])

    assert len(citations) == 1
    assert citations[0].document_name == "employment_contract.pdf"
    assert citations[0].page_number == 3
    assert citations[0].relevance_score == 0.92

def test_empty_citations():
    """Test handling of empty document list"""
    citations = extract_citations([])
    assert citations == []

def test_citation_text_truncation():
    """Test that chunk text is truncated to 200 chars"""
    mock_doc = MagicMock()
    mock_doc.metadata = {"source": "test.pdf", "page": 1}
    mock_doc.page_content = "A" * 300

    citations = extract_citations([(mock_doc, 0.85)])
    assert len(citations[0].chunk_text) <= 204

def test_missing_metadata():
    """Test graceful handling of missing metadata"""
    mock_doc = MagicMock()
    mock_doc.metadata = {}
    mock_doc.page_content = "Some legal text here"

    citations = extract_citations([(mock_doc, 0.75)])

    assert citations[0].document_name == "Unknown"
    assert citations[0].page_number == 0

def test_format_citations():
    """Test citation formatting output"""
    mock_doc = MagicMock()
    mock_doc.metadata = {"source": "nda.pdf", "page": 2}
    mock_doc.page_content = "Confidentiality clause text"

    citations = extract_citations([(mock_doc, 0.88)])
    formatted = format_citations(citations)

    assert "nda.pdf" in formatted
    assert "Page 2" in formatted
    assert "0.88" in formatted

def test_empty_citations_message():
    """Test message shown when no citations found"""
    formatted = format_citations([])
    assert "No specific document sources" in formatted

def test_legal_disclaimer():
    """Test legal disclaimer is present"""
    disclaimer = format_legal_disclaimer()
    assert "NOT legal advice" in disclaimer
    assert "qualified lawyer" in disclaimer