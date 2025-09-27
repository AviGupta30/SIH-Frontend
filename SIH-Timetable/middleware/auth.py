from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.database import supabase

security = HTTPBearer()

async def auth_middleware(request: Request, credentials: HTTPAuthorizationCredentials = security):
    try:
        user = supabase.auth.get_user(credentials.credentials)
        request.state.user = user
        return user
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
