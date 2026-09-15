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
# Configuration
# ---------------------------------------------------------------------

API_URL = os.getenv(
    "IMAGETRUST_API_URL",
    "http://127.0.0.1:8000",
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg:#030914; --card:#09172d; --border:#1b3154;
        --text:#edf3ff; --muted:#9eafd0; --blue:#6f8cff;
        --blue2:#9aaeff; --green:#62e5b5; --red:#ff7d8a; --amber:#f4c76c;
    }
    html,body,[class*="css"]{font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;}
    .stApp{background:radial-gradient(circle at 80% 0%,rgba(79,101,210,.15),transparent 34rem),radial-gradient(circle at 10% 20%,rgba(75,87,180,.08),transparent 28rem),var(--bg);color:var(--text);}
    .block-container{max-width:1180px;padding-top:1.4rem;padding-bottom:4rem;}
    #MainMenu,footer{visibility:hidden;}
    .brand-bar{display:flex;align-items:center;justify-content:space-between;padding:4px 0 25px;margin-bottom:46px;border-bottom:1px solid rgba(111,140,255,.12);}
    .brand-logo{height:150px;width:170px;display:block;}
    .nav-pill{padding:9px 15px;border:1px solid #21385d;border-radius:9px;background:#09172d;color:#9aaeff;font-size:10px;font-weight:800;letter-spacing:1px;}
    .hero-kicker{color:#7895ff;font-size:10px;font-weight:800;letter-spacing:2px;margin-bottom:10px;}
    .hero h1{margin:0;max-width:760px;color:#edf3ff;font-size:clamp(34px,5vw,54px);line-height:1.03;letter-spacing:-2.4px;font-weight:800;}
    .hero h1 .accent{background:linear-gradient(90deg,#fff,#91a5ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .hero p{max-width:700px;margin:15px 0 0;color:#9eafd0;font-size:14px;line-height:1.75;}
    .feature-row{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:25px 0 30px;}
    .feature{display:flex;align-items:center;gap:10px;min-height:62px;}
    .feature-icon{width:39px;height:39px;flex:0 0 39px;border:1px solid #3556a2;border-radius:11px;background:linear-gradient(145deg,#183d88,#101f47);color:#b8c7ff;display:flex;align-items:center;justify-content:center;font-weight:800;}
    .feature-title{color:#dbe5ff;font-size:12px;font-weight:700}.feature-copy{color:#7f91b2;font-size:10px;margin-top:2px;}
    .upload-card{background:linear-gradient(145deg,rgba(11,27,54,.98),rgba(6,18,37,.98));border:1px solid #203c69;border-radius:18px;padding:23px;box-shadow:0 20px 60px rgba(0,0,0,.22);}
    .card-kicker{color:#7693ff;font-size:10px;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;}
    .card-title{color:#edf3ff;font-size:17px;font-weight:700;margin-top:5px}.card-copy{color:#9eafd0;font-size:12px;line-height:1.6;margin:5px 0 16px;}
    div[data-testid="stFileUploader"]{background:#08152b;border:1px dashed #5275c7;border-radius:14px;padding:7px;}
    div[data-testid="stFileUploader"] section{padding:21px 12px;}
    div[data-testid="stFileUploader"] span,div[data-testid="stFileUploader"] small{color:#a8b8d7!important;}
    div.stButton>button{width:100%;min-height:48px;margin-top:10px;border-radius:11px;border:1px solid #526fc6;background:linear-gradient(135deg,#5574dc,#3554ad);color:white;font-weight:700;box-shadow:0 8px 24px rgba(50,79,170,.22);}
    div.stButton>button:hover{background:linear-gradient(135deg,#6785ed,#4262bd);border-color:#7893ff;color:white;}
    .preview-card{background:#09172d;border:1px solid #1b3154;border-radius:18px;padding:14px}.preview-card img{border-radius:11px}.preview-caption{color:#7184a7;font-size:10px;text-align:center;margin-top:9px;}
    .empty-state{min-height:275px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;background:rgba(7,20,40,.68);border:1px dashed #28446f;border-radius:18px;}
    .empty-icon{width:45px;height:45px;border:1px solid #31529b;border-radius:13px;background:#0e2450;color:#91a6ff;display:flex;align-items:center;justify-content:center;font-size:20px;margin-bottom:12px;}
    .empty-title{color:#dce6ff;font-size:14px;font-weight:700}.empty-copy{max-width:330px;margin-top:6px;color:#7285a7;font-size:11px;line-height:1.55;}
    .verdict-card{margin-top:22px;padding:21px;border:1px solid #237f72;border-radius:17px;background:linear-gradient(110deg,rgba(5,37,38,.98),rgba(7,26,45,.98));display:flex;align-items:center;justify-content:space-between;gap:20px;}
    .verdict-card.ai{border-color:#82404d;background:linear-gradient(110deg,rgba(49,17,28,.98),rgba(15,24,43,.98));}.verdict-card.uncertain{border-color:#80672f;background:linear-gradient(110deg,rgba(47,36,12,.98),rgba(15,24,43,.98));}
    .verdict-main{display:flex;align-items:center;gap:15px;min-width:0}.verdict-icon{width:51px;height:51px;flex:0 0 51px;border:2px solid var(--green);border-radius:50%;background:rgba(65,217,166,.09);color:var(--green);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:800;}
    .ai .verdict-icon{border-color:var(--red);color:var(--red)}.uncertain .verdict-icon{border-color:var(--amber);color:var(--amber)}
    .eyebrow{color:#7588ab;font-size:9px;font-weight:800;letter-spacing:1.2px;text-transform:uppercase}.verdict-title{color:#eaf2ff;font-size:23px;font-weight:800;letter-spacing:-.7px;margin-top:3px}.verdict-subtitle{color:#9bafd1;font-size:11px;line-height:1.5;margin-top:4px;}
    .confidence{min-width:150px;text-align:right}.confidence-label{color:#7690bf;font-size:9px;font-weight:800;letter-spacing:1.1px}.confidence-value{color:var(--green);font-size:25px;font-weight:800;margin-top:2px}.ai .confidence-value{color:var(--red)}.uncertain .confidence-value{color:var(--amber)}
    .confidence-bar{height:7px;margin-top:7px;overflow:hidden;border-radius:99px;background:#1b3154}.confidence-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,#56dcae,#78edc1)}.ai .confidence-fill{background:linear-gradient(90deg,#ff6677,#ff9a9f)}.uncertain .confidence-fill{background:linear-gradient(90deg,#d9aa49,#f5d27e)}
    .metric-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:13px}.metric{background:rgba(8,23,46,.96);border:1px solid #1b3154;border-radius:14px;padding:17px}.metric-label{color:#6f86ae;font-size:9px;font-weight:800;letter-spacing:1px;text-transform:uppercase}.metric-value{color:#e7efff;font-size:17px;font-weight:750;margin-top:7px}.metric-detail{color:#8195b7;font-size:10px;line-height:1.55;margin-top:4px;}
    .section-title{color:#dfe8ff;font-size:15px;font-weight:800;margin:28px 0 6px}.section-description{color:#7387a9;font-size:10px;margin-bottom:10px;}
    div[data-testid="stVerticalBlockBorderWrapper"]{background:linear-gradient(145deg,#0b1b35,#08162b);border-color:#1b3154!important;border-radius:14px!important;}
    div[data-testid="stVerticalBlockBorderWrapper"] p,div[data-testid="stVerticalBlockBorderWrapper"] span,div[data-testid="stVerticalBlockBorderWrapper"] label{color:#c1cee5!important;}
    div[data-testid="stExpander"]{background:linear-gradient(145deg,#0b1b35,#08162b);border:1px solid #1b3154;border-radius:13px;margin-bottom:9px;}
    div[data-testid="stExpander"] summary,div[data-testid="stExpander"] summary span{color:#d8e4ff!important;font-weight:700!important;}
    div[data-testid="stJson"]{background:#061225;border-radius:10px;}
    .report{margin-top:13px;padding:21px;background:linear-gradient(145deg,#0b1b35,#08162b);border:1px solid #1b3154;border-radius:16px}.report-header{display:flex;align-items:center;gap:11px;padding-bottom:14px;border-bottom:1px solid #1a2d4b}.report-icon{width:35px;height:35px;border-radius:10px;background:linear-gradient(145deg,#234b9e,#142e65);color:#c8d4ff;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800}.report-title{color:#e2ebff;font-size:20px;font-weight:800}.report-subtitle{color:#7387aa;font-size:15px;margin-top:2px}.report-body{color:#b1c0da;font-size:16px;line-height:1.75;padding-top:5px}.report-body h2{color:#e3ebff;font-size:14px;margin:18px 0 7px}.report-body h3{color:#c5d1e9;font-size:12px;margin:16px 0 5px}.report-body strong{color:#d8e3fb;}
    .footer{margin-top:38px;padding-top:17px;border-top:1px solid #132541;color:#5e7194;font-size:10px;text-align:center;}
    @media(max-width:760px){.feature-row{grid-template-columns:repeat(2,1fr)}.verdict-card{align-items:flex-start;flex-direction:column}.confidence{text-align:left;width:100%}.metric-grid{grid-template-columns:1fr}.brand-bar{margin-bottom:30px}}
    @media(max-width:480px){.feature-row{grid-template-columns:1fr}}
    </style>
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
# Results
# ---------------------------------------------------------------------

if result:
    verdict_key = result.get("verdict", "uncertain")
    verdict_labels = {
        "likely_ai_generated": "Likely AI-Generated",
        "likely_real": "Likely Real",
    }

    verdict = verdict_labels.get(
        verdict_key,
        pretty_label(verdict_key),
    )

    confidence = result.get("confidence")

    if verdict_key == "likely_ai_generated":
        verdict_class = "ai"
        verdict_icon = "AI"
        verdict_subtitle = (
            "Image characteristics are more consistent with AI generation."
        )
    elif verdict_key == "likely_real":
        verdict_class = "real"
        verdict_icon = "✓"
        verdict_subtitle = (
            "Image characteristics are more consistent with a real image."
        )
    else:
        verdict_class = "uncertain"
        verdict_icon = "?"
        verdict_subtitle = (
            "The available evidence does not strongly favor either conclusion."
        )

    real_ai = result.get("real_vs_ai") or {}
    attribution = result.get("generator_attribution") or {}
    forensics = result.get("forensics") or {}

    detector_label = pretty_label(real_ai.get("label"))
    detector_confidence = real_ai.get("confidence")

    attribution_label = pretty_label(attribution.get("label"))
    attribution_confidence = attribution.get("confidence")

    generator = result.get("likely_generator")
    generator_confidence = result.get("generator_confidence")

    if verdict_key == "likely_ai_generated" and generator:
        generator_value = html.escape(str(generator))
        generator_detail = (
            f"Attribution confidence: {pct(generator_confidence)}"
        )
    elif verdict_key == "likely_ai_generated":
        generator_value = "Unknown"
        generator_detail = (
            "No supported generator matched with sufficient confidence."
        )
    else:
        generator_value = "Not applicable"
        generator_detail = "Generator attribution is shown for AI-generated findings."

    st.markdown(
        f"""
        <div class="verdict-card {verdict_class}">
            <div class="verdict-main">
                <div class="verdict-icon">{verdict_icon}</div>
                <div>
                    <div class="eyebrow">ImageTrust assessment</div>
                    <div class="verdict-title">{html.escape(verdict)}</div>
                    <div class="verdict-subtitle">
                        {html.escape(verdict_subtitle)}
                    </div>
                </div>
            </div>
            <div class="confidence">
                <div class="confidence-label">CONFIDENCE</div>
                <div class="confidence-value">{pct(confidence)}</div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width:{max(0, min(100, (confidence or 0) * 100)):.1f}%"></div>
                </div>
            </div>
        </div>

        <div class="metric-grid">
            <div class="metric">
                <div class="metric-label">Classification</div>
                <div class="metric-value">{html.escape(detector_label)}</div>
                <div class="metric-detail">
                    Detector confidence: {pct(detector_confidence)}
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Likely generator</div>
                <div class="metric-value">{generator_value}</div>
                <div class="metric-detail">{html.escape(generator_detail)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Model results
    st.markdown(
        """
        <div class="section-title">Model analysis</div>
        <div class="section-description">
            Detailed outputs from the image detector and generator attribution model.
        </div>
        """,
        unsafe_allow_html=True,
    )

    model_col1, model_col2 = st.columns(2)

    with model_col1:
        with st.container(border=True):
            st.markdown("**Real vs AI**")
            st.caption("Primary image classification")
            st.write("Prediction", detector_label)
            st.write("Confidence", pct(detector_confidence))

    with model_col2:
        with st.container(border=True):
            st.markdown("**Generator Attribution**")
            st.caption("Supported-source similarity")
            st.write("Prediction", attribution_label)
            st.write("Confidence", pct(attribution_confidence))

    # LLM report
    llm_report = result.get("llm_report")

    st.markdown(
        '<div class="section-title">Assessment report</div>',
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
                    <div class="report-subtitle">Automated evidence summary</div>
                </div>
            </div>
            <div class="report-body">
                {report_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Full Explanation", expanded=False):
        st.markdown(
            str(result.get("explanation", "No explanation was provided."))
        )

    # Technical details
    st.markdown(
        '<div class="section-title">Technical details</div>',
        unsafe_allow_html=True,
    )

    technical_col1, technical_col2 = st.columns(2)

    with technical_col1:
        with st.expander("Model results", expanded=False):
            st.json(
                {
                    "real_vs_ai": real_ai,
                    "generator_attribution": attribution,
                }
            )

    with technical_col2:
        with st.expander("Digital forensics", expanded=False):
            st.json(forensics)


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------

st.markdown(
    """
    <div class="footer">
        ImageTrust · AI Image Detection · Generator Attribution · Digital Forensics
    </div>
    """,
    unsafe_allow_html=True,
)
