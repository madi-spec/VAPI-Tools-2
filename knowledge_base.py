from fastapi import APIRouter, Depends, HTTPException
from app.models import KnowledgeBaseIn
from app.deps import require_api_key
import os, uuid
import httpx

router = APIRouter(prefix="/tools", tags=["tools"]) 
QUERY_BASE = os.getenv("QUERY_BASE")
QUERY_KEY = os.getenv("QUERY_KEY")
COLL = os.getenv("QUERY_COLLECTION_KB", "goforth-kb")

@router.post("/Knowledge_Base")
async def knowledge_base(payload: KnowledgeBaseIn, _: bool = Depends(require_api_key)):
    req_id = str(uuid.uuid4())
    if not payload.question:
        raise HTTPException(status_code=422, detail={"ok": False, "error": {"code": "BAD_INPUT", "message": "question is required"}})
    if not QUERY_BASE or not QUERY_KEY:
        return {"ok": True, "data": {"answer": "(dev stub) configure QUERY_BASE and QUERY_KEY", "covered": None}, "requestId": req_id}
    body = {
        "collection": COLL,
        "question": payload.question,
        "metadata": {"plan": payload.plan, "pest": payload.pest}
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(QUERY_BASE + "/ask", json=body, headers={"Authorization": "Bearer " + QUERY_KEY})
        r.raise_for_status()
        ans = r.json().get("answer")
    covered = None
    return {"ok": True, "data": {"answer": ans, "covered": covered}, "requestId": req_id}
