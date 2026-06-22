import io
import html as _html
import streamlit as st
import streamlit.components.v1 as components
from core.scrape_article import scrape_article
from llm_generators.generator import generate_response
from llm_generators.img_gen_prompt import get_image_gen_prompt
from core.generate_image import generate_image
from dotenv import load_dotenv
load_dotenv()

# ── Platform config ───────────────────────────────────────────────────────────
PLATFORM_MAP = {
    "LinkedIn":  "linkedin",
    "Instagram": "instagram",
    "Twitter":   "twitter",
    "Facebook":  "facebook",
    "Blog":      "blog post",
}

PLATFORM_META = {
    "LinkedIn":  {"icon": "💼", "color": "#0A66C2", "light": "#EEF5FF", "border": "#0A66C240"},
    "Instagram": {"icon": "📸", "color": "#E1306C", "light": "#FEF0F5", "border": "#E1306C40"},
    "Twitter":   {"icon": "🐦", "color": "#1DA1F2", "light": "#E8F6FE", "border": "#1DA1F240"},
    "Facebook":  {"icon": "📘", "color": "#1877F2", "light": "#EEF4FF", "border": "#1877F240"},
    "Blog":      {"icon": "✍️", "color": "#7C3AED", "light": "#F5F0FF", "border": "#7C3AED40"},
}

STEPS = [
    "Fetching article content",
    "Select Target Platforms",
    "Generating content",
    "Review & Export",
]

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Content Curation Pipeline", page_icon="📝", layout="wide")

# ── Global CSS (injected via st.markdown so it reaches the real DOM) ──────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}
.stApp { background: #F0F4F8 !important; }

/* ── Page title ── */
h1 { font-size: 1.9rem !important; font-weight: 800 !important;
     color: #0F172A !important; letter-spacing: -0.03em !important; }

/* ── Card: use Streamlit's bordered container as the card shell ── */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 6px rgba(15,23,42,0.04), 0 8px 24px rgba(15,23,42,0.06) !important;
    overflow: hidden !important;
    transition: box-shadow 0.25s ease, transform 0.25s ease !important;
    background: #FFFFFF !important;
    margin-bottom: 24px !important;
    padding: 0 !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 6px 20px rgba(15,23,42,0.09), 0 20px 48px rgba(15,23,42,0.10) !important;
    transform: translateY(-2px) !important;
}
/* Kill inner gap/padding — our .pc-header / .pc-body control all spacing */
div[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
    padding: 0 !important;
}

/* ── Card header ── */
.pc-header {
    padding: 16px 24px 15px;
    border-bottom: 1px solid #F1F5F9;
}
.pc-header-name {
    font-size: 1.0rem;
    font-weight: 700;
    color: #0F172A;
    letter-spacing: -0.01em;
}

/* ── Content body: relative so copy btn floats inside ── */
.pc-body {
    position: relative;
    padding: 20px 24px 20px;
    font-size: 0.93rem;
    line-height: 1.85;
    color: #334155;
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Floating copy button ── */
.pc-copy-btn {
    position: absolute;
    top: 14px;
    right: 16px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(248,250,252,0.92);
    border: 1.5px solid #E2E8F0;
    border-radius: 7px;
    padding: 5px 11px;
    font-size: 12px;
    font-weight: 500;
    color: #64748B;
    cursor: pointer;
    font-family: 'Inter', sans-serif;
    transition: all 0.15s ease;
    outline: none;
    white-space: nowrap;
    backdrop-filter: blur(4px);
    z-index: 2;
}
.pc-copy-btn:hover { background: #F1F5F9; border-color: #CBD5E1; color: #1E293B; }
.pc-copy-btn:active { transform: scale(0.97); }

/* ── Section divider ── */
.pc-divider {
    height: 1px;
    background: #F1F5F9;
    margin: 0;
}

/* ── Image inside card: flush, no extra border-radius ── */
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stImage"] {
    line-height: 0;
    margin: 0 !important;
    padding: 0 !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stImage"] > img {
    display: block !important;
    width: 100% !important;
    border-radius: 0 !important;
}

/* ── Button row (download + regenerate / generate) ── */
div[data-testid="stVerticalBlockBorderWrapper"] > div > div[data-testid="stHorizontalBlock"] {
    padding: 12px 20px 16px !important;
    gap: 12px !important;
    border-top: 1px solid #F1F5F9 !important;
}

/* ── Error card ── */
.pc-error {
    background: #FFF5F5;
    border: 1px solid #FED7D7;
    border-left: 4px solid #FC8181;
    border-radius: 10px;
    padding: 14px 18px;
    color: #C53030;
    font-size: 0.9rem;
    margin-bottom: 24px;
}

/* ── Streamlit native overrides ── */
div[data-testid="stButton"] button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    transition: all 0.15s ease !important;
}
div[data-testid="stDownloadButton"] button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "step_idx" not in st.session_state:
    st.session_state.step_idx = 0
if "platforms" not in st.session_state:
    st.session_state.platforms = []

# ── Timeline sidebar ──────────────────────────────────────────────────────────
def draw_vertical_timeline(steps, active_idx):
    parts = ["<div style='font-family:Inter,sans-serif;padding:16px;background:#fff;"
             "border-radius:12px;border:1px solid #E2E8F0;box-shadow:0 1px 4px rgba(0,0,0,0.04);"
             "margin-bottom:20px;'>"]
    for i, step in enumerate(steps):
        if i < active_idx:
            dot_bg, dot_fg, badge = "#10B981", "#fff", "✓"
            text_css = "color:#64748B;font-size:0.88rem;"
        elif i == active_idx:
            dot_bg, dot_fg, badge = "#6366F1", "#fff", "●"
            text_css = "color:#0F172A;font-weight:600;font-size:0.92rem;"
        else:
            dot_bg, dot_fg, badge = "#E2E8F0", "#94A3B8", "○"
            text_css = "color:#94A3B8;font-size:0.88rem;"

        parts.append(f"""
        <div style='display:flex;align-items:flex-start;margin-bottom:2px;'>
            <div style='display:flex;flex-direction:column;align-items:center;margin-right:14px;'>
                <div style='width:28px;height:28px;border-radius:50%;background:{dot_bg};
                            color:{dot_fg};display:flex;align-items:center;justify-content:center;
                            font-size:12px;font-weight:700;flex-shrink:0;'>
                    {badge}
                </div>
        """)
        if i < len(steps) - 1:
            line_bg = "#10B981" if i < active_idx else "#E2E8F0"
            parts.append(f"<div style='width:2px;height:42px;background:{line_bg};margin-top:2px;'></div>")
        parts.append(f"</div><div style='padding-top:5px;{text_css}'>{step}</div></div>")

    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


# ── Helper: PIL → PNG bytes ───────────────────────────────────────────────────
def _img_to_bytes(pil_image):
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    return buf.getvalue()


# ── Card renderer ─────────────────────────────────────────────────────────────
def render_platform_card(platform, content):
    img_key    = f"{platform}_image"
    prompt_key = f"{platform}_image_prompt"
    has_image  = img_key in st.session_state

    safe_content  = _html.escape(content)
    # Store copy text in a data attribute — html.escape makes it safe in any attribute context.
    # Never embed arbitrary content inside a JS string literal (breaks on quotes, backticks, etc.)
    safe_for_attr = _html.escape(content, quote=True)

    with st.container(border=True):

        # ── Header ────────────────────────────────────────────────────────────
        st.markdown(f"""
<div class="pc-header">
    <span class="pc-header-name">{_html.escape(platform)}</span>
</div>""", unsafe_allow_html=True)

        # ── Content with floating copy button ─────────────────────────────────
        # The copy text lives in data-copy; JS reads it via getAttribute — no injection risk.
        st.markdown(f"""
<div class="pc-body">
    <button class="pc-copy-btn" id="pcb_{platform}"
      data-copy="{safe_for_attr}"
      onclick="(function(b){{
        navigator.clipboard.writeText(b.getAttribute('data-copy'))
          .then(()=>{{
            b.textContent='\u2705 Copied!';
            b.style.color='#059669';b.style.borderColor='#6EE7B7';
            setTimeout(()=>{{b.textContent='📋 Copy';b.style.color='';b.style.borderColor='';}},2000);
          }})
          .catch(()=>{{b.textContent='\u274c Failed';}})
      }})(this)">📋 Copy</button>
    {safe_content}
</div>
<div class="pc-divider"></div>""", unsafe_allow_html=True)

        # ── Image & action buttons ─────────────────────────────────────────────
        if has_image:
            # session_state holds PNG bytes — st.image accepts bytes directly
            st.image(st.session_state[img_key], use_container_width=True)

            dl_col, regen_col = st.columns(2)
            with dl_col:
                st.download_button(
                    label="⬇️ Download Image",
                    data=st.session_state[img_key],  # bytes — no conversion on render
                    file_name=f"{platform.lower()}_image.png",
                    mime="image/png",
                    key=f"dl_{platform}",
                    use_container_width=True,
                )
            with regen_col:
                if st.button("🔄 Regenerate Image", key=f"regen_{platform}",
                             type="secondary", use_container_width=True):
                    with st.spinner("Regenerating image..."):
                        new_img = generate_image(st.session_state[prompt_key])
                    if new_img:
                        st.session_state[img_key] = _img_to_bytes(new_img)
                        st.rerun()
                    else:
                        st.error("Couldn't regenerate the image!")
        else:
            gen_col, _ = st.columns(2)
            with gen_col:
                if st.button("🖼️ Generate Image", key=f"gen_img_{platform}",
                             type="secondary", use_container_width=True):
                    if prompt_key not in st.session_state:
                        with st.spinner("Building image prompt..."):
                            prompt = get_image_gen_prompt(content)
                        if not prompt:
                            st.error("Couldn't generate image prompt!")
                            return
                        st.session_state[prompt_key] = prompt
                    with st.spinner("Generating image..."):
                        image = generate_image(st.session_state[prompt_key])
                    if image:
                        # Convert PIL → bytes at storage time; never store PIL in session_state
                        st.session_state[img_key] = _img_to_bytes(image)
                        st.rerun()
                    else:
                        st.error("Couldn't generate the image!")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ── Page layout ───────────────────────────────────────────────────────────────
st.title("📝 Content Curation")
st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

sidebar_col, main_col = st.columns([1, 2.4], gap="large")

# Left: progress timeline
with sidebar_col:
    st.markdown("**Pipeline progress**")
    draw_vertical_timeline(STEPS, st.session_state.step_idx)

# Right: active step content
with main_col:

    # Back button on final step
    if st.session_state.step_idx == len(STEPS) - 1:
        if st.button("⬅️ Back", type="secondary", help="Go back to platform selection"):
            st.session_state.step_idx = 1
            st.session_state.platforms = []
            st.session_state.generated_content = None
            st.rerun()

    # Current step label
    label = STEPS[st.session_state.step_idx] if st.session_state.step_idx < len(STEPS) else "Pipeline Complete!"
    st.markdown(f"<h3 style='margin-top:0;color:#0F172A;font-weight:700;'>{label}</h3>",
                unsafe_allow_html=True)

    # ── STEP 0: Scrape ───────────────────────────────────────────────────────
    if st.session_state.step_idx == 0:
        st.info("Initiating backend web scrapers…")
        with st.spinner("Fetching article content…"):
            article_content = scrape_article(st.session_state["selected_article_url"])
        if article_content is None:
            st.error("⚠️ Failed to fetch article content. Go back and select a different article.")
        else:
            st.session_state.article_content = article_content
            st.session_state.step_idx = 1
            st.rerun()

    # ── STEP 1: Platform picker ───────────────────────────────────────────────
    elif st.session_state.step_idx == 1:
        st.success("Article content pulled successfully!")
        with st.form("platform_selector_form"):
            selected = st.multiselect(
                "Choose distribution channels:",
                options=list(PLATFORM_MAP.keys()),
                accept_new_options=False,
                help="Select the platforms where you want to publish the content.",
            )
            if st.form_submit_button("Confirm & Proceed →", type="primary"):
                if not selected:
                    st.error("Please select at least one platform.")
                else:
                    st.session_state.platforms = selected
                    st.session_state.step_idx = 2
                    st.rerun()

    # ── STEP 2: Generate content ──────────────────────────────────────────────
    elif st.session_state.step_idx == 2:
        st.info("🤖 AI engine is generating content…")
        with st.spinner("Generating content for selected platforms…"):
            mapped = [PLATFORM_MAP.get(p, p.lower()) for p in st.session_state.platforms]
            st.session_state.generated_content = generate_response(
                st.session_state.article_content, mapped
            )
        st.session_state.step_idx = 3
        st.rerun()

    # ── STEP 3: Review & Export ───────────────────────────────────────────────
    elif st.session_state.step_idx == 3:
        st.success("✨ Content generation complete! Review and export below.")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        for platform in st.session_state.platforms:
            key     = PLATFORM_MAP.get(platform, platform.lower())
            content = st.session_state.generated_content.get_content(key)

            if content:
                render_platform_card(platform, content)
            else:
                st.markdown(f"""
<div class="pc-error">
    ⚠️ Content generation failed for <strong>{_html.escape(platform)}</strong>.
</div>""", unsafe_allow_html=True)
