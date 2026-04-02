import os
import json
import re
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
import gspread
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"

groq_client = Groq(api_key=GROQ_API_KEY)

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_PATH = os.path.join(BASE_DIR, "creds.json")

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, SCOPE)
gsheet_client = gspread.authorize(credentials)
sheet = gsheet_client.open("Fintech Outbound CRM").sheet1

BASE_PROMPT = """
You are an expert fintech outbound strategist.

Your task is to analyze a LinkedIn profile and generate a structured outreach message.

Also extract:
Name:
Role:
Company:
Location:
Industry:

----------------------------------------
RULE: YOU MUST ALWAYS GENERATE A MESSAGE
----------------------------------------

Never output:
- "No message"
- Empty response
- Partial response

----------------------------------------
CLASSIFICATION
----------------------------------------

Buyer Intent = YES if:
- Founder, CEO, CTO, Head roles
- Fintech / payments / crypto / SaaS infra

Referral Potential = YES if:
- VC, advisor, regulator, ecosystem leader

DEFAULT:
If unsure → Buyer = NO, Referral = YES

----------------------------------------
STRICT OUTPUT FORMAT
----------------------------------------

You MUST return EXACTLY this:

Decision Summary
Buyer Intent: YES / NO
Referral Potential: YES / NO

InMail Draft

Subject:
<one-line subject>

Message:
Hi <First Name>,

<paragraph 1: personalized>

<paragraph 2: insight>

• White-label Payment Gateway & Digital Banking Platforms (with full source code)
• Crypto Exchange, Wallet & Payment Gateway infrastructure (with full source code)
• PCI DSS, ISO 27001, GDPR compliance services
• MSB / VASP Licensing (USA, Canada, EU)
• IBAN / SWIFT account issuance
• Virtual and physical card issuing
• Real-time, scalable infrastructure

<closing>

Best regards,  
Rahul

----------------------------------------
RULES
----------------------------------------

- ALWAYS include Subject
- ALWAYS include Message
- ALWAYS include Decision Summary
- NEVER merge into one paragraph
- NEVER skip sections
- NEVER output JSON
- NEVER explain anything

----------------------------------------
FINAL OUTPUT
----------------------------------------

Return ONLY formatted output.
"""

NOISE_WORDS = [
    "Messaging", "Compose message", "More inboxes",
    "Recommendation transparency", "Select language"
]


def is_valid_output(text: str):
    return (
        "Decision Summary" in text and
        "Subject:" in text and
        "Message:" in text
    )


def init_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    if "login_error" not in st.session_state:
        st.session_state.login_error = ""


def login_user(email: str, password: str) -> bool:
    if email == "admin" and password == "1234":
        st.session_state.logged_in = True
        st.session_state.user_email = email
        st.session_state.login_error = ""
        return True

    st.session_state.login_error = "Invalid email or password."
    return False


def logout_user():
    st.session_state.logged_in = False
    st.session_state.user_email = ""


def inject_global_styles():
    st.markdown(
        """
        <style>
        :root {
            color-scheme: dark;
        }
        body {
            color: #e5e7eb;
            background-color: #0f172a;
        }
        .app-shell {
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: #e5e7eb;
        }
        .app-card {
            background: #111827;
            border: 1px solid #3730a3;
            border-radius: 24px;
            padding: 28px;
            box-shadow: 0 18px 45px rgba(99, 102, 241, 0.16);
            margin-bottom: 24px;
        }
        .app-section {
            margin-top: 24px;
            margin-bottom: 24px;
        }
        .app-title {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
            color: #f8fafc;
        }
        .app-subtitle {
            color: #c7d2fe;
            margin-bottom: 20px;
        }
        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 700;
            margin-bottom: 16px;
            font-size: 18px;
            color: #8b5cf6;
        }
        .sidebar-user {
            background: #1e293b;
            border: 1px solid #3730a3;
            border-radius: 18px;
            padding: 18px;
            margin-bottom: 18px;
            color: #c7d2fe;
        }
        .sidebar-section {
            margin-top: 24px;
            margin-bottom: 8px;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            color: #a5b4fc;
        }
        .app-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            padding: 6px 14px;
            font-size: 12px;
            font-weight: 700;
            line-height: 1;
        }
        .badge-hot { background: #fef3c7; color: #92400e; }
        .badge-warm { background: #c7d2fe; color: #4338ca; }
        .badge-cold { background: #d1fae5; color: #065f46; }
        .message-box {
            background: #1f2937;
            border: 1px solid #3730a3;
            border-radius: 20px;
            padding: 22px;
            white-space: pre-wrap;
            line-height: 1.7;
            color: #e2e8f0;
        }
        .input-card .stTextInput>div>div>input,
        .input-card .stTextArea>div>div>textarea {
            border-radius: 16px;
            padding: 16px;
            background: #0f172a;
            color: #e2e8f0;
            border: 1px solid #3730a3;
        }
        .input-card label {
            color: #e2e8f0;
        }
        .stButton>button {
            border-radius: 16px;
            padding: 12px 20px;
            background-color: #7c3aed;
            color: white;
            border: none;
        }
        .stButton>button:hover {
            background-color: #9333ea;
        }
        .stMetric,
        div[data-testid="metric-container"] {
            background: #111827 !important;
            border: 1px solid #3730a3 !important;
            border-radius: 20px !important;
            color: #e5e7eb !important;
        }
        div[data-testid="metric-container"] span,
        .stMetric .stMetricLabel,
        .stMetric .stMetricValue {
            color: #e5e7eb !important;
        }
        div[data-testid="stDataFrame"],
        .stDataFrame,
        .stDataFrame td,
        .stDataFrame th {
            background: #0f172a !important;
            color: #e5e7eb !important;
        }
        div[data-testid="stDataFrame"] table {
            border-color: #3730a3 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    init_session()
    st.sidebar.markdown("<div class='sidebar-brand'>🚀 <span>AI Lead System</span></div>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    if st.session_state.logged_in:
        st.sidebar.markdown(
            "<div class='sidebar-user'><strong>Signed in as</strong><br>admin</div>",
            unsafe_allow_html=True,
        )
        if st.sidebar.button("Logout"):
            logout_user()
    else:
        st.sidebar.info("Log in on any page to get started.")

    st.sidebar.markdown("<div class='sidebar-section'>Navigation</div>", unsafe_allow_html=True)


def require_login():
    init_session()
    if st.session_state.logged_in:
        return

    st.warning("Please log in to access this page.")
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if login_user(email, password):
                st.success("Login successful. Choose a page from the sidebar.")
                return
            st.error(st.session_state.login_error)

    st.info("Use email `admin` and password `1234`.")
    st.stop()


def extract_json(text: str):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0).strip())
    except json.JSONDecodeError:
        return None
    except Exception:
        return None
    return None


def get_score(buyer, referral):
    if buyer == "YES":
        return "🔥 HOT"
    if referral == "YES":
        return "⚡ WARM"
    return "❄️ COLD"


def clean_value(value):
    if value is None or value == "UNKNOWN":
        return ""
    return value


def analyze_lead(profile_text: str, url: str):
    if len(profile_text.strip()) < 80:
        return None, None, "⚠️ Paste full LinkedIn profile"

    profile_text = profile_text.replace("·", "").replace("|", "\n")
    for word in NOISE_WORDS:
        profile_text = profile_text.replace(word, "")

    full_prompt = f"{BASE_PROMPT}\n\nPROFILE DATA:\n{profile_text}"
    response_text = ""

    try:
        for _ in range(3):
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.2,
                max_tokens=700,
            )

            response_text = response.choices[0].message.content or ""
            response_text = response_text.replace("\\n", "\n")

            if is_valid_output(response_text):
                break

        if not is_valid_output(response_text):
            response_text = (
                "Decision Summary\n"
                "Buyer Intent: NO\n"
                "Referral Potential: YES\n\n"
                "InMail Draft\n\n"
                "Subject:\n"
                "Quick thought\n\n"
                "Message:\n"
                "Hi,\n\n"
                "I came across your profile and found your work interesting.\n\n"
                "Would be great to connect and exchange thoughts.\n\n"
                "Best regards,  \nRahul\n"
            )

        name = ""
        role = ""
        company = ""
        location = ""
        industry = ""
        buyer = "NO"
        referral = "YES"
        subject = ""
        message_lines = []
        in_inmail = False
        in_message = False

        for line in response_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("Name:"):
                name = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Role:"):
                role = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Company:"):
                company = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Location:"):
                location = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Industry:"):
                industry = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Buyer Intent:"):
                buyer_value = stripped.split(":", 1)[1].strip().upper()
                buyer = buyer_value if buyer_value in ("YES", "NO") else "NO"
            elif stripped.startswith("Referral Potential:"):
                referral_value = stripped.split(":", 1)[1].strip().upper()
                referral = referral_value if referral_value in ("YES", "NO") else "YES"
            elif stripped == "InMail Draft":
                in_inmail = True
            elif in_inmail and stripped.startswith("Subject:"):
                subject = stripped.split(":", 1)[1].strip()
                in_message = False
            elif in_inmail and stripped.startswith("Message:"):
                in_message = True
            elif in_message:
                message_lines.append(line)

        message_text = "\n".join(message_lines).strip()
        if subject:
            message_text = f"Subject: {subject}\n\n{message_text}"

        score = get_score(buyer, referral)

        sheet.append_row([
            name,
            url,
            company,
            role,
            location,
            industry,
            buyer,
            referral,
            score,
            datetime.now().strftime("%Y-%m-%d"),
            "New"
        ])

        return {
            "name": name,
            "role": role,
            "company": company,
            "location": location,
            "industry": industry,
            "buyer": buyer,
            "referral": referral,
            "message": message_text
        }, score, None
    except Exception as exc:
        return None, None, str(exc)


def fetch_all_leads():
    try:
        records = sheet.get_all_records()
        if records:
            return list(reversed(records))

        values = sheet.get_all_values()
        if len(values) <= 1:
            return []

        headers = values[0]
        rows = [dict(zip(headers, row)) for row in reversed(values[1:])]
        return rows
    except Exception:
        return []


def normalize_leads(records):
    def get_field(row, *keys):
        for key in keys:
            value = row.get(key)
            if value not in (None, ""):
                return value
        return ""

    normalized = []
    for row in records:
        normalized.append({
            "name": get_field(row, "name", "Name"),
            "company": get_field(row, "company", "Company"),
            "role": get_field(row, "role", "Role"),
            "score": get_field(row, "score", "Score"),
            "date": get_field(row, "date", "Date"),
            "url": get_field(row, "url", "LinkedIn URL", "URL"),
        })
    return normalized
