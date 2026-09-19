import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from upstash_redis import Redis

app = FastAPI()

# Upstash Redis Connection Setup
# Ensure UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN are set in Vercel Environment Variables
redis = Redis.from_env()

class LicenseRequest(BaseModel):
    license_key: str
    hwid: str

@app.get("/")
def home():
    return {"status": "online", "message": "Romeo365 License Server is running!"}

# Both routes defined to handle both /verify and /verify/ without 405 error
@app.post("/verify")
@app.post("/verify/")
async def verify_license(req: LicenseRequest):
    key = req.license_key.strip()
    client_hwid = req.hwid.strip()

    if not key or not client_hwid:
        raise HTTPException(status_code=400, detail="Missing key or HWID")

    # Upstash Redis lookup
    stored_hwid = redis.get(key)

    if stored_hwid is None:
        raise HTTPException(status_code=401, detail="Invalid License Key")

    # Decoded string handling if byte response returned
    if isinstance(stored_hwid, bytes):
        stored_hwid = stored_hwid.decode("utf-8")

    stored_hwid = str(stored_hwid).strip()

    # Case 1: Unbound key (first time activation)
    if stored_hwid == "UNBOUND" or stored_hwid == "":
        redis.set(key, client_hwid)
        return {"status": "success", "message": "Key successfully activated and bound to your device!"}

    # Case 2: Key matches this device's HWID
    elif stored_hwid == client_hwid:
        return {"status": "success", "message": "Access Granted! Welcome back."}

    # Case 3: HWID mismatch
    else:
        raise HTTPException(
            status_code=403, 
            detail="Key already registered to another device. Contact support to reset HWID."
        )
