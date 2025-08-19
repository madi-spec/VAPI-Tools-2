from fastapi import Header, HTTPException
import os

API_KEY = os.getenv("SERVICE_API_KEY", "")

async def require_api_key(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"ok": False, "error": {"code": "NO_AUTH", "message": "Missing bearer"}})
    token = authorization.split(" ", 1)[1]
    if token != API_KEY:
        raise HTTPException(status_code=403, detail={"ok": False, "error": {"code": "BAD_AUTH", "message": "Invalid key"}})
    return True
