import streamlit as st
from utils import inject_global_styles, init_session, render_sidebar, require_login

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

inject_global_styles()
init_session()
render_sidebar()
require_login()

st.markdown("<div class='app-card'>", unsafe_allow_html=True)
st.markdown("<div class='app-title'>Settings</div>", unsafe_allow_html=True)
st.markdown("<div class='app-subtitle'>Manage your preferences and app behavior.</div>", unsafe_allow_html=True)

st.markdown("<div class='app-card'>", unsafe_allow_html=True)
st.markdown("<strong>Feature roadmap</strong>", unsafe_allow_html=True)
st.markdown("<p class='app-subtitle'>Coming soon: custom templates, user settings, and lead filters.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='app-card'>", unsafe_allow_html=True)
st.markdown("<strong>Integrations</strong>", unsafe_allow_html=True)
st.markdown("<p class='app-subtitle'>Placeholder content for future settings and integrations.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
