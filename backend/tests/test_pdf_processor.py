import pytest
from unittest.mock import patch, MagicMock, call
import os
from pathlib import Path
from app.services import pdf_processor

def test_clean_markdown_thai():
    raw = "test \u200b\u200c text"
    cleaned = pdf_processor.clean_markdown_thai(raw)
    assert cleaned == "test text"

def test_evaluate_markdown_quality():
    md = "# Header\n\nSome text here\n| col1 | col2 |\n|---|---|\n| val1 | val2 |\n\n$E=mc^2$"
    metrics = pdf_processor.evaluate_markdown_quality(md)
    assert metrics["word_count"] > 0
    assert metrics["header_presence"] is True
    assert metrics["table_presence"] is True
    assert metrics["formula_presence"] is True
    assert metrics["avg_line_length"] > 0

@patch("app.services.pdf_processor.fitz.open")
def test_determine_pdf_type_scanned(mock_fitz_open):
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "   "
    mock_page.get_images.return_value = []
    mock_doc.__getitem__.return_value = mock_page
    mock_fitz_open.return_value.__enter__.return_value = mock_doc
    
    pdf_type = pdf_processor._determine_pdf_type("test.pdf")
    assert pdf_type == "scanned"

@patch("app.services.pdf_processor.fitz.open")
def test_determine_pdf_type_image_heavy(mock_fitz_open):
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "this is a very long string that is definitely more than fifty characters long"
    mock_page.get_images.return_value = [1, 2, 3] # More than 2
    mock_doc.__getitem__.return_value = mock_page
    mock_fitz_open.return_value.__enter__.return_value = mock_doc
    
    pdf_type = pdf_processor._determine_pdf_type("test.pdf")
    assert pdf_type == "image_heavy"

@patch("app.services.pdf_processor.fitz.open")
def test_determine_pdf_type_digital(mock_fitz_open):
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "this is a very long string that is definitely more than fifty characters long"
    mock_page.get_images.return_value = [1] # <= 2
    mock_doc.__getitem__.return_value = mock_page
    mock_fitz_open.return_value.__enter__.return_value = mock_doc
    
    pdf_type = pdf_processor._determine_pdf_type("test.pdf")
    assert pdf_type == "digital"

@patch("app.services.pdf_processor.DocumentConverter")
def test_process_scanned_pdf(mock_docling):
    mock_conv = MagicMock()
    mock_docling.return_value = mock_conv
    mock_conv.convert.return_value.document.export_to_markdown.return_value = "scanned md"
    
    res = pdf_processor._process_scanned_pdf("test.pdf")
    assert res == "scanned md"

@patch.dict("sys.modules", {"pymupdf4llm": MagicMock(to_markdown=MagicMock(return_value="digital md"))})
def test_process_digital_pdf():
    res = pdf_processor._process_digital_pdf("test.pdf")
    assert res == "digital md"

@patch("app.services.pdf_processor.DocumentConverter")
def test_process_general_document(mock_docling):
    mock_conv = MagicMock()
    mock_docling.return_value = mock_conv
    mock_conv.convert.return_value.document.export_to_markdown.return_value = "general md"
    
    res = pdf_processor._process_general_document("test.txt")
    assert res == "general md"

@patch("app.services.pdf_processor.Path.exists")
@patch("app.services.pdf_processor.Path.mkdir")
@patch("app.services.pdf_processor._determine_pdf_type")
@patch("app.services.pdf_processor._process_digital_pdf")
@patch("builtins.open")
def test_process_file_success(mock_open, mock_process_digital, mock_determine, mock_mkdir, mock_exists):
    # Setup Path exists
    def exists_side_effect():
        # First call is for input file (return True)
        # Second call is for output file (return False)
        if mock_exists.call_count == 1:
            return True
        return False
    mock_exists.side_effect = exists_side_effect
    
    mock_determine.return_value = "digital"
    mock_process_digital.return_value = "markdown content"
    
    res = pdf_processor.process_file("test.pdf", "out_dir")
    
    assert res.endswith("test.md")
    mock_open.assert_called_once()
    mock_process_digital.assert_called_once_with("test.pdf")

@patch("app.services.pdf_processor.Path.exists")
def test_process_file_not_found(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError):
        pdf_processor.process_file("not_found.pdf", "out_dir")

@patch("app.services.pdf_processor.Path.iterdir")
@patch("app.services.pdf_processor.process_file")
def test_process_folder(mock_process_file, mock_iterdir):
    mock_file1 = MagicMock()
    mock_file1.is_file.return_value = True
    mock_file1.suffix = ".pdf"
    mock_file1.__str__.return_value = "test1.pdf"
    
    mock_file2 = MagicMock()
    mock_file2.is_file.return_value = True
    mock_file2.suffix = ".txt"
    mock_file2.__str__.return_value = "test2.txt"
    
    mock_iterdir.return_value = [mock_file1, mock_file2]
    
    mock_process_file.side_effect = ["out/test1.md", Exception("Failed")]
    
    results = pdf_processor.process_folder("in_dir", "out_dir")
    
    assert "test1.pdf" in results
    assert results["test1.pdf"] == "out/test1.md"
    assert "test2.txt" in results
    assert "Error: Failed" in results["test2.txt"]
