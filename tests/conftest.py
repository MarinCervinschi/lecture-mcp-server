import base64

import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Generate a simple PDF for testing."""
    from io import BytesIO

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Page 1
    c.drawString(100, 750, "Test PDF Document")
    c.drawString(100, 700, "This is a test lecture about Python programming.")
    c.drawString(100, 650, "Page 1 contains basic information.")
    c.showPage()

    # Page 2
    c.drawString(100, 750, "Advanced Topics")
    c.drawString(100, 700, "This page discusses advanced concepts.")
    c.drawString(100, 650, "Including async/await and type hints.")
    c.showPage()

    c.save()
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def sample_pdf_base64(sample_pdf_bytes: bytes) -> str:
    """Generate base64 encoded PDF."""
    return base64.b64encode(sample_pdf_bytes).decode("utf-8")


@pytest.fixture
def invalid_pdf_base64() -> str:
    """Generate invalid base64 that's not a PDF."""
    return base64.b64encode(b"This is not a PDF").decode("utf-8")


@pytest.fixture
def corrupted_base64() -> str:
    """Generate corrupted base64 string."""
    return "not_valid_base64!@#$"
