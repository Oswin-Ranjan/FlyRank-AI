from fastapi import Header, HTTPException
from database import supabase

# SIGNUP
def signup_user(email: str, password: str):
    return supabase.auth.sign_up({
        "email": email,
        "password": password
    })

# LOGIN
def login_user(email: str, password: str):
    return supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

# AUTH GUARD (Middleware / Dependency)
def get_current_user(authorization: str = Header(None)):

    # Check header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    # Extract token
    token = authorization.split(" ")[1]

    # Verify token with Supabase
    try:
        response = supabase.auth.get_user(token)
        user = response.user
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    # Return user (used in routes)
    return user

# LOGOUT
def logout_user():
    try:
        supabase.auth.sign_out()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Logout failed"
        )