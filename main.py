from fastapi import FastAPI
from app.routers import account_lookup, knowledge_base, schedule_check

app = FastAPI(title="Vapi Tools", version="1.0.0")
app.include_router(account_lookup.router)
app.include_router(knowledge_base.router)
app.include_router(schedule_check.router)

@app.get("/health")
async def health():
    return {"ok": True}
