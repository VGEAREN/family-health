#!/usr/bin/env python3
"""
Generate a comprehensive family-health PDF report for one member.

Usage:
    python3 generate-pdf.py <member_dir> [output_path]

Example:
    python3 generate-pdf.py family-health/members/姈姈/
    python3 generate-pdf.py family-health/members/姈姈/ family-health/members/姈姈/健康综合报告_20260101.pdf

Reads:
    <member_dir>/profile.md    — basic info + concerns list
    <member_dir>/summary.md    — trends + concerns section + diagnosis timeline
    <member_dir>/records/*.md  — all structured reports

Dependencies:
    pip3 install reportlab
"""

import sys
import os
import re
from datetime import date
from pathlib import Path


def check_dependencies():
    try:
        import reportlab  # noqa: F401
    except ImportError:
        print("Error: Missing dependency: reportlab")
        print("Install with: pip3 install reportlab")
        sys.exit(1)


def parse_markdown_table(text):
    """Parse a Markdown table into a list of dicts."""
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    if len(lines) < 2:
        return []

    header_line = None
    data_start = 0
    for i, line in enumerate(lines):
        if "|" in line and set(line.replace("|", "").replace("-", "").replace(":", "").strip()) == set():
            if i > 0:
                header_line = lines[i - 1]
                data_start = i + 1
            break

    if header_line is None and len(lines) >= 2:
        header_line = lines[0]
        data_start = 2

    if header_line is None:
        return []

    headers = [h.strip() for h in header_line.split("|") if h.strip()]
    rows = []
    for line in lines[data_start:]:
        cols = [c.strip() for c in line.split("|") if c.strip()]
        if cols:
            row = {}
            for j, h in enumerate(headers):
                row[h] = cols[j] if j < len(cols) else ""
            rows.append(row)

    return rows


def read_file(path):
    """Read a file and return its content, or empty string if not found."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def extract_profile(content):
    """Extract key-value pairs from profile.md."""
    info = {}
    for line in content.split("\n"):
        match = re.match(r"^-\s*(.+?)：(.+)$", line.strip())
        if match:
            info[match.group(1).strip()] = match.group(2).strip()
    return info


def extract_sections(content):
    """Split Markdown content into sections by ## headings."""
    sections = {}
    current_title = None
    current_lines = []
    for line in content.split("\n"):
        match = re.match(r"^##\s+(.+)$", line)
        if match:
            if current_title:
                sections[current_title] = "\n".join(current_lines)
            current_title = match.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_title:
        sections[current_title] = "\n".join(current_lines)
    return sections


def split_h3_subsections(content):
    """Split a section's content by ### headings, returning [(title, body), ...]."""
    subs = []
    current_title = None
    current_lines = []
    for line in content.split("\n"):
        match = re.match(r"^###\s+(.+)$", line)
        if match:
            if current_title is not None:
                subs.append((current_title, "\n".join(current_lines)))
            current_title = match.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_title is not None:
        subs.append((current_title, "\n".join(current_lines)))
    return subs


def _make_table(rows, chinese_font, header_color):
    """Build a reportlab Table from list-of-dicts rows."""
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle

    headers = list(rows[0].keys())
    table_data = [headers]
    for row in rows:
        table_data.append([row.get(h, "") for h in headers])

    t = Table(table_data, repeatRows=1)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), chinese_font),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_color)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#ecf0f1")]),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def generate_pdf(member_dir, output_path):
    """Generate the PDF report for a single member."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak,
    )
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    chinese_font = "Helvetica"
    chinese_font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for font_path in chinese_font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont("ChineseFont", font_path, subfontIndex=0))
                chinese_font = "ChineseFont"
                break
            except Exception:
                continue

    profile_content = read_file(os.path.join(member_dir, "profile.md"))
    summary_content = read_file(os.path.join(member_dir, "summary.md"))
    profile = extract_profile(profile_content)
    summary_sections = extract_sections(summary_content)

    records_dir = os.path.join(member_dir, "records")
    record_files = sorted(Path(records_dir).glob("*.md")) if os.path.isdir(records_dir) else []

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=25 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "ChTitle", fontName=chinese_font, fontSize=22, leading=30,
        alignment=1, spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        "ChH2", fontName=chinese_font, fontSize=16, leading=22,
        spaceAfter=10, spaceBefore=15, textColor=colors.HexColor("#2c3e50")
    ))
    styles.add(ParagraphStyle(
        "ChH3", fontName=chinese_font, fontSize=12, leading=18,
        spaceAfter=8, spaceBefore=10, textColor=colors.HexColor("#34495e")
    ))
    styles.add(ParagraphStyle(
        "ChBody", fontName=chinese_font, fontSize=10, leading=16, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        "ChSmall", fontName=chinese_font, fontSize=8, leading=12,
        textColor=colors.grey
    ))

    story = []

    # Cover
    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph("家人健康检查综合报告", styles["ChTitle"]))
    story.append(Spacer(1, 10 * mm))

    today = date.today().strftime("%Y-%m-%d")
    cover_info = [
        f"姓名：{profile.get('姓名', profile.get('真名', '-'))}",
        f"年龄：{profile.get('年龄', '-')}",
        f"性别：{profile.get('性别', '-')}",
        f"报告生成日期：{today}",
        f"检查记录数：{len(record_files)} 份",
    ]
    for line in cover_info:
        story.append(Paragraph(line, styles["ChBody"]))

    story.append(PageBreak())

    # Concerns section（关注点专段）— rendered first because it's the priority
    if "关注点" in summary_sections:
        story.append(Paragraph("关注点", styles["ChTitle"]))
        for h3_title, h3_body in split_h3_subsections(summary_sections["关注点"]):
            story.append(Paragraph(h3_title, styles["ChH3"]))
            rows = parse_markdown_table(h3_body)
            if rows:
                story.append(_make_table(rows, chinese_font, "#e67e22"))
                story.append(Spacer(1, 3 * mm))
            # 也渲染表格之外的 plain text（如建议、备注）
            for line in h3_body.split("\n"):
                line = line.strip()
                if not line or line.startswith("|") or line.startswith("-|"):
                    continue
                # 跳过分隔线
                if set(line.replace("|", "").replace("-", "").strip()) == set():
                    continue
                # 已渲染过的表头/数据行不再渲染（粗略：包含 "|" 的全跳过）
                if "|" in line:
                    continue
                story.append(Paragraph(line, styles["ChBody"]))
            story.append(Spacer(1, 3 * mm))
        story.append(PageBreak())

    # Trends（保留 pregnancy-care 的"趋势"识别逻辑）
    has_trends = any("趋势" in t for t in summary_sections)
    if has_trends:
        story.append(Paragraph("指标趋势", styles["ChTitle"]))
        for section_title, section_content in summary_sections.items():
            if "趋势" in section_title:
                story.append(Paragraph(section_title, styles["ChH2"]))
                rows = parse_markdown_table(section_content)
                if rows:
                    story.append(_make_table(rows, chinese_font, "#3498db"))
                    story.append(Spacer(1, 5 * mm))
                else:
                    story.append(Paragraph("暂无数据", styles["ChSmall"]))

    # Diagnosis timeline（影像/专科诊断时间线段）
    if "诊断时间线" in summary_sections:
        story.append(PageBreak())
        story.append(Paragraph("诊断时间线", styles["ChTitle"]))
        for line in summary_sections["诊断时间线"].split("\n"):
            line = line.strip()
            if line.startswith("###"):
                story.append(Paragraph(line.lstrip("#").strip(), styles["ChH3"]))
            elif line.startswith("- "):
                story.append(Paragraph(line, styles["ChBody"]))
            elif line:
                story.append(Paragraph(line, styles["ChBody"]))

    # Individual records summary
    if record_files:
        story.append(PageBreak())
        story.append(Paragraph("检查记录明细", styles["ChTitle"]))

        for rec_path in record_files:
            rec_content = read_file(rec_path)
            rec_sections = extract_sections(rec_content)
            rec_name = rec_path.stem

            story.append(Paragraph(rec_name, styles["ChH2"]))

            if "基本信息" in rec_sections:
                for line in rec_sections["基本信息"].strip().split("\n"):
                    line = line.strip()
                    if line.startswith("-"):
                        story.append(Paragraph(line, styles["ChBody"]))

            if "检查指标" in rec_sections:
                rows = parse_markdown_table(rec_sections["检查指标"])
                if rows:
                    t = _make_table(rows, chinese_font, "#27ae60")
                    story.append(t)
                    story.append(Spacer(1, 3 * mm))

            if "诊断 / 印象" in rec_sections or "诊断/印象" in rec_sections:
                impression = rec_sections.get("诊断 / 印象") or rec_sections.get("诊断/印象")
                if impression and impression.strip():
                    story.append(Paragraph("诊断 / 印象：", styles["ChBody"]))
                    for line in impression.split("\n"):
                        line = line.strip()
                        if line:
                            story.append(Paragraph(line, styles["ChSmall"]))

            if "异常分析" in rec_sections:
                analysis = rec_sections["异常分析"].strip()
                if analysis:
                    story.append(Paragraph("异常分析：", styles["ChBody"]))
                    for line in analysis.split("\n"):
                        line = line.strip()
                        if line:
                            story.append(Paragraph(line, styles["ChSmall"]))

            story.append(Spacer(1, 5 * mm))

    # Footer
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(
        "以上报告由 AI 自动生成，仅供参考，不构成医学建议。请咨询专业医生。",
        styles["ChSmall"],
    ))

    doc.build(story)
    print(f"PDF generated: {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate-pdf.py <member_dir> [output_path]")
        sys.exit(1)

    check_dependencies()

    member_dir = sys.argv[1]
    if not os.path.isdir(member_dir):
        print(f"Error: Directory not found: {member_dir}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        today = date.today().strftime("%Y%m%d")
        output_path = os.path.join(member_dir, f"健康综合报告_{today}.pdf")

    generate_pdf(member_dir, output_path)


if __name__ == "__main__":
    main()
