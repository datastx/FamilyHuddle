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


def create_client() -> "Client":
    """Create a Supabase client using environment variables.

    Returns:
        Client: Supabase client configured from SUPABASE_URL and SUPABASE_ANON_KEY.

    Raises:
        ValueError: If required environment variables are missing.
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "Supabase configuration missing. "
            "Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
        )

    return create_supabase_client(supabase_url, supabase_key)


def create_admin_client() -> "Client":
    """Create a Supabase client with service role for admin operations.

    Returns:
        Client: Supabase client configured with service role key for admin operations.

    Raises:
        ValueError: If required environment variables are missing.
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "Supabase admin configuration missing. "
            "Set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables."
        )

    return create_supabase_client(supabase_url, supabase_key)
