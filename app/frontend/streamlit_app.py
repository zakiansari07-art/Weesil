import html
import json
import mimetypes
import os
from typing import Any
import base64
import markdown
import requests
import streamlit as st
from pathlib import Path

LOGO_PATH = Path(__file__).parent / "assets" / "imagetrust-logo.png"

with open(LOGO_PATH, "rb") as logo_file:
    logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

API_URL = os.getenv(
    "IMAGETRUST_API_URL",
    
).rstrip("/")

ANALYZE_URL = f"{API_URL}/analyze"
HEALTH_URL = f"{API_URL}/health"


# ---------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="ImageTrust — AI Image Forensics",
    page_icon="IT",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* ================================================================
       ImageTrust Design System
       Centralized CSS for typography, layout, cards, results and report.
       Adjust font sizes here rather than changing individual HTML blocks.
       ================================================================ */

    /* ----------------------------------------------------------------
       1. Design tokens & global typography
       ---------------------------------------------------------------- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg:#030914;
        --card:#09172d;
        --border:#1b3154;
        --text:#edf3ff;
        --muted:#9eafd0;
        --blue:#6f8cff;
        --blue2:#9aaeff;
        --green:#62e5b5;
        --red:#ff7d8a;
        --amber:#f4c76c;
    }

    html, body, [class*="css"] {
        font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
    }

    .stApp {
        background:radial-gradient(circle at 80% 0%,rgba(79,101,210,.15),transparent 34rem),
                   radial-gradient(circle at 10% 20%,rgba(75,87,180,.08),transparent 28rem),
                   var(--bg);
        color:var(--text);
    }

    .block-container {
        max-width:1180px;
        padding-top:1.4rem;
        padding-bottom:4rem;
    }

    #MainMenu, footer {
        visibility:hidden;
    }

    /* ----------------------------------------------------------------
       2. Header / navigation / hero
       ---------------------------------------------------------------- */
    .brand-bar {
        display:flex;
        align-items:center;
        justify-content:space-between;
        padding:4px 0 20px;
        margin-bottom:42px;
        border-bottom:1px solid rgba(111,140,255,.12);
    }

    .brand-logo {
        height:100px;
        width:120px;
        max-width:180px;
        display:block;
        object-fit:contain;
    }

    .nav-pill {
        padding:9px 15px;
        border:1px solid #21385d;
        border-radius:9px;
        background:#09172d;
        color:#9aaeff;
        font-size:10px;
        font-weight:800;
        letter-spacing:1px;
    }

    .hero-kicker {
        color:#7895ff;
        font-size:15px;
        font-weight:800;
        letter-spacing:2px;
        margin-bottom:10px;
    }

    .hero h1 {
        margin:0;
        max-width:760px;
        color:#edf3ff;
        font-size:clamp(34px,5vw,54px);
        line-height:1.03;
        letter-spacing:-2.4px;
        font-weight:800;
    }

    .hero h1 .accent {
        background:linear-gradient(90deg,#fff,#91a5ff);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
    }

    .hero p {
        max-width:700px;
        margin:15px 0 0;
        color:#9eafd0;
        font-size:14px;
        line-height:1.75;
    }

    /* ----------------------------------------------------------------
       3. Feature highlights
       ---------------------------------------------------------------- */
    .feature-row {
        display:grid;
        grid-template-columns:repeat(4,1fr);
        gap:10px;
        margin:25px 0 30px;
    }

    .feature {
        display:flex;
        align-items:center;
        gap:10px;
        min-height:62px;
    }

    .feature-icon {
        width:39px;
        height:39px;
        flex:0 0 39px;
        border:1px solid #3556a2;
        border-radius:11px;
        background:linear-gradient(145deg,#183d88,#101f47);
        color:#b8c7ff;
        display:flex;
        align-items:center;
        justify-content:center;
        font-weight:800;
    }

    .feature-title {
        color:#dbe5ff;
        font-size:12px;
        font-weight:700;
    }

    /* Feature descriptions such as "Real or AI-generated". */
    .feature-copy {
        color:#7f91b2;
        font-size:14px;
        line-height:1.4;
        margin-top:3px;
    }

    /* ----------------------------------------------------------------
       4. Upload / preview cards
       ---------------------------------------------------------------- */
    .upload-card {
        background:linear-gradient(145deg,rgba(11,27,54,.98),rgba(6,18,37,.98));
        border:1px solid #203c69;
        border-radius:18px;
        padding:23px;
        box-shadow:0 20px 60px rgba(0,0,0,.22);
    }

    .card-kicker {
        color:#7693ff;
        font-size:10px;
        font-weight:800;
        letter-spacing:1.4px;
        text-transform:uppercase;
    }

    .card-title {
        color:#edf3ff;
        font-size:17px;
        font-weight:700;
        margin-top:5px;
    }

    .card-copy {
        color:#9eafd0;
        font-size:12px;
        line-height:1.6;
        margin:5px 0 16px;
    }

    div[data-testid="stFileUploader"] {
        background:#08152b;
        border:1px dashed #5275c7;
        border-radius:14px;
        padding:7px;
    }

    div[data-testid="stFileUploader"] section {
        padding:21px 12px;
    }

    div[data-testid="stFileUploader"] span,
    div[data-testid="stFileUploader"] small {
        color:#a8b8d7!important;
    }

    div.stButton>button {
        width:100%;
        min-height:48px;
        margin-top:10px;
        border-radius:11px;
        border:1px solid #526fc6;
        background:linear-gradient(135deg,#5574dc,#3554ad);
        color:white;
        font-weight:700;
        box-shadow:0 8px 24px rgba(50,79,170,.22);
    }

    div.stButton>button:hover {
        background:linear-gradient(135deg,#6785ed,#4262bd);
        border-color:#7893ff;
        color:white;
    }

    .preview-card {
        background:#09172d;
        border:1px solid #1b3154;
        border-radius:18px;
        padding:14px;
    }

    .preview-card img {
        border-radius:11px;
    }

    .preview-caption {
        color:#7184a7;
        font-size:10px;
        text-align:center;
        margin-top:9px;
    }

    .empty-state {
        min-height:275px;
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
        text-align:center;
        background:rgba(7,20,40,.68);
        border:1px dashed #28446f;
        border-radius:18px;
    }

    .empty-icon {
        width:45px;
        height:45px;
        border:1px solid #31529b;
        border-radius:13px;
        background:#0e2450;
        color:#91a6ff;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:20px;
        margin-bottom:12px;
    }

    .empty-title {
        color:#dce6ff;
        font-size:14px;
        font-weight:700;
    }

    .empty-copy {
        max-width:330px;
        margin-top:6px;
        color:#7285a7;
        font-size:11px;
        line-height:1.55;
    }

    /* ----------------------------------------------------------------
       5. Main verdict
       ---------------------------------------------------------------- */
    .verdict-card {
        margin-top:22px;
        padding:21px;
        border:1px solid #237f72;
        border-radius:17px;
        background:linear-gradient(110deg,rgba(5,37,38,.98),rgba(7,26,45,.98));
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:20px;
    }

    .verdict-card.ai {
        border-color:#82404d;
        background:linear-gradient(110deg,rgba(49,17,28,.98),rgba(15,24,43,.98));
    }

    .verdict-card.uncertain {
        border-color:#80672f;
        background:linear-gradient(110deg,rgba(47,36,12,.98),rgba(15,24,43,.98));
    }

    .verdict-main {
        display:flex;
        align-items:center;
        gap:15px;
        min-width:0;
    }

    .verdict-icon {
        width:51px;
        height:51px;
        flex:0 0 51px;
        border:2px solid var(--green);
        border-radius:50%;
        background:rgba(65,217,166,.09);
        color:var(--green);
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:14px;
        font-weight:800;
    }

    .ai .verdict-icon {
        border-color:var(--red);
        color:var(--red);
    }

    .uncertain .verdict-icon {
        border-color:var(--amber);
        color:var(--amber);
    }

    .eyebrow {
        color:#7588ab;
        font-size:9px;
        font-weight:800;
        letter-spacing:1.2px;
        text-transform:uppercase;
    }

    .verdict-title {
        color:#eaf2ff;
        font-size:23px;
        font-weight:800;
        letter-spacing:-.7px;
        margin-top:3px;
    }

    .verdict-subtitle {
        color:#9bafd1;
        font-size:11px;
        line-height:1.5;
        margin-top:4px;
    }

    .confidence {
        min-width:150px;
        text-align:right;
    }

    .confidence-label {
        color:#7690bf;
        font-size:9px;
        font-weight:800;
        letter-spacing:1.1px;
    }

    .confidence-value {
        color:var(--green);
        font-size:25px;
        font-weight:800;
        margin-top:2px;
    }

    .ai .confidence-value {
        color:var(--red);
    }

    .uncertain .confidence-value {
        color:var(--amber);
    }

    .confidence-bar {
        height:7px;
        margin-top:7px;
        overflow:hidden;
        border-radius:99px;
        background:#1b3154;
    }

    .confidence-fill {
        height:100%;
        border-radius:99px;
        background:linear-gradient(90deg,#56dcae,#78edc1);
    }

    .ai .confidence-fill {
        background:linear-gradient(90deg,#ff6677,#ff9a9f);
    }

    .uncertain .confidence-fill {
        background:linear-gradient(90deg,#d9aa49,#f5d27e);
    }

    /* ----------------------------------------------------------------
       6. Findings, sections & metric cards
       ---------------------------------------------------------------- */
    .section-title {
        color:#dfe8ff;
        font-size:20px;
        font-weight:800;
        margin:28px 0 6px;
    }

    .section-description {
        color:#7387a9;
        font-size:15px;
        line-height:1.55;
        margin-bottom:10px;
    }

    .metric-grid {
        display:grid;
        grid-template-columns:repeat(3,minmax(0,1fr));
        gap:12px;
        margin-top:13px;
    }

    .metric {
        background:rgba(8,23,46,.96);
        border:1px solid #1b3154;
        border-radius:14px;
        padding:17px;
    }
    
    .metric-label {
        color:#6f86ae;
        font-size:9px;
        font-weight:800;
        letter-spacing:1px;
        text-transform:uppercase;
    }

    .metric-value {
        color:#e7efff;
        font-size:17px;
        font-weight:750;
        margin-top:7px;
    }

    .metric-detail {
        color:#8195b7;
        font-size:15px;
        line-height:1.55;
        margin-top:4px;
    }

  
    /* ----------------------------------------------------------------
       Key findings grid
       A dedicated CSS grid guarantees equal card heights. The cards
       are not dependent on Streamlit's column sizing, so increasing
       or decreasing font sizes will not change the relative heights.
       ---------------------------------------------------------------- */
    .key-findings-grid {
        --key-finding-height:170px;
        display:grid;
        grid-template-columns:repeat(3,minmax(0,1fr));
        grid-template-rows:var(--key-finding-height);
        gap:12px;
        width:100%;
        align-items:stretch;
    }

    .key-finding-card {
        height:var(--key-finding-height);
        min-height:var(--key-finding-height);
        max-height:var(--key-finding-height);
        box-sizing:border-box;
        display:flex;
        flex-direction:column;
        overflow:hidden;
    }

    /* Keep the descriptive line anchored at the bottom of every card. */
    .key-finding-card .metric-detail {
        margin-top:auto;
    }

    /* Allow long descriptions to wrap without changing card height. */
    .key-finding-card .metric-detail {
        overflow-wrap:anywhere;
    }

    /* ----------------------------------------------------------------
       Provenance cards
       A dedicated CSS grid keeps EXIF, XMP, and C2PA cards at exactly
       the same height, independent of text length or font size.
       ---------------------------------------------------------------- */
    .provenance-grid {
        --provenance-card-height:190px;
        display:grid;
        grid-template-columns:repeat(3,minmax(0,1fr));
        grid-template-rows:var(--provenance-card-height);
        grid-auto-rows:var(--provenance-card-height);
        gap:12px;
        width:100%;
        align-items:stretch;
        margin-top:13px;
    }

    .provenance-grid .provenance-card {
        height:var(--provenance-card-height) !important;
        min-height:var(--provenance-card-height) !important;
        max-height:var(--provenance-card-height) !important;
        box-sizing:border-box;
        display:flex;
        flex-direction:column;
        overflow:hidden;
    }

    .provenance-grid .provenance-card .metric-detail {
        margin-top:auto;
        min-height:20px;
        line-height:20px;
        overflow:hidden;
        text-overflow:ellipsis;
        white-space:nowrap;
        overflow-wrap:normal;
    }

    /* Prevent long metadata values from changing the card height. */
    .provenance-grid .provenance-card .detail-row {
        flex-shrink:0;
        min-width:0;
    }

    .provenance-grid .provenance-card .detail-row span,
    .provenance-grid .provenance-card .detail-row strong {
        min-width:0;
        line-height:18px;
        overflow:hidden;
        text-overflow:ellipsis;
        white-space:nowrap;
    }

    /* Provenance values are intentionally regular-weight, not bold. */
    .provenance-card .metric-value {
        font-size:15px;
        font-weight:400;
    }

    /* ----------------------------------------------------------------
       7. Provenance detail rows
       ---------------------------------------------------------------- */
    .provenance-card .detail-row {
        font-size:12px;
        line-height:1.5;
    }

    .provenance-card .detail-row span {
        font-size:12px;
        font-weight:400;
    }

    /* Signature issuer and all provenance values use the same weight. */
    .provenance-card .detail-row strong {
        font-size:12px;
        font-weight:400;
    }

    /* General detail rows used by forensics and file/image details. */
    .detail-row {
        display:flex;
        justify-content:space-between;
        align-items:flex-start;
        gap:16px;
        padding:8px 0;
        border-bottom:1px solid rgba(42,64,98,.45);
        font-size:13px;
    }

    .detail-row:last-child {
        border-bottom:0;
    }

    .detail-row span {
        color:#7186a9;
    }

    .detail-row strong {
        color:#d2def3;
        text-align:right;
        font-weight:700;
    }

    /* ----------------------------------------------------------------
       8. Streamlit containers & expanders
       ---------------------------------------------------------------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background:linear-gradient(145deg,#0b1b35,#08162b);
        border-color:#1b3154!important;
        border-radius:14px!important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] span,
    div[data-testid="stVerticalBlockBorderWrapper"] label {
        color:#c1cee5!important;
    }

    div[data-testid="stExpander"] {
        background:linear-gradient(145deg,#0b1b35,#08162b);
        border:1px solid #1b3154;
        border-radius:13px;
        margin-bottom:9px;
    }

    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary span {
        color:#d8e4ff!important;
        font-weight:700!important;
    }

    div[data-testid="stJson"] {
        background:#061225;
        border-radius:10px;
    }

    /* ----------------------------------------------------------------
       9. Probability distribution
       ---------------------------------------------------------------- */
    .prob-card {
        background:rgba(8,23,46,.96);
        border:1px solid #1b3154;
        border-radius:12px;
        padding:13px 14px;
        margin-bottom:10px;
    }

    .prob-top {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:10px;
    }

    .prob-name {
        color:#cbd8ef;
        font-size:11px;
        font-weight:700;
    }

    .prob-value {
        color:#e8efff;
        font-size:11px;
        font-weight:800;
    }

    .prob-track {
        height:5px;
        margin-top:9px;
        background:#172a48;
        border-radius:99px;
        overflow:hidden;
    }

    .prob-fill {
        height:100%;
        border-radius:99px;
        background:linear-gradient(90deg,#667fe6,#9baaff);
    }

    /* ----------------------------------------------------------------
       10. Confidence note
       ---------------------------------------------------------------- */
    .confidence-note {
        margin-top:10px;
        padding:13px 16px;
        border:1px solid #263d62;
        border-radius:12px;
        background:rgba(7,20,40,.72);
    }

    .confidence-note-title {
        color:#b9c9ea;
        font-size:11px;
        font-weight:800;
        letter-spacing:.6px;
        text-transform:uppercase;
    }

    .confidence-note-copy {
        color:#7f93b6;
        font-size:10px;
        line-height:1.55;
        margin-top:3px;
    }

    /* ----------------------------------------------------------------
       11. Assessment report
       ---------------------------------------------------------------- */
    .report {
        margin-top:13px;
        padding:21px;
        background:linear-gradient(145deg,#0b1b35,#08162b);
        border:1px solid #1b3154;
        border-radius:16px;
    }

    .report-header {
        display:flex;
        align-items:center;
        gap:11px;
        padding-bottom:14px;
        border-bottom:1px solid #1a2d4b;
    }

    .report-icon {
        width:35px;
        height:35px;
        border-radius:10px;
        background:linear-gradient(145deg,#234b9e,#142e65);
        color:#c8d4ff;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:10px;
        font-weight:800;
    }

    .report-title {
        color:#e2ebff;
        font-size:20px;
        font-weight:800;
    }

    .report-subtitle {
        color:#7387aa;
        font-size:17px;
        line-height:1.5;
        margin-top:3px;
    }

    .report-body {
        color:#b1c0da;
        font-size:16px;
        line-height:1.75;
        padding-top:5px;
    }

    .report-body h2 {
        color:#e3ebff;
        font-size:14px;
        margin:18px 0 7px;
    }

    .report-body h3 {
        color:#c5d1e9;
        font-size:12px;
        margin:16px 0 5px;
    }

    .report-body strong {
        color:#d8e3fb;
    }

    /* ----------------------------------------------------------------
       12. Footer
       ---------------------------------------------------------------- */
    .footer {
        margin-top:38px;
        padding-top:17px;
        border-top:1px solid #132541;
        color:#5e7194;
        font-size:10px;
        text-align:center;
    }

    /* ----------------------------------------------------------------
       13. Responsive layout
       ---------------------------------------------------------------- */
    @media(max-width:760px) {
        /* Stack Key findings on smaller screens while preserving
           equal height for every card in the active grid. */
        .key-findings-grid {
            grid-template-columns:1fr;
            grid-template-rows:repeat(3,var(--key-finding-height));
        }

        .key-finding-card {
            height:var(--key-finding-height);
            min-height:var(--key-finding-height);
            max-height:var(--key-finding-height);
        }

        .provenance-grid {
            grid-template-columns:1fr;
            grid-template-rows:repeat(3,var(--provenance-card-height));
            grid-auto-rows:var(--provenance-card-height);
        }

        .provenance-grid .provenance-card {
            height:var(--provenance-card-height) !important;
            min-height:var(--provenance-card-height) !important;
            max-height:var(--provenance-card-height) !important;
        }

        .feature-row {
            grid-template-columns:repeat(2,1fr);
        }

        .verdict-card {
            align-items:flex-start;
            flex-direction:column;
        }

        .confidence {
            text-align:left;
            width:100%;
        }

        .metric-grid {
            grid-template-columns:1fr;
        }

        .brand-bar {
            margin-bottom:30px;
        }
    }

    @media(max-width:480px) {
        .feature-row {
            grid-template-columns:1fr;
        }
    }

    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def pct(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.1%}"
    return "N/A"


def pretty_label(value: Any) -> str:
    if value is None:
        return "Unknown"
    return str(value).replace("_", " ").title()


def markdown_to_html(text: str) -> str:
    return markdown.markdown(
        text or "",
        extensions=["extra", "sane_lists"],
    )


def analyze_image(uploaded_file) -> dict:
    content_type = (
        uploaded_file.type
        or mimetypes.guess_type(uploaded_file.name)[0]
        or "application/octet-stream"
    )

    response = requests.post(
        ANALYZE_URL,
        files={
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                content_type,
            )
        },
        timeout=180,
    )

    response.raise_for_status()
    return response.json()


def api_error_message(error: Exception) -> str:
    if isinstance(error, requests.ConnectionError):
        return (
            f"Could not connect to the ImageTrust API at "
            f"`{ANALYZE_URL}`. Make sure FastAPI is running."
        )

    if isinstance(error, requests.Timeout):
        return "The analysis request timed out. The model may still be processing the image."

    if isinstance(error, requests.HTTPError):
        try:
            detail = error.response.json().get("detail", error.response.text)
        except Exception:
            detail = error.response.text
        return f"ImageTrust API returned an error: {detail}"

    return f"Analysis failed: {error}"


# ---------------------------------------------------------------------
# Header

st.markdown(
    f"""
    <div class="brand-bar">
        <div>
            <img class="brand-logo" src="data:image/png;base64,{logo_b64}">
        </div>
        <div class="nav-pill">AI IMAGE FORENSICS</div>
    </div>

    <div class="hero">
        <div class="hero-kicker">AI IMAGE FORENSICS</div>
        <h1>See the <span class="accent">truth behind</span><br>every image.</h1>
        <p>
            Detect AI-generated images, identify their likely source, and
            uncover forensic details — with ImageTrust.
        </p>
    </div>

    <div class="feature-row">
        <div class="feature"><div class="feature-icon">✓</div><div><div class="feature-title">AI Detection</div><div class="feature-copy">Real or AI-generated</div></div></div>
        <div class="feature"><div class="feature-icon">▦</div><div><div class="feature-title">Generator Attribution</div><div class="feature-copy">Identify AI source</div></div></div>
        <div class="feature"><div class="feature-icon">⌕</div><div><div class="feature-title">Digital Forensics</div><div class="feature-copy">In-depth analysis</div></div></div>
        <div class="feature"><div class="feature-icon">◈</div><div><div class="feature-title">Provenance Analysis</div><div class="feature-copy">More context. More trust.</div></div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------
# Upload / preview
# ---------------------------------------------------------------------

left, right = st.columns([1.05, 0.95], gap="large")

with left:
    st.markdown(
        """
        <div class="upload-card">
            <div class="card-kicker">Image analysis</div>
            <div class="card-title">Analyze an image</div>
            <div class="card-copy">
                Supported image formats are accepted. ImageTrust will run the
                detector and, when appropriate, generator attribution models.
            </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload image",
        type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"],
        label_visibility="collapsed",
    )

    analyze_clicked = st.button(
        "Analyze Image",
        type="primary",
        disabled=uploaded_file is None,
    )

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    if uploaded_file is not None:
        st.markdown(
            '<div class="card-kicker" style="margin-bottom:8px;">Preview</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="preview-card">', unsafe_allow_html=True)
        st.image(uploaded_file, use_container_width=True)
        st.markdown(
            f'<div class="preview-caption">{html.escape(uploaded_file.name)}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">↑</div>
                <div class="empty-title">Ready for analysis</div>
                <div class="empty-copy">
                    Upload an image to see its ImageTrust assessment and
                    supporting model results.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------

if analyze_clicked and uploaded_file is not None:
    with st.spinner("Analyzing image with ImageTrust models..."):
        try:
            st.session_state["analysis_result"] = analyze_image(uploaded_file)
            st.session_state["analysis_filename"] = uploaded_file.name
        except Exception as error:
            st.session_state.pop("analysis_result", None)
            st.error(api_error_message(error))


result = st.session_state.get("analysis_result")


# ---------------------------------------------------------------------
# Result helpers
# ---------------------------------------------------------------------

def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def confidence_label(probabilities: dict) -> tuple[str, str]:
    """Describe confidence from the distribution without inventing a new verdict."""
    values = sorted(
        [(str(k), safe_float(v)) for k, v in (probabilities or {}).items()],
        key=lambda x: x[1],
        reverse=True,
    )
    if not values:
        return "Confidence unavailable", "The model probability distribution was not returned."

    top_name, top_prob = values[0]
    second_prob = values[1][1] if len(values) > 1 else 0.0
    margin = top_prob - second_prob

    if top_prob >= 0.80 and margin >= 0.50:
        return "High confidence", f"{pretty_label(top_name)} is strongly separated from the alternatives."
    if top_prob >= 0.60 and margin >= 0.20:
        return "Moderate confidence", f"{pretty_label(top_name)} leads, but other classes retain some probability."
    return "Limited confidence", "The probability distribution is relatively spread out; treat the classification as less decisive."


def provenance_status(provenance: dict) -> tuple[str, str, str]:
    # Normalize optional provenance blocks so missing data never breaks the UI.
    exif = provenance.get("exif") or {}
    xmp = provenance.get("xmp") or {}
    c2pa = provenance.get("c2pa") or {}

    if c2pa.get("verified") is True:
        return "Verified provenance", "C2PA credentials were successfully verified.", "verified"
    if c2pa.get("analysis_error"):
        return "C2PA unavailable", "C2PA provenance could not be read from this file.", "warning"
    if c2pa.get("present") is False and not exif.get("present") and not xmp.get("present"):
        return "No provenance metadata found", "No EXIF, XMP, or C2PA provenance was available in this file.", "neutral"
    if exif.get("present") or xmp.get("present"):
        return "Metadata found", "The file contains EXIF and/or XMP metadata. Metadata presence does not prove authenticity.", "neutral"
    return "Provenance not verified", "No verified provenance signal was available.", "neutral"


# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

if result:
    verdict_key = str(result.get("verdict", "unknown"))
    verdict_labels = {
        "likely_ai_generated": "Likely AI-Generated",
        "likely_real": "Likely Real",
    }
    verdict = verdict_labels.get(verdict_key, pretty_label(verdict_key))
    confidence = safe_float(result.get("confidence"))

    # Prefer the top-level probabilities; fall back to the nested model response.
    probabilities = result.get("probabilities") or {}
    if not probabilities:
        probabilities = (result.get("model_predictions") or {}).get("probabilities") or {}

    # Keep model-specific fields separate from the final user-facing verdict.
    model_predictions = result.get("model_predictions") or {}
    likely_generator = result.get("likely_generator") or model_predictions.get("label")
    model_name = model_predictions.get("model_name", "Not specified")

    conf_label, conf_detail = confidence_label(probabilities)

    if verdict_key == "likely_ai_generated":
        verdict_class, verdict_icon = "ai", "AI"
        verdict_subtitle = "The available model evidence is more consistent with an AI-generated image."
    elif verdict_key == "likely_real":
        verdict_class, verdict_icon = "real", "✓"
        verdict_subtitle = "The available model evidence is more consistent with a real image."
    else:
        verdict_class, verdict_icon = "uncertain", "?"
        verdict_subtitle = "The API returned a classification that is not one of the standard ImageTrust verdicts."

    # Main assessment
    st.markdown(
        f"""
        <div class="verdict-card {verdict_class}">
            <div class="verdict-main">
                <div class="verdict-icon">{verdict_icon}</div>
                <div>
                    <div class="eyebrow">ImageTrust assessment</div>
                    <div class="verdict-title">{html.escape(verdict)}</div>
                    <div class="verdict-subtitle">{html.escape(verdict_subtitle)}</div>
                </div>
            </div>
            <div class="confidence">
                <div class="confidence-label">MODEL CONFIDENCE</div>
                <div class="confidence-value">{confidence:.1%}</div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width:{max(0, min(100, confidence * 100)):.1f}%"></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Confidence interpretation
    st.markdown(
        f"""
        <div class="confidence-note">
            <div class="confidence-note-title">{html.escape(conf_label)}</div>
            <div class="confidence-note-copy">{html.escape(conf_detail)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Key findings
    st.markdown('<div class="section-title">Key findings</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-description">The most useful signals from this assessment, presented before the technical details.</div>',
        unsafe_allow_html=True,
    )

    likely_generator_text = html.escape(str(likely_generator)) if likely_generator else "Not identified"
    generator_prob = safe_float(probabilities.get(likely_generator, 0)) if likely_generator else 0.0

    forensics = result.get("forensics") or {}
    file_info = forensics.get("file") or {}
    image_info = forensics.get("image") or {}
    resampling = forensics.get("resampling") or {}
    resizing = forensics.get("resizing") or {}
    frequency = forensics.get("frequency") or {}
    compression = forensics.get("compression") or {}
    noise = forensics.get("noise") or {}
    quality = forensics.get("quality") or {}
    provenance = forensics.get("provenance") or {}
    ela = forensics.get("ela") or {}

    p_status, p_detail, p_kind = provenance_status(provenance)

        # Key findings
    card_data = [
        (
            "Likely generator",
            str(likely_generator) if likely_generator else "Not identified",
            f"{generator_prob:.1%} probability"
            if likely_generator
            else "No attribution returned",
        ),
        (
            "Resampling signal",
            f"{safe_float(resampling.get('resampling_score')):.3f}",
            "Higher values indicate stronger resampling evidence",
        ),
        (
            "Provenance",
            p_status,
            p_detail,
        ),
    ]

    cards_html = '<div class="key-findings-grid">'

    for label, value, detail in card_data:
        cards_html += (
            '<div class="metric key-finding-card">'
            f'<div class="metric-label">{html.escape(str(label))}</div>'
            f'<div class="metric-value">{html.escape(str(value))}</div>'
            f'<div class="metric-detail">{html.escape(str(detail))}</div>'
            '</div>'
        )

    cards_html += "</div>"

    st.markdown(cards_html, unsafe_allow_html=True)

    # Probability distribution
    st.markdown('<div class="section-title">Model probability distribution</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-description">These probabilities show how the attribution model distributed its prediction across supported classes. They are evidence, not proof of origin.</div>',
        unsafe_allow_html=True,
    )

    preferred_order = ["Real", "SD21", "SDXL", "SD3", "DALLE3", "Midjourney"]
    probability_items = [(name, safe_float(probabilities.get(name, 0))) for name in preferred_order]
    probability_items += [
        (str(name), safe_float(prob))
        for name, prob in probabilities.items()
        if str(name) not in preferred_order
    ]

    prob_cols = st.columns(3)
    for i, (name, prob) in enumerate(probability_items):
        with prob_cols[i % 3]:
            st.markdown(
                f"""
                <div class="prob-card">
                    <div class="prob-top">
                        <span class="prob-name">{html.escape(name)}</span>
                        <span class="prob-value">{prob:.2%}</span>
                    </div>
                    <div class="prob-track"><div class="prob-fill" style="width:{max(0, min(100, prob*100)):.2f}%"></div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Provenance
    st.markdown('<div class="section-title">Provenance & authenticity context</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-description">Metadata can provide useful context, but its absence does not establish that an image is real or AI-generated.</div>',
        unsafe_allow_html=True,
    )

    exif = provenance.get("exif") or {}
    xmp = provenance.get("xmp") or {}
    c2pa = provenance.get("c2pa") or {}

    def add_detail(items, label, value):
        if value is not None and str(value).strip():
            items.append((label, str(value)))

    def c2pa_status():
        if c2pa.get("verified") is True:
            return "Verified"
        if c2pa.get("present") is True:
            return "Present"
        if c2pa.get("present") is False:
            return "Not detected"
        if c2pa.get("analysis_error"):
            return "Could not read"
        return "Not verified"

    exif_details = []
    camera = exif.get("camera") or {}
    add_detail(exif_details, "Camera", camera.get("make"))
    add_detail(exif_details, "Model", camera.get("model"))
    add_detail(exif_details, "Software", camera.get("software"))
    add_detail(exif_details, "Date / time", camera.get("date_time"))

    for name, value in (exif.get("fields") or {}).items():
        if name in {"Make", "Model", "Software", "DateTime"}:
            continue
        if len(exif_details) >= 8:
            break
        add_detail(exif_details, pretty_label(name), value)

    xmp_details = []
    for name, value in (xmp.get("fields") or {}).items():
        if len(xmp_details) >= 8:
            break
        add_detail(xmp_details, pretty_label(name), value)

    c2pa_details = []
    manifest = c2pa.get("active_manifest_summary") or {}
    signature = manifest.get("signature") or {}
    add_detail(c2pa_details, "Signature issuer", signature.get("issuer"))

    def provenance_card(label, status, details, empty_message):
        if details:
            body = "".join(
                f'<div class="detail-row"><span>{html.escape(str(k))}</span>'
                f'<strong>{html.escape(str(v))}</strong></div>'
                for k, v in details
            )
        else:
            body = f'<div class="metric-detail">{html.escape(empty_message)}</div>'

        return (
            f'<div class="metric provenance-card">'
            f'<div class="metric-label">{html.escape(label)}</div>'
            f'<div class="metric-value">{html.escape(status)}</div>'
            f'{body}'
            f'</div>'
        )

    if c2pa.get("present") is False:
        c2pa_empty = "No C2PA content credentials were detected."
    elif c2pa.get("analysis_error"):
        c2pa_empty = "C2PA provenance could not be read from this file."
    else:
        c2pa_empty = "No verified C2PA details were available."

    # Render all provenance cards inside one fixed-row CSS grid so their
    # heights remain identical regardless of metadata length or font size.
    provenance_cards_html = f'''
        <div class="provenance-grid">
            {provenance_card(
                "EXIF",
                "Present" if exif.get("present") else "Not detected",
                exif_details,
                "No camera or EXIF metadata was detected.",
            )}
            {provenance_card(
                "XMP",
                "Present" if xmp.get("present") else "Not detected",
                xmp_details,
                "No XMP metadata was detected.",
            )}
            {provenance_card(
                "C2PA",
                c2pa_status(),
                c2pa_details,
                c2pa_empty,
            )}
        </div>
    '''

    st.markdown(provenance_cards_html, unsafe_allow_html=True)

    # Forensics
    st.markdown('<div class="section-title">Digital forensics</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-description">Supporting image-level signals. These indicators can arise from generation or ordinary post-processing and should not be interpreted in isolation.</div>',
        unsafe_allow_html=True,
    )

    forensic_cols = st.columns(3)
    forensic_items = [
        ("Image quality", [
            ("Sharpness", f"{safe_float(quality.get('sharpness_score')):.2f}"),
            ("Contrast", f"{safe_float(quality.get('contrast')):.2f}"),
            ("Entropy", f"{safe_float(quality.get('entropy')):.4f}"),
        ]),
        ("Frequency characteristics", [
            ("High-frequency ratio", f"{safe_float(frequency.get('high_frequency_ratio')):.4%}"),
            ("DCT high-frequency ratio", f"{safe_float(compression.get('dct', {}).get('high_frequency_dct_ratio')):.4%}"),
            ("High-frequency energy", f"{safe_float(frequency.get('high_frequency_energy')):,.0f}"),
        ]),
        ("Resampling & resizing", [
            ("Resampling score", f"{safe_float(resampling.get('resampling_score')):.3f}"),
            ("Interpolation error", f"{safe_float(resampling.get('interpolation_error')):.4f}"),
            ("Reconstruction error", f"{safe_float(resizing.get('reconstruction_error')):.4f}"),
        ]),
        ("Noise", [
            ("Noise standard deviation", f"{safe_float(noise.get('noise_std')):.3f}"),
            ("Spatial noise std", f"{safe_float(noise.get('noise_spatial_std')):.4f}"),
            ("Noise median", f"{safe_float(noise.get('noise_median')):.3f}"),
        ]),
        ("Compression", [
            ("JPEG detected", "Yes" if compression.get("jpeg_detected") else "No"),
            ("JPEG quality", str(compression.get("estimated_jpeg_quality") or "N/A")),
            ("Block artifact score", f"{safe_float(compression.get('block_artifact_score')):.3f}"),
        ]),
        ("ELA / double compression", [
            ("ELA", "Available" if ela.get("applicable") else "Not applicable"),
            ("Double compression", "Detected" if (forensics.get("double_compression") or {}).get("double_compression_indicator") else "Not detected"),
            ("Format", str(file_info.get("file_format") or "Unknown")),
        ]),
    ]

    for idx, (title, items) in enumerate(forensic_items):
        with forensic_cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                for label, value in items:
                    st.markdown(
                        f'<div class="detail-row"><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong></div>',
                        unsafe_allow_html=True,
                    )

    # File and image metadata
    st.markdown('<div class="section-title">File & image details</div>', unsafe_allow_html=True)
    metadata_cols = st.columns(2)
    with metadata_cols[0]:
        with st.container(border=True):
            st.markdown("**File**")
            st.markdown(
                f"""
                <div class="detail-row"><span>Filename</span><strong>{html.escape(str(file_info.get("file_name") or st.session_state.get("analysis_filename", "Unknown")))}</strong></div>
                <div class="detail-row"><span>Format</span><strong>{html.escape(str(file_info.get("file_format") or "Unknown"))}</strong></div>
                <div class="detail-row"><span>File size</span><strong>{safe_float(file_info.get("file_size_bytes"))/1024:.1f} KB</strong></div>
                """,
                unsafe_allow_html=True,
            )
    with metadata_cols[1]:
        with st.container(border=True):
            st.markdown("**Image**")
            st.markdown(
                f"""
                <div class="detail-row"><span>Dimensions</span><strong>{html.escape(str(image_info.get("width") or "—"))} × {html.escape(str(image_info.get("height") or "—"))}</strong></div>
                <div class="detail-row"><span>Channels</span><strong>{html.escape(str(image_info.get("channels") or "—"))}</strong></div>
                <div class="detail-row"><span>Aspect ratio</span><strong>{safe_float(image_info.get("aspect_ratio")):.4f}</strong></div>
                """,
                unsafe_allow_html=True,
            )

    # LLM report
    llm_report = result.get("llm_report")
    st.markdown('<div class="section-title">Assessment report</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-description">A human-readable synthesis of the model and forensic evidence.</div>',
        unsafe_allow_html=True,
    )

    if llm_report:
        report_html = markdown_to_html(str(llm_report))
    else:
        report_html = f"<p>{html.escape(str(result.get('explanation', 'No explanation was provided.')))}</p>"

    st.markdown(
        f"""
        <div class="report">
            <div class="report-header">
                <div class="report-icon">IT</div>
                <div>
                    <div class="report-title">ImageTrust Assessment</div>
                    <div class="report-subtitle">Automated evidence synthesis</div>
                </div>
            </div>
            <div class="report-body">{report_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Technical output
    st.markdown('<div class="section-title">Technical output</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-description">Raw API structures for debugging, validation, and advanced review.</div>',
        unsafe_allow_html=True,
    )
    with st.expander("Raw model output", expanded=False):
        st.json(model_predictions)
    with st.expander("Raw forensics output", expanded=False):
        st.json(forensics)
    with st.expander("Complete API response", expanded=False):
        st.json(result)


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------

st.markdown(
    """
    <div class="footer">
        ImageTrust · AI Image Detection · Generator Attribution · Digital Forensics · Provenance Analysis
    </div>
    """,
    unsafe_allow_html=True,
)
