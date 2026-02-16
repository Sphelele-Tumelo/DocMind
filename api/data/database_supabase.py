from fastapi import Depends, HTTPException
from supabase import create_client, Client
import os
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY") # Make sure to set this in your .env file

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("Supabase URL and Service Key must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_db():
    return supabase