import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from upstash_redis import Redis

app = FastAPI()

# Safe Environment Lookup
UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL", "https://YOUR-UPSTASH-REST-URL.upstash.io")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "YOUR-UPSTASH-REST-TOKEN")

@app.get("/")
def home():
    return {"status": "online", "message": "Romeo365 License Server is running!"}

class LicenseRequest(BaseModel):
    license_key: str
    hwid: str

@app.post("/verify")
@app.post("/verify/")
async def verify_license(req: LicenseRequest):
    key = req.license_key.strip()
    client_hwid = req.hwid.strip()

    if not key or not client_hwid:
        raise HTTPException(status_code=400, detail="Missing key or HWID")

    # Connect inside endpoint to catch invalid credentials gracefully
    try:
        redis = Redis(url=UPSTASH_URL, token=UPSTASH_TOKEN)
        stored_hwid = redis.get(key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis Connection Failed: Check your REST_URL & TOKEN.")

    if stored_hwid is None:
        raise HTTPException(status_code=401, detail="Invalid License Key")

    if isinstance(stored_hwid, bytes):
        stored_hwid = stored_hwid.decode("utf-8")

    stored_hwid = str(stored_hwid).strip()

    if stored_hwid == "UNBOUND" or stored_hwid == "":
        redis.set(key, client_hwid)
        return {"status": "success", "message": "Key successfully activated and bound to your device!"}

    elif stored_hwid == client_hwid:
        return {"status": "success", "message": "Access Granted! Welcome back."}

    else:
        raise HTTPException(
            status_code=403, 
            detail="Key already registered to another device. Contact support to reset HWID."
        )
