from fastapi import Request

@app.get("/api/check-session")
def check_session(request: Request):
    user = request.session.get("user")
    return {
        "logged_in": bool(user),
        "user": user if user else None
    }