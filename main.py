from datetime import datetime, timedelta
import hashlib
import hmac
import os

from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import joinedload
import jwt
from fastapi.responses import JSONResponse

from database import Base, SessionLocal, engine
from models.user_model import Feedback, User, UserProfile, UserActivity
from api.api import router as api_router
from api.blogs import router as admin_blog_router


# ============================================================
# CONFIG
# ============================================================

JWT_SECRET      = os.environ.get("JWT_SECRET", "astro-jwt-secret-change-in-prod")
JWT_ALGORITHM   = "HS256"
JWT_EXPIRE_DAYS = 7

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "astro123"

security = HTTPBearer(auto_error=False)


# ============================================================
# APP SETUP
# ============================================================

app = FastAPI(title="AstroLogic Backend")

# Session middleware (admin panel only — user auth uses JWT)
app.add_middleware(SessionMiddleware, secret_key="astro-session-secret-change-in-prod")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://astrologic-vedic-1.onrender.com",
        "https://astro-logic-vedic.vercel.app",   # ← your Vercel frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix="/api")
app.include_router(admin_blog_router)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# ============================================================
# AUTH HELPERS
# ============================================================

def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000
    ).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, digest = stored_hash.split("$", 1)
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000
    ).hex()
    return hmac.compare_digest(check, digest)


def create_jwt(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt(token: str) -> dict | None:
    """Returns decoded payload or None if invalid/expired."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_request(request: Request) -> str | None:
    """
    Reads JWT from:
      1. Authorization: Bearer <token>  header
      2. astro_token cookie (set on login for page-based auth)
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return request.cookies.get("astro_token")


def get_current_user_jwt(request: Request, db) -> User | None:
    """Validate JWT and return User object, or None."""
    token = get_token_from_request(request)
    if not token:
        return None
    payload = decode_jwt(token)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    return db.query(User).filter(User.id == user_id).first()


def require_user(request: Request, db) -> User:
    """Use in API endpoints — raises 401 if not authenticated."""
    user = get_current_user_jwt(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


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
# JWT AUTH API  (/api/login  /api/signup  /api/logout)
# These are called by auth.html via fetch — return JSON + set cookie
# ============================================================

@app.post("/api/login")
async def api_login(request: Request):
    """
    Called by auth.html JS fetch.
    Returns { access_token, token_type } and sets httpOnly cookie.
    """
    data = await request.form()
    email    = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return JSONResponse({"error": "Email and password required"}, status_code=400)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            return JSONResponse({"error": "Invalid email or password"}, status_code=401)

        user.last_login_at = datetime.utcnow()
        db.commit()

        token = create_jwt(user.id, user.email)
        log_activity(db, request, "login", user.id, "JWT login")

        response = JSONResponse({
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": user.id, "name": user.name, "email": user.email},
        })
        # Also set a cookie so server-rendered pages can read the token
        response.set_cookie(
            key="astro_token",
            value=token,
            httponly=True,
            samesite="none", secure=True,
            max_age=60 * 60 * 24 * JWT_EXPIRE_DAYS,
        )
        return response
    finally:
        db.close()


@app.post("/api/signup")
async def api_signup(request: Request):
    """
    Called by auth.html JS fetch (signup mode).
    Returns { access_token } and sets cookie.
    """
    data = await request.form()
    name     = str(data.get("name", "")).strip()
    email    = str(data.get("email", "")).strip().lower()
    phone    = str(data.get("phone", "")).strip()
    password = str(data.get("password", ""))

    if not name or not email or not password:
        return JSONResponse({"error": "Name, email and password required"}, status_code=400)

    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            return JSONResponse({"error": "Email already registered"}, status_code=409)

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        db.add(UserProfile(user_id=user.id, phone=phone))
        db.commit()

        token = create_jwt(user.id, user.email)
        log_activity(db, request, "signup", user.id, "User created account")

        response = JSONResponse({
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": user.id, "name": user.name, "email": user.email},
        })
        response.set_cookie(
            key="astro_token",
            value=token,
            httponly=True,
            samesite="none", secure=True,
            max_age=60 * 60 * 24 * JWT_EXPIRE_DAYS,
        )
        return response
    finally:
        db.close()


@app.post("/api/logout")
async def api_logout(request: Request):
    db = SessionLocal()
    try:
        db_session = SessionLocal()
        token = get_token_from_request(request)
        if token:
            payload = decode_jwt(token)
            if payload:
                user_id = int(payload.get("sub", 0))
                log_activity(db, request, "logout", user_id, "JWT logout")
    finally:
        db.close()

    response = JSONResponse({"ok": True})
    response.delete_cookie("astro_token")
    return response


@app.get("/api/check-session")
def check_session(request: Request):
    """Used by kundali.html JS to verify login state."""
    db = SessionLocal()
    try:
        user = get_current_user_jwt(request, db)
        if user:
            return {"logged_in": True, "authenticated": True,
                    "user": {"id": user.id, "name": user.name, "email": user.email}}
        return {"logged_in": False, "authenticated": False}
    finally:
        db.close()


@app.get("/api/me")
def get_me(request: Request):
    """Returns current user info — used by frontend to personalise UI."""
    db = SessionLocal()
    try:
        user = get_current_user_jwt(request, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return {"id": user.id, "name": user.name, "email": user.email}
    finally:
        db.close()


# ============================================================
# PUBLIC PAGES
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    db = SessionLocal()
    try:
        user = get_current_user_jwt(request, db)
        return templates.TemplateResponse("index.html", context={"request": request, "user": user})
    finally:
        db.close()


@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse("about.html", context={"request": request})


@app.get("/blogs", response_class=HTMLResponse)
def blogs_page(request: Request):
    return templates.TemplateResponse("blogs.html", context={"request": request})


@app.get("/blog/{blog_id}", response_class=HTMLResponse)
def blog_detail(request: Request, blog_id: int):
    return templates.TemplateResponse("blog-detail.html", context={"request": request, "blog_id": blog_id})


@app.get("/horoscope", response_class=HTMLResponse)
def horoscope_page(request: Request):
    return templates.TemplateResponse("daily-horoscope.html", context={"request": request})


@app.get("/panchang.html", response_class=HTMLResponse)
def panchang_page(request: Request):
    return templates.TemplateResponse("panchang.html", context={"request": request})


# ============================================================
# POPUP-PROTECTED PAGES  (page loads, JS popup fires if not logged in)
# ============================================================

@app.get("/kundali", response_class=HTMLResponse)
def kundali_page(request: Request):
    db = SessionLocal()
    try:
        user = get_current_user_jwt(request, db)
        return templates.TemplateResponse("kundali.html", context={
            "request": request,
            "user": user,
            "require_login": user is None,
        })
    finally:
        db.close()


@app.get("/prediction", response_class=HTMLResponse)
def prediction_page(request: Request):
    db = SessionLocal()
    try:
        user = get_current_user_jwt(request, db)
        return templates.TemplateResponse("prediction.html", context={
            "request": request,
            "user": user,
            "require_login": user is None,
        })
    finally:
        db.close()


ALLOWED_REDIRECT_HOSTS = {
    "localhost", "127.0.0.1",
    "astrologic-vedic-1.onrender.com",
    "astro-logic-vedic.vercel.app",
}

def safe_redirect(url: str | None, fallback: str = "/") -> str:
    """Allow redirects to known hosts only — prevents open redirect attacks."""
    if not url:
        return fallback
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return url
        if parsed.hostname in ALLOWED_REDIRECT_HOSTS:
            return url
    except Exception:
        pass
    return fallback


# ============================================================
# AUTH PAGES  — served statically by Vercel, NOT by FastAPI
# These routes kept only as fallback for local development
# ============================================================

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, redirect: str = None, next: str = None):
    """In production, /login is served by Vercel. This is local dev fallback."""
    redirect_to = safe_redirect(redirect or next)
    db = SessionLocal()
    try:
        if get_current_user_jwt(request, db):
            return RedirectResponse(redirect_to, status_code=303)
    finally:
        db.close()
    return templates.TemplateResponse("auth.html", context={"request": request, "redirect": redirect_to})


@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request, redirect: str = None):
    """In production, /signup is served by Vercel. This is local dev fallback."""
    redirect_to = safe_redirect(redirect)
    db = SessionLocal()
    try:
        if get_current_user_jwt(request, db):
            return RedirectResponse(redirect_to, status_code=303)
    finally:
        db.close()
    return templates.TemplateResponse("auth.html", context={"request": request, "redirect": redirect_to})


@app.get("/logout")
def logout(request: Request):
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("astro_token")
    return response


# ============================================================
# CHAT PAGE
# ============================================================

@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    db = SessionLocal()
    try:
        user = get_current_user_jwt(request, db)
        return templates.TemplateResponse("chat.html", context={"request": request, "user": user})
    finally:
        db.close()


# ============================================================
# USER PROFILE
# ============================================================

@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    db = SessionLocal()
    try:
        user = get_current_user_jwt(request, db)
        if not user:
            return RedirectResponse(f"/login?redirect=/profile", status_code=303)
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        activities = (
            db.query(UserActivity)
            .filter(UserActivity.user_id == user.id)
            .order_by(UserActivity.created_at.desc())
            .limit(10)
            .all()
        )
        return templates.TemplateResponse("profile.html", context={
            "request": request,
            "user": user,
            "profile": profile,
            "activities": activities,
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
    notes: str = Form(""),
):
    db = SessionLocal()
    try:
        user = get_current_user_jwt(request, db)
        if not user:
            return RedirectResponse("/login?redirect=/profile", status_code=303)
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
# USER ACTIVITY & FEEDBACK API ENDPOINTS
# ============================================================

@app.post("/api/user-activity")
async def record_user_activity(request: Request):
    db = SessionLocal()
    try:
        user = require_user(request, db)
        payload = await request.json()
        module      = str(payload.get("module", "activity"))[:40]
        action      = str(payload.get("action", "view"))[:40]
        person_name = str(payload.get("person_name", "") or "")
        birth_date  = str(payload.get("birth_date", "") or "")
        birth_time  = str(payload.get("birth_time", "") or "")
        birth_city  = str(payload.get("birth_city", "") or "")
        details = f"{module}: {person_name} | {birth_date} {birth_time} | {birth_city}"
        log_activity(db, request, f"{module}_{action}", user.id, details)
        return JSONResponse({"ok": True})
    finally:
        db.close()


@app.post("/api/testing-feedback")
async def submit_testing_feedback(request: Request):
    db = SessionLocal()
    try:
        user = require_user(request, db)
        payload = await request.json()
        item = Feedback(
            user_id=user.id,
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
            user.id,
            f"Feedback: {item.person_name or item.birth_city}"
        )
        return JSONResponse({"ok": True})
    finally:
        db.close()


# ============================================================
# ADMIN ROUTES  (still session-based — admin is separate)
# ============================================================

@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)
    return RedirectResponse("/admin/blogs", status_code=303)


@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin-login.html", context={"request": request})


@app.post("/admin/login")
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["admin"] = "true"
        return RedirectResponse("/admin/blogs", status_code=303)
    return templates.TemplateResponse("admin-login.html", context={
        "request": request, "error": "Invalid credentials"
    })


@app.get("/admin/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@app.get("/admin/blogs", response_class=HTMLResponse)
def admin_blog_page(request: Request):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)
    return templates.TemplateResponse("admin-blog.html", context={"request": request})


# @app.get("/admin/users", response_class=HTMLResponse)
# def admin_users_page(request: Request):
#     if request.session.get("admin") != "true":
#         return RedirectResponse("/admin/login", status_code=303)
#     db = SessionLocal()
#     try:
#         users = (
#             db.query(User)
#             .options(joinedload(User.profile))
#             .order_by(User.created_at.desc())
#             .all()
#         )
#         return templates.TemplateResponse("admin-users.html", context={
#             "request": request,
#             "users": users,
#             "total_users": db.query(User).count(),
#             "total_profiles": db.query(UserProfile).count(),
#             "total_activities": db.query(UserActivity).count(),
#         })
#     finally:
#         db.close()
@app.get("/admin/users", response_class=HTMLResponse)
def admin_users_page(request: Request):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)
    
    db = SessionLocal()
    try:
        # Add debug print
        print("=" * 50)
        print("ADMIN USERS PAGE - Fetching data...")
        
        users = (
            db.query(User)
            .options(joinedload(User.profile))
            .order_by(User.created_at.desc())
            .all()
        )
        
        total_users = db.query(User).count()
        total_profiles = db.query(UserProfile).count()
        total_activities = db.query(UserActivity).count()
        
        # Debug prints
        print(f"Total users in DB: {total_users}")
        print(f"Total profiles in DB: {total_profiles}")
        print(f"First user: {users[0].name if users else 'No users found'}")
        print("=" * 50)
        
        return templates.TemplateResponse("admin-users.html", {
            "request": request,
            "users": users,
            "total_users": total_users,
            "total_profiles": total_profiles,
            "total_activities": total_activities,
        })
    except Exception as e:
        print(f"ERROR in admin/users: {e}")
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse("admin-users.html", {
            "request": request,
            "users": [],
            "total_users": 0,
            "total_profiles": 0,
            "total_activities": 0,
            "error": str(e)
        })
    finally:
        db.close()

# ============================================================
# TEST DATA ENDPOINT (Admin only - for testing)
# ============================================================

@app.post("/admin/debug/create-test-user")
def admin_create_test_user(request: Request):
    """Create a test user - ADMIN ONLY"""
    if request.session.get("admin") != "true":
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    db = SessionLocal()
    try:
        # Check if test user already exists
        existing = db.query(User).filter(User.email == "test@example.com").first()
        if existing:
            return {"message": "Test user already exists", "user": {"id": existing.id, "name": existing.name}}
        
        # Create test user
        test_user = User(
            name="Test User",
            email="test@example.com",
            password_hash=hash_password("test123")
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Create profile for test user
        profile = UserProfile(
            user_id=test_user.id,
            phone="+1234567890",
            birth_date="1990-01-15",
            birth_time="10:30",
            birth_city="Mumbai",
            zodiac_sign="Capricorn"
        )
        db.add(profile)
        db.commit()
        
        return {"success": True, "message": "Test user created", "user": {"id": test_user.id, "name": test_user.name, "email": test_user.email}}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()
# ============================================================
# DATABASE DEBUG ENDPOINT (Admin only)
# ============================================================

@app.get("/admin/debug/db")
def admin_debug_db(request: Request):
    """Debug endpoint to check database status - ADMIN ONLY"""
    if request.session.get("admin") != "true":
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        profile_count = db.query(UserProfile).count()
        activity_count = db.query(UserActivity).count()
        feedback_count = db.query(Feedback).count()
        
        # Get first few users
        users = db.query(User).limit(5).all()
        user_sample = [{"id": u.id, "name": u.name, "email": u.email} for u in users]
        
        return {
            "database_connected": True,
            "users_count": user_count,
            "profiles_count": profile_count,
            "activities_count": activity_count,
            "feedback_count": feedback_count,
            "sample_users": user_sample,
            "database_url": str(engine.url).split("@")[-1] if "@" in str(engine.url) else "sqlite_local"
        }
    except Exception as e:
        return {"database_connected": False, "error": str(e)}
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
        return templates.TemplateResponse("admin-activity.html", context={
            "request": request,
            "activities": activities,
            "total_users": db.query(User).count(),
            "total_activities": db.query(UserActivity).count(),
            "recent_signups": db.query(User).filter(User.created_at >= since).count(),
        })
    finally:
        db.close()


@app.get("/admin/feedback", response_class=HTMLResponse)
def admin_feedback_page(request: Request):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)
    db = SessionLocal()
    try:
        feedback_items = (
            db.query(Feedback)
            .options(joinedload(Feedback.user))
            .order_by(Feedback.created_at.desc())
            .limit(200)
            .all()
        )
        return templates.TemplateResponse("admin-feedback.html", context={
            "request": request,
            "feedback_items": feedback_items,
            "total_feedback": db.query(Feedback).count(),
            "kundali_feedback": db.query(Feedback).filter(Feedback.module == "kundali").count(),
            "prediction_feedback": db.query(Feedback).filter(Feedback.module == "prediction").count(),
        })
    finally:
        db.close()


# ============================================================
# PROFILE API ENDPOINTS (for AJAX calls from frontend)
# ============================================================

@app.get("/api/profile")
def api_get_profile(request: Request):
    """Get current user's profile data as JSON (for AJAX calls)"""
    db = SessionLocal()
    try:
        user = get_current_user_jwt(request, db)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        
        return JSONResponse({
            "success": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            },
            "profile": {
                "phone": profile.phone if profile else "",
                "birth_date": profile.birth_date if profile else "",
                "birth_time": profile.birth_time if profile else "",
                "birth_city": profile.birth_city if profile else "",
                "zodiac_sign": profile.zodiac_sign if profile else "",
                "timezone": profile.timezone if hasattr(profile, 'timezone') else "",
                "notes": profile.notes if profile else "",
            } if profile else {}
        })
    finally:
        db.close()


@app.post("/api/profile/update")
async def api_update_profile(request: Request):
    """Update user profile via JSON (for AJAX calls from frontend)"""
    db = SessionLocal()
    try:
        user = get_current_user_jwt(request, db)
        if not user:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)
        
        data = await request.json()
        
        # Update user name if provided
        if "name" in data and data["name"]:
            user.name = data["name"].strip()
        
        # Get or create profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        if not profile:
            profile = UserProfile(user_id=user.id)
            db.add(profile)
        
        # Update profile fields
        if "phone" in data:
            profile.phone = data["phone"].strip() if data["phone"] else ""
        if "birth_date" in data:
            profile.birth_date = data["birth_date"] if data["birth_date"] else None
        if "birth_time" in data:
            profile.birth_time = data["birth_time"] if data["birth_time"] else ""
        if "birth_city" in data:
            profile.birth_city = data["birth_city"].strip() if data["birth_city"] else ""
        if "zodiac_sign" in data:
            profile.zodiac_sign = data["zodiac_sign"].strip() if data["zodiac_sign"] else ""
        if "timezone" in data:
            profile.timezone = data["timezone"] if data["timezone"] else ""
        if "notes" in data:
            profile.notes = data["notes"].strip() if data["notes"] else ""
        
        db.commit()
        
        # Log activity
        log_activity(db, request, "profile_update", user.id, "User updated profile via API")
        
        return JSONResponse({"success": True, "message": "Profile updated successfully"})
        
    except Exception as e:
        db.rollback()
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        db.close()

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 50)
    print("🚀 AstroLogic Server Starting...")
    print("=" * 50)
    print("📍 Home:        http://localhost:8000")
    print("🔮 Kundali:     http://localhost:8000/kundali")
    print("🌟 Prediction:  http://localhost:8000/prediction")
    print("⭐ Horoscope:   http://localhost:8000/horoscope")
    print("🌙 Panchang:    http://localhost:8000/panchang")
    print("📚 Blogs:       http://localhost:8000/blogs")
    print("🛠  Admin:       http://localhost:8000/admin")
    print("📊 API Docs:    http://localhost:8000/docs")
    print("=" * 50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)