import streamlit as st
from utils import init_session, render_sidebar, require_login, inject_global_styles

st.set_page_config(page_title="AI CRM", page_icon="🚀", layout="wide")

inject_global_styles()
init_session()
render_sidebar()
require_login()

st.markdown("<div class='app-card'>", unsafe_allow_html=True)
st.markdown("<div class='app-title'>Welcome back</div>", unsafe_allow_html=True)
st.markdown("<div class='app-subtitle'>You are logged in. Use the sidebar to access Analyze Lead, My Leads, or Settings.</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
