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
# Styling: dark theme + prettier elements + improved input visibility
# -----------------------------
st.markdown(
    """
    <style>
    :root{
      --bg-1: #07102a;
      --bg-2: #0b1630;
      --card-bg: rgba(255,255,255,0.03);
      --muted: #94a3b8;
      --accent1: #06b6d4;
      --accent2: #7c3aed;
    }

    /* page background */
    .reportview-container, .main, .block-container {
        background: linear-gradient(180deg, var(--bg-1), var(--bg-2));
        color: #e6eef8;
    }

    .header {
        background: linear-gradient(90deg,var(--accent1),var(--accent2));
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align:center;
        font-size:28px;
        font-weight:700;
        box-shadow: 0 8px 30px rgba(124,58,237,0.18);
        margin-bottom: 10px;
    }
    .sub {
        color:var(--muted);
        font-size:13px;
        margin-top:6px;
    }
    .card {
        background: var(--card-bg);
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 6px 18px rgba(2,6,23,0.6);
        border: 1px solid rgba(255,255,255,0.03);
        color: #e6eef8;
    }
    .small { font-size:12px; color:var(--muted); }
    .muted { color: var(--muted); }
    .pill {
        display:inline-block;
        padding:6px 10px;
        border-radius:999px;
        font-size:12px;
        background: rgba(124,58,237,0.12);
        color:#d5c3ff;
        margin-right:8px;
    }
    .btn {
  background: linear-gradient(90deg,var(--accent1),var(--accent2));
  color: white !important;
  padding: 8px 12px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
}

.stButton>button {
  background: linear-gradient(90deg,var(--accent1),var(--accent2));
  color: #ffffff !important;       /* default text color */
  border-radius: 8px;
  padding: 8px 10px;
  border: none;
  font-weight: 600;
  transition: background 0.2s, transform 0.2s, color 0.2s;
}

.stButton>button:hover {
  transform: translateY(-2px);
  background-color: #000000 !important;  /* black background on hover */
  color: #ffffff !important;             /* text stays white on hover */
}

.stButton>button:active {
  background-color: #ffffff !important;  /* white background when clicked */
  color: #000000 !important;             /* text black when clicked */
  transform: translateY(0px);
}



    /* INPUT STYLING: improved visibility while typing */
    input[type="text"], input[type="password"], textarea, select {
      background: rgba(255,255,255,0.06) !important;
      color: #000000 !important;
      border-radius: 8px !important;
      padding: 10px !important;
      border: 1px solid rgba(255,255,255,0.12) !important;
    }
    input::placeholder, textarea::placeholder {
      color: #cbd5e1 !important;
    }
    /* make number_input fields clearer */
    .stNumberInput input {
      background: rgba(255,255,255,0.06) !important;
      color: #ffffff !important;
    }

    div[data-testid="stExpander"] {
      border-radius: 12px;
      background: rgba(255,255,255,0.01);
      border: 1px solid rgba(255,255,255,0.02);
      padding: 8px;
    }
    .footer-note {
      font-size:12px;
      color:var(--muted);
    }
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
if "user_role" not in st.session_state:
    st.session_state.user_role: Optional[str] = None
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

def try_fetch_user_by_email(email: str) -> Optional[dict]:
    """Fallback: list users and match email to get full user object."""
    try:
        r = requests.get(f"{BASE_URL}/users/", headers=get_headers(), timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            users = r.json()
            for u in users:
                if u.get("email") == email:
                    return u
    except Exception:
        pass
    return None

def require_login_ui():
    """If not logged in, show authentication UI only and stop execution."""
    if not st.session_state.access_token:
        st.info("Please login to access the dashboard. Use the left panel to signup/login.")
        st.stop()

# -----------------------------
# Layout: left column = auth; right = content
# -----------------------------
left, right = st.columns([1, 3])

with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🔐 Authentication & Session")
    # Show quick session summary
    if st.session_state.user_email:
        st.markdown(f"**Logged in as**: `{st.session_state.user_email}`")
        st.markdown(f"**Role**: <span class='pill'>{st.session_state.user_role}</span>", unsafe_allow_html=True)
        st.write("")
    else:
        st.markdown("Not logged in")

    st.markdown("---")

    # SIGNUP (unchanged)
    with st.expander("Signup", expanded=False):
        with st.form("signup"):
            s_full_name = st.text_input("Full name", key="s_full")
            s_email = st.text_input("Email", key="s_email")
            s_password = st.text_input("Password", type="password", key="s_pass")
            # Only admins should be able to create admin users — but initial signup may create admin.
            # We'll keep same UI options to be compatible with your backend.
            s_role = st.selectbox("Role", ["user", "admin"], index=0, key="s_role")
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

    # LOGIN (Resilient: JSON -> params -> form-data)
    with st.expander("Login", expanded=True):
        with st.form("login"):
            l_email = st.text_input("Email", key="l_email")
            l_password = st.text_input("Password", type="password", key="l_pass")
            l_submit = st.form_submit_button("Login")

        if l_submit:
            if not l_email or not l_password:
                st.warning("Email and password are required")
            else:
                # Attempt 1: JSON body
                payload = {"email": l_email.strip(), "password": l_password.strip()}
                tried_methods = []
                success = False
                last_resp = None

                # Helper to attempt and record responses
                def try_request_json():
                    try:
                        r = requests.post(
                            f"{BASE_URL}/auth/login",
                            json=payload,
                            headers={"Content-Type": "application/json"},
                            timeout=REQUEST_TIMEOUT
                        )
                        return r
                    except Exception as e:
                        st.error(f"Login request (json) failed: {e}")
                        return None

                def try_request_params():
                    try:
                        r = requests.post(
                            f"{BASE_URL}/auth/login",
                            params=payload,
                            timeout=REQUEST_TIMEOUT
                        )
                        return r
                    except Exception as e:
                        st.error(f"Login request (params) failed: {e}")
                        return None

                def try_request_form():
                    try:
                        r = requests.post(
                            f"{BASE_URL}/auth/login",
                            data=payload,
                            timeout=REQUEST_TIMEOUT
                        )
                        return r
                    except Exception as e:
                        st.error(f"Login request (form) failed: {e}")
                        return None

                # 1) JSON
                tried_methods.append("json")
                r = try_request_json()
                if r is not None:
                    last_resp = r
                    data = show_api_response(r)
                    if r.status_code == 200:
                        success = True
                    else:
                        # If server explicitly says query params missing, try params next
                        # If it's 422 indicating validation error for query, also try params
                        if r.status_code in (422, 400):
                            pass  # will try next
                        else:
                            # try next methods anyway if not success
                            pass

                # 2) params (query)
                if not success:
                    tried_methods.append("params")
                    r2 = try_request_params()
                    if r2 is not None:
                        last_resp = r2
                        data = show_api_response(r2)
                        if r2.status_code == 200:
                            r = r2
                            success = True

                # 3) form-data (x-www-form-urlencoded)
                if not success:
                    tried_methods.append("form")
                    r3 = try_request_form()
                    if r3 is not None:
                        last_resp = r3
                        data = show_api_response(r3)
                        if r3.status_code == 200:
                            r = r3
                            success = True

                # finalize
                if success and last_resp is not None:
                    try:
                        data = last_resp.json()
                    except Exception:
                        data = {}
                    # store tokens and user info if available
                    st.session_state.access_token = data.get("access_token") or data.get("accessToken") or data.get("access")
                    st.session_state.refresh_token = data.get("refresh_token") or data.get("refreshToken") or data.get("refresh")
                    st.session_state.user_email = l_email
                    # try to get user object
                    user_obj = data.get("user") or {}
                    if user_obj.get("id"):
                        st.session_state.user_id = user_obj.get("id")
                    else:
                        fallback = try_fetch_user_by_email(l_email)
                        if fallback:
                            st.session_state.user_id = fallback.get("id")
                    if user_obj.get("role"):
                        st.session_state.user_role = user_obj.get("role")
                    else:
                        fallback = try_fetch_user_by_email(l_email)
                        if fallback:
                            st.session_state.user_role = fallback.get("role")
                    st.success("Logged in ✅")
                    st.rerun()

                else:
                    st.error("Login failed — tried methods: " + ", ".join(tried_methods) + ". See response(s) above for details.")

    st.markdown("---")
    st.markdown("**Tokens & Session**")
    access_display = (st.session_state.access_token[:40] + "...") if st.session_state.access_token else None
    refresh_display = (st.session_state.refresh_token[:40] + "...") if st.session_state.refresh_token else None
    st.write(f"**Access:** `{access_display}`")
    st.write(f"**Refresh:** `{refresh_display}`")
    st.write(f"**User email:** {st.session_state.user_email}")
    st.write(f"**User UUID:** {st.session_state.user_id}")
    st.write(f"**User role:** {st.session_state.user_role}")

    # Refresh token
    if st.button("Refresh Access Token"):
        if st.session_state.refresh_token:
            try:
                r = requests.post(f"{BASE_URL}/auth/refresh", json={"refresh_token": st.session_state.refresh_token}, timeout=REQUEST_TIMEOUT)
                data = show_api_response(r)
                if r.status_code == 200:
                    # backend returns new access_token
                    new_access = data.get("access_token") or data.get("accessToken") or data.get("access")
                    if new_access:
                        st.session_state.access_token = new_access
                        st.success("Access token refreshed ✅")
                    else:
                        st.warning("Refresh succeeded but no access token returned.")
                else:
                    st.error("Refresh failed — check response")
            except Exception as e:
                st.error(f"Refresh failed: {e}")
        else:
            st.warning("No refresh token — login first")

    # Logout
    if st.button("Logout"):
        try:
            # try to call backend logout to invalidate refresh token (best-effort)
            if st.session_state.refresh_token:
                requests.post(f"{BASE_URL}/auth/logout", json={"refresh_token": st.session_state.refresh_token}, timeout=REQUEST_TIMEOUT)
        except Exception:
            pass
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.user_email = None
        st.session_state.user_id = None
        st.session_state.user_role = None
        st.success("Local session cleared")

    st.markdown("---")
    if st.button("Show last API response"):
        st.write(st.session_state.last_response)

    st.markdown("</div>", unsafe_allow_html=True)

# If not logged in, stop here — show only left panel
if not st.session_state.access_token:
    # friendly reminder and early exit
    right.warning("You must login to access the dashboard. Use the Login form on the left.")
    st.stop()

# -----------------------------
# Right: tabs for resources (visible only after login)
# -----------------------------
with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("")  # spacer

    tabs = st.tabs(["Users", "Agents", "Reports", "Tools", "Jobs"])

    # ----------------- USERS TAB -----------------
    with tabs[0]:
        st.markdown("<div class='card'><h3>Users — (Admin only: create/list/delete)</h3></div>", unsafe_allow_html=True)
        # Admin-only actions
        if st.session_state.user_role == "admin":
            with st.expander("Create user (admin only)", expanded=False):
                with st.form("create_user"):
                    u_full = st.text_input("Full name", key="u_full")
                    u_email = st.text_input("Email", key="u_email")
                    u_pass = st.text_input("Password", type="password", key="u_pass")
                    u_role = st.selectbox("Role", ["user", "admin"], key="u_role")
                    u_submit = st.form_submit_button("Create")
                if u_submit:
                    payload = {"full_name": u_full, "email": u_email, "password": u_pass, "role": u_role}
                    try:
                        r = requests.post(f"{BASE_URL}/users/", json=payload, headers=get_headers(), timeout=REQUEST_TIMEOUT)
                        show_api_response(r)
                        if r.status_code in (200, 201):
                            st.success("User created")
                    except Exception as e:
                        st.error(f"Create user failed: {e}")

            st.write("---")
            with st.expander("List users", expanded=False):
                with st.form("list_users"):
                    skip = st.number_input("skip", min_value=0, value=0)
                    limit = st.number_input("limit", min_value=1, value=50)
                    role_filter = st.selectbox("Filter role (optional)", options=["", "admin", "user"], index=0)
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

            # Get / Delete by ID
            with st.form("get_delete_user"):
                uid = st.text_input("Get / Delete user by ID", key="uid")
                g = st.form_submit_button("Get user by ID")
                d = st.form_submit_button("Delete user by ID")
            if g:
                try:
                    r = requests.get(f"{BASE_URL}/users/{uid}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                    show_api_response(r)
                except Exception as e:
                    st.error(f"Get failed: {e}")
            if d:
                try:
                    r = requests.delete(f"{BASE_URL}/users/{uid}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                    show_api_response(r)
                except Exception as e:
                    st.error(f"Delete failed: {e}")
        else:
            st.info("Users list and management are admin-only. You can view your own profile in Diagnostics.")

    # ----------------- AGENTS TAB -----------------
    with tabs[1]:
        st.markdown("<div class='card'><h3>Agents</h3></div>", unsafe_allow_html=True)
        st.write("Admins can create/edit/delete agents. Users can view agents read-only.")

        # Create Agent - admin only UI
        if st.session_state.user_role == "admin":
            with st.expander("Create Agent (admin only)", expanded=False):
                with st.form("create_agent"):
                    a_name = st.text_input("Agent name", key="a_name")
                    a_desc = st.text_area("Description", key="a_desc")
                    a_created_by = st.text_input("created_by UUID (leave blank to use logged-in user)", value=st.session_state.user_id or "", key="a_created_by")
                    a_submit = st.form_submit_button("Create agent")
                if a_submit:
                    created_by_val = a_created_by.strip() or st.session_state.user_id
                    if not created_by_val:
                        st.error("created_by (UUID) is required.")
                    else:
                        payload = {"name": a_name, "description": a_desc or None, "created_by": created_by_val}
                        try:
                            r = requests.post(f"{BASE_URL}/agents/", json=payload, headers=get_headers(), timeout=REQUEST_TIMEOUT)
                            show_api_response(r)
                        except Exception as e:
                            st.error(f"Create agent failed: {e}")

        # List agents (both roles)
        if st.button("Refresh agents list"):
            try:
                r = requests.get(f"{BASE_URL}/agents/", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                data = show_api_response(r)
                if r.status_code == 200:
                    st.dataframe(pd.DataFrame(data))
            except Exception as e:
                st.error(f"Agents list failed: {e}")

        # Get / Delete agent
        ag_id = st.text_input("Agent ID (get/delete)", key="ag_id")
        if st.button("Get agent"):
            try:
                r = requests.get(f"{BASE_URL}/agents/{ag_id}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                show_api_response(r)
            except Exception as e:
                st.error(f"Get agent failed: {e}")
        if st.button("Delete agent"):
            if st.session_state.user_role != "admin":
                st.error("Only admin can delete agents")
            else:
                try:
                    r = requests.delete(f"{BASE_URL}/agents/{ag_id}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                    show_api_response(r)
                except Exception as e:
                    st.error(f"Delete agent failed: {e}")

    # ----------------- REPORTS TAB -----------------
    with tabs[2]:
        st.markdown("<div class='card'><h3>Reports</h3></div>", unsafe_allow_html=True)
        st.write("Admins can create/edit/delete reports. Users can view reports (their own or read-only depending on backend).")

        if st.session_state.user_role == "admin":
            with st.expander("Create Report (admin only)", expanded=False):
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
            if st.session_state.user_role != "admin":
                st.error("Only admin can delete reports")
            else:
                try:
                    r = requests.delete(f"{BASE_URL}/reports/{rep_id}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                    show_api_response(r)
                except Exception as e:
                    st.error(f"Delete report failed: {e}")

    # ----------------- TOOLS TAB -----------------
    with tabs[3]:
        st.markdown("<div class='card'><h3>Tools</h3></div>", unsafe_allow_html=True)
        st.write("Admins can create/edit/delete tools. Users can view tools read-only.")

        if st.session_state.user_role == "admin":
            with st.expander("Create Tool (admin only)", expanded=False):
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
            if st.session_state.user_role != "admin":
                st.error("Only admin can delete tools")
            else:
                try:
                    r = requests.delete(f"{BASE_URL}/tools/{tool_id}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                    show_api_response(r)
                except Exception as e:
                    st.error(f"Delete tool failed: {e}")

# ----------------- JOBS TAB -----------------
import time
import pandas as pd
import requests
import streamlit as st

with tabs[4]:
    st.markdown("<div class='card'><h3>Jobs</h3></div>", unsafe_allow_html=True)
    st.write("Users can create jobs and view their own jobs. Admin can view all jobs and cancel any job.")

    # ----------------- Create Job -----------------
    with st.expander("Create Job (Upload Document / JSON Input)", expanded=False):
        with st.form("create_job_form"):
            j_agent_id = st.text_input("Agent ID (UUID)", key="j_agent_id")
            j_created_by = st.text_input(
                "Created by UUID (leave blank for logged-in user)",
                value=st.session_state.user_id or "",
                key="j_created_by"
            )
            j_file = st.file_uploader("Upload document (PDF/TXT/DOCX)", type=["pdf", "txt", "docx"])
            j_input_data = st.text_area("Or enter JSON input manually (optional)", key="j_input_data")
            j_submit = st.form_submit_button("Create Job")

        if j_submit:
            created_by_val = j_created_by.strip() or st.session_state.user_id
            if not created_by_val:
                st.error("Created_by (UUID) is required.")
            elif not j_agent_id.strip():
                st.error("Agent ID is required.")
            elif not j_file and not j_input_data.strip():
                st.error("Please provide a file or JSON input to create a job.")
            else:
                try:
                    files = {"input_file": (j_file.name, j_file.getvalue())} if j_file else None
                    data = {"agent_id": j_agent_id, "created_by": created_by_val}
                    if j_input_data.strip():
                        data["input_data"] = j_input_data.strip()

                    r = requests.post(
                        f"{BASE_URL}/jobs/",
                        headers=get_headers(),
                        data=data,
                        files=files,
                        timeout=REQUEST_TIMEOUT
                    )
                    job_response = r.json()
                    show_api_response(r)

                    # Poll for progress if job created successfully
                    if r.status_code == 200:
                        job_id = job_response["id"]
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        report_text = st.empty()

                        while True:
                            r_poll = requests.get(f"{BASE_URL}/jobs/{job_id}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                            job_data = r_poll.json()
                            progress = job_data.get("progress", 0)
                            status = job_data.get("status", "pending")
                            progress_bar.progress(progress)
                            status_text.markdown(f"**Status:** {status} | **Progress:** {progress}%")

                            if status in ["completed", "failed", "cancelled"]:
                                if status == "completed" and job_data.get("output_data"):
                                    report_text.markdown(f"**Report Output:**\n```\n{job_data['output_data'].get('final_report', '')}\n```")
                                break
                            time.sleep(2)  # poll every 2 seconds

                except Exception as e:
                    st.error(f"Create job failed: {e}")

    st.write("---")

    # ----------------- Jobs List -----------------
    if st.button("Refresh jobs list"):
        try:
            r = requests.get(f"{BASE_URL}/jobs/", headers=get_headers(), timeout=REQUEST_TIMEOUT)
            data = show_api_response(r)
            if r.status_code == 200:
                df = pd.DataFrame(r.json())
                # Filter for normal users
                if st.session_state.user_role != "admin" and "created_by" in df.columns:
                    df = df[df["created_by"] == st.session_state.user_id]
                if "progress" in df.columns:
                    df["progress_display"] = df["progress"].astype(str) + "%"
                st.dataframe(df)
        except Exception as e:
            st.error(f"Jobs list failed: {e}")

    # ----------------- Get / Cancel Job -----------------
    job_id_input = st.text_input("Job ID (get/cancel)", key="job_id_action")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Get job"):
            try:
                r = requests.get(f"{BASE_URL}/jobs/{job_id_input}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                job_data = r.json()
                show_api_response(r)
                if r.status_code == 200 and job_data.get("output_data"):
                    st.markdown(f"**Report Output:**\n```\n{job_data['output_data'].get('final_report', '')}\n```")
            except Exception as e:
                st.error(f"Get job failed: {e}")

    with col2:
        if st.button("Cancel job"):
            try:
                r = requests.delete(f"{BASE_URL}/jobs/{job_id_input}", headers=get_headers(), timeout=REQUEST_TIMEOUT)
                show_api_response(r)
            except Exception as e:
                st.error(f"Cancel job failed: {e}")



    # ----------------- EVENTS TAB -----------------
    with tabs[5]:
        st.markdown("<div class='card'><h3>Event logs</h3></div>", unsafe_allow_html=True)
        st.write("Admin can view system event logs. Users get a notification if they have personal events (backend dependent).")

        # This reads local event file if present (your previous behavior)
        event_file = os.path.join("event", "events.jsonl")
        if os.path.exists(event_file):
            try:
                with open(event_file, "r", encoding="utf-8") as f:
                    logs = [json.loads(line) for line in f if line.strip()]
                if logs:
                    # show all logs only to admin
                    df = pd.DataFrame(logs)
                    if st.session_state.user_role != "admin":
                        # attempt to filter user-specific logs if they include 'user_id' field
                        if "user_id" in df.columns:
                            df = df[df["user_id"] == st.session_state.user_id]
                    if df.empty:
                        st.info("No events visible for you.")
                    else:
                        st.dataframe(df)
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
        st.write("- Current user role:", st.session_state.user_role)
        st.write("- Access token present:", bool(st.session_state.access_token))
        st.write("- Refresh token present:", bool(st.session_state.refresh_token))
        st.write("---")
        st.write("Useful endpoints (open in browser):")
        st.write(f"- {BASE_URL}/docs  (FastAPI interactive docs)")
        st.write(f"- {BASE_URL}/openapi.json")
        st.write("Start backend with:")
        st.code("uvicorn app.main:app --reload", language="bash")

# -----------------------------
# Footer / tips
# -----------------------------
st.markdown("---")
st.markdown("<div class='small footer-note'>Tip: run FastAPI and Streamlit in separate terminals. Streamlit: <code>streamlit run streamlit_app.py</code>. Backend: <code>uvicorn app.main:app --reload</code>.</div>", unsafe_allow_html=True)
