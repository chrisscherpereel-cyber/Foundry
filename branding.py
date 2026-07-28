"""
branding.py — Venture Foundry visual identity.

Holds the simulation's custom logo (an inline SVG: a foundry hex badge with rising
"evidence bars" and a spark of insight) and small helpers to render it in the app.

IMPORTANT: Streamlit's Markdown renderer treats any line indented 4+ spaces as a
code block, which would print raw HTML/SVG to the screen. So every string we hand
to st.markdown is collapsed to a single unindented line via _oneline() before use.
"""

import streamlit as st

# Raw logo artwork. Kept multi-line here for readability; _oneline() flattens it
# before it ever reaches st.markdown. assets/logo.svg holds the same artwork.
_LOGO_SVG = """
<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Venture Foundry logo" width="{w}" height="{w}"
     style="display:block;flex:0 0 auto;">
  <defs>
    <linearGradient id="vfBg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2b3a5c"/><stop offset="1" stop-color="#141c2e"/>
    </linearGradient>
    <linearGradient id="vfBar" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="#2b9d8f"/><stop offset="1" stop-color="#41d3bd"/>
    </linearGradient>
    <linearGradient id="vfAmber" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#ffd97a"/><stop offset="1" stop-color="#f5a623"/>
    </linearGradient>
  </defs>
  <path d="M60 5 L106 31 V85 L60 111 L14 85 V31 Z" fill="url(#vfBg)"
        stroke="url(#vfAmber)" stroke-width="3.5" stroke-linejoin="round"/>
  <rect x="33" y="82" width="54" height="8" rx="4" fill="#c9d6f0"/>
  <rect x="40" y="66" width="11" height="16" rx="3" fill="url(#vfBar)"/>
  <rect x="55" y="54" width="11" height="28" rx="3" fill="url(#vfBar)"/>
  <rect x="70" y="42" width="11" height="40" rx="3" fill="url(#vfBar)"/>
  <path d="M78 27 L80.5 33.5 L87 36 L80.5 38.5 L78 45 L75.5 38.5 L69 36 L75.5 33.5 Z"
        fill="url(#vfAmber)"/>
</svg>
"""


def _oneline(html):
    """Collapse markup to a single line with no leading indentation.

    This is what prevents Streamlit's Markdown parser from rendering the HTML as a
    literal code block.
    """
    return " ".join(line.strip() for line in html.strip().splitlines() if line.strip())


def logo_svg(width=64):
    """Return the logo SVG markup, flattened and sized to `width` pixels."""
    return _oneline(_LOGO_SVG).replace("{w}", str(width))


def header(subtitle="THE EVIDENCE ECONOMY"):
    """Large logo + wordmark for the landing page."""
    html = (
        '<div style="display:flex;align-items:center;gap:16px;margin:4px 0 8px;">'
        + logo_svg(76)
        + '<div style="line-height:1.15;">'
        + '<div style="font-size:30px;font-weight:800;letter-spacing:.5px;">VENTURE FOUNDRY</div>'
        + f'<div style="font-size:13px;letter-spacing:3px;opacity:.65;">{subtitle}</div>'
        + '</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def sidebar_logo(caption=""):
    """Compact logo + wordmark for a sidebar."""
    html = (
        '<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
        + logo_svg(38)
        + '<div style="line-height:1.1;">'
        + '<div style="font-size:15px;font-weight:800;letter-spacing:.4px;">VENTURE FOUNDRY</div>'
        + '<div style="font-size:10px;letter-spacing:2px;opacity:.6;">EVIDENCE ECONOMY</div>'
        + '</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)
    if caption:
        st.caption(caption)
