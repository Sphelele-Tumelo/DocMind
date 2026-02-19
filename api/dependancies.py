from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security
from supabase import Client
from fastapi import HTTPException
import supabase

auth_scheme = HTTPBearer()


def get_current_user(
    token: HTTPAuthorizationCredentials = Security(auth_scheme)):
    
    try:
        user = supabase.auth.api.get_user(token.credentials)
        if user:
            return user.user.id
    except:    
        
        raise HTTPException(status_code=401, detail="Invalid token")