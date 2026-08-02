import io
import re
from datetime import datetime
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, Preformatted, HRFlowable,
)

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
SEVERITY_COLORS = {
    "CRITICAL": "#DC2626",
    "HIGH": "#EA580C",
    "MEDIUM": "#D97706",
    "LOW": "#2563EB",
}


def _severity_pie_chart(findings: List[dict]) -> io.BytesIO:
    counts = {s: 0 for s in SEVERITY_ORDER}
    for f in findings:
        sev = f.get("severity", "MEDIUM")
        counts[sev] = counts.get(sev, 0) + 1

    labels = [s for s in SEVERITY_ORDER if counts[s] > 0]
    sizes = [counts[s] for s in labels]
    slice_colors = [SEVERITY_COLORS[s] for s in labels]

    fig, ax = plt.subplots(figsize=(3.4, 3.0))
    if sizes:
        ax.pie(sizes, labels=labels, colors=slice_colors, autopct="%1.0f%%",
               startangle=90, textprops={"fontsize": 8})
    else:
        ax.text(0.5, 0.5, "No findings", ha="center", va="center")
    ax.set_title("Findings by Severity", fontsize=10)
    ax.axis("equal")

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    buf.seek(0)
    return buf


def _category_bar_chart(quality_count: int, security_count: int) -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(3.4, 3.0))
    categories = ["Quality", "Security"]
    values = [quality_count, security_count]
    bars = ax.bar(categories, values, color=["#2563EB", "#DC2626"])
    ax.set_title("Findings by Category", fontsize=10)
    ax.bar_label(bars, fontsize=8)
    ax.set_ylabel("Count", fontsize=8)

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    buf.seek(0)
    return buf


def _md_inline(text: str) -> str:
    """Escapes XML-sensitive characters, then converts a small subset of markdown
    (**bold**, *italic*) into reportlab's limited HTML-like Paragraph markup."""
    text = str(text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    return text


def _pr_summary_flowables(pr_summary: str, styles) -> List:
    """Converts the PR summary markdown (headings, bullets, plain text; markdown tables
    are rendered as monospaced blocks since reportlab has no native table-markdown parser)
    into a list of reportlab flowables."""
    flowables = []
    table_buffer: List[str] = []

    def flush_table():
        if table_buffer:
            flowables.append(Preformatted("\n".join(table_buffer), styles["CodeBlock"]))
            flowables.append(Spacer(1, 6))
            table_buffer.clear()

    for line in str(pr_summary).splitlines():
        stripped = line.strip()
        if not stripped:
            flush_table()
            flowables.append(Spacer(1, 4))
            continue

        if stripped.startswith("|"):
            table_buffer.append(line)
            continue
        flush_table()

        if stripped.startswith("### "):
            flowables.append(Paragraph(_md_inline(stripped[4:]), styles["Heading3"]))
        elif stripped.startswith("## "):
            flowables.append(Paragraph(_md_inline(stripped[3:]), styles["Heading2"]))
        elif stripped.startswith("# "):
            flowables.append(Paragraph(_md_inline(stripped[2:]), styles["Heading1"]))
        elif stripped.startswith(("- ", "* ")):
            flowables.append(Paragraph("&bull; " + _md_inline(stripped[2:]), styles["Normal"]))
        else:
            flowables.append(Paragraph(_md_inline(stripped), styles["Normal"]))

    flush_table()
    return flowables


def generate_pdf_report(submission_id: str, project_name: str, language: str, results: Dict) -> io.BytesIO:
    """Builds the full PDF code review report and returns it as an in-memory buffer
    ready to hand to Streamlit's download_button. Submission ID, project name, and
    language are placed at the very beginning of the report as required."""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
        leftMargin=0.6 * inch, rightMargin=0.6 * inch,
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CodeBlock", fontName="Courier", fontSize=8, leading=10))

    story = []

    # ---- Header: submission id, project name, language (first thing in the report) ----
    story.append(Paragraph("AI Code Review &amp; Security Audit Report", styles["Title"]))
    story.append(Spacer(1, 10))

    header_table = Table(
        [
            ["Submission ID", submission_id],
            ["Project Name", project_name or "Untitled Project"],
            ["Language", language],
            ["Generated On", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ],
        colWidths=[1.6 * inch, 4.5 * inch],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F4F6")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 16))

    # ---- Executive metrics ----
    findings = results.get("findings", [])
    remediations = results.get("remediations", [])
    total_issues = results.get("total_issues", len(findings))
    quality_count = results.get("quality_count", 0)
    security_count = results.get("security_count", 0)

    metrics_table = Table(
        [["Total Issues", "Quality Issues", "Security Issues"],
         [str(total_issues), str(quality_count), str(security_count)]],
        colWidths=[2.03 * inch] * 3,
    )
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 16))

    # ---- Charts (graphical presentation of findings) ----
    story.append(Paragraph("Visual Overview", styles["Heading2"]))
    story.append(Spacer(1, 6))
    pie_buf = _severity_pie_chart(findings)
    bar_buf = _category_bar_chart(quality_count, security_count)

    chart_table = Table(
        [[Image(pie_buf, width=2.5 * inch, height=2.2 * inch),
          Image(bar_buf, width=2.5 * inch, height=2.2 * inch)]],
    )
    chart_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(chart_table)
    story.append(Spacer(1, 16))

    # ---- PR Summary ----
    story.append(Paragraph("Pull Request Review Summary", styles["Heading2"]))
    story.extend(_pr_summary_flowables(results.get("pr_summary", "No summary generated."), styles))
    story.append(PageBreak())

    # ---- Detailed findings & remediations ----
    story.append(Paragraph("Detailed Findings &amp; Remediations", styles["Heading2"]))
    story.append(Spacer(1, 8))

    remediations_map = {r.get("type"): r for r in remediations}

    if not findings:
        story.append(Paragraph("No issues were detected.", styles["Normal"]))

    for idx, issue in enumerate(findings, 1):
        issue_type = issue.get("type", "Issue")
        severity = issue.get("severity", "MEDIUM")
        color_hex = SEVERITY_COLORS.get(severity, "#6B7280")

        heading = (
            f'{idx}. [{_md_inline(issue.get("category", "Issue"))}] {_md_inline(issue_type)} '
            f'<font color="{color_hex}"><b>({severity})</b></font>'
        )
        story.append(Paragraph(heading, styles["Heading3"]))

        if issue.get("line") is not None:
            story.append(Paragraph(f"<b>Line:</b> {issue.get('line')}", styles["Normal"]))
        story.append(Paragraph(f"<b>Description:</b> {_md_inline(issue.get('description', ''))}", styles["Normal"]))

        rem = remediations_map.get(issue_type)
        if rem:
            story.append(Spacer(1, 4))
            story.append(Paragraph("<b>Remediation:</b>", styles["Normal"]))
            story.append(Paragraph(_md_inline(rem.get("explanation", "")), styles["Normal"]))
            corrected_code = rem.get("corrected_code")
            if corrected_code:
                story.append(Spacer(1, 4))
                story.append(Preformatted(str(corrected_code), styles["CodeBlock"]))

        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", color=colors.HexColor("#E5E7EB")))
        story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return buffer
