import pytest
import tempfile
import os
from fpdf import FPDF

def create_test_pdf(content: str, filename: str) -> str:
    """Creates a real PDF file for testing"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    tmp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )
    pdf.output(tmp.name)
    return tmp.name

@pytest.fixture
def sample_legal_pdf():
    """Creates a real PDF with legal content"""
    content = (
        "EMPLOYMENT CONTRACT\n"
        "Position: Senior Software Engineer\n"
        "Salary: INR 15,00,000 per annum\n"
        "Notice Period: 3 months\n"
        "Non-compete clause: 1 year post employment\n"
        "Probation Period: 6 months\n"
        "Governing Law: Indian Contract Act 1872"
    )
    path = create_test_pdf(content, "employment.pdf")
    yield (path, "employment.pdf")
    os.unlink(path)

def test_document_ingestion(sample_legal_pdf):
    """Test real PDF can be ingested into pipeline"""
    from src.rag.pipeline import ingest_documents
    result = ingest_documents([sample_legal_pdf])

    assert result["documents_processed"] == 1
    assert result["chunks_created"] > 0
    assert result["vector_db"] in ["chroma", "pinecone", "faiss"]

def test_pdf_creates_searchable_chunks(sample_legal_pdf):
    """Test PDF content is chunked correctly"""
    from src.rag.pipeline import ingest_documents
    result = ingest_documents([sample_legal_pdf])
    assert result["chunks_created"] >= 1