from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import SessionLocal
from models.blog_model import Blog
from typing import List
from fastapi import Request

router = APIRouter(prefix="/api/admin", tags=["Admin Blogs"])


# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/blogs")
def get_all_blogs(request: Request, db: Session = Depends(get_db)):

    if not request.session.get("admin"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db.query(Blog).all()
# ---------------------------
# Get All Blogs (Admin View)
# ---------------------------
@router.get("/blogs")
def get_all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(Blog).order_by(Blog.id.desc()).all()
    return blogs


# ---------------------------
# Create Blog
# ---------------------------
@router.post("/blogs")
def create_blog(
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    blog = Blog(title=title, content=content)
    db.add(blog)
    db.commit()
    return RedirectResponse(url="/admin/blogs", status_code=303)


# ---------------------------
# Delete Blog
# ---------------------------
@router.post("/blogs/delete/{blog_id}")
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
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
    blog_id: int,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    blog.title = title
    blog.content = content
    db.commit()

    return RedirectResponse(url="/admin/blogs", status_code=303)