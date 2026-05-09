"""Tests for generate-pdf.py"""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "generate-pdf.py"
SAMPLE = Path(__file__).parent / "fixtures" / "sample-member"


def test_generates_pdf_for_member(tmp_path):
    out = tmp_path / "report.pdf"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(SAMPLE), str(out)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert out.is_file()
    assert out.stat().st_size > 1000  # 非空 PDF


def test_pdf_contains_concerns_section(tmp_path):
    """生成的 PDF 必须包含 summary.md 里的"关注点"专段。"""
    import fitz  # PyMuPDF

    out = tmp_path / "report.pdf"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(SAMPLE), str(out)],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    doc = fitz.open(str(out))
    text = "".join(page.get_text() for page in doc)
    doc.close()

    assert "关注点" in text
    assert "TG" in text or "甘油三酯" in text
    # 趋势表也应被渲染
    assert "血脂趋势" in text or "趋势" in text
    # 检查记录明细应被渲染
    assert "检查记录明细" in text or "2023-06-15" in text


def test_pdf_has_no_pregnancy_terms(tmp_path):
    """family-health 生成的 PDF 不应出现孕期术语。"""
    import fitz

    out = tmp_path / "report.pdf"
    subprocess.run(
        [sys.executable, str(SCRIPT), str(SAMPLE), str(out)],
        capture_output=True, text=True, check=True
    )
    doc = fitz.open(str(out))
    text = "".join(page.get_text() for page in doc)
    doc.close()

    assert "孕期" not in text
    assert "产检" not in text
    assert "预产期" not in text
