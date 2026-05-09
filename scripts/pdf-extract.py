#!/usr/bin/env python3
"""
Extract text and per-page images from a PDF for the family-health skill.

Usage:
    python3 pdf-extract.py <input_pdf> <output_dir>

Example:
    python3 pdf-extract.py checkup_2024.pdf family-health/members/姈姈/reports/2024-09-15/

Output:
    output_dir/
    ├── extracted.txt        ← 全文文字提取
    ├── page_001.jpg         ← 每页一张高清图（视觉读图兜底）
    ├── page_002.jpg
    └── ...

Dependencies:
    pip3 install pymupdf
"""

import sys
from pathlib import Path


def check_dependencies():
    missing = []
    try:
        import fitz  # noqa: F401
    except ImportError:
        missing.append("pymupdf")
    return missing


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: python3 pdf-extract.py <input_pdf> <output_dir>",
            file=sys.stderr,
        )
        sys.exit(2)

    missing = check_dependencies()
    if missing:
        print(
            f"Missing dependencies: {', '.join(missing)}\n"
            f"Install: pip3 install {' '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(3)

    input_pdf = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not input_pdf.is_file():
        print(f"Input not found: {input_pdf}", file=sys.stderr)
        sys.exit(4)

    output_dir.mkdir(parents=True, exist_ok=True)

    extract_pdf(input_pdf, output_dir)


def extract_pdf(input_pdf: Path, output_dir: Path):
    """Extract text and per-page JPG images from PDF."""
    import fitz

    doc = fitz.open(str(input_pdf))
    text_parts = []
    for page_num, page in enumerate(doc, start=1):
        page_text = page.get_text()
        text_parts.append(f"=== Page {page_num} ===\n{page_text}")

        pix = page.get_pixmap(dpi=200)
        jpg_path = output_dir / f"page_{page_num:03d}.jpg"
        pix.save(str(jpg_path), "jpeg")

    doc.close()

    text_file = output_dir / "extracted.txt"
    text_file.write_text("\n".join(text_parts), encoding="utf-8")


if __name__ == "__main__":
    main()
