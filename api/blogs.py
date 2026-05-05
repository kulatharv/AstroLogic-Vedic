from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import SessionLocal
from models.blog_model import Blog

router = APIRouter(prefix="/api/admin", tags=["Admin Blogs"])


# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_admin(request: Request):
    if not request.session.get("admin"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    

# ---------------------------
# Get All Blogs (Admin View)
# ---------------------------
@router.get("/blogs")
def get_all_blogs(request: Request, db: Session = Depends(get_db)):
    require_admin(request)
    blogs = db.query(Blog).order_by(Blog.id.desc()).all()
    return blogs


# ---------------------------
# Create Blog
# ---------------------------
@router.post("/blogs")
@router.post("/blogs.html")
def create_blog(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    require_admin(request)
    blog = Blog(title=title, content=content)
    db.add(blog)
    db.commit()
    return RedirectResponse(url="/admin/blogs", status_code=303)


# ---------------------------
# Delete Blog
# ---------------------------
@router.post("/blogs/delete/{blog_id}")
def delete_blog(request: Request, blog_id: int, db: Session = Depends(get_db)):
    require_admin(request)
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    db.delete(blog)
    db.commit()

    return RedirectResponse(url="/admin/blogs", status_code=303)


# ---------------------------
# Update Blog
# ---------------------------
@router.post("/blogs/update/{blog_id}")
def update_blog(
    request: Request,
    blog_id: int,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    require_admin(request)
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    blog.title = title
    blog.content = content
    db.commit()

    return RedirectResponse(url="/admin/blogs", status_code=303)
