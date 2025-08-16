from fastapi import Request, HTTPException

def require_login(req: Request):
    if not req.session.get("auth"):
        raise HTTPException(status_code=401, detail="Login requerido")
