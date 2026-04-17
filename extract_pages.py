from pathlib import Path
import fitz  # PyMuPDF
from page_classifier import classify_page

ROOT_FOLDER = Path("classes")
OUTPUT_FOLDER = Path("rendered_pages")


def render_pdf_to_images(pdf_path: Path, output_dir: Path, zoom: float = 2.0):
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    matrix = fitz.Matrix(zoom, zoom)

    for page_index, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        image_path = output_dir / f"page_{page_index}.png"
        pix.save(str(image_path))


def extract_text_pages(pdf_path: Path):
    doc = fitz.open(pdf_path)
    pages = []

    for page in doc:
        text = page.get_text("text") or ""
        pages.append(text)

    return pages

def main():
    pdf_files = list(ROOT_FOLDER.rglob("*.pdf"))

    if not pdf_files:
        print(f"No PDFs found in: {ROOT_FOLDER}")
        return

    for pdf_file in pdf_files:
        relative_path = pdf_file.relative_to(ROOT_FOLDER)
        target_dir = OUTPUT_FOLDER / relative_path.with_suffix("")

        print(f"\nProcessing: {pdf_file}")

        # 1. Render images
        render_pdf_to_images(pdf_file, target_dir)

        # 2. Extract text (light)
        pages_text = extract_text_pages(pdf_file)

        # 3. Classify pages
        for page_num, text in enumerate(pages_text, start=1):
            page_type = classify_page(text)
            print(f"Page {page_num}: {page_type}")

if __name__ == "__main__":
    main()
    