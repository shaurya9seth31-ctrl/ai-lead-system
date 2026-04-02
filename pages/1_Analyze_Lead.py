import streamlit as st
from utils import inject_global_styles, init_session, render_sidebar, require_login, analyze_lead

st.set_page_config(page_title="Analyze Lead", page_icon="🧠", layout="wide")

inject_global_styles()

page_css = """
<style>
.stApp {
    background: #0f172a;
}
input[type='text'], textarea {
    background: #1f2937 !important;
    color: #f8fafc !important;
    border: 1px solid #4b5563 !important;
    caret-color: #f8fafc !important;
}
textarea {
    min-height: 220px;
}
input::placeholder, textarea::placeholder {
    color: #94a3b8 !important;
}
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background: #1f2937 !important;
    color: #f8fafc !important;
}
.stButton>button {
    border-radius: 14px !important;
    background-color: #7c3aed !important;
    color: #ffffff !important;
    border: 1px solid #7c3aed !important;
}
.stButton>button:hover {
    background-color: #9333ea !important;
}
.app-card {
    background: #111827 !important;
    border: 1px solid #3730a3 !important;
}
.message-box {
    background: #111827 !important;
    border: 1px solid #3730a3 !important;
    color: #f8fafc !important;
}
.app-title {
    color: #f8fafc !important;
}
.app-subtitle {
    color: #c7d2fe !important;
}
</style>
"""
st.markdown(page_css, unsafe_allow_html=True)

init_session()
render_sidebar()
require_login()

st.markdown("<div class='app-card'>", unsafe_allow_html=True)
st.markdown("<div class='app-title'>Analyze Lead</div>", unsafe_allow_html=True)
st.markdown("<div class='app-subtitle'>Paste a full LinkedIn profile and generate a personalized outreach message with AI.</div>", unsafe_allow_html=True)

with st.form("analyze_form", clear_on_submit=False):
    st.markdown("<div class='input-card'>", unsafe_allow_html=True)
    url = st.text_input("LinkedIn URL")
    profile = st.text_area("Paste Full LinkedIn Profile", height=300)
    st.markdown("</div>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Analyze Lead")

st.markdown("</div>", unsafe_allow_html=True)

if submitted:
    with st.spinner("Analyzing lead with Groq..."):
        data, score, error = analyze_lead(profile, url)

    if error:
        st.error(error)
    else:
        st.success(f"Lead Score: {score}")

        st.markdown("---")

        summary_text = (
            f"**Role:** {data['role']}  \n"
            f"**Company:** {data['company']}  \n"
            f"**Location:** {data['location']}  \n"
            f"**Industry:** {data['industry']}"
        )
        st.markdown(summary_text)

        st.markdown("---")

        st.markdown("### 🧠 Qualification")
        qualification_text = (
            f"**Buyer Intent:** {data['buyer']}  \n"
            f"**Referral Potential:** {data['referral']}"
        )
        st.markdown(qualification_text)

        st.markdown("---")
        st.markdown("### 📩 InMail")

        message = data.get("message", "")
        subject = ""
        body_lines = []

        for line in message.splitlines():
            if line.strip().lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
            else:
                body_lines.append(line)

        if subject:
            st.subheader("Subject")
            st.markdown(f"**{subject}**")

        if body_lines:
            body_text = "\n".join(body_lines).strip()
            st.markdown(f"<div class='message-box'>{body_text}</div>", unsafe_allow_html=True)
        else:
            st.info("No message content was generated.")
