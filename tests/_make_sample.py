"""一次性脚本：生成脱敏样本 PDF。"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pathlib import Path

out = Path(__file__).parent / "fixtures" / "sample-checkup.pdf"
out.parent.mkdir(parents=True, exist_ok=True)

c = canvas.Canvas(str(out), pagesize=A4)
c.setFont("Helvetica", 12)
c.drawString(100, 800, "Health Checkup Report")
c.drawString(100, 780, "Name: Test Patient")
c.drawString(100, 760, "Date: 2024-09-15")
c.drawString(100, 740, "TG: 4.2 mmol/L")
c.drawString(100, 720, "HGB: 130 g/L")
c.showPage()

c.setFont("Helvetica", 12)
c.drawString(100, 800, "Page 2 - Imaging")
c.drawString(100, 780, "Liver ultrasound: normal")
c.showPage()

c.save()
print(f"Wrote {out}")
