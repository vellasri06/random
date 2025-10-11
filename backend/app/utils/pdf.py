from typing import Any, Dict, List, Optional
from fpdf import FPDF
import textwrap


def _wrap_text(text: str, width: int = 90) -> List[str]:
    wrapped: List[str] = []
    for paragraph in text.splitlines():
        if not paragraph.strip():
            wrapped.append("")
            continue
        wrapped.extend(textwrap.wrap(paragraph, width=width))
    return wrapped


def render_mom_pdf(mom: Dict[str, Any], out_path: str) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, mom.get("meeting_title", "Meeting"), ln=True)

    pdf.set_font("Arial", size=12)
    date_val = mom.get("date") or "-"
    pdf.cell(0, 8, f"Date: {date_val}", ln=True)

    attendees = mom.get("attendees", [])
    attendees_str = ", ".join(attendees) if attendees else "-"
    pdf.cell(0, 8, f"Attendees: {attendees_str}", ln=True)

    pdf.ln(4)
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(0, 9, "Executive Summary", ln=True)
    pdf.set_font("Arial", size=12)
    for line in _wrap_text(mom.get("executive_summary", "-")):
        pdf.cell(0, 7, line, ln=True)

    pdf.ln(3)
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(0, 9, "Key Decisions Made", ln=True)
    pdf.set_font("Arial", size=12)
    decisions = mom.get("key_decisions", [])
    if not decisions:
        pdf.cell(0, 7, "-", ln=True)
    else:
        for d in decisions:
            for line in _wrap_text(f"• {d}", width=100):
                pdf.cell(0, 7, line, ln=True)

    pdf.ln(3)
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(0, 9, "Action Items", ln=True)
    pdf.set_font("Arial", size=12)

    items = mom.get("action_items", [])
    if not items:
        pdf.cell(0, 7, "-", ln=True)
    else:
        # simple table-like layout
        col_widths = [90, 50, 40]
        headers = ["Task", "Assigned To", "Deadline"]
        pdf.set_font("Arial", style="B", size=12)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 8, h, border=1)
        pdf.ln(8)
        pdf.set_font("Arial", size=12)
        for row in items:
            task = str(row.get("task") or "-")
            assigned = str(row.get("assigned_to") or "-")
            deadline = str(row.get("deadline") or "-")
            pdf.cell(col_widths[0], 8, task[:64], border=1)
            pdf.cell(col_widths[1], 8, assigned[:32], border=1)
            pdf.cell(col_widths[2], 8, deadline[:24], border=1)
            pdf.ln(8)

    pdf.output(out_path)
