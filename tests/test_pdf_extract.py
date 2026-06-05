"""Tests for pdf-extract.py（视觉优先：每页 300DPI PNG 为主，文字层仅交叉校验）"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "pdf-extract.py"
SAMPLE = Path(__file__).parent / "fixtures" / "sample-checkup.pdf"


def _load_module():
    spec = importlib.util.spec_from_file_location("pdf_extract", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_no_args_shows_usage():
    """无参数应输出用法到 stderr 并以非零退出。"""
    result = subprocess.run([sys.executable, str(SCRIPT)],
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert "usage" in result.stderr.lower()


def test_extract_text_contains_known_strings(tmp_path):
    _load_module().extract_pdf(SAMPLE, tmp_path)
    text = (tmp_path / "extracted.txt").read_text()
    assert "Test Patient" in text
    assert "TG: 4.2" in text
    assert "Liver ultrasound" in text  # second page


def test_extract_text_handles_two_pages(tmp_path):
    _load_module().extract_pdf(SAMPLE, tmp_path)
    text = (tmp_path / "extracted.txt").read_text()
    assert "Page 2" in text


def test_renders_one_png_per_page_in_pages_dir(tmp_path):
    """主产物：每页一张无损 PNG，放在 pages/ 子目录。"""
    _load_module().extract_pdf(SAMPLE, tmp_path)
    pngs = sorted((tmp_path / "pages").glob("page_*.png"))
    assert len(pngs) == 2
    assert pngs[0].name == "page_001.png"
    assert pngs[1].name == "page_002.png"
    assert pngs[0].stat().st_size > 1000


def test_default_dpi_is_300_high_res(tmp_path):
    """默认 300 DPI：A4 长边应 ≥3000px（旧版 200DPI 仅 2339）。"""
    meta = _load_module().extract_pdf(SAMPLE, tmp_path)
    assert meta["dpi"] == 300
    long_edge = max(meta["page_meta"][0]["px"])
    assert long_edge >= 3000, f"长边 {long_edge} 不足，密集小字会糊"


def test_meta_marks_text_layer_and_image_only(tmp_path):
    """数字 PDF 有文字层 → image_only_pages 为空；_pdfmeta.json 落盘。"""
    meta = _load_module().extract_pdf(SAMPLE, tmp_path)
    assert (tmp_path / "_pdfmeta.json").is_file()
    on_disk = json.loads((tmp_path / "_pdfmeta.json").read_text())
    assert on_disk["image_only_pages"] == []
    assert all(p["has_text_layer"] for p in meta["page_meta"])


def test_cli_end_to_end(tmp_path):
    """命令行调用：退出码 0，主产物 PNG + meta 齐全，stdout 为 JSON。"""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(SAMPLE), str(tmp_path)],
        capture_output=True, text=True)
    assert result.returncode == 0, f"stderr: {result.stderr}"
    out = json.loads(result.stdout)
    assert out["ok"] is True and out["dpi"] == 300
    assert (tmp_path / "pages" / "page_001.png").is_file()
    assert (tmp_path / "extracted.txt").is_file()


def test_cli_missing_input(tmp_path):
    """输入文件不存在应以非零退出，stderr 含 'not found'。"""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "/nonexistent.pdf", str(tmp_path)],
        capture_output=True, text=True)
    assert result.returncode != 0
    assert "not found" in result.stderr.lower()
