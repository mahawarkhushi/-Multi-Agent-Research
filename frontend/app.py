# streamlit_app.py
import streamlit as st
import requests
import json
import pandas as pd
import os
from typing import Optional

# -----------------------------
# Config
# -----------------------------
BASE_URL = "http://127.0.0.1:8000"  # change if your backend runs elsewhere
REQUEST_TIMEOUT = 12
st.set_page_config(page_title="Multi-Agent Research Dashboard", layout="wide", page_icon="🚀")

# -----------------------------
# Simple CSS for color & cards
# -----------------------------
st.markdown(
    """
    <style>
    .header {
        background: linear-gradient(90deg,#6a11cb,#2575fc);
        padding: 18px;
        border-radius: 12px;
        color: white;
        text-align:center;
        font-size:28px;
        font-weight:600;
    }
    .card {
        background: linear-gradient(180deg, #ffffff, #f6f8ff);
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
    .muted { color:#6b7280; }
    .small { font-size:12px; color:#6b7280; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='header'>🚀 Multi-Agent Research Dashboard</div>", unsafe_allow_html=True)
st.write("")  # spacer

# -----------------------------
# Session state defaults
# -----------------------------
if "access_token" not in st.session_state:
    st.session_state.access_token: Optional[str] = None
if "refresh_token" not in st.session_state:
    st.session_state.refresh_token: Optional[str] = None
if "user_email" not in st.session_state:
    st.session_state.user_email: Optional[str] = None
if "user_id" not in st.session_state:
    st.session_state.user_id: Optional[str] = None
if "last_response" not in st.session_state:
    st.session_state.last_response = None

# -----------------------------
# Helpers
# -----------------------------
def get_headers():
    if st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}

def show_api_response(resp: requests.Response):
    """Show response in an expander and save to session."""
    try:
        data = resp.json()
    except Exception:
        data = resp.text
    with st.expander(f"Response — Status {resp.status_code}", expanded=False):
        st.write(data)
    st.session_state.last_response = {"status": resp.status_code, "body": data}
    return data

def try_fetch_user_id_by_email(email: str) -> Optional[str]:
    """Fallback: list users and match email to get id."""
    try:
        r = requests.get(f"{BASE_URL}/users/", headers=get_headers(), timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            users = r.json()
            for u in users:
                # user object may contain 'email' and 'id'
                if u.get("email") == email:
                    return str(u.get("id"))
    except Exception:
        pass
    return None

# -----------------------------
# Layout columns: left = auth, right = tabs
# -----------------------------
left, right = st.columns([1, 3])

with left:
    st.markdown("### 🔐 Authentication", unsafe_allow_html=True)

    # SIGNUP
    with st.expander("Signup", expanded=False):
        with st.form("signup"):
            s_full_name = st.text_input("Full name", key="s_full")
            s_email = st.text_input("Email", key="s_email")
            s_password = st.text_input("Password", type="password", key="s_pass")
            s_role = st.selectbox("Role", ["admin", "analyst", "viewer"], key="s_role")
            s_submit = st.form_submit_button("Create account")
        if s_submit:
            payload = {"full_name": s_full_name, "email": s_email, "password": s_password, "role": s_role}
            try:
                r = requests.post(f"{BASE_URL}/auth/signup", json=payload, timeout=REQUEST_TIMEOUT)
                show_api_response(r)
                if r.status_code in (200, 201):
                    st.success("Signup success — you can login now")
            except Exception as e:
                st.error(f"Signup failed: {e}")

    # LOGIN
    with st.expander("Login", expanded=True):
        with st.form("login"):
            l_email = st.text_input("Email", key="l_email")
            l_password = st.text_input("Password", type="password", key="l_pass")
            l_submit = st.form_submit_button("Login")
        if l_submit:
            try:
                # Your backend login uses query params as in provided code
                r = requests.post(f"{BASE_URL}/auth/login", params={"email": l_email, "password": l_password}, timeout=REQUEST_TIMEOUT)
                data = show_api_response(r)
                if r.status_code == 200:
                    # store tokens
                    st.session_state.access_token = data.get("access_token")
                    st.session_state.refresh_token = data.get("refresh_token")
                    st.session_state.user_email = l_email
                    # try to get user_id from response
                    if data.get("user_id"):
                        st.session_state.user_id = data.get("user_id")
                    elif isinstance(data.get("user"), dict) and data["user"].get("id"):
                        st.session_state.user_id = data["user"]["id"]
                    else:
                        # fallback: list users and match by email
                        fallback = try_fetch_user_id_by_email(l_email)
                        if fallback:
                            st.session_state.user_id = fallback
                    st.success("Logged in ✅")
                else:
                    st.error("Login failed — check response")
            except Exception as e:
                st.error(f"Login request failed: {e}")

    st.markdown("---")
    st.markdown("**Tokens & Session**")
    st.write(f"**Access:** `{st.session_state.access_token[:40]+'...' if st.session_state.access_token else None}`")
    st.write(f"**Refresh:** `{st.session_state.refresh_token[:40]+'...' if st.session_state.refresh_token else None}`")
    st.write(f"**User email:** {st.session_state.user_email}")
    st.write(f"**User UUID:** {st.session_state.user_id}")

    # Refresh token
    if st.button("Refresh Access Token"):
        if st.session_state.refresh_token:
            try:
                r = requests.post(f"{BASE_URL}/auth/refresh", json={"refresh_token": st.session_state.refresh_token}, timeout=REQUEST_TIMEOUT)
                data = show_api_response(r)
                if r.status_code == 200:
                    st.session_state.access_token = data.get("access_token")
                    st.success("Access token refreshed ✅")
            except Exception as e:
                st.error(f"Refresh failed: {e}")
        else:
            st.warning("No refresh token — login first")

    # Logout
    if st.button("Logout"):
        try:
            r = requests.post(f"{BASE_URL}/auth/logout", headers=get_headers(), timeout=REQUEST_TIMEOUT)
            show_api_response(r)
        except Exception:
            pass
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.user_email = None
        st.session_state.user_id = None
        st.success("Local session cleared")

    st.markdown("---")
    if st.button("Show last API response"):
        st.write(st.session_state.last_response)

# -----------------------------
# Right: tabs for resources
# -----------------------------
with right:
    tabs = st.tabs(["Users", "Agents", "Reports", "Tools", "Jobs", "Events", "Diagnostics"])

    # ----------------- USERS TAB -----------------
    with tabs[0]:
        st.markdown("<div class='card'><h3>Users — Create / List / Get / Delete</h3></div>", unsafe_allow_html=True)

        # Create user form (matches UserCreate)
        with st.form("create_user"):
            u_full = st.text_input("Full name", key="u_full")
            u_email = st.text_input("Email", key="u_email")
            u_pass = st.text_input("Password", type="password", key="u_pass")
            u_role = st.selectbox("Role", ["admin", "analyst", "viewer"], key="u_role")
            u_submit = st.form_submit_button("Create")
        if u_submit:
            payload = {"full_name": u_full, "email": u_email, "password": u_pass, "role": u_role}
            try:
                r = requests.post(f"{BASE_URL}/users/", json=payload, headers=get_headers(), timeout=REQUEST_TIMEOUT)
                show_api_response(r)
            except Exception as e:
                st.error(f"Create user failed: {e}")

        st.write("---")
        # List / Get / Delete
        with st.form("list_users"):
            skip = st.number_input("skip", min_value=0, value=0)
            limit = st.number_input("limit", min_value=1, value=25)
            role_filter = st.selectbox("Filter role (optional)", options=["", "admin", "analyst", "viewer"], index=0)
            list_submit = st.form_submit_button("List users")
        if list_submit:
            params = {"skip": skip, "limit": limit}
            if role_filter:
                params["role"] = role_filter
            try:
                r = requests.get(f"{BASE_URL}/users/", headers=get_headers(), params=params, timeout=REQUEST_TIMEOUT)
                data = show_api_response(r)
                if r.status_code == 200:
                    st.dataframe(pd.DataFrame(data))
            except Exception as e:
                st.error(f"List users failed: {e}")

        uid = st.text_input("Get / Delete user by ID", key="uid")
        if st.button("Get user by ID"):
            try:
                r = requests.get(f"{BASE_URL}/users/{uid}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                show_api_response(r)
            except Exception as e:
                st.error(f"Get failed: {e}")
        if st.button("Delete user by ID"):
            try:
                r = requests.delete(f"{BASE_URL}/users/{uid}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                show_api_response(r)
            except Exception as e:
                st.error(f"Delete failed: {e}")

    # ----------------- AGENTS TAB -----------------
    with tabs[1]:
        st.markdown("<div class='card'><h3>Agents — Create / List / Get / Delete</h3></div>", unsafe_allow_html=True)

        # Create Agent (AgentCreate expects name, description, created_by:UUID)
        with st.form("create_agent"):
            a_name = st.text_input("Agent name", key="a_name")
            a_desc = st.text_area("Description", key="a_desc")
            a_created_by = st.text_input("created_by UUID (leave blank to use logged-in user)", value=st.session_state.user_id or "", key="a_created_by")
            a_submit = st.form_submit_button("Create agent")
        if a_submit:
            created_by_val = a_created_by.strip() or st.session_state.user_id
            if not created_by_val:
                st.error("created_by (UUID) is required — set it or login so it is auto-filled.")
            else:
                payload = {"name": a_name, "description": a_desc or None, "created_by": created_by_val}
                try:
                    r = requests.post(f"{BASE_URL}/agents/", json=payload, headers=get_headers(), timeout=REQUEST_TIMEOUT)
                    show_api_response(r)
                except Exception as e:
                    st.error(f"Create agent failed: {e}")

        st.write("---")
        if st.button("Refresh agents list"):
            try:
                r = requests.get(f"{BASE_URL}/agents/", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                data = show_api_response(r)
                if r.status_code == 200:
                    st.dataframe(pd.DataFrame(data))
            except Exception as e:
                st.error(f"Agents list failed: {e}")

        ag_id = st.text_input("Agent ID (get/delete)", key="ag_id")
        if st.button("Get agent"):
            try:
                r = requests.get(f"{BASE_URL}/agents/{ag_id}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                show_api_response(r)
            except Exception as e:
                st.error(f"Get agent failed: {e}")
        if st.button("Delete agent"):
            try:
                r = requests.delete(f"{BASE_URL}/agents/{ag_id}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                show_api_response(r)
            except Exception as e:
                st.error(f"Delete agent failed: {e}")

    # ----------------- REPORTS TAB -----------------
    with tabs[2]:
        st.markdown("<div class='card'><h3>Reports — Create / List / Get / Delete</h3></div>", unsafe_allow_html=True)

        # Create Report (ReportCreate expects title, summary, created_by UUID)
        with st.form("create_report"):
            rp_title = st.text_input("Title", key="rp_title")
            rp_summary = st.text_area("Summary", key="rp_summary")
            rp_created_by = st.text_input("created_by UUID (leave blank for logged-in user)", value=st.session_state.user_id or "", key="rp_created_by")
            rp_submit = st.form_submit_button("Create report")
        if rp_submit:
            created_by_val = rp_created_by.strip() or st.session_state.user_id
            if not created_by_val:
                st.error("created_by (UUID) is required.")
            else:
                payload = {"title": rp_title, "summary": rp_summary, "created_by": created_by_val}
                try:
                    r = requests.post(f"{BASE_URL}/reports/", json=payload, headers=get_headers(), timeout=REQUEST_TIMEOUT)
                    show_api_response(r)
                except Exception as e:
                    st.error(f"Create report failed: {e}")

        st.write("---")
        if st.button("Refresh reports list"):
            try:
                r = requests.get(f"{BASE_URL}/reports/", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                data = show_api_response(r)
                if r.status_code == 200:
                    st.dataframe(pd.DataFrame(data))
            except Exception as e:
                st.error(f"Reports list failed: {e}")

        rep_id = st.text_input("Report ID (get/delete)", key="rep_id")
        if st.button("Get report"):
            try:
                r = requests.get(f"{BASE_URL}/reports/{rep_id}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                show_api_response(r)
            except Exception as e:
                st.error(f"Get report failed: {e}")
        if st.button("Delete report"):
            try:
                r = requests.delete(f"{BASE_URL}/reports/{rep_id}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                show_api_response(r)
            except Exception as e:
                st.error(f"Delete report failed: {e}")

    # ----------------- TOOLS TAB -----------------
    with tabs[3]:
        st.markdown("<div class='card'><h3>Tools — Create / List / Get / Delete</h3></div>", unsafe_allow_html=True)

        # Create Tool (ToolCreate: name, type, config (dict) optional, agent_id UUID optional)
        with st.form("create_tool"):
            t_name = st.text_input("Tool name", key="t_name")
            t_type = st.text_input("Tool type", key="t_type")
            t_config = st.text_area("Config (JSON) - optional", key="t_config")
            t_agent_id = st.text_input("agent_id (UUID) - optional", key="t_agent_id")
            t_submit = st.form_submit_button("Create tool")
        if t_submit:
            cfg = None
            if t_config.strip():
                try:
                    cfg = json.loads(t_config)
                except Exception:
                    st.error("Invalid JSON in config")
                    cfg = None
            payload = {"name": t_name, "type": t_type, "config": cfg, "agent_id": t_agent_id or None}
            try:
                r = requests.post(f"{BASE_URL}/tools/", json=payload, headers=get_headers(), timeout=REQUEST_TIMEOUT)
                show_api_response(r)
            except Exception as e:
                st.error(f"Create tool failed: {e}")

        st.write("---")
        if st.button("Refresh tools list"):
            try:
                r = requests.get(f"{BASE_URL}/tools/", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                data = show_api_response(r)
                if r.status_code == 200:
                    st.dataframe(pd.DataFrame(data))
            except Exception as e:
                st.error(f"Tools list failed: {e}")

        tool_id = st.text_input("Tool ID (get/delete)", key="tool_id")
        if st.button("Get tool"):
            try:
                r = requests.get(f"{BASE_URL}/tools/{tool_id}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                show_api_response(r)
            except Exception as e:
                st.error(f"Get tool failed: {e}")
        if st.button("Delete tool"):
            try:
                r = requests.delete(f"{BASE_URL}/tools/{tool_id}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                show_api_response(r)
            except Exception as e:
                st.error(f"Delete tool failed: {e}")

    # ----------------- JOBS TAB -----------------
    with tabs[4]:
        st.markdown("<div class='card'><h3>Jobs — Create / List / Get / Cancel</h3></div>", unsafe_allow_html=True)

        # Create Job (JobCreate: agent_id:UUID, created_by:UUID, input_data:Optional[Any])
        with st.form("create_job"):
            j_agent_id = st.text_input("agent_id (UUID)", key="j_agent_id")
            j_created_by = st.text_input("created_by UUID (leave blank to use logged-in user)", value=st.session_state.user_id or "", key="j_created_by")
            j_input = st.text_area("input_data (JSON) - optional", value='{"text":"example"}', key="j_input")
            j_submit = st.form_submit_button("Create job")
        if j_submit:
            try:
                input_data = json.loads(j_input) if j_input.strip() else None
            except Exception:
                st.error("Invalid JSON in input_data")
                input_data = None
            created_by_val = j_created_by.strip() or st.session_state.user_id
            if not created_by_val:
                st.error("created_by (UUID) is required.")
            elif not j_agent_id.strip():
                st.error("agent_id (UUID) is required.")
            else:
                payload = {"agent_id": j_agent_id, "created_by": created_by_val, "input_data": input_data}
                try:
                    r = requests.post(f"{BASE_URL}/jobs/", json=payload, headers=get_headers(), timeout=REQUEST_TIMEOUT)
                    show_api_response(r)
                except Exception as e:
                    st.error(f"Create job failed: {e}")

        st.write("---")
        if st.button("Refresh jobs list"):
            try:
                r = requests.get(f"{BASE_URL}/jobs/", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                data = show_api_response(r)
                if r.status_code == 200:
                    df = pd.DataFrame(r.json())
                    if "progress" in df.columns:
                        df["progress_display"] = df["progress"].astype(str) + "%"
                    st.dataframe(df)
            except Exception as e:
                st.error(f"Jobs list failed: {e}")

        job_id = st.text_input("Job ID (get/cancel)", key="job_id")
        if st.button("Get job"):
            try:
                r = requests.get(f"{BASE_URL}/jobs/{job_id}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                show_api_response(r)
            except Exception as e:
                st.error(f"Get job failed: {e}")
        if st.button("Cancel job"):
            try:
                r = requests.delete(f"{BASE_URL}/jobs/{job_id}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                show_api_response(r)
            except Exception as e:
                st.error(f"Cancel job failed: {e}")

    # ----------------- EVENTS TAB -----------------
    with tabs[5]:
        st.markdown("<div class='card'><h3>Event logs</h3></div>", unsafe_allow_html=True)
        st.info("Shows events from local event file (if available).")
        event_file = os.path.join("event", "events.jsonl")
        if os.path.exists(event_file):
            try:
                with open(event_file, "r", encoding="utf-8") as f:
                    logs = [json.loads(line) for line in f if line.strip()]
                if logs:
                    st.dataframe(pd.DataFrame(logs))
                else:
                    st.info("Event file exists but contains no lines.")
            except Exception as e:
                st.error(f"Failed to read events: {e}")
        else:
            st.info("No event file found at 'event/events.jsonl' (relative to the Streamlit working dir).")

    # ----------------- DIAGNOSTICS TAB -----------------
    with tabs[6]:
        st.markdown("<div class='card'><h3>Diagnostics & Helpful Links</h3></div>", unsafe_allow_html=True)
        st.write("- Backend BASE_URL:", BASE_URL)
        st.write("- Current logged in user:", st.session_state.user_email)
        st.write("- Current user UUID:", st.session_state.user_id)
        st.write("- Access token present:", bool(st.session_state.access_token))
        st.write("- Refresh token present:", bool(st.session_state.refresh_token))
        st.write("---")
        st.write("Useful endpoints (open in browser):")
        st.write(f"- {BASE_URL}/docs  (FastAPI interactive docs)")
        st.write(f"- {BASE_URL}/openapi.json")
        st.write("")
        st.write("Start backend with:")
        st.code("uvicorn app.main:app --reload", language="bash")

# -----------------------------
# Footer / tips
# -----------------------------
st.markdown("---")
st.markdown("<div class='small'>Tip: run FastAPI and Streamlit in separate terminals. Streamlit: <code>streamlit run streamlit_app.py</code>. Backend: <code>uvicorn app.main:app --reload</code>.</div>", unsafe_allow_html=True)
