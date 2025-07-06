"""Database service using Supabase client."""

import os
from typing import TYPE_CHECKING

from dotenv import load_dotenv

if TYPE_CHECKING:
    from supabase import Client

load_dotenv()

try:
    from supabase import create_client as create_supabase_client
except ImportError as e:
    raise ImportError("Supabase client not available. Install with: pip install supabase") from e

try:
    import streamlit as st
    _STREAMLIT_AVAILABLE = True
except ImportError:
    _STREAMLIT_AVAILABLE = False


def _get_config_value(key: str, streamlit_path: str | None = None) -> str | None:
    """Get configuration value from Streamlit secrets or environment variables.
    
    Args:
        key: Environment variable key to look for.
        streamlit_path: Path in Streamlit secrets (e.g., "supabase.url").
        
    Returns:
        str | None: Configuration value if found, None otherwise.
    """
    # Try Streamlit secrets first (for production deployment)
    if _STREAMLIT_AVAILABLE and streamlit_path:
        try:
            # Navigate through nested keys (e.g., "supabase.url" -> st.secrets["supabase"]["url"])
            keys = streamlit_path.split(".")
            value = st.secrets
            for k in keys:
                value = value[k]
            return str(value)
        except (KeyError, AttributeError):
            pass
    
    # Fall back to environment variables (for local development)
    return os.getenv(key)


def create_client() -> "Client":
    """Create a Supabase client using Streamlit secrets or environment variables.

    Returns:
        Client: Supabase client configured from secrets or environment.

    Raises:
        ValueError: If required configuration is missing.
    """
    supabase_url = _get_config_value("SUPABASE_URL", "supabase.url")
    supabase_key = _get_config_value("SUPABASE_ANON_KEY", "supabase.anon_key")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "Supabase configuration missing. "
            "Set SUPABASE_URL and SUPABASE_ANON_KEY in environment variables "
            "or configure supabase.url and supabase.anon_key in Streamlit secrets."
        )

    return create_supabase_client(supabase_url, supabase_key)


def create_admin_client() -> "Client":
    """Create a Supabase client with service role for admin operations.

    Returns:
        Client: Supabase client configured with service role key for admin operations.

    Raises:
        ValueError: If required configuration is missing.
    """
    supabase_url = _get_config_value("SUPABASE_URL", "supabase.url")
    supabase_key = _get_config_value("SUPABASE_SERVICE_KEY", "supabase.service_key")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "Supabase admin configuration missing. "
            "Set SUPABASE_URL and SUPABASE_SERVICE_KEY in environment variables "
            "or configure supabase.url and supabase.service_key in Streamlit secrets."
        )

    return create_supabase_client(supabase_url, supabase_key)
