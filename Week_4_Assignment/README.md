# 🔐 FastAPI Auth System with Supabase

## 🚀 Overview

This project is a backend authentication system built using FastAPI and Supabase. It includes user signup, login, logout, JWT authentication, protected routes using middleware, and Swagger UI with bearer authentication.

---

## ⚙️ Features

- User Signup & Login  
- JWT Authentication (Access + Refresh Tokens)  
- Middleware-based Route Protection  
- Logout Functionality  
- Public & Protected Routes  
- Swagger UI with Authorization  

---

## 🛠️ Tech Stack

- FastAPI  
- Supabase  
- Python  
- Uvicorn  

---

## 📦 Installation & Setup

### 1. Clone Repository

git clone [https://github.com/Oswin-Ranjan/FlyRank-AI/tree/main/Week_4_Assignment]

cd [this_repo_path]  

### 2. Create Virtual Environment

python -m venv .venv  
.venv\Scripts\activate  

### 3. Install Dependencies

pip install -r requirements.txt  

### 4. Environment Variables

Create a `.env` file:

SUPABASE_URL=your_project_url  
SUPABASE_KEY=your_anon_key  
PORT=3000

---

## ▶️ Run Server

uvicorn app:app --reload  

Server runs at: http://localhost:8000  

---

## 📡 API Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|--------------|-------------|
| /auth/signup | POST | ❌ | Register user |
| /auth/login | POST | ❌ | Login user |
| /public/info | GET | ❌ | Public route |
| /protected/profile | GET | ✅ | User profile |
| /protected/dashboard | GET | ✅ | Dashboard |
| /auth/logout | POST | ✅ | Logout |

---

## 🔐 Authentication

Authorization: Bearer \<access_token>

---

## 📄 Swagger UI

Open: http://localhost:8000/docs  

Steps:

1. Click **Authorize**  
2. Enter: Bearer \<your_access_token>  
3. Test protected routes  

---

## 📸 Screenshot

<img width="1238" height="14204" alt="localhost_8000_docs" src="https://github.com/user-attachments/assets/f6aceb65-898b-4ebe-af0e-5e27fde509ea" />
