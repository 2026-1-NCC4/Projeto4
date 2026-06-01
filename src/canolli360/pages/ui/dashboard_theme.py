"""
Tokens visuais do design system Figma (`theme.css` do export).

Referência: `Dashboard financeiro Cannoli Food Tech` — :root em `src/styles/theme.css`
(primário #FF7A00, secundário #0D1440, fundo #F9FAFB, cards brancos, borda #E4E7EC).
"""

from __future__ import annotations

import streamlit as st

FONT_SIZE = "16px"
BACKGROUND = "#F9FAFB"
FOREGROUND = "#101828"
CARD = "#FFFFFF"
PRIMARY = "#FF7A00"
SECONDARY = "#0D1440"
MUTED = "#F2F4F7"
MUTED_FOREGROUND = "#667085"
ACCENT_BG = "#FFF4ED"
ACCENT_FOREGROUND = "#FF7A00"
BORDER = "#E4E7EC"
RADIUS = "12px"

CHART_1 = "#FF7A00"
CHART_2 = "#0D1440"
CHART_3 = "#FFB380"
CHART_4 = "#12B76A"
CHART_5 = "#F04438"

SIDEBAR = "#0D1440"
SIDEBAR_ACCENT = "#1a2557"

ACCENT = PRIMARY
TEXT = FOREGROUND
TEXT_MUTED = MUTED_FOREGROUND

PLOTLY_LAYOUT = dict(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=CARD,
    font=dict(color=FOREGROUND, family="Inter, Segoe UI, system-ui, sans-serif", size=13),
    margin=dict(l=48, r=24, t=56, b=48),
    hoverlabel=dict(
        bgcolor=CARD,
        bordercolor=BORDER,
        font=dict(color=FOREGROUND, size=13),
    ),
    colorway=[CHART_1, CHART_2, CHART_3, CHART_4, CHART_5],
    xaxis=dict(
        showgrid=True,
        gridcolor=BORDER,
        gridwidth=1,
        zerolinecolor=BORDER,
        linecolor=BORDER,
        tickfont=dict(color=MUTED_FOREGROUND, size=11),
        title_font=dict(color=FOREGROUND, size=12),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor=BORDER,
        gridwidth=1,
        zerolinecolor=BORDER,
        linecolor=BORDER,
        tickfont=dict(color=MUTED_FOREGROUND, size=11),
        title_font=dict(color=FOREGROUND, size=12),
    ),
)


def inject_executive_dashboard_css() -> None:
    st.markdown(
        f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] {{
    font-family: "Inter", "Segoe UI", system-ui, sans-serif;
    font-size: {FONT_SIZE};
  }}

  [data-testid="stAppViewContainer"] {{
    background-color: {BACKGROUND};
    color: {FOREGROUND};
  }}

  [data-testid="stHeader"] {{
    background: {CARD};
    border-bottom: 1.5px solid {BORDER};
  }}

  section[data-testid="stSidebar"] > div {{
    background: linear-gradient(180deg, {SIDEBAR} 0%, #0a0e1a 100%) !important;
    border-right: 1.5px solid {SIDEBAR_ACCENT};
  }}

  [data-testid="stMetric"] {{
    background: {CARD};
    border: 1.5px solid {BORDER};
    border-radius: {RADIUS};
    padding: 1.1rem 1.2rem;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
    transition: box-shadow 0.2s ease;
  }}
  [data-testid="stMetric"]:hover {{
    box-shadow: 0 4px 12px rgba(16, 24, 40, 0.08);
  }}
  [data-testid="stMetric"] label {{
    color: {MUTED_FOREGROUND} !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
  }}
  [data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {FOREGROUND} !important;
    font-weight: 600 !important;
    font-size: 1.65rem !important;
  }}
  [data-testid="stMetricDelta"] {{
    font-size: 0.8rem !important;
  }}

  div[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    gap: 0.25rem;
    background: {MUTED};
    padding: 0.25rem;
    border-radius: {RADIUS};
    border: 1px solid {BORDER};
  }}
  div[data-testid="stTabs"] button {{
    color: {MUTED_FOREGROUND};
    font-weight: 600;
    border-radius: 8px !important;
  }}
  div[data-testid="stTabs"] [aria-selected="true"] {{
    color: {PRIMARY} !important;
    background: {CARD} !important;
    box-shadow: 0 1px 2px rgba(16,24,40,0.06);
  }}

  .exec-hero {{
    background: {CARD};
    border: 1.5px solid {BORDER};
    border-radius: calc({RADIUS} + 4px);
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
    border-top: 4px solid {PRIMARY};
  }}
  .exec-hero h1 {{
    margin: 0 0 0.35rem 0;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: {FOREGROUND};
  }}
  .exec-hero .sub {{
    color: {MUTED_FOREGROUND};
    font-size: 0.95rem;
    margin-bottom: 1rem;
    font-weight: 400;
  }}
  .exec-pills {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem 0.75rem;
    align-items: center;
  }}
  .exec-pill {{
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    border: 1px solid {BORDER};
    background: {MUTED};
    color: {FOREGROUND};
  }}
  .exec-pill.ok {{
    color: #027A48;
    border-color: #ABEFC6;
    background: #ECFDF3;
  }}
  .exec-pill.brand {{
    background: {ACCENT_BG};
    color: {ACCENT_FOREGROUND};
    border-color: #FFD6B3;
  }}

  .alert-strip {{
    border-radius: {RADIUS};
    border: 1.5px solid {BORDER};
    padding: 0.75rem 1rem;
    background: {CARD};
    margin-bottom: 0.45rem;
    font-size: 0.9rem;
    color: {FOREGROUND};
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
  }}

  [data-testid="stExpander"] {{
    background: {CARD};
    border: 1.5px solid {BORDER} !important;
    border-radius: {RADIUS} !important;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
  }}

  div.block-container {{
    padding-top: 1rem;
    max-width: 1400px;
  }}

  h3, [data-testid="stMarkdownContainer"] h3 {{
    color: {FOREGROUND};
    font-weight: 600;
  }}
</style>
""",
        unsafe_allow_html=True,
    )


def fmt_milhares(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f} mi"
    if n >= 1_000:
        return f"{n / 1_000:.0f} mil"
    return str(n)
