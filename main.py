from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mangum import Mangum
import os
import redis

app = FastAPI()

# Vercel KV Database connection
KV_URL = os.environ.get("KV_URL") or os.environ.get("REDIS_URL")

def get_redis():
    if not KV_URL:
        raise HTTPException(status_code=500, detail="Database disconnect hai")
    return redis.Redis.from_url(KV_URL, decode_responses=True)

class VerifyRequest(BaseModel):
    license_key: str
    hwid: str

@app.get("/")
def home():
    return {"status": "Server Active!"}

@app.post("/verify")
def verify_license(data: VerifyRequest):
    r = get_redis()
    redis_key = f"license:{data.license_key}"
    
    # Key exist nahi karti
    if not r.exists(redis_key):
        raise HTTPException(status_code=400, detail="Invalid License Key")
        
    db_hwid = r.get(redis_key)
    
    # Key bilkul new hai (unbound)
    if db_hwid == "UNBOUND":
        r.set(redis_key, data.hwid)
        return {"status": "success", "message": "Device successfully bound"}
        
    # Validation Match
    if db_hwid == data.hwid:
        return {"status": "success", "message": "Access Granted"}
    else:
        raise HTTPException(status_code=401, detail="Key bound to another device")

handler = Mangum(app)
