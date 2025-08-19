from fastapi import APIRouter, Depends, HTTPException
from app.models import AccountLookupIn
from app.deps import require_api_key
import uuid, os, csv

router = APIRouter(prefix="/tools", tags=["tools"]) 
CSV_PATH = os.getenv("ACCOUNTS_CSV", "/srv/data/accounts_clean.csv")

def digits_only(s: str) -> str:
    return "".join(ch for ch in s if ch.isdigit())

def norm_phone(s: str | None):
    if not s:
        return None
    d = digits_only(str(s))
    if len(d) == 10:
        return "+1" + d
    if len(d) == 11 and d.startswith("1"):
        return "+" + d
    return "+" + d if d else None

@router.post("/Account_lookup")
async def account_lookup(payload: AccountLookupIn, _: bool = Depends(require_api_key)):
    req_id = str(uuid.uuid4())
    if payload.action != "get":
        raise HTTPException(status_code=405, detail={"ok": False, "error": {"code": "READ_ONLY", "message": "Read-only: updates disabled"}})
    if not payload.phone:
        raise HTTPException(status_code=422, detail={"ok": False, "error": {"code": "BAD_INPUT", "message": "phone is required"}})
    target = norm_phone(payload.phone)
    try:
        with open(CSV_PATH, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if norm_phone(row.get("phone")) == target:
                    data = {
                        "accountId": row.get("accountId"),
                        "name": row.get("name"),
                        "phones": [row.get("phone")],
                        "address": row.get("address"),
                        "plans": [p.strip() for p in (row.get("plans") or "").split(";") if p.strip()],
                    }
                    return {"ok": True, "data": data, "requestId": req_id}
        raise HTTPException(status_code=404, detail={"ok": False, "error": {"code": "NOT_FOUND", "message": "Account not found"}})
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail={"ok": False, "error": {"code": "DATA_MISSING", "message": "accounts CSV not found"}})
