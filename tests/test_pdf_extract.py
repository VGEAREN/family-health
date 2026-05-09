"""Tests for pdf-extract.py"""
import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "pdf-extract.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("pdf_extract", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_no_args_shows_usage():
    """无参数应输出用法到 stderr 并以非零退出。"""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "Usage" in result.stderr or "usage" in result.stderr


def test_extract_text_contains_known_strings(tmp_path):
    pdf_extract = _load_module()
    sample = Path(__file__).parent / "fixtures" / "sample-checkup.pdf"
    pdf_extract.extract_pdf(sample, tmp_path)

    text_file = tmp_path / "extracted.txt"
    assert text_file.exists()
    text = text_file.read_text()
    assert "Test Patient" in text
    assert "TG: 4.2" in text
    assert "Liver ultrasound" in text  # second page


def test_extract_text_handles_two_pages(tmp_path):
    pdf_extract = _load_module()
    sample = Path(__file__).parent / "fixtures" / "sample-checkup.pdf"
    pdf_extract.extract_pdf(sample, tmp_path)

    text = (tmp_path / "extracted.txt").read_text()
    assert "Page 2" in text


def test_extract_writes_one_jpg_per_page(tmp_path):
    pdf_extract = _load_module()
    sample = Path(__file__).parent / "fixtures" / "sample-checkup.pdf"
    pdf_extract.extract_pdf(sample, tmp_path)

    jpgs = sorted(tmp_path.glob("page_*.jpg"))
    assert len(jpgs) == 2
    assert jpgs[0].name == "page_001.jpg"
    assert jpgs[1].name == "page_002.jpg"
    assert jpgs[0].stat().st_size > 1000


def test_cli_end_to_end(tmp_path):
    """走完整命令行调用，验证 stdout/stderr/退出码/输出文件。"""
    sample = Path(__file__).parent / "fixtures" / "sample-checkup.pdf"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(sample), str(tmp_path)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert (tmp_path / "extracted.txt").is_file()
    assert (tmp_path / "page_001.jpg").is_file()


def test_cli_missing_input(tmp_path):
    """输入文件不存在应以非零退出，stderr 给出清晰原因。"""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "/nonexistent.pdf", str(tmp_path)],
        capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "not found" in result.stderr.lower()
