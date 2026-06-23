from datetime import datetime, timedelta
import inspect
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import joinedload
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api.api import router as api_router

from app.database import SessionLocal


from app.api.blogs import router as admin_blog_router
from app.core.config import settings
from app.core.constants import PUBLIC_PATH_PREFIXES
from app.core.security import hash_password, verify_password
from app.database import SessionLocal
from app.models.user_model import Feedback, User, UserActivity, UserProfile
from app.services.translation_service import load_translations
from app.database import engine
from app.models.user_model import Base

#Base.metadata.create_all(bind=engine)
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title=settings.app_name)

@app.on_event("startup")
async def startup():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database connected successfully.")
    except Exception as e:
        print(f"Database connection failed: {e}")

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates"),
)
_template_response_params = tuple(inspect.signature(templates.TemplateResponse).parameters)
_template_response_expects_request_first = (
    len(_template_response_params) > 0 and _template_response_params[0] == "request"
)


# def render_template(
#     request: Request,
#     template_name: str,
#     context: dict | None = None,
#     status_code: int = 200,
# ):
#     template_context = {"request": request}
#     if context:
#         template_context.update(context)

#     if _template_response_expects_request_first:
#         return templates.TemplateResponse(
#             request,
#             template_name,
#             template_context,
#             status_code=status_code,
#         )

#     return templates.TemplateResponse(
#         template_name,
#         template_context,
#         status_code=status_code,
#     )
def render_template(
    request: Request,
    template_name: str,
    context: dict | None = None,
    status_code: int = 200,
):
    template_context = {"request": request}

    if context:
        template_context.update(context)

    lang = request.cookies.get("lang", "en")

    template_context["lang"] = lang
    template_context["t"] = load_translations(lang)

    if _template_response_expects_request_first:
        return templates.TemplateResponse(
            request,
            template_name,
            template_context,
            status_code=status_code,
        )

    return templates.TemplateResponse(
        template_name,
        template_context,
        status_code=status_code,
    )


app.include_router(api_router)
app.include_router(admin_blog_router)


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "astro123"


def get_current_user(request: Request, db):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()

@app.get("/change-language/{lang}")
def change_language(lang: str):

    response = RedirectResponse(
        "/",
        status_code=303
    )

    response.set_cookie(
        key="lang",
        value=lang,
        max_age=31536000
    )

    return response
# def log_activity(db, request: Request, action: str, user_id=None, details: str | None = None):
#     activity = UserActivity(
#         user_id=user_id,
#         action=action,
#         details=details,
#         ip_address=request.client.host if request.client else None,
#         user_agent=request.headers.get("user-agent"),
#     )
#     db.add(activity)
#     db.commit()
def log_activity(
    db,
    request,
    action,
    user_id,
    details
):

    if not user_id:
        return

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        return

    activity = UserActivity(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=request.client.host,
        user_agent=request.headers.get(
            "user-agent"
        )
    )

    db.add(activity)
    db.commit() 

async def require_user_authentication(request: Request, call_next):
    # TODO: Replace this temporary session guard with API-first JWT auth,
    # refresh tokens, and route-level permission dependencies.
    path = request.url.path
    if (
        request.method == "GET"
        and not path.startswith(PUBLIC_PATH_PREFIXES)
        and not request.session.get("user_id")
    ):
        return RedirectResponse("/login", status_code=303)
    return await call_next(request)


app.add_middleware(BaseHTTPMiddleware, dispatch=require_user_authentication)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keep session auth during the template migration. This middleware must wrap
# session-dependent auth/admin handlers so request.session is available.
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    same_site="lax",
    https_only=settings.is_production,
)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return render_template(request, "index.html")


@app.get("/prediction", response_class=HTMLResponse)
def prediction_page(request: Request):
    return render_template(request, "prediction.html")


@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    return render_template(request, "chat.html")


@app.get("/panchang.html", response_class=HTMLResponse)
def panchang_page(request: Request):
    return render_template(request, "panchang.html")


@app.get("/blogs", response_class=HTMLResponse)
def blogs_page(request: Request):
    return render_template(request, "blogs.html")


@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    return render_template(request, "about.html")


@app.get("/horoscope", response_class=HTMLResponse)
def horoscope_page(request: Request):
    return render_template(request, "daily-horoscope.html")


@app.get("/kundali", response_class=HTMLResponse)
def kundali_page(request: Request):
    return render_template(request, "kundali.html")


@app.get("/blog/{blog_id}", response_class=HTMLResponse)
def blog_detail(request: Request, blog_id: int):
    return render_template(request, "blog-detail.html", {"blog_id": blog_id})


@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return render_template(request, "auth.html")


@app.post("/signup")
def signup(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
):
    db = SessionLocal()
    try:
        email = email.strip().lower()

        if db.query(User).filter(User.email == email).first():
            return render_template(
                request,
                "auth.html",
                {
                    "mode": "signup",
                    "title": "Create Account",
                    "button": "Create Account",
                    "error": "Email already registered",
                },
            )

        user = User(
            name=name.strip(),
            email=email,
            password_hash=hash_password(password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        profile = UserProfile(user_id=user.id, phone=phone.strip())
        db.add(profile)
        db.commit()

        request.session["user_id"] = user.id
        log_activity(db, request, "signup", user.id, "User created account")

        return RedirectResponse("/profile", status_code=303)
    finally:
        db.close()


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return render_template(request, "auth.html")


@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    try:
        email = email.strip().lower()
        user = db.query(User).filter(User.email == email).first()

        if not user or not verify_password(password, user.password_hash):
            return render_template(
                request,
                "auth.html",
                {
                    "mode": "login",
                    "title": "User Login",
                    "button": "Login",
                    "error": "Invalid email or password",
                },
            )

        request.session["user_id"] = user.id
        user.last_login_at = datetime.utcnow()
        db.commit()

        log_activity(db, request, "login", user.id, "User logged in")

        return RedirectResponse("/", status_code=303)
    finally:
        db.close()


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
@app.get("/logout")
def logout(request: Request):
    print("Logout function called")

    db = SessionLocal()
    print("DB session created")

    try:
        user_id = request.session.get("user_id")
        print("User ID:", user_id)

        request.session.clear()

        return RedirectResponse("/", status_code=303)

    finally:
        db.close()

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

        return render_template(
            request,
            "profile.html",
            {
                "user": user,
                "profile": profile,
                "activities": activities,
            },
        )
    finally:
        db.close()


@app.middleware("http")
async def language_middleware(
    request,
    call_next
):

    lang = request.cookies.get(
        "lang",
        "en"
    )

    request.state.lang = lang

    response = await call_next(
        request
    )

    return response

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

        return RedirectResponse("/", status_code=303)
    finally:
        db.close()


@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)
    return RedirectResponse("/admin/blogs", status_code=303)


@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return render_template(request, "admin-login.html")


@app.post("/admin/login")
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["admin"] = "true"
        return RedirectResponse("/admin/blogs", status_code=303)

    return render_template(request, "admin-login.html", {"error": "Invalid credentials"})


@app.get("/admin/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@app.get("/admin/blogs", response_class=HTMLResponse)
def admin_blog_page(request: Request):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)
    return render_template(request, "admin-blog.html")


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

        return render_template(
            request,
            "admin-activity.html",
            {
                "activities": activities,
                "total_users": db.query(User).count(),
                "total_activities": db.query(UserActivity).count(),
                "recent_signups": db.query(User).filter(User.created_at >= since).count(),
            },
        )
    finally:
        db.close()


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

        return render_template(
            request,
            "admin-users.html",
            {
                "users": users,
                "total_users": db.query(User).count(),
                "total_profiles": db.query(UserProfile).count(),
                "total_activities": db.query(UserActivity).count(),
            },
        )
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
        return render_template(
            request,
            "admin-feedback.html",
            {
                "feedback_items": feedback_items,
                "total_feedback": db.query(Feedback).count(),
                "kundali_feedback": db.query(Feedback).filter(Feedback.module == "kundali").count(),
                "prediction_feedback": db.query(Feedback).filter(Feedback.module == "prediction").count(),
            },
        )
    finally:
        db.close()


@app.post("/api/user-activity")
async def record_user_activity(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return {"ok": False, "error": "Authentication required"}

    payload = await request.json()
    module = str(payload.get("module", "activity"))[:40]
    action = str(payload.get("action", "view"))[:40]
    person_name = str(payload.get("person_name", "") or "")
    birth_date = str(payload.get("birth_date", "") or "")
    birth_time = str(payload.get("birth_time", "") or "")
    birth_city = str(payload.get("birth_city", "") or "")
    details = f"{module}: {person_name} | {birth_date} {birth_time} | {birth_city}"

    db = SessionLocal()
    try:
        log_activity(db, request, f"{module}_{action}", user_id, details)
        return {"ok": True}
    finally:
        db.close()


@app.post("/api/testing-feedback")
async def submit_testing_feedback(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return {"ok": False, "error": "Authentication required"}

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
            db,
            request,
            f"{item.module}_feedback",
            user_id,
            f"Feedback submitted for {item.person_name or item.birth_city}",
        )
        return {"ok": True}
    finally:
        db.close()
