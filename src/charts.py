from typing import Dict, List

import plotly.graph_objects as go

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
SEVERITY_COLORS = {
    "CRITICAL": "#DC2626",
    "HIGH": "#EA580C",
    "MEDIUM": "#D97706",
    "LOW": "#2563EB",
}


def build_severity_pie_chart(findings: List[Dict]) -> go.Figure:
    """Pie chart of findings grouped by severity (CRITICAL/HIGH/MEDIUM/LOW)."""
    counts = {s: 0 for s in SEVERITY_ORDER}
    for f in findings:
        sev = f.get("severity", "MEDIUM")
        counts[sev] = counts.get(sev, 0) + 1

    labels = [s for s in SEVERITY_ORDER if counts[s] > 0]
    values = [counts[s] for s in labels]
    colors = [SEVERITY_COLORS[s] for s in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hole=0.4,
        textinfo="label+percent",
    )])
    fig.update_layout(
        title="Findings by Severity",
        margin=dict(l=10, r=10, t=40, b=10),
        height=320,
        showlegend=True,
    )
    return fig


def build_category_bar_chart(quality_count: int, security_count: int) -> go.Figure:
    """Bar chart comparing Quality vs Security finding counts."""
    fig = go.Figure(data=[go.Bar(
        x=["Quality", "Security"],
        y=[quality_count, security_count],
        marker_color=["#2563EB", "#DC2626"],
        text=[quality_count, security_count],
        textposition="outside",
    )])
    fig.update_layout(
        title="Findings by Category",
        margin=dict(l=10, r=10, t=40, b=10),
        height=320,
        yaxis_title="Count",
    )
    return fig


def build_severity_by_category_chart(findings: List[Dict]) -> go.Figure:
    """Stacked bar chart: severity breakdown within each category (Quality / Security)."""
    categories = ["Quality", "Security"]
    fig = go.Figure()
    for sev in SEVERITY_ORDER:
        y_values = []
        for cat in categories:
            count = sum(1 for f in findings if f.get("category") == cat and f.get("severity") == sev)
            y_values.append(count)
        fig.add_trace(go.Bar(name=sev, x=categories, y=y_values, marker_color=SEVERITY_COLORS[sev]))

    fig.update_layout(
        title="Severity Breakdown by Category",
        barmode="stack",
        margin=dict(l=10, r=10, t=40, b=10),
        height=320,
        yaxis_title="Count",
    )
    return fig
