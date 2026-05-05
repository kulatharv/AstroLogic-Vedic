from models.user_model import Feedback, User, UserProfile, UserActivity
# '''
# from fastapi import FastAPI
# from api.api import router

# app = FastAPI(title="AstroLogic Backend")

# app.include_router(router)


# from astro_engine.chart_engine import generate_full_chart
# from astro_engine.prediction_builder import build_prediction_prompt
# from astro_engine.llm_engine import ask_llm
# from astro_engine.chat_mode import chat_with_chart
# import json

# # -----------------------------
# # INPUT
# # -----------------------------

# year = int(input("Enter year: "))
# month = int(input("Enter month: "))
# day = int(input("Enter day: "))
# hour = float(input("Enter hour: "))

# latitude = 18.5204
# longitude = 73.8567

# # -----------------------------
# # GENERATE CHART
# # -----------------------------

# chart = generate_full_chart(year, month, day, hour, latitude, longitude)

# # Optional: Print JSON (can remove later)
# print("\n========= RAW CHART DATA =========\n")
# print(json.dumps(chart, indent=4, default=str))

# # -----------------------------
# # TEST EVENT PREDICTION
# # -----------------------------

# marriage_prompt = build_prediction_prompt(chart, "marriage")
# marriage_output = ask_llm(marriage_prompt)

# print("\n========= AI Marriage Interpretation =========\n")
# print(marriage_output)

# # -----------------------------
# # START CHAT MODE
# # -----------------------------

# chat_with_chart(chart)

# '''
# #01/05/2026
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# # ✅ ADD IMMEDIATELY AFTER app creation
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # THEN import rest
# from fastapi import Request
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from fastapi.responses import HTMLResponse

# from database import Base, SessionLocal, engine
# from models.blog_model import Blog
# from models.user_model import User, UserProfile, UserActivity

# from api.api import router

# app.include_router(router, prefix="/api")
# '''
# #26/04/2026

# from fastapi import FastAPI, Request
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from fastapi.responses import HTMLResponse

# from database import engine
# from models.blog_model import Blog

# from api.api import router

# app = FastAPI()

# from fastapi.middleware.cors import CORSMiddleware

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # for now (later restrict)
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# '''
# #Blog.metadata.create_all(bind=engine)

# Base.metadata.create_all(bind=engine)

# # Include API routes
# app.include_router(router)
# app.include_router(router, prefix="/api")
# #app.include_router(router, prefix="/api", tags=["API"])
# # Setup templates
# templates = Jinja2Templates(directory="templates")

# # Mount static folder
# app.mount("/static", StaticFiles(directory="static"), name="static")


# # ------------------ HTML Pages ------------------

# @app.get("/", response_class=HTMLResponse)
# def home(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})


# #@app.get("/prediction", response_class=HTMLResponse)
# #def prediction_page(request: Request):
# #    return templates.TemplateResponse("prediction.html", {"request": request})

# @app.get("/prediction", response_class=HTMLResponse)
# def prediction_page(request: Request):
#     # If prediction.html is in templates folder
#     return templates.TemplateResponse("prediction.html", {"request": request})
#     # OR if it's in root directory:
#     # from fastapi.responses import FileResponse
#     # return FileResponse("prediction.html")

# @app.get("/chat", response_class=HTMLResponse)
# def chat_page(request: Request):
#     return templates.TemplateResponse("chat.html", {"request": request})


# @app.get("/panchang.html", response_class=HTMLResponse)
# def panchang_page(request: Request):
#     return templates.TemplateResponse("panchang.html", {"request": request})


# @app.get("/blogs", response_class=HTMLResponse)
# def blogs_page(request: Request):
#     return templates.TemplateResponse("blogs.html", {"request": request})


# @app.get("/about", response_class=HTMLResponse)
# def about_page(request: Request):
#     return templates.TemplateResponse("about.html", {"request": request})


# @app.get("/horoscope", response_class=HTMLResponse)
# def horoscope_page(request: Request):
#     return templates.TemplateResponse("daily-horoscope.html", {"request": request})


# @app.get("/kundali", response_class=HTMLResponse)
# def kundali_page(request: Request):
#     return templates.TemplateResponse("kundali.html", {"request": request})

# @app.get("/blog/{blog_id}", response_class=HTMLResponse)
# def blog_detail(request: Request, blog_id: int):
#     return templates.TemplateResponse("blog-detail.html", {
#         "request": request,
#         "blog_id": blog_id
#     })
# from starlette.middleware.sessions import SessionMiddleware
# import secrets

# app.add_middleware(
#     SessionMiddleware,
#     secret_key="super-secret-key-change-this"
# )
# from fastapi import Form
# from fastapi.responses import RedirectResponse
# from fastapi import Request

# ADMIN_USERNAME = "admin"
# ADMIN_PASSWORD = "astro123"

# @app.get("/admin/blogs", response_class=HTMLResponse)
# def admin_blog_page(request: Request):

#     if request.session.get("admin") != "true":
#         return RedirectResponse("/admin/login", status_code=303)

#     return templates.TemplateResponse("admin-blog.html", {"request": request})

# # ------------------ LOGIN PAGE ------------------

# @app.get("/admin/login", response_class=HTMLResponse)
# def admin_login_page(request: Request):
#     return templates.TemplateResponse("admin-login.html", {"request": request})


# # ------------------ LOGIN PROCESS ------------------

# @app.post("/admin/login")
# def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):

#     if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
#         request.session["admin"] = "true"   # store string
#         return RedirectResponse("/admin/blogs", status_code=303)

#     return templates.TemplateResponse("admin-login.html", {
#         "request": request,
#         "error": "Invalid credentials"
#     })

# # ------------------ LOGOUT ------------------

# @app.get("/admin/logout")
# def admin_logout(request: Request):
#     request.session.clear()
#     return RedirectResponse("/", status_code=303)



# from api.blogs import router as admin_blog_router

# app.include_router(admin_blog_router)





# '''

# import json
# import sys
# from astro_engine.chart_engine import generate_full_chart
# from astro_engine.llm_engine import ask_llm
# from astro_engine.prediction_builder import build_prediction_prompt
# from astro_engine.chat_mode import chat_with_chart

# def main():
#     print("--- AstroLogic Backend Engine ---")
    
#     try:
#         # 1. Collect Birth Details
#         # Using a try-except block to handle non-integer inputs
#         year = int(input("Enter year (YYYY): "))
#         month = int(input("Enter month (1-12): "))
#         day = int(input("Enter day (1-31): "))
#         hour = float(input("Enter hour (0-23.99): "))
        
#         # Default coordinates (Pune, India) - Consider making these inputs too
#         latitude = 18.5204
#         longitude = 73.8567

#         print(f"\n[1/3] Generating Chart for {year}-{month}-{day} at {hour}h...")
        
#         # 2. Generate Astronomical Data
#         chart = generate_full_chart(year, month, day, hour, latitude, longitude)
        
#         # Optional: Save chart to a local file for debugging
#         with open("last_chart.json", "w") as f:
#             json.dump(chart, f, indent=4, default=str)

#         # 3. Prediction Phase
#         print("\n[2/3] Analyzing Marriage Prospects via AI...")
#         marriage_prompt = build_prediction_prompt(chart, "marriage")
#         marriage_output = ask_llm(marriage_prompt)

#         print("\n" + "="*45)
#         print("         AI MARRIAGE INTERPRETATION         ")
#         print("="*45)
#         print(marriage_output)
#         print("="*45 + "\n")

#         # 4. Interactive Mode
#         print("[3/3] Entering Interactive Chat Mode (type 'exit' to stop)...")
#         chat_with_chart(chart)

#     except ValueError:
#         print("\nError: Please enter valid numbers for date and time.")
#     except Exception as e:
#         print(f"\nAn unexpected error occurred: {e}")

# if __name__ == "__main__":
#     main()

#     '''
# '''
# #update on 26/04/2026
# from fastapi import FastAPI, Request, Form
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from fastapi.responses import HTMLResponse, RedirectResponse
# from starlette.middleware.sessions import SessionMiddleware
# import secrets

# from database import engine
# from models.blog_model import Blog
# from api.api import router
# from api.blogs import router as admin_blog_router

# # Create FastAPI app
# app = FastAPI(title="AstroLogic Backend")

# # Create database tables
# Blog.metadata.create_all(bind=engine)

# # Include API routes - ONLY ONCE with proper prefix
# app.include_router(router, prefix="/api")  # All API routes are under /api

# # Include admin blog routes
# app.include_router(admin_blog_router)

# # Setup templates
# templates = Jinja2Templates(directory="templates")

# # Mount static folder
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # Session middleware for admin
# app.add_middleware(
#     SessionMiddleware,
#     secret_key="super-secret-key-change-this"
# )

# # Admin credentials
# ADMIN_USERNAME = "admin"
# ADMIN_PASSWORD = "astro123"

# # ============================================================
# # HTML PAGE ROUTES
# # ============================================================

# @app.get("/", response_class=HTMLResponse)
# def home(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# @app.get("/prediction", response_class=HTMLResponse)
# def prediction_page(request: Request):
#     return templates.TemplateResponse("prediction.html", {"request": request})

# @app.get("/chat", response_class=HTMLResponse)
# def chat_page(request: Request):
#     return templates.TemplateResponse("chat.html", {"request": request})

# @app.get("/panchang.html", response_class=HTMLResponse)
# def panchang_page(request: Request):
#     return templates.TemplateResponse("panchang.html", {"request": request})

# @app.get("/blogs", response_class=HTMLResponse)
# def blogs_page(request: Request):
#     return templates.TemplateResponse("blogs.html", {"request": request})

# @app.get("/about", response_class=HTMLResponse)
# def about_page(request: Request):
#     return templates.TemplateResponse("about.html", {"request": request})

# @app.get("/horoscope", response_class=HTMLResponse)
# def horoscope_page(request: Request):
#     return templates.TemplateResponse("daily-horoscope.html", {"request": request})

# @app.get("/kundali", response_class=HTMLResponse)
# def kundali_page(request: Request):
#     return templates.TemplateResponse("kundali.html", {"request": request})

# @app.get("/blog/{blog_id}", response_class=HTMLResponse)
# def blog_detail(request: Request, blog_id: int):
#     return templates.TemplateResponse("blog-detail.html", {
#         "request": request,
#         "blog_id": blog_id
#     })

# # ============================================================
# # ADMIN ROUTES
# # ============================================================

# @app.get("/admin/blogs", response_class=HTMLResponse)
# def admin_blog_page(request: Request):
#     if request.session.get("admin") != "true":
#         return RedirectResponse("/admin/login", status_code=303)
#     return templates.TemplateResponse("admin-blog.html", {"request": request})

# @app.get("/admin/login", response_class=HTMLResponse)
# def admin_login_page(request: Request):
#     return templates.TemplateResponse("admin-login.html", {"request": request})

# @app.post("/admin/login")
# def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
#     if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
#         request.session["admin"] = "true"
#         return RedirectResponse("/admin/blogs", status_code=303)
#     return templates.TemplateResponse("admin-login.html", {
#         "request": request,
#         "error": "Invalid credentials"
#     })

# @app.get("/admin/logout")
# def admin_logout(request: Request):
#     request.session.clear()
#     return RedirectResponse("/", status_code=303)

# # ============================================================
# # RUN THE APP
# # ============================================================

# if __name__ == "__main__":
#     import uvicorn
#     print("\n" + "="*50)
#     print("🚀 AstroLogic Server Starting...")
#     print("="*50)
#     print(f"📍 Main Page: http://localhost:8000")
#     print(f"📊 API Docs: http://localhost:8000/docs")
#     print(f"⭐ Horoscope: http://localhost:8000/horoscope")
#     print(f"🌙 Panchang: http://localhost:8000/panchang")
#     print(f"🔮 Prediction: http://localhost:8000/prediction")
#     print(f"📚 Blogs: http://localhost:8000/blogs")
#     print("="*50 + "\n")
    
#     uvicorn.run(
#         app,
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         log_level="info"
#     )
#     '''


# #02/05/2025
# #implementing authentication
# from datetime import datetime, timedelta
# import hashlib
# import hmac
# import os
# from sqlalchemy.orm import joinedload
# from fastapi import Form
# from fastapi.responses import HTMLResponse, RedirectResponse
# from database import SessionLocal
# from models.user_model import User, UserProfile
# def hash_password(password: str) -> str:
#     salt = os.urandom(16).hex()
#     digest = hashlib.pbkdf2_hmac(
#         "sha256",
#         password.encode("utf-8"),
#         salt.encode("utf-8"),
#         120000
#     ).hex()
#     return f"{salt}${digest}"

# def verify_password(password: str, stored_hash: str) -> bool:
#     try:
#         salt, digest = stored_hash.split("$", 1)
#     except ValueError:
#         return False

#     check = hashlib.pbkdf2_hmac(
#         "sha256",
#         password.encode("utf-8"),
#         salt.encode("utf-8"),
#         120000
#     ).hex()
#     return hmac.compare_digest(check, digest)

# def get_current_user(request: Request, db):
#     user_id = request.session.get("user_id")
#     if not user_id:
#         return None
#     return db.query(User).filter(User.id == user_id).first()

# def log_activity(db, request: Request, action: str, user_id=None, details: str = None):
#     activity = UserActivity(
#         user_id=user_id,
#         action=action,
#         details=details,
#         ip_address=request.client.host if request.client else None,
#         user_agent=request.headers.get("user-agent"),
#     )
#     db.add(activity)
#     db.commit()
# @app.get("/signup", response_class=HTMLResponse)
# def signup_page(request: Request):
#     if request.session.get("user_id"):
#         return RedirectResponse("/", status_code=303)

#     return templates.TemplateResponse("auth.html", {"request": request})

# @app.post("/signup")
# def signup(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
#     db = SessionLocal()
#     try:
#         email = email.strip().lower()

#         if db.query(User).filter(User.email == email).first():
#             return templates.TemplateResponse("auth.html", {
#                 "request": request,
#                 "mode": "signup",
#                 "title": "Create Account",
#                 "button": "Create Account",
#                 "error": "Email already registered"
#             })

#         user = User(
#             name=name.strip(),
#             email=email,
#             password_hash=hash_password(password)
#         )
#         db.add(user)
#         db.commit()
#         db.refresh(user)

#         profile = UserProfile(user_id=user.id)
#         db.add(profile)
#         db.commit()

#         request.session["user_id"] = user.id
#         log_activity(db, request, "signup", user.id, "User created account")

#         return RedirectResponse("/profile", status_code=303)
#     finally:
#         db.close()

# @app.get("/login", response_class=HTMLResponse)
# def login_page(request: Request):
#     if request.session.get("user_id"):
#         return RedirectResponse("/", status_code=303)

#     return templates.TemplateResponse("auth.html", {"request": request})


# @app.post("/login")
# def login(request: Request, email: str = Form(...), password: str = Form(...)):
#     db = SessionLocal()
#     try:
#         email = email.strip().lower()
#         user = db.query(User).filter(User.email == email).first()

#         if not user or not verify_password(password, user.password_hash):
#             return templates.TemplateResponse("auth.html", {
#                 "request": request,
#                 "mode": "login",
#                 "title": "User Login",
#                 "button": "Login",
#                 "error": "Invalid email or password"
#             })

#         request.session["user_id"] = user.id
#         user.last_login_at = datetime.utcnow()
#         db.commit()

#         log_activity(db, request, "login", user.id, "User logged in")

#         return RedirectResponse("/", status_code=303)
#     finally:
#         db.close()

# @app.get("/logout")
# def logout(request: Request):
#     db = SessionLocal()
#     try:
#         user_id = request.session.get("user_id")
#         if user_id:
#             log_activity(db, request, "logout", user_id, "User logged out")

#         request.session.pop("user_id", None)
#         return RedirectResponse("/", status_code=303)
#     finally:
#         db.close()
# @app.get("/profile", response_class=HTMLResponse)
# def profile_page(request: Request):
#     db = SessionLocal()
#     try:
#         user = get_current_user(request, db)
#         if not user:
#             return RedirectResponse("/login", status_code=303)

#         profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
#         activities = (
#             db.query(UserActivity)
#             .filter(UserActivity.user_id == user.id)
#             .order_by(UserActivity.created_at.desc())
#             .limit(10)
#             .all()
#         )

#         return templates.TemplateResponse("profile.html", {
#             "request": request,
#             "user": user,
#             "profile": profile,
#             "activities": activities
#         })
#     finally:
#         db.close()

# @app.post("/profile")
# def update_profile(
#     request: Request,
#     name: str = Form(...),
#     phone: str = Form(""),
#     birth_date: str = Form(""),
#     birth_time: str = Form(""),
#     birth_city: str = Form(""),
#     zodiac_sign: str = Form(""),
#     notes: str = Form("")
# ):
#     db = SessionLocal()
#     try:
#         user = get_current_user(request, db)
#         if not user:
#             return RedirectResponse("/login", status_code=303)

#         profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
#         if not profile:
#             profile = UserProfile(user_id=user.id)
#             db.add(profile)

#         user.name = name.strip()
#         profile.phone = phone.strip()
#         profile.birth_date = birth_date
#         profile.birth_time = birth_time
#         profile.birth_city = birth_city.strip()
#         profile.zodiac_sign = zodiac_sign.strip()
#         profile.notes = notes.strip()

#         db.commit()
#         log_activity(db, request, "profile_update", user.id, "User updated profile")

#         return RedirectResponse("/", status_code=303)

#     finally:
#         db.close()
# @app.get("/admin/activity", response_class=HTMLResponse)
# def admin_activity_page(request: Request):
#     if request.session.get("admin") != "true":
#         return RedirectResponse("/admin/login", status_code=303)

#     db = SessionLocal()
#     try:
#         activities = (
#             db.query(UserActivity)
#             .options(joinedload(UserActivity.user))
#             .order_by(UserActivity.created_at.desc())
#             .limit(100)
#             .all()
#         )

#         since = datetime.utcnow() - timedelta(days=7)

#         return templates.TemplateResponse("admin-activity.html", {
#             "request": request,
#             "activities": activities,
#             "total_users": db.query(User).count(),
#             "total_activities": db.query(UserActivity).count(),
#             "recent_signups": db.query(User).filter(User.created_at >= since).count()
#         })
#     finally:
#         db.close()


from datetime import datetime, timedelta
import hashlib
import hmac
import os

from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import joinedload

from database import Base, SessionLocal, engine
from models.blog_model import Blog
from models.user_model import User, UserProfile, UserActivity
from api.api import router
from api.blogs import router as admin_blog_router
from api.api import router as api_router
from api.blogs import router as admin_blog_router


from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
# ============================================================
# APP SETUP
# ============================================================

app = FastAPI(title="AstroLogic Backend")
# Include the API router
Base.metadata.create_all(bind=engine)

# Include routers (ADD THESE LINES)
app.include_router(api_router, prefix="/api")
app.include_router(admin_blog_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key-change-this"
)

Base.metadata.create_all(bind=engine)

app.include_router(router, prefix="/api")
app.include_router(admin_blog_router)


app.mount("/static", StaticFiles(directory="static"), name="static")

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "astro123"


# ============================================================
# AUTH HELPERS
# ============================================================

def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 120000
    ).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, digest = stored_hash.split("$", 1)
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 120000
    ).hex()
    return hmac.compare_digest(check, digest)


def get_current_user(request: Request, db):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def log_activity(db, request: Request, action: str, user_id=None, details: str = None):
    activity = UserActivity(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(activity)
    db.commit()


# ============================================================
# PUBLIC PAGES
# ============================================================

# @app.get("/", response_class=HTMLResponse)
# def home(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/prediction", response_class=HTMLResponse)
def prediction_page(request: Request):
    return templates.TemplateResponse("prediction.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/panchang.html", response_class=HTMLResponse)
def panchang_page(request: Request):
    return templates.TemplateResponse("panchang.html", {"request": request})

@app.get("/blogs", response_class=HTMLResponse)
def blogs_page(request: Request):
    return templates.TemplateResponse("blogs.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/horoscope", response_class=HTMLResponse)
def horoscope_page(request: Request):
    return templates.TemplateResponse("daily-horoscope.html", {"request": request})

# @app.get("/kundali", response_class=HTMLResponse)
# def kundali_page(request: Request):
#     return templates.TemplateResponse("kundali.html", {"request": request})

# Add this helper function if not already present
def get_current_user(request: Request, db):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()

@app.get("/kundali", response_class=HTMLResponse)
def kundali_page(request: Request):
    db = SessionLocal()
    try:
        user = get_current_user(request, db)
        return templates.TemplateResponse("kundali.html", {
            "request": request,
            "user": user,
            "require_login": user is None,  # True only when user is NOT logged in
        })
    finally:
        db.close()

@app.get("/blog/{blog_id}", response_class=HTMLResponse)
def blog_detail(request: Request, blog_id: int):
    return templates.TemplateResponse("blog-detail.html", {
        "request": request,
        "blog_id": blog_id
    })


# # ============================================================
# # AUTH ROUTES
# # ============================================================

# @app.get("/signup", response_class=HTMLResponse)
# def signup_page(request: Request):
#     if request.session.get("user_id"):
#         return RedirectResponse("/", status_code=303)
#     return templates.TemplateResponse("auth.html", {"request": request})

# @app.post("/signup")
# def signup(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
#     db = SessionLocal()
#     try:
#         email = email.strip().lower()
#         if db.query(User).filter(User.email == email).first():
#             return templates.TemplateResponse("auth.html", {
#                 "request": request,
#                 "mode": "signup",
#                 "error": "Email already registered"
#             })
#         user = User(name=name.strip(), email=email, password_hash=hash_password(password))
#         db.add(user)
#         db.commit()
#         db.refresh(user)

#         db.add(UserProfile(user_id=user.id))
#         db.commit()

#         request.session["user_id"] = user.id
#         log_activity(db, request, "signup", user.id, "User created account")
#         return RedirectResponse("/profile", status_code=303)
#     finally:
#         db.close()

# @app.get("/login", response_class=HTMLResponse)
# def login_page(request: Request):
#     if request.session.get("user_id"):
#         return RedirectResponse("/", status_code=303)
#     return templates.TemplateResponse("auth.html", {"request": request})

# @app.post("/login")
# def login(request: Request, email: str = Form(...), password: str = Form(...)):
#     db = SessionLocal()
#     try:
#         email = email.strip().lower()
#         user = db.query(User).filter(User.email == email).first()
#         if not user or not verify_password(password, user.password_hash):
#             return templates.TemplateResponse("auth.html", {
#                 "request": request,
#                 "mode": "login",
#                 "error": "Invalid email or password"
#             })
#         request.session["user_id"] = user.id
#         user.last_login_at = datetime.utcnow()
#         db.commit()
#         log_activity(db, request, "login", user.id, "User logged in")
#         return RedirectResponse("/", status_code=303)
#     finally:
#         db.close()

# @app.get("/logout")
# def logout(request: Request):
#     db = SessionLocal()
#     try:
#         user_id = request.session.get("user_id")
#         if user_id:
#             log_activity(db, request, "logout", user_id, "User logged out")
#         request.session.pop("user_id", None)
#         return RedirectResponse("/", status_code=303)
#     finally:
#         db.close()
# ============================================================
# AUTH ROUTES
# ============================================================

@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request, redirect: str = None):
    if request.session.get("user_id"):
        # If already logged in, redirect to the original page or home
        redirect_to = redirect or "/"
        return RedirectResponse(redirect_to, status_code=303)
    return templates.TemplateResponse("auth.html", {"request": request, "redirect": redirect})

@app.post("/signup")
def signup(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...), redirect: str = Form(None)):
    db = SessionLocal()
    try:
        email = email.strip().lower()
        if db.query(User).filter(User.email == email).first():
            return templates.TemplateResponse("auth.html", {
                "request": request,
                "mode": "signup",
                "error": "Email already registered",
                "redirect": redirect
            })
        user = User(name=name.strip(), email=email, password_hash=hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)

        db.add(UserProfile(user_id=user.id))
        db.commit()

        request.session["user_id"] = user.id
        log_activity(db, request, "signup", user.id, "User created account")
        
        # Redirect to original page if specified, otherwise profile
        redirect_to = redirect or "/profile"
        return RedirectResponse(redirect_to, status_code=303)
    finally:
        db.close()

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, redirect: str = None):
    if request.session.get("user_id"):
        # If already logged in, redirect to the original page or home
        redirect_to = redirect or "/"
        return RedirectResponse(redirect_to, status_code=303)
    return templates.TemplateResponse("auth.html", {"request": request, "redirect": redirect})

@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), redirect: str = Form(None)):
    db = SessionLocal()
    try:
        email = email.strip().lower()
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            return templates.TemplateResponse("auth.html", {
                "request": request,
                "mode": "login",
                "error": "Invalid email or password",
                "redirect": redirect
            })
        request.session["user_id"] = user.id
        user.last_login_at = datetime.utcnow()
        db.commit()
        log_activity(db, request, "login", user.id, "User logged in")
        
        # Redirect to original page if specified, otherwise home
        redirect_to = redirect or "/"
        return RedirectResponse(redirect_to, status_code=303)
    finally:
        db.close()

@app.get("/logout")
def logout(request: Request):
    db = SessionLocal()
    try:
        user_id = request.session.get("user_id")
        if user_id:
            log_activity(db, request, "logout", user_id, "User logged out")
        request.session.pop("user_id", None)
        return RedirectResponse("/", status_code=303)
    finally:
        db.close()

# ============================================================
# PROFILE ROUTES
# ============================================================

@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    db = SessionLocal()
    try:
        user = get_current_user(request, db)
        if not user:
            return RedirectResponse("/login", status_code=303)
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        activities = (
            db.query(UserActivity)
            .filter(UserActivity.user_id == user.id)
            .order_by(UserActivity.created_at.desc())
            .limit(10)
            .all()
        )
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user,
            "profile": profile,
            "activities": activities
        })
    finally:
        db.close()

@app.post("/profile")
def update_profile(
    request: Request,
    name: str = Form(...),
    phone: str = Form(""),
    birth_date: str = Form(""),
    birth_time: str = Form(""),
    birth_city: str = Form(""),
    zodiac_sign: str = Form(""),
    notes: str = Form("")
):
    db = SessionLocal()
    try:
        user = get_current_user(request, db)
        if not user:
            return RedirectResponse("/login", status_code=303)
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        if not profile:
            profile = UserProfile(user_id=user.id)
            db.add(profile)
        user.name = name.strip()
        profile.phone = phone.strip()
        profile.birth_date = birth_date
        profile.birth_time = birth_time
        profile.birth_city = birth_city.strip()
        profile.zodiac_sign = zodiac_sign.strip()
        profile.notes = notes.strip()
        db.commit()
        log_activity(db, request, "profile_update", user.id, "User updated profile")
        return RedirectResponse("/", status_code=303)
    finally:
        db.close()


# ============================================================
# ADMIN ROUTES
# ============================================================

@app.get("/admin/blogs", response_class=HTMLResponse)
def admin_blog_page(request: Request):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)
    return templates.TemplateResponse("admin-blog.html", {"request": request})

@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin-login.html", {"request": request})

@app.post("/admin/login")
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["admin"] = "true"
        return RedirectResponse("/admin/blogs", status_code=303)
    return templates.TemplateResponse("admin-login.html", {
        "request": request,
        "error": "Invalid credentials"
    })

@app.get("/admin/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)

@app.get("/admin/activity", response_class=HTMLResponse)
def admin_activity_page(request: Request):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)
    db = SessionLocal()
    try:
        activities = (
            db.query(UserActivity)
            .options(joinedload(UserActivity.user))
            .order_by(UserActivity.created_at.desc())
            .limit(100)
            .all()
        )
        since = datetime.utcnow() - timedelta(days=7)
        return templates.TemplateResponse("admin-activity.html", {
            "request": request,
            "activities": activities,
            "total_users": db.query(User).count(),
            "total_activities": db.query(UserActivity).count(),
            "recent_signups": db.query(User).filter(User.created_at >= since).count()
        })
    finally:
        db.close()


# # ============================================================
# # RUN
# # ============================================================

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

# from datetime import datetime, timedelta
# import hashlib
# import hmac
# import os

# from fastapi import FastAPI, Request, Form
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from starlette.middleware.sessions import SessionMiddleware
# from sqlalchemy.orm import joinedload

from database import Base, SessionLocal, engine
from models.user_model import Feedback, User, UserProfile, UserActivity
from api.api import router
from api.blogs import router as admin_blog_router


# # ============================================================
# # APP SETUP
# # ============================================================

# app = FastAPI(title="AstroLogic Backend")

# # Middleware order matters: Session first, then CORS
# app.add_middleware(
#     SessionMiddleware,
#     secret_key="super-secret-key-change-this"
# )
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Base.metadata.create_all(bind=engine)

# app.include_router(router, prefix="/api")
# app.include_router(admin_blog_router)

# templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")

# ADMIN_USERNAME = "admin"
# ADMIN_PASSWORD = "astro123"


# # ============================================================
# # AUTH HELPERS
# # ============================================================

# def hash_password(password: str) -> str:
#     salt = os.urandom(16).hex()
#     digest = hashlib.pbkdf2_hmac(
#         "sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000
#     ).hex()
#     return f"{salt}${digest}"


# def verify_password(password: str, stored_hash: str) -> bool:
#     try:
#         salt, digest = stored_hash.split("$", 1)
#     except ValueError:
#         return False
#     check = hashlib.pbkdf2_hmac(
#         "sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000
#     ).hex()
#     return hmac.compare_digest(check, digest)


# def get_current_user(request: Request, db):
#     user_id = request.session.get("user_id")
#     if not user_id:
#         return None
#     return db.query(User).filter(User.id == user_id).first()


# def log_activity(db, request: Request, action: str, user_id=None, details: str = None):
#     activity = UserActivity(
#         user_id=user_id,
#         action=action,
#         details=details,
#         ip_address=request.client.host if request.client else None,
#         user_agent=request.headers.get("user-agent"),
#     )
#     db.add(activity)
#     db.commit()


# # ============================================================
# # MIDDLEWARE — redirect unauthenticated users to login
# # Public routes: login, signup, admin/*, api/*, static, docs
# # Homepage "/" is public but passes user=None if not logged in
# # Kundali & Prediction load but inject require_login flag
# # ============================================================

# ALWAYS_PUBLIC = (
#     "/login",
#     "/signup",
#     "/admin",
#     "/api",
#     "/static",
#     "/favicon.ico",
#     "/docs",
#     "/openapi.json",
#     "/about",
#     "/blogs",
#     "/horoscope",
#     "/panchang",
#     "/blog/",
# )

# # These pages LOAD for guests but show a login popup
# POPUP_PROTECTED = ("/kundali", "/prediction")


# @app.middleware("http")
# async def require_user_authentication(request: Request, call_next):
#     path = request.url.path

#     # Always let public routes through
#     if request.method != "GET":
#         return await call_next(request)
#     if path == "/" or path.startswith(ALWAYS_PUBLIC) or path.startswith(POPUP_PROTECTED):
#         return await call_next(request)

#     # Everything else requires login
#     if not request.session.get("user_id"):
#         return RedirectResponse("/login", status_code=303)

#     return await call_next(request)


# # ============================================================
# # PUBLIC PAGES
# # ============================================================

# @app.get("/", response_class=HTMLResponse)
# def home(request: Request):
#     db = SessionLocal()
#     try:
#         user = get_current_user(request, db)
#         return templates.TemplateResponse("index.html", {
#             "request": request,
#             "user": user,           # None if not logged in — template handles both states
#         })
#     finally:
#         db.close()


# @app.get("/about", response_class=HTMLResponse)
# def about_page(request: Request):
#     return templates.TemplateResponse("about.html", {"request": request})


# @app.get("/blogs", response_class=HTMLResponse)
# def blogs_page(request: Request):
#     return templates.TemplateResponse("blogs.html", {"request": request})


# @app.get("/blog/{blog_id}", response_class=HTMLResponse)
# def blog_detail(request: Request, blog_id: int):
#     return templates.TemplateResponse("blog-detail.html", {
#         "request": request,
#         "blog_id": blog_id
#     })


# @app.get("/horoscope", response_class=HTMLResponse)
# def horoscope_page(request: Request):
#     return templates.TemplateResponse("daily-horoscope.html", {"request": request})


# @app.get("/panchang.html", response_class=HTMLResponse)
# def panchang_page(request: Request):
#     return templates.TemplateResponse("panchang.html", {"request": request})


# # ============================================================
# # POPUP-PROTECTED PAGES
# # Page loads for everyone, but require_login=True triggers popup
# # ============================================================

# @app.get("/kundali", response_class=HTMLResponse)
# def kundali_page(request: Request):
#     db = SessionLocal()
#     try:
#         user = get_current_user(request, db)
#         return templates.TemplateResponse("kundali.html", {
#             "request": request,
#             "user": user,
#             "require_login": user is None,
#         })
#     finally:
#         db.close()


# @app.get("/prediction", response_class=HTMLResponse)
# def prediction_page(request: Request):
#     db = SessionLocal()
#     try:
#         user = get_current_user(request, db)
#         return templates.TemplateResponse("prediction.html", {
#             "request": request,
#             "user": user,
#             "require_login": user is None,
#         })
#     finally:
#         db.close()


# # ============================================================
# # AUTH-REQUIRED PAGES
# # ============================================================

# @app.get("/chat", response_class=HTMLResponse)
# def chat_page(request: Request):
#     db = SessionLocal()
#     try:
#         user = get_current_user(request, db)
#         return templates.TemplateResponse("chat.html", {"request": request, "user": user})
#     finally:
#         db.close()


# # ============================================================
# # AUTH ROUTES
# # ============================================================

# @app.get("/signup", response_class=HTMLResponse)
# def signup_page(request: Request):
#     if request.session.get("user_id"):
#         return RedirectResponse("/", status_code=303)
#     return templates.TemplateResponse("auth.html", {"request": request})


# @app.post("/signup")
# def signup(
#     request: Request,
#     name: str = Form(...),
#     email: str = Form(...),
#     phone: str = Form(...),
#     password: str = Form(...),
# ):
#     db = SessionLocal()
#     try:
#         email = email.strip().lower()
#         if db.query(User).filter(User.email == email).first():
#             return templates.TemplateResponse("auth.html", {
#                 "request": request,
#                 "mode": "signup",
#                 "error": "Email already registered"
#             })
#         user = User(
#             name=name.strip(),
#             email=email,
#             password_hash=hash_password(password)
#         )
#         db.add(user)
#         db.commit()
#         db.refresh(user)

#         db.add(UserProfile(user_id=user.id, phone=phone.strip()))
#         db.commit()

#         request.session["user_id"] = user.id
#         log_activity(db, request, "signup", user.id, "User created account")
#         return RedirectResponse("/profile", status_code=303)
#     finally:
#         db.close()


# @app.get("/login", response_class=HTMLResponse)
# def login_page(request: Request):
#     if request.session.get("user_id"):
#         return RedirectResponse("/", status_code=303)
#     return templates.TemplateResponse("auth.html", {"request": request})


# @app.post("/login")
# def login(request: Request, email: str = Form(...), password: str = Form(...)):
#     db = SessionLocal()
#     try:
#         email = email.strip().lower()
#         user = db.query(User).filter(User.email == email).first()
#         if not user or not verify_password(password, user.password_hash):
#             return templates.TemplateResponse("auth.html", {
#                 "request": request,
#                 "mode": "login",
#                 "error": "Invalid email or password"
#             })
#         request.session["user_id"] = user.id
#         user.last_login_at = datetime.utcnow()
#         db.commit()
#         log_activity(db, request, "login", user.id, "User logged in")
#         return RedirectResponse("/", status_code=303)
#     finally:
#         db.close()


# @app.get("/logout")
# def logout(request: Request):
#     db = SessionLocal()
#     try:
#         user_id = request.session.get("user_id")
#         if user_id:
#             log_activity(db, request, "logout", user_id, "User logged out")
#         request.session.pop("user_id", None)
#         return RedirectResponse("/", status_code=303)
#     finally:
#         db.close()


# # ============================================================
# # USER PROFILE
# # ============================================================

# @app.get("/profile", response_class=HTMLResponse)
# def profile_page(request: Request):
#     db = SessionLocal()
#     try:
#         user = get_current_user(request, db)
#         if not user:
#             return RedirectResponse("/login", status_code=303)
#         profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
#         activities = (
#             db.query(UserActivity)
#             .filter(UserActivity.user_id == user.id)
#             .order_by(UserActivity.created_at.desc())
#             .limit(10)
#             .all()
#         )
#         return templates.TemplateResponse("profile.html", {
#             "request": request,
#             "user": user,
#             "profile": profile,
#             "activities": activities,
#         })
#     finally:
#         db.close()


@app.post("/profile")
def update_profile(
    request: Request,
    name: str = Form(...),
    phone: str = Form(""),
    birth_date: str = Form(""),
    birth_time: str = Form(""),
    birth_city: str = Form(""),
    zodiac_sign: str = Form(""),
    notes: str = Form(""),
):
    db = SessionLocal()
    try:
        user = get_current_user(request, db)
        if not user:
            return RedirectResponse("/login", status_code=303)
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        if not profile:
            profile = UserProfile(user_id=user.id)
            db.add(profile)
        user.name = name.strip()
        profile.phone = phone.strip()
        profile.birth_date = birth_date
        profile.birth_time = birth_time
        profile.birth_city = birth_city.strip()
        profile.zodiac_sign = zodiac_sign.strip()
        profile.notes = notes.strip()
        db.commit()
        log_activity(db, request, "profile_update", user.id, "User updated profile")
        return RedirectResponse("/profile", status_code=303)
    finally:
        db.close()


# ============================================================
# API ENDPOINTS
# ============================================================

@app.post("/api/user-activity")
async def record_user_activity(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"ok": False, "error": "Authentication required"}, status_code=401)

    payload = await request.json()
    module      = str(payload.get("module", "activity"))[:40]
    action      = str(payload.get("action", "view"))[:40]
    person_name = str(payload.get("person_name", "") or "")
    birth_date  = str(payload.get("birth_date", "") or "")
    birth_time  = str(payload.get("birth_time", "") or "")
    birth_city  = str(payload.get("birth_city", "") or "")
    details = f"{module}: {person_name} | {birth_date} {birth_time} | {birth_city}"

    db = SessionLocal()
    try:
        log_activity(db, request, f"{module}_{action}", user_id, details)
        return JSONResponse({"ok": True})
    finally:
        db.close()


@app.post("/api/testing-feedback")
async def submit_testing_feedback(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"ok": False, "error": "Authentication required"}, status_code=401)

    payload = await request.json()
    db = SessionLocal()
    try:
        item = Feedback(
            user_id=user_id,
            module=str(payload.get("module", ""))[:40],
            person_name=str(payload.get("person_name", "") or "")[:120],
            birth_date=str(payload.get("birth_date", "") or "")[:20],
            birth_time=str(payload.get("birth_time", "") or "")[:20],
            birth_city=str(payload.get("birth_city", "") or "")[:120],
            accuracy=str(payload.get("accuracy", "") or "")[:40],
            experience=str(payload.get("experience", "") or "")[:40],
            usefulness=str(payload.get("usefulness", "") or "")[:40],
            comments=str(payload.get("comments", "") or ""),
        )
        db.add(item)
        db.commit()
        log_activity(
            db, request,
            f"{item.module}_feedback",
            user_id,
            f"Feedback submitted for {item.person_name or item.birth_city}"
        )
        return JSONResponse({"ok": True})
    finally:
        db.close()


# ============================================================
# ADMIN ROUTES
# ============================================================

@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)
    return RedirectResponse("/admin/blogs", status_code=303)


@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin-login.html", {"request": request})


@app.post("/admin/login")
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["admin"] = "true"
        return RedirectResponse("/admin/blogs", status_code=303)
    return templates.TemplateResponse("admin-login.html", {
        "request": request,
        "error": "Invalid credentials"
    })


@app.get("/admin/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@app.get("/admin/blogs", response_class=HTMLResponse)
def admin_blog_page(request: Request):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)
    return templates.TemplateResponse("admin-blog.html", {"request": request})


@app.get("/admin/users", response_class=HTMLResponse)
def admin_users_page(request: Request):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)
    db = SessionLocal()
    try:
        users = (
            db.query(User)
            .options(joinedload(User.profile))
            .order_by(User.created_at.desc())
            .all()
        )
        return templates.TemplateResponse("admin-users.html", {
            "request": request,
            "users": users,
            "total_users": db.query(User).count(),
            "total_profiles": db.query(UserProfile).count(),
            "total_activities": db.query(UserActivity).count(),
        })
    finally:
        db.close()


@app.get("/admin/activity", response_class=HTMLResponse)
def admin_activity_page(request: Request):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)
    db = SessionLocal()
    try:
        activities = (
            db.query(UserActivity)
            .options(joinedload(UserActivity.user))
            .order_by(UserActivity.created_at.desc())
            .limit(100)
            .all()
        )
        since = datetime.utcnow() - timedelta(days=7)
        return templates.TemplateResponse("admin-activity.html", {
            "request": request,
            "activities": activities,
            "total_users": db.query(User).count(),
            "total_activities": db.query(UserActivity).count(),
            "recent_signups": db.query(User).filter(User.created_at >= since).count(),
        })
    finally:
        db.close()


# @app.get("/admin/feedback", response_class=HTMLResponse)
# def admin_feedback_page(request: Request):
#     if request.session.get("admin") != "true":
#         return RedirectResponse("/admin/login", status_code=303)
#     db = SessionLocal()
#     try:
#         feedback_items = (
#             db.query(Feedback)
#             .options(joinedload(Feedback.user))
#             .order_by(Feedback.created_at.desc())
#             .limit(200)
#             .all()
#         )
#         return templates.TemplateResponse("admin-feedback.html", {
#             "request": request,
#             "feedback_items": feedback_items,
#             "total_feedback": db.query(Feedback).count(),
#             "kundali_feedback": db.query(Feedback).filter(Feedback.module == "kundali").count(),
#             "prediction_feedback": db.query(Feedback).filter(Feedback.module == "prediction").count(),
#         })
#     finally:
#         db.close()
@app.get("/admin/feedback", response_class=HTMLResponse)
def admin_feedback_page(request: Request):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)
    db = SessionLocal()
    try:
        # Now Feedback is defined
        feedback_items = (
            db.query(Feedback)
            .options(joinedload(Feedback.user))
            .order_by(Feedback.created_at.desc())
            .limit(200)
            .all()
        )
        return templates.TemplateResponse("admin-feedback.html", {
            "request": request,
            "feedback_items": feedback_items,
            "total_feedback": db.query(Feedback).count(),
            "kundali_feedback": db.query(Feedback).filter(Feedback.module == "kundali").count(),
            "prediction_feedback": db.query(Feedback).filter(Feedback.module == "prediction").count(),
        })
    finally:
        db.close()

# # ============================================================
# # RUN
# # ============================================================

# if __name__ == "__main__":
#     import uvicorn
#     print("\n" + "=" * 50)
#     print("🚀 AstroLogic Server Starting...")
#     print("=" * 50)
#     print("📍 Home:        http://localhost:8000")
#     print("🔮 Kundali:     http://localhost:8000/kundali")
#     print("🌟 Prediction:  http://localhost:8000/prediction")
#     print("⭐ Horoscope:   http://localhost:8000/horoscope")
#     print("🌙 Panchang:    http://localhost:8000/panchang")
#     print("📚 Blogs:       http://localhost:8000/blogs")
#     print("🛠  Admin:       http://localhost:8000/admin")
#     print("📊 API Docs:    http://localhost:8000/docs")
#     print("=" * 50 + "\n")
#     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)