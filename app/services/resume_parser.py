import re
from io import BytesIO
from pathlib import Path
import re
import pdfplumber
import pymupdf
import pytesseract
from PIL import Image
from docx import Document


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def needs_ocr(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        return True

    first_line_words = re.findall(r"[A-Za-z]{2,}", lines[0])

    return len(first_line_words) < 2


def extract_text(file_content: bytes, filename: str) -> str:
    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        with pdfplumber.open(BytesIO(file_content)) as pdf:
            text = "\n".join(
                page.extract_text(
                    x_tolerance=2,
                    y_tolerance=3,
                    layout=False
                ) or ""
                for page in pdf.pages
            )

        if needs_ocr(text):
            document = pymupdf.open(
                stream=file_content,
                filetype="pdf"
            )

            ocr_text = []

            for page in document:
                pix = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False
                )

                image = Image.frombytes(
                    "RGB",
                    [pix.width, pix.height],
                    pix.samples
                )

                page_text = pytesseract.image_to_string(
                    image,
                    lang="eng"
                )

                ocr_text.append(page_text)

            document.close()

            extracted_ocr_text = "\n".join(ocr_text)

            if extracted_ocr_text.strip():
                text = extracted_ocr_text

    elif extension == ".docx":
        document = Document(BytesIO(file_content))
        text = "\n".join(
            paragraph.text for paragraph in document.paragraphs
        )

    else:
        raise ValueError("Only PDF and DOCX files are supported")
    text = re.sub(r"\bAl(?=[\s-])", "AI", text)
    if not text.strip():
        raise ValueError("No readable text found in the resume")

    return text
