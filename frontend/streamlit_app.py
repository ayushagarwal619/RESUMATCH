import streamlit as st
import sys
from pathlib import Path
import textwrap

# Put the repo root on sys.path so `from frontend.views import ...` resolves
# regardless of the directory streamlit was launched from.
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure page
st.set_page_config(
    page_title="RESUMATCH — Match. Optimize. Get Hired.",
    page_icon="frontend/assets/logo.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auth state. Populated by Supabase sign-in / sign-up / OAuth.
# All four are None when signed out, all four are set when signed in.
for key, default in [
    ("access_token", None),
    ("refresh_token", None),
    ("user_id", None),       # Supabase auth user id (uuid); also used by api_client
    ("user_email", None),
    ("auth_error", None),
    ("auth_info", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# If we just came back from Google OAuth, Supabase appends `?code=<authcode>`
# to the redirect URL. Exchange it for a session before rendering anything.
if (
    not st.session_state.access_token
    and "code" in st.query_params
):
    from frontend.services import supabase_client
    result = supabase_client.exchange_code_for_session(st.query_params["code"])

    #Always clear the ?code= param so a refresh doesn't try to re-exchange.
    st.query_params.clear()
    if "error" in result:
        st.session_state.auth_error = f"Google sign-in failed: {result['error']}"
    else:
        st.session_state.access_token  = result["access_token"]
        st.session_state.refresh_token = result["refresh_token"]
        st.session_state.user_id       = result["user_id"]
        st.session_state.user_email    = result["email"]
        st.rerun()

#Load custom CSS
def load_css():
    try:
        css_path = Path(__file__).parent / 'assets' / 'styles.css'
        with open(css_path, 'r') as f:
            css_content = f.read()
            
        theme = st.session_state.get('theme', 'dark')
        if theme == 'light':
            variables = """
            :root {
                --bg-main: #F8FAFC;
                --bg-secondary: #F1F5F9;
                --bg-card: #FFFFFF;
                --bg-sidebar: #FFFFFF;
                --accent-primary: #4F46E5;
                --accent-secondary: #2563EB;
                --accent-highlight: #06B6D4;
                --color-success: #10B981;
                --color-warning: #F59E0B;
                --color-danger: #EF4444;
                --text-primary: #111827;
                --text-secondary: #374151;
                --text-muted: #6B7280;
                --border-soft: 1px solid #D1D5DB;
                --shadow-premium: 0 4px 20px rgba(0, 0, 0, 0.05);
                --grad-primary: linear-gradient(135deg, #4F46E5 0%, #2563EB 100%);
                --glow-color: rgba(79, 70, 229, 0.05);
                --border-glow: 1px solid #D1D5DB;
            }
            """
            theme_slider = """
            div[data-element-id="theme_toggle_btn"] button::after {
                left: 3px !important;
            }
            """
        else:
            variables = """
            :root {
                --bg-main: #070B18;
                --bg-secondary: #0E1324;
                --bg-card: #111827;
                --bg-sidebar: #0B1220;
                --accent-primary: #7C5CFF;
                --accent-secondary: #3BA8FF;
                --accent-highlight: #00E5FF;
                --color-success: #10B981;
                --color-warning: #F59E0B;
                --color-danger: #EF4444;
                --text-primary: #FFFFFF;
                --text-secondary: #A8B3CF;
                --text-muted: #9CA3AF;
                --border-soft: 1px solid rgba(255,255,255,0.12);
                --shadow-premium: 0 20px 40px rgba(0, 0, 0, 0.5);
                --grad-primary: linear-gradient(135deg, #7C5CFF 0%, #3BA8FF 100%);
                --glow-color: rgba(124, 92, 255, 0.2);
                --border-glow: 1px solid rgba(255, 255, 255, 0.12);
            }
            """
            theme_slider = """
            div[data-element-id="theme_toggle_btn"] button::after {
                left: calc(50% + 3px) !important;
            }
            """
        return f'<style>{variables}\n{theme_slider}\n{css_content}</style>'
    except FileNotFoundError:
        return ''

st.markdown(load_css(), unsafe_allow_html=True)

def html_inject(html_str: str) -> None:
    import re
    clean = re.sub(r'\s+', ' ', html_str).strip()
    st.markdown(clean, unsafe_allow_html=True)

def get_image_base64(path):
    import base64
    from pathlib import Path
    try:
        data = Path(path).read_bytes()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

# Initialize session state for view management and theme
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'landing'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Sidebar navigation
with st.sidebar:
    # Premium branding header using official logo icon
    logo_base64 = get_image_base64("frontend/assets/logo_icon.jpg")
    html_inject(f"""
    <div style="display: flex; align-items: center; gap: 14px; padding: 1rem 0; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 1.5rem;">
        <img src="data:image/jpeg;base64,{logo_base64}" style="width: 38px; height: 38px; border-radius: 8px; transition: transform 0.2s;" class="logo-img" />
        <span style="font-weight: 800; font-size: 1.6rem; letter-spacing: -0.03em; background: linear-gradient(135deg, #C084FC 0%, #6366F1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-family: 'Plus Jakarta Sans', sans-serif;">RESUMATCH</span>
    </div>
    """)
    
    if st.button("Home", key="nav_home", use_container_width=True):
        st.session_state.current_view = 'landing'
        st.rerun()
    
    if st.button("Analyze Resume", key="nav_scorer", use_container_width=True):
        st.session_state.current_view = 'scorer'
        st.rerun()
    
    if st.button("History", key="nav_history", use_container_width=True):
        st.session_state.current_view = 'history'
        st.rerun()
    
    if st.button("Resources", key="nav_resources", use_container_width=True):
        st.session_state.current_view = 'resources'
        st.rerun()
    
    st.markdown("<div style='margin: 1.5rem 0 1rem 0; border-top: 1px solid rgba(255,255,255,0.05);'></div>", unsafe_allow_html=True)
    st.markdown("### 🌓 Appearance")
    
    # Theme pill switch logic
    current_theme = st.session_state.get("theme", "dark")
    toggle_text = "☀️ Light   🌙 Dark"
    if st.button(toggle_text, key="theme_toggle_btn", use_container_width=True):
        st.session_state.theme = "light" if current_theme == "dark" else "dark"
        st.rerun()

    st.markdown("<div style='margin: 1.5rem 0 1rem 0; border-top: 1px solid rgba(255,255,255,0.05);'></div>", unsafe_allow_html=True)
    st.markdown("### 👤 Account")

    from frontend.services import supabase_client

    if st.session_state.access_token:
        # Signed-in state: show premium account card.
        user_email = st.session_state.user_email
        username = user_email.split('@')[0].capitalize()
        html_inject(f"""
        <div class="account-card" style="margin-bottom: 1rem; padding: 1rem; background: rgba(255, 255, 255, 0.03); border: var(--border-soft); border-radius: var(--radius-lg);">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background: var(--grad-primary); display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 1.1rem;">
                    {username[0]}
                </div>
                <div style="flex: 1; overflow: hidden;">
                    <h4 style="margin: 0; color: var(--text-primary); font-size: 0.95rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{username}</h4>
                    <p style="margin: 0; color: var(--text-secondary); font-size: 0.75rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{user_email}</p>
                </div>
            </div>
        </div>
        """)
        if st.button("Sign out", key="btn_signout", use_container_width=True):
            supabase_client.sign_out()
            for k in ("access_token", "refresh_token", "user_id", "user_email"):
                st.session_state[k] = None
            st.rerun()
    else:
        # Signed-out state: tabs for sign-in vs sign-up + Google OAuth button.
        if st.session_state.auth_error:
            st.error(st.session_state.auth_error)
            st.session_state.auth_error = None
        if st.session_state.auth_info:
            st.info(st.session_state.auth_info)
            st.session_state.auth_info = None

        tab_in, tab_up = st.tabs(["Sign in", "Sign up"])

        with tab_in:
            with st.form("signin_form", clear_on_submit=False):
                email = st.text_input("Email", key="signin_email")
                password = st.text_input("Password", type="password", key="signin_pw")
                submitted = st.form_submit_button("Sign in", use_container_width=True)
            if submitted:
                result = supabase_client.sign_in_with_password(email, password)
                if "error" in result:
                    st.session_state.auth_error = result["error"]
                else:
                    st.session_state.access_token  = result["access_token"]
                    st.session_state.refresh_token = result["refresh_token"]
                    st.session_state.user_id       = result["user_id"]
                    st.session_state.user_email    = result["email"]
                st.rerun()

        with tab_up:
            with st.form("signup_form", clear_on_submit=False):
                email_up = st.text_input("Email", key="signup_email")
                password_up = st.text_input("Password (min 6 chars)", type="password", key="signup_pw")
                submitted_up = st.form_submit_button("Create account", use_container_width=True)
            if submitted_up:
                result = supabase_client.sign_up_with_password(email_up, password_up)
                if "error" in result:
                    st.session_state.auth_error = result["error"]
                elif result.get("pending_confirmation"):
                    st.session_state.auth_info = (
                        f"Check your inbox — confirmation email sent to {result['email']}."
                    )
                else:
                    st.session_state.access_token  = result["access_token"]
                    st.session_state.refresh_token = result["refresh_token"]
                    st.session_state.user_id       = result["user_id"]
                    st.session_state.user_email    = result["email"]
                st.rerun()

        html_inject("<div class='auth-divider'><span>or</span></div>")

        oauth = supabase_client.google_oauth_url()
        if "error" in oauth:
            st.caption(f"Google sign-in unavailable: {oauth['error']}")
        else:
            st.link_button(
                "Continue with Google",
                url=oauth["url"],
                use_container_width=True,
            )

# Main content area - render based on current view
if st.session_state.current_view == 'landing':
    # Import and render landing page
    from frontend.views import landing
    landing.render()

elif st.session_state.current_view == 'scorer':
    # Import and render scorer page
    from frontend.views import scorer
    scorer.render()

elif st.session_state.current_view == 'history':
    # Import and render history page
    from frontend.views import history
    history.render()

elif st.session_state.current_view == 'resources':
    # Import and render resources page
    from frontend.views import resources
    resources.render()
