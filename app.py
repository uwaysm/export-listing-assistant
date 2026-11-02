"""Streamlit entry point. Run with: streamlit run app.py."""
import os
import streamlit as st
from openai import APIError, AuthenticationError, RateLimitError
from pydantic import ValidationError
from export_listing.examples import DEMO_PRODUCT, EXAMPLES, demo_drafts
from export_listing.generator import GenerationError, email_text, generate, listing_text
from export_listing.models import FIELD_GUIDANCE, LABELS, Product, checklist

st.set_page_config(page_title="Export Listing Assistant", page_icon="🌱", layout="wide")
st.markdown("""<style>
.block-container {max-width:1480px;padding-top:2.4rem;padding-bottom:3rem}
h1 {font-size:clamp(2rem, 4vw, 3.2rem)!important;letter-spacing:-.065em;line-height:1.08!important}
h2,h3 {letter-spacing:-.035em}
[data-testid="stMetricValue"] {font-size:1.5rem}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:16px}
.hero-tag {font-size:.72rem;letter-spacing:.18em;font-weight:700;color:#467459;margin-bottom:18px}
.hero-copy {font-size:1.05rem;color:#647369;max-width:650px;line-height:1.7}
.topline {display:flex;justify-content:space-between;border-bottom:1px solid #dce2d4;padding-bottom:16px;margin-bottom:32px;font-size:.82rem;font-weight:600}
.small-tag {color:#6a795e;font-weight:400}
.footer {margin-top:28px;border-top:1px solid #dce2d4;padding-top:16px;color:#697569;font-size:.8rem}
</style>""", unsafe_allow_html=True)
st.markdown('<div class="topline"><span>🌱 &nbsp; EXPORT LISTING ASSISTANT</span><span class="small-tag">Grown here. Shared worldwide.</span></div>', unsafe_allow_html=True)


def setting(name, default=""):
    if name in os.environ:
        return os.environ[name]
    try:
        return st.secrets.get(name, default)
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return default


api_key = setting("OPENAI_API_KEY")
live_enabled = str(setting("ENABLE_LIVE_GENERATION", "false")).lower() == "true" and bool(api_key)

with st.sidebar:
    st.markdown("### From farm to first contact")
    st.caption("A focused drafting workspace for Australian growers and exporters.")
    st.divider()
    mode = st.radio("Workspace", ["Demo preview", "Live generation"],
                    help="The demo is a fixed illustrative example. Live mode uses your configured OpenAI key.")
    st.caption("English · Bahasa Indonesia · 简体中文")
    st.divider()
    st.markdown("**How it works**")
    st.markdown("1. Describe your product\n2. Create three language drafts\n3. Review details before sending")
    st.caption("No database. Drafts remain in this browser session. In live mode, submitted product details are sent to OpenAI.")
    if mode == "Live generation" and not live_enabled:
        st.info("Live generation is not configured. See the README to enable it, or explore the demo.")

st.markdown('<div class="hero-tag">AUSTRALIAN PRODUCE → ASIAN MARKETS</div>', unsafe_allow_html=True)
st.title("Your next market starts with the right words.")
st.markdown('<p class="hero-copy">Turn product details into a buyer-ready first draft. Three languages, a clear offer, and fewer details left behind.</p>', unsafe_allow_html=True)
st.write("")

is_demo = mode == "Demo preview"
if is_demo:
    st.info("Demo preview · Fictional mango inventory, prewritten sample copy. No API key or API calls required.")
else:
    st.caption("AI drafts require factual and native-speaker review. No market-access or compliance assessment is performed.")

left, right = st.columns([1, 2.05], gap="large")
with left:
    st.subheader("01 / Product details")
    if not is_demo:
        sample_name = st.selectbox("Start with an example", list(EXAMPLES))
        st.caption("Illustrative fixtures, not real supplier offers.")
        initial = EXAMPLES[sample_name]
    else:
        sample_name = "WA mangoes"
        initial = DEMO_PRODUCT
    with st.form(f"product_{mode}_{sample_name}"):
        fields = {}
        fields["product_name"] = st.text_input("Product name *", initial.product_name, max_chars=120, disabled=is_demo)
        fields["target_market"] = st.text_input("Target market *", initial.target_market, max_chars=120, disabled=is_demo)
        for field in ["variety", "grade", "volume", "packaging", "origin", "shipping_window", "certifications", "price"]:
            fields[field] = st.text_input(LABELS[field], getattr(initial, field),
                                         max_chars=300 if field == "certifications" else 200, disabled=is_demo,
                                         help=FIELD_GUIDANCE[field])
        with st.expander("Buyer details · optional"):
            for field in ["phytosanitary", "shelf_life", "moq", "incoterms"]:
                fields[field] = st.text_input(LABELS[field], max_chars=200, disabled=is_demo,
                                             help=FIELD_GUIDANCE[field])
        submitted = st.form_submit_button("View sample drafts" if is_demo else "Generate three language drafts →",
                                         type="primary", use_container_width=True,
                                         disabled=not is_demo and not live_enabled)
    st.caption("Required fields are marked with an asterisk. Unknown details stay unknown.")

if submitted and not is_demo:
    # Clear stale results before attempting a different product.
    st.session_state.pop("live_result", None)
    try:
        product = Product(**fields)
        with st.spinner("Preparing your three language drafts…"):
            drafts = generate(product, api_key, setting("OPENAI_MODEL", "gpt-4o-mini"))
        st.session_state.live_result = (product, drafts)
    except ValidationError:
        st.error("Enter a product name and target market. Check that your details fit the field limits.")
    except AuthenticationError:
        st.error("The API key was not accepted. Check the server's OpenAI configuration.")
    except RateLimitError:
        st.error("The API usage limit was reached. Check your OpenAI quota or try again later.")
    except GenerationError as exc:
        st.error(str(exc))
    except APIError:
        st.error("The generation service could not complete the request. Please try again shortly.")

result = (DEMO_PRODUCT, demo_drafts()) if is_demo else st.session_state.get("live_result")
with right:
    st.subheader("02 / Your export drafts")
    if result is None:
        with st.container(border=True):
            st.markdown("### A new market. A clear introduction.")
            st.write("Add your product details, then generate a listing and first-contact email in all three languages.")
            st.caption("Your export readiness checklist will appear here too.")
    else:
        product, drafts = result
        st.caption(f"Draft snapshot: {product.product_name} · {product.target_market} · {product.origin or 'Origin not supplied'}")
        if not is_demo:
            st.caption("Form edits are applied when you generate again. The snapshot above identifies the displayed draft.")
        from export_listing.exports import export_pack
        st.download_button("Download complete draft pack ↓", export_pack(product, drafts, is_demo),
                           file_name="export-draft-pack.zip", mime="application/zip")
        view = st.radio("Reading layout", ["Language tabs", "Side by side"], horizontal=True, label_visibility="collapsed")
        names = ["English", "Bahasa Indonesia", "简体中文"]
        panes = st.tabs(names) if view == "Language tabs" else st.columns(3)
        for pane, language, name in zip(panes, ["en", "id", "zh"], names):
            draft = getattr(drafts, language)
            with pane:
                if view == "Side by side":
                    st.markdown(f"**{name}**")
                with st.container(border=True):
                    st.caption("PRODUCT LISTING")
                    st.subheader(draft.listing.title)
                    st.write(draft.listing.description)
                    st.dataframe([{"Specification": s.label, "Detail": s.value} for s in draft.listing.specs],
                                 hide_index=True, use_container_width=True)
                    for point in draft.listing.selling_points:
                        st.write(f"• {point}")
                    with st.expander("Copy listing"):
                        st.caption("Use the copy icon in the top-right corner of the text below.")
                        st.code(listing_text(draft), language=None, wrap_lines=True)
                with st.container(border=True):
                    st.caption("BUYER EMAIL")
                    st.markdown(f"**{draft.email.subject}**")
                    st.text(draft.email.body)
                    with st.expander("Copy email"):
                        st.code(email_text(draft), language=None, wrap_lines=True)
                st.download_button(f"Download {name} draft", listing_text(draft) + "\n\n" + email_text(draft),
                                   file_name=f"export-draft-{language}.txt", mime="text/plain", key=f"download_{language}")
        st.write("")
        st.subheader("03 / Before you contact a buyer")
        checks = checklist(product)
        missing = sum(item.status == "missing" for item in checks)
        st.warning(f"{missing} details to confirm · This is a completeness checklist, not legal advice or export clearance.")
        with st.expander("Review export readiness", expanded=True):
            checks = sorted(checks, key=lambda item: item.status != "missing")
            for item in checks:
                icon = "○" if item.status == "missing" else "✓"
                st.markdown(f"{icon} **{item.item}** · {'Missing' if item.status == 'missing' else 'Supplied, not verified'}")
                st.caption(item.note)
        st.caption("Confirm destination-specific requirements with your importer and relevant authorities. Review all translations and claims before use.")

st.markdown('<div class="footer">Built for the first conversation. &nbsp; English / Bahasa Indonesia / 简体中文 &nbsp; · &nbsp; Python + Streamlit + OpenAI</div>', unsafe_allow_html=True)
