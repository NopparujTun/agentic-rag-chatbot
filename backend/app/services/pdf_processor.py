"""PDF processing module for document ingestion.

Handles conversion of PDFs into Markdown using various tools depending on document complexity.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

import fitz
import pythainlp.util
from docling.document_converter import DocumentConverter

logger = logging.getLogger(__name__)

PDF_TYPE_SCANNED = 'scanned'
PDF_TYPE_IMAGE_HEAVY = 'image_heavy'
PDF_TYPE_DIGITAL = 'digital'
TARGET_DPI = 300
POINTS_PER_INCH = 72
IMAGE_SCALE_FACTOR = 2.0

SYSTEM_PROMPT = """You are an expert document parser specializing in converting PDF pages to markdown format.

**Your task:**
Extract ALL content from the provided page image and return it as clean, well-structured markdown.

**Text Extraction Rules:**
1. Preserve the EXACT text as written (including typos, formatting, special characters)
2. Maintain the logical reading order (top-to-bottom, left-to-right)
3. Preserve hierarchical structure using appropriate markdown headers (#, ##, ###)
4. Keep paragraph breaks and line spacing as they appear
5. Use markdown lists (-, *, 1.) for bullet points and numbered lists
6. Preserve text emphasis: **bold**, *italic*, `code`
7. For multi-column layouts, extract left column first, then right column

**Tables:**
- Convert all tables to markdown table format
- Preserve column alignment and structure
- Use | for columns and - for headers

**Mathematical Formulas:**
- Convert to LaTeX format: inline `$formula$`, display `$$formula$$`
- If LaTeX conversion is uncertain, describe the formula clearly

**Images, Diagrams, Charts:**
- Insert markdown image placeholder: `![Description](image)`
- Provide a detailed, informative description including:
  * Type of visual (photo, diagram, chart, graph, illustration)
  * Main subject or purpose
  * Key elements, labels, or data points
  * Colors, patterns, or notable visual features
  * Context or relationship to surrounding text
- For charts/graphs: mention axes, data trends, and key values
- For diagrams: describe components and their relationships

**Special Elements:**
- Footnotes: Use markdown footnote syntax `[^1]`
- Citations: Preserve as written
- Code blocks: Use triple backticks with language specification
- Quotes: Use `>` for blockquotes
- Links: Preserve as `[text](url)` if visible

**Quality Guidelines:**
- DO NOT add explanations, comments, or meta-information
- DO NOT skip or summarize content
- DO NOT invent or hallucinate text not present in the image
- DO NOT include "Here is the markdown..." or similar preambles
- Output ONLY the markdown content, nothing else

**Output Format:**
Return raw markdown with no wrapper, no code blocks, no explanations.
Start immediately with the page content.
"""


def clean_markdown_thai(markdown_text: str) -> str:
    """Fix common spacing artifacts produced by PDF text extraction.

    Args:
        markdown_text: The markdown string to clean.

    Returns:
        The cleaned markdown string.
    """
    cleaned_text = markdown_text.replace('\u200b', '').replace('\u200c', '')
    cleaned_text = pythainlp.util.normalize(cleaned_text)
    return cleaned_text


def evaluate_markdown_quality(markdown_text: str) -> Dict[str, Any]:
    """Validate output markdown quality and return metrics.

    Args:
        markdown_text: The generated markdown text.

    Returns:
        A dictionary containing validation metrics like word count and formatting presence.
    """
    word_count = len(markdown_text.split())
    has_headers = "#" in markdown_text
    has_tables = "|" in markdown_text and "-|-" in markdown_text.replace(" ", "")
    has_formulas = "$" in markdown_text or "\\(" in markdown_text or "\\[" in markdown_text

    text_lines = markdown_text.split('\n')
    average_line_length = sum(len(line) for line in text_lines) / len(text_lines) if text_lines else 0

    return {
        "word_count": word_count,
        "header_presence": has_headers,
        "table_presence": has_tables,
        "formula_presence": has_formulas,
        "avg_line_length": round(average_line_length, 2)
    }


def convert_complex_pdfs_vlm(pdf_path: str, api_key: str, model_name: str = "gemini-2.5-flash") -> str:
    """Convert an image-heavy PDF using the Gemini Vision-Language Model.

    Args:
        pdf_path: Path to the complex PDF file.
        api_key: The Google API key.
        model_name: The Gemini model to use.

    Returns:
        The extracted markdown string.
    """
    from google import genai

    gemini_client = genai.Client(api_key=api_key)
    markdown_pages = {}

    with fitz.open(pdf_path) as pdf_document:
        for page_index in range(pdf_document.page_count):
            _process_single_page_vlm(
                pdf_document, page_index, gemini_client, model_name, markdown_pages
            )

    combined_markdown = "\n\n---\n\n".join([
        f"# Page {page_number}\n\n{content}"
        for page_number, content in markdown_pages.items()
    ])

    return combined_markdown


def _process_single_page_vlm(
    pdf_document: fitz.Document,
    page_index: int,
    gemini_client: Any,
    model_name: str,
    markdown_pages: Dict[int, str]
) -> None:
    """Helper to process a single PDF page using VLM.

    Args:
        pdf_document: The opened fitz document.
        page_index: Zero-based page index.
        gemini_client: GenAI client.
        model_name: GenAI model name.
        markdown_pages: Dictionary to store the result.
    """
    from google.genai import types

    page_number = page_index + 1
    try:
        pdf_page = pdf_document[page_index]
        matrix_scale = TARGET_DPI / POINTS_PER_INCH
        page_pixmap = pdf_page.get_pixmap(matrix=fitz.Matrix(matrix_scale, matrix_scale))
        image_bytes = page_pixmap.tobytes("png")

        part_image = types.Part.from_bytes(data=image_bytes, mime_type="image/png")

        prompt_text = (
            "Convert this PDF page to clean, structured markdown. "
            "Extract all text, describe images, and preserve the layout."
        )

        generation_config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1
        )

        response = gemini_client.models.generate_content(
            config=generation_config,
            model=model_name,
            contents=[prompt_text, part_image],
        )

        markdown_pages[page_number] = response.text
        logger.info(f"Processed page {page_number}/{pdf_document.page_count} with VLM")

    except Exception as exception:
        logger.error(f"Error on page {page_number}: {exception}")
        markdown_pages[page_number] = f"<!-- Error processing page: {exception} -->"


def _determine_pdf_type(file_path: str) -> str:
    """Determine the type of PDF (scanned, image-heavy, or digital).

    Args:
        file_path: Path to the PDF file.

    Returns:
        A string indicating the type: 'scanned', 'image_heavy', or 'digital'.
    """
    with fitz.open(file_path) as pdf_document:
        sample_page = pdf_document[0]

        extracted_text = sample_page.get_text()
        is_scanned = len(extracted_text.strip()) < 50

        image_count = len(sample_page.get_images())
        has_many_images = image_count > 2

    if is_scanned:
        return PDF_TYPE_SCANNED
    if has_many_images:
        return PDF_TYPE_IMAGE_HEAVY
    return PDF_TYPE_DIGITAL


def _process_scanned_pdf(file_path: str) -> str:
    """Process a scanned PDF using Docling with OCR enabled.

    Args:
        file_path: Path to the scanned PDF.

    Returns:
        The extracted markdown string.
    """
    logger.info("→ Using Docling (scanned document)")
    from docling.document_converter import PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_table_structure = True
    pipeline_options.do_ocr = True
    pipeline_options.images_scale = 2.0
    pipeline_options.generate_picture_images = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    conversion_result = converter.convert(file_path)
    return conversion_result.document.export_to_markdown()


def _process_digital_pdf(file_path: str) -> str:
    """Process a digital PDF using PyMuPDF4LLM.

    Args:
        file_path: Path to the digital PDF.

    Returns:
        The extracted markdown string.
    """
    logger.info("→ Using PyMuPDF4LLM (simple digital PDF)")
    import pymupdf4llm
    return pymupdf4llm.to_markdown(file_path)


def _process_general_document(file_path: str) -> str:
    """Process non-PDF documents using Docling.

    Args:
        file_path: Path to the document.

    Returns:
        The extracted markdown string.
    """
    logger.info("Using Docling for general document conversion")
    converter = DocumentConverter()
    conversion_result = converter.convert(file_path)
    return conversion_result.document.export_to_markdown()


def process_file(file_path: str, output_dir: str, api_key: Optional[str] = None) -> str:
    """Process a file into Markdown based on its characteristics.

    Args:
        file_path: Path to the input file.
        output_dir: Directory to save the output markdown.
        api_key: Optional Google API key for VLM processing.

    Returns:
        The path to the saved markdown file.

    Raises:
        FileNotFoundError: If the input file does not exist.
        RuntimeError: If document conversion fails.
    """
    path_object = Path(file_path)
    if not path_object.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_name = path_object.stem
    out_dir_object = Path(output_dir)
    out_dir_object.mkdir(parents=True, exist_ok=True)

    output_file_path = out_dir_object / f"{file_name}.md"

    if output_file_path.exists():
        logger.info(f"Skipping {file_path}, already processed. Output exists at {output_file_path}.")
        return str(output_file_path)

    logger.info(f"Processing file: {file_path}")

    try:
        if file_path.lower().endswith(".pdf"):
            pdf_type = _determine_pdf_type(file_path)
            active_api_key = api_key or os.environ.get("GOOGLE_API_KEY")

            if pdf_type == PDF_TYPE_SCANNED:
                markdown_text = _process_scanned_pdf(file_path)
            elif pdf_type == PDF_TYPE_IMAGE_HEAVY and active_api_key:
                logger.info("→ Using VLM (image-heavy)")
                markdown_text = convert_complex_pdfs_vlm(file_path, active_api_key)
            else:
                markdown_text = _process_digital_pdf(file_path)
        else:
            markdown_text = _process_general_document(file_path)

    except Exception as exception:
        logger.error(f"Document pipeline failed for {file_path}: {exception}")
        raise RuntimeError(f"Pipeline failed: {exception}") from exception

    cleaned_markdown = clean_markdown_thai(markdown_text)

    with open(output_file_path, "w", encoding="utf-8") as file_handle:
        file_handle.write(cleaned_markdown)

    logger.info(f"Output successfully saved to {output_file_path}")

    validation_metrics = evaluate_markdown_quality(cleaned_markdown)
    logger.info(f"Validation metrics for {file_name}: {validation_metrics}")

    return str(output_file_path)


def process_folder(input_directory: str, output_directory: str, api_key: Optional[str] = None) -> Dict[str, str]:
    """Batch process a folder of documents.

    Args:
        input_directory: Path to the folder containing input documents.
        output_directory: Path to save the processed markdown files.
        api_key: Optional Google API key.

    Returns:
        A dictionary mapping input file paths to output file paths or error messages.
    """
    input_path_object = Path(input_directory)
    processing_results = {}

    for input_file in input_path_object.iterdir():
        if input_file.is_file() and input_file.suffix.lower() in ['.pdf', '.docx', '.txt']:
            try:
                output_path = process_file(str(input_file), output_directory, api_key)
                processing_results[str(input_file)] = output_path
            except Exception as exception:
                logger.error(f"Failed to process {input_file}: {exception}")
                processing_results[str(input_file)] = f"Error: {exception}"

    return processing_results
