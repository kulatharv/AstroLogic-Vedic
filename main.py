
'''
from fastapi import FastAPI
from api.api import router

app = FastAPI(title="AstroLogic Backend")

app.include_router(router)


from astro_engine.chart_engine import generate_full_chart
from astro_engine.prediction_builder import build_prediction_prompt
from astro_engine.llm_engine import ask_llm
from astro_engine.chat_mode import chat_with_chart
import json

# -----------------------------
# INPUT
# -----------------------------

year = int(input("Enter year: "))
month = int(input("Enter month: "))
day = int(input("Enter day: "))
hour = float(input("Enter hour: "))

latitude = 18.5204
longitude = 73.8567

# -----------------------------
# GENERATE CHART
# -----------------------------

chart = generate_full_chart(year, month, day, hour, latitude, longitude)

# Optional: Print JSON (can remove later)
print("\n========= RAW CHART DATA =========\n")
print(json.dumps(chart, indent=4, default=str))

# -----------------------------
# TEST EVENT PREDICTION
# -----------------------------

marriage_prompt = build_prediction_prompt(chart, "marriage")
marriage_output = ask_llm(marriage_prompt)

print("\n========= AI Marriage Interpretation =========\n")
print(marriage_output)

# -----------------------------
# START CHAT MODE
# -----------------------------

chat_with_chart(chart)

'''

#26/04/2026

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from database import engine
from models.blog_model import Blog

from api.api import router

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for now (later restrict)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Blog.metadata.create_all(bind=engine)

# Include API routes
app.include_router(router)
app.include_router(router, prefix="/api")
#app.include_router(router, prefix="/api", tags=["API"])
# Setup templates
templates = Jinja2Templates(directory="templates")

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")


# ------------------ HTML Pages ------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


#@app.get("/prediction", response_class=HTMLResponse)
#def prediction_page(request: Request):
#    return templates.TemplateResponse("prediction.html", {"request": request})

@app.get("/prediction", response_class=HTMLResponse)
def prediction_page(request: Request):
    # If prediction.html is in templates folder
    return templates.TemplateResponse("prediction.html", {"request": request})
    # OR if it's in root directory:
    # from fastapi.responses import FileResponse
    # return FileResponse("prediction.html")

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


@app.get("/kundali", response_class=HTMLResponse)
def kundali_page(request: Request):
    return templates.TemplateResponse("kundali.html", {"request": request})

@app.get("/blog/{blog_id}", response_class=HTMLResponse)
def blog_detail(request: Request, blog_id: int):
    return templates.TemplateResponse("blog-detail.html", {
        "request": request,
        "blog_id": blog_id
    })
from starlette.middleware.sessions import SessionMiddleware
import secrets

app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key-change-this"
)
from fastapi import Form
from fastapi.responses import RedirectResponse
from fastapi import Request

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "astro123"

@app.get("/admin/blogs", response_class=HTMLResponse)
def admin_blog_page(request: Request):

    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)

    return templates.TemplateResponse("admin-blog.html", {"request": request})

# ------------------ LOGIN PAGE ------------------

@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin-login.html", {"request": request})


# ------------------ LOGIN PROCESS ------------------

@app.post("/admin/login")
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["admin"] = "true"   # store string
        return RedirectResponse("/admin/blogs", status_code=303)

    return templates.TemplateResponse("admin-login.html", {
        "request": request,
        "error": "Invalid credentials"
    })

# ------------------ LOGOUT ------------------

@app.get("/admin/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)



from api.blogs import router as admin_blog_router

app.include_router(admin_blog_router)





'''

import json
import sys
from astro_engine.chart_engine import generate_full_chart
from astro_engine.llm_engine import ask_llm
from astro_engine.prediction_builder import build_prediction_prompt
from astro_engine.chat_mode import chat_with_chart

def main():
    print("--- AstroLogic Backend Engine ---")
    
    try:
        # 1. Collect Birth Details
        # Using a try-except block to handle non-integer inputs
        year = int(input("Enter year (YYYY): "))
        month = int(input("Enter month (1-12): "))
        day = int(input("Enter day (1-31): "))
        hour = float(input("Enter hour (0-23.99): "))
        
        # Default coordinates (Pune, India) - Consider making these inputs too
        latitude = 18.5204
        longitude = 73.8567

        print(f"\n[1/3] Generating Chart for {year}-{month}-{day} at {hour}h...")
        
        # 2. Generate Astronomical Data
        chart = generate_full_chart(year, month, day, hour, latitude, longitude)
        
        # Optional: Save chart to a local file for debugging
        with open("last_chart.json", "w") as f:
            json.dump(chart, f, indent=4, default=str)

        # 3. Prediction Phase
        print("\n[2/3] Analyzing Marriage Prospects via AI...")
        marriage_prompt = build_prediction_prompt(chart, "marriage")
        marriage_output = ask_llm(marriage_prompt)

        print("\n" + "="*45)
        print("         AI MARRIAGE INTERPRETATION         ")
        print("="*45)
        print(marriage_output)
        print("="*45 + "\n")

        # 4. Interactive Mode
        print("[3/3] Entering Interactive Chat Mode (type 'exit' to stop)...")
        chat_with_chart(chart)

    except ValueError:
        print("\nError: Please enter valid numbers for date and time.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

    '''
'''
#update on 26/04/2026
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import secrets

from database import engine
from models.blog_model import Blog
from api.api import router
from api.blogs import router as admin_blog_router

# Create FastAPI app
app = FastAPI(title="AstroLogic Backend")

# Create database tables
Blog.metadata.create_all(bind=engine)

# Include API routes - ONLY ONCE with proper prefix
app.include_router(router, prefix="/api")  # All API routes are under /api

# Include admin blog routes
app.include_router(admin_blog_router)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Session middleware for admin
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key-change-this"
)

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "astro123"

# ============================================================
# HTML PAGE ROUTES
# ============================================================

@app.get("/", response_class=HTMLResponse)
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

@app.get("/kundali", response_class=HTMLResponse)
def kundali_page(request: Request):
    return templates.TemplateResponse("kundali.html", {"request": request})

@app.get("/blog/{blog_id}", response_class=HTMLResponse)
def blog_detail(request: Request, blog_id: int):
    return templates.TemplateResponse("blog-detail.html", {
        "request": request,
        "blog_id": blog_id
    })

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

# ============================================================
# RUN THE APP
# ============================================================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("🚀 AstroLogic Server Starting...")
    print("="*50)
    print(f"📍 Main Page: http://localhost:8000")
    print(f"📊 API Docs: http://localhost:8000/docs")
    print(f"⭐ Horoscope: http://localhost:8000/horoscope")
    print(f"🌙 Panchang: http://localhost:8000/panchang")
    print(f"🔮 Prediction: http://localhost:8000/prediction")
    print(f"📚 Blogs: http://localhost:8000/blogs")
    print("="*50 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    '''