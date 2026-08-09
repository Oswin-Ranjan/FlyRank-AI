from fastapi import FastAPI, Body, HTTPException
from auth import signup_user, login_user

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Server running and connected to Supabase"}

# 🔐 SIGNUP
@app.post("/auth/signup", status_code=201)
def signup(body: dict = Body(...)):
    email = body.get("email")
    password = body.get("password")

    # ❗ Validation (PDF requirement)
    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    response = signup_user(email, password)

    return response

# 🔐 LOGIN
@app.post("/auth/login")
def login(body: dict = Body(...)):
    email = body.get("email")
    password = body.get("password")

    # ❗ Validation
    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    response = login_user(email, password)

    # ❗ Handle invalid credentials
    if response.user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials"
        )

    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token
    }