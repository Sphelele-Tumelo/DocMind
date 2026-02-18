from fastapi import Depends, HTTPException
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from pathlib import Path


# Load environment variables from .env file in the api directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY") # Make sure to set this in your .env file

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("Supabase URL and Service Key must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_db():
    return supabase