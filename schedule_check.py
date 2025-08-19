from fastapi import APIRouter, Depends, HTTPException
from app.models import ScheduleCheckIn
from app.deps import require_api_key
import uuid, os
import httpx
import datetime as dt

router = APIRouter(prefix="/tools", tags=["tools"]) 
ICS = os.getenv("CALENDAR_ICS_URL")

async def busy_blocks_ics():
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(ICS)
        resp.raise_for_status()
        text = resp.text
    events = []
    chunks = text.split("BEGIN:VEVENT")
    for raw in chunks[1:]:
        lines = raw.splitlines()
        def get(field):
            for line in lines:
                if line.startswith(field + ":") or line.startswith(field + ";"):
                    return line.split(":", 1)[1].strip()
            return None
        s = get("DTSTART"); e = get("DTEND")
        if not s or not e:
            continue
        try:
            ss = dt.datetime.strptime(s[:15], "%Y%m%dT%H%M%S")
            ee = dt.datetime.strptime(e[:15], "%Y%m%dT%H%M%S")
        except Exception:
            continue
        events.append((ss, ee))
    return events

@router.post("/Schedule_Check")
async def schedule_check(payload: ScheduleCheckIn, _: bool = Depends(require_api_key)):
    req_id = str(uuid.uuid4())
    if payload.action == "check":
        now = dt.datetime.utcnow()
        busy = await busy_blocks_ics()
        slots = []
        for i in range(1, 6):
            day = now.date() + dt.timedelta(days=i)
            morning = dt.datetime.combine(day, dt.time(9, 0))
            afternoon = dt.datetime.combine(day, dt.time(13, 0))
            def overlaps(beg, fin):
                for s, e in busy:
                    if s.date() == day and not (e <= beg or s >= fin):
                        return True
                return False
            if not overlaps(morning, morning + dt.timedelta(hours=3)):
                slots.append({"start": morning.isoformat(), "end": (morning + dt.timedelta(hours=3)).isoformat(), "label": "morning"})
            if not overlaps(afternoon, afternoon + dt.timedelta(hours=3)):
                slots.append({"start": afternoon.isoformat(), "end": (afternoon + dt.timedelta(hours=3)).isoformat(), "label": "afternoon"})
        return {"ok": True, "data": {"slots": slots}, "requestId": req_id}
    if payload.action == "book":
        raise HTTPException(status_code=501, detail={"ok": False, "error": {"code": "BOOKING_UNAVAILABLE", "message": "Provide Google Calendar API credentials to enable booking."}})
    raise HTTPException(status_code=422, detail={"ok": False, "error": {"code": "BAD_INPUT", "message": "unknown action"}})
