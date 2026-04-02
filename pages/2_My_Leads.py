import streamlit as st
from utils import inject_global_styles, init_session, render_sidebar, require_login, fetch_all_leads, normalize_leads

st.set_page_config(page_title="My Leads", page_icon="📊", layout="wide")

inject_global_styles()

page_css = """
<style>
.stApp {
    background: #0f172a;
}
.app-card {
    background: #111827 !important;
    border: 1px solid #3730a3 !important;
}
.lead-card {
    background: #111827 !important;
    border: 1px solid #3730a3 !important;
    padding: 20px;
    border-radius: 20px;
    margin-bottom: 18px;
}
.lead-name {
    color: #ffffff !important;
    font-weight: 700;
}
.lead-details {
    color: #cbd5e1 !important;
}
.lead-url a {
    color: #a5b4fc !important;
    text-decoration: none;
}
.lead-url a:hover {
    text-decoration: underline;
}
.app-badge {
    color: #ffffff !important;
}
.badge-hot { background: #f97316 !important; }
.badge-warm { background: #a855f7 !important; }
.badge-cold { background: #22c55e !important; }
.badge-unknown { background: #475569 !important; color: #f8fafc !important; }
</style>
"""
st.markdown(page_css, unsafe_allow_html=True)

init_session()
render_sidebar()
require_login()

st.markdown("<div class='app-card'>", unsafe_allow_html=True)
st.markdown("<div class='app-title'>My Leads</div>", unsafe_allow_html=True)
st.markdown("<div class='app-subtitle'>Review your saved leads and track outreach readiness.</div>", unsafe_allow_html=True)

records = fetch_all_leads()
leads = normalize_leads(records)

col1, col2 = st.columns([1, 3])
with col1:
    st.metric("Total leads", len(leads))
with col2:
    st.write(" ")

st.markdown("</div>", unsafe_allow_html=True)

if not leads:
    st.info("No leads found yet. Analyze a lead first to store leads in Google Sheets.")
else:
    def badge_html(score):
        value = (score or "").strip()
        normalized = value.upper()

        if "HOT" in normalized:
            return "<span class='app-badge badge-hot'>HOT</span>"
        if "WARM" in normalized:
            return "<span class='app-badge badge-warm'>WARM</span>"
        if "COLD" in normalized:
            return "<span class='app-badge badge-cold'>COLD</span>"
        if normalized:
            return f"<span class='app-badge badge-unknown'>{value}</span>"
        return ""

    for lead in leads:
        name = lead.get("name", "Unknown")
        company = lead.get("company", "")
        role = lead.get("role", "")
        score = lead.get("score", "")
        date = lead.get("date", "")
        url = lead.get("url", "")

        st.markdown("<div class='lead-card'>", unsafe_allow_html=True)
        row_cols = st.columns([3, 1])
        with row_cols[0]:
            st.markdown(f"<div class='lead-name'>{name}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='lead-details'>{company} • {role}</div>", unsafe_allow_html=True)
            if url:
                st.markdown(f"<div class='lead-url'><a href='{url}' target='_blank'>View Profile</a></div>", unsafe_allow_html=True)
        with row_cols[1]:
            st.markdown(f"<div style='display:flex; justify-content:flex-end; gap:10px; align-items:center;'><span style='color:#cbd5e1; font-size:13px;'>{date}</span>{badge_html(score)}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
