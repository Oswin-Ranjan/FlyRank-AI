from fastapi import FastAPI, Body, HTTPException, Depends
from auth import signup_user, login_user, get_current_user, logout_user

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Server running and connected to Supabase"}

# SIGNUP
@app.post("/auth/signup", status_code=201)
def signup(body: dict = Body(...)):
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    return signup_user(email, password)

# LOGIN
@app.post("/auth/login")
def login(body: dict = Body(...)):
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    response = login_user(email, password)

    if response.user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials"
        )

    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token
    }

# PUBLIC ROUTE
@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}

# PROTECTED PROFILE
@app.get("/protected/profile")
def protected_profile(user = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }

# SECOND PROTECTED ROUTE 
@app.get("/protected/dashboard")
def dashboard(user = Depends(get_current_user)):
    return {
        "message": f"Welcome {user.email} to your dashboard"
    }

# LOGOUT (protected)
@app.post("/auth/logout", status_code=204)
def logout(user = Depends(get_current_user)):
    logout_user()