"""Tests for preprocess-image.py（拍照件预处理：体检 / 矫正增强 / 裁剪）"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "preprocess-image.py"

pytest.importorskip("PIL")
pytest.importorskip("numpy")
from PIL import Image, ImageDraw  # noqa: E402


def _make_report_img(path, w, h):
    """造一张带黑色文字行的"报告"图，边缘锐利（高拉普拉斯方差）。"""
    im = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(im)
    for i in range(8):
        y = 40 + i * (h // 12)
        d.text((30, y), f"{i+1}  WBC {6.5+i}  10^9/L  3.50-9.50", fill="black")
        d.line((20, y - 6, w - 20, y - 6), fill="black", width=2)
    im.save(path)
    return path


def _run(*args):
    r = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                       capture_output=True, text=True)
    return r


def test_probe_outputs_required_keys(tmp_path):
    img = _make_report_img(tmp_path / "big.png", 2600, 1800)
    r = _run(img, "--probe")
    assert r.returncode == 0, r.stderr
    j = json.loads(r.stdout)
    for k in ("width", "height", "long_edge", "blur_var", "low_res", "blurry", "ok", "advice"):
        assert k in j


def test_probe_flags_low_res(tmp_path):
    """小图应判 low_res 且 ok=false，并给重拍建议。"""
    img = _make_report_img(tmp_path / "small.png", 600, 400)
    j = json.loads(_run(img, "--probe").stdout)
    assert j["low_res"] is True
    assert j["ok"] is False
    assert any("分辨率" in a for a in j["advice"])


def test_probe_passes_hires_sharp(tmp_path):
    """高清锐利图应 ok=true。"""
    img = _make_report_img(tmp_path / "big.png", 2600, 1800)
    j = json.loads(_run(img, "--probe").stdout)
    assert j["low_res"] is False
    assert j["ok"] is True


def test_process_upsamples_small_image(tmp_path):
    """低清图经处理应升采样到长边 ≥ 默认 3000。"""
    img = _make_report_img(tmp_path / "small.png", 800, 600)
    out = tmp_path / "out.png"
    r = _run(img, out)
    assert r.returncode == 0, r.stderr
    assert out.is_file()
    assert max(Image.open(out).size) >= 3000


def test_rotate_90_swaps_orientation(tmp_path):
    """--rotate 90 应把横图转成竖图（高>宽）。"""
    img = _make_report_img(tmp_path / "wide.png", 2000, 1000)
    out = tmp_path / "rot.png"
    r = _run(img, out, "--rotate", "90", "--no-deskew")
    assert r.returncode == 0, r.stderr
    w, h = Image.open(out).size
    assert h > w


def test_crop_region(tmp_path):
    """--crop 取右半再放大 → 纵横比应比全图更窄长（证明确实只取了子区域）。"""
    img = _make_report_img(tmp_path / "f.png", 2400, 1600)
    full = tmp_path / "full.png"
    crop = tmp_path / "crop.png"
    _run(img, full, "--no-deskew")
    _run(img, crop, "--no-deskew", "--crop", "0.5,0.0,1.0,1.0")
    fw, fh = Image.open(full).size
    cw, ch = Image.open(crop).size
    assert cw / ch < fw / fh


def test_missing_input_errors(tmp_path):
    r = _run("/nonexistent.png", "--probe")
    assert r.returncode != 0
