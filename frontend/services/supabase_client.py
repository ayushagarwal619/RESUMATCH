import os
import logging
import json
import time
import jwt
from pathlib import Path
from typing import Any, Dict
import streamlit as st
from supabase import Client, create_client

logger = logging.getLogger('ats_resume_scorer')


try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / '.env')
except ImportError:
    pass


def _secret(key: str, section: str = 'supabase') -> str:
    """Read from env first, then fall back to st.secrets[section][key]."""
    val = os.getenv(key, '')
    if val:
        return val
    try:
        return st.secrets[section][key]
    except (KeyError, FileNotFoundError, AttributeError):
        return ''


SUPABASE_URL = _secret('SUPABASE_URL')
SUPABASE_ANON_KEY = _secret('SUPABASE_ANON_KEY')

OAUTH_REDIRECT_URL = (
    os.getenv('AUTH_REDIRECT_URL')
    or _secret('redirect_uri', 'google_oauth')
    or 'http://localhost:8501'
)


def _missing_config() -> str | None:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return 'Supabase is not configured — set SUPABASE_URL and SUPABASE_ANON_KEY in .env or .streamlit/secrets.toml'
    return None


@st.cache_resource
def get_client() -> Client | None:
    """Cached singleton — preserves PKCE state across Streamlit reruns."""
    if _missing_config():
        return None
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


SESSION_FILE_PATH = Path("c:/Users/ayush/Desktop/PRIME_PROJECTS/ATS/.streamlit_session.json")

def save_session_locally(session, user) -> None:
    try:
        data = {
            'access_token':  session.access_token,
            'refresh_token': session.refresh_token,
            'user_id':       user.id,
            'email':         user.email,
        }
        SESSION_FILE_PATH.write_text(json.dumps(data), encoding="utf-8")
    except Exception as e:
        logger.warning(f"Failed to save local session: {e}")

def clear_local_session() -> None:
    try:
        if SESSION_FILE_PATH.exists():
            SESSION_FILE_PATH.unlink()
    except Exception as e:
        logger.warning(f"Failed to clear local session: {e}")

def _session_dict(session, user) -> Dict[str, Any]:
    save_session_locally(session, user)
    return {
        'access_token':  session.access_token,
        'refresh_token': session.refresh_token,
        'user_id':       user.id,
        'email':         user.email,
        'full_name':     user.email.split('@')[0].capitalize(),
        'authenticated': True,
        'session':       {
            'access_token': session.access_token,
            'refresh_token': session.refresh_token,
            'expires_at': session.expires_at if hasattr(session, 'expires_at') else None
        }
    }

def restore_session() -> Dict[str, Any] | None:
    """Attempts to restore the session from the local file, auto-refreshing if expired."""
    try:
        if not SESSION_FILE_PATH.exists():
            return None
        
        data = json.loads(SESSION_FILE_PATH.read_text(encoding="utf-8"))
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        user_id = data.get("user_id")
        email = data.get("email")
        
        if not access_token or not refresh_token:
            return None
        
        client = get_client()
        if not client:
            return None
            
        try:
            claims = jwt.decode(access_token, options={"verify_signature": False})
            exp = claims.get("exp", 0)
            now = time.time()
            if exp - now < 120:  # less than 2 minutes left
                logger.info("Local access token is expired or close to expiry. Refreshing session...")
                resp = client.auth.refresh_session(refresh_token)
                if resp.session and resp.user:
                    save_session_locally(resp.session, resp.user)
                    return _session_dict(resp.session, resp.user)
                else:
                    clear_local_session()
                    return None
        except Exception as e:
            logger.warning(f"JWT check or auto-refresh failed: {e}")
            try:
                resp = client.auth.refresh_session(refresh_token)
                if resp.session and resp.user:
                    save_session_locally(resp.session, resp.user)
                    return _session_dict(resp.session, resp.user)
            except Exception:
                pass
            clear_local_session()
            return None
            
        try:
            client.auth.set_session(access_token, refresh_token)
        except Exception as e:
            logger.warning(f"set_session on client memory failed: {e}")
            
        return {
            'access_token':  access_token,
            'refresh_token': refresh_token,
            'user_id':       user_id,
            'email':         email,
            'full_name':     email.split('@')[0].capitalize() if email else "User",
            'authenticated': True,
            'session':       {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_at': None
            }
        }
    except Exception as e:
        logger.warning(f"restore_session failed: {e}")
        return None

def sign_in_with_password(email: str, password: str) -> Dict[str, Any]:
    err = _missing_config()
    if err:
        return {'error': err}
    try:
        resp = get_client().auth.sign_in_with_password(
            {'email': email, 'password': password}
        )
        if not resp.session or not resp.user:
            return {'error': 'Invalid credentials'}
        return _session_dict(resp.session, resp.user)
    except Exception as exc:
        logger.warning(f'sign_in_with_password failed: {exc}')
        return {'error': _humanize(exc)}

def sign_up_with_password(email: str, password: str) -> Dict[str, Any]:
    err = _missing_config()
    if err:
        return {'error': err}
    try:
        resp = get_client().auth.sign_up({'email': email, 'password': password})
        if resp.session and resp.user:
            return _session_dict(resp.session, resp.user)
        if resp.user:
            return {'pending_confirmation': True, 'email': email}
        return {'error': 'Sign-up failed'}
    except Exception as exc:
        logger.warning(f'sign_up failed: {exc}')
        return {'error': _humanize(exc)}

def google_oauth_url() -> Dict[str, Any]:
    err = _missing_config()
    if err:
        return {'error': err}
    try:
        resp = get_client().auth.sign_in_with_oauth({
            'provider': 'google',
            'options': {'redirect_to': OAUTH_REDIRECT_URL},
        })
        return {'url': resp.url}
    except Exception as exc:
        logger.warning(f'oauth url generation failed: {exc}')
        return {'error': _humanize(exc)}

def exchange_code_for_session(auth_code: str) -> Dict[str, Any]:
    """Called once after the OAuth provider redirects back with `?code=...`."""
    err = _missing_config()
    if err:
        return {'error': err}
    client = get_client()
    try:
        storage_key = f'{client.auth._storage_key}-code-verifier'
        code_verifier = client.auth._storage.get_item(storage_key) or ''
        resp = client.auth.exchange_code_for_session({
            'auth_code': auth_code,
            'code_verifier': code_verifier,
            'redirect_to': OAUTH_REDIRECT_URL,
        })
        if not resp.session or not resp.user:
            return {'error': 'OAuth exchange returned no session'}
        return _session_dict(resp.session, resp.user)
    except Exception as exc:
        logger.warning(f'exchange_code_for_session failed: {exc}')
        return {'error': _humanize(exc)}

def sign_out() -> None:
    if _missing_config():
        return
    try:
        get_client().auth.sign_out()
    except Exception as exc:
        logger.warning(f'sign_out failed: {exc}')
    clear_local_session()


def _humanize(exc: Exception) -> str:
    msg = str(exc)
    # supabase errors arrive as "<status>: {json blob}" — surface the human bit
    if 'invalid_grant' in msg.lower() or 'invalid login' in msg.lower():
        return 'Wrong email or password'
    if 'user already registered' in msg.lower() or 'already been registered' in msg.lower():
        return 'An account with this email already exists — try signing in'
    if 'password should be at least' in msg.lower():
        return 'Password too short (Supabase default is 6 characters)'
    return msg
