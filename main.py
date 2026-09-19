from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

def init_db():
    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            key TEXT PRIMARY KEY,
            hwid TEXT,
            is_active INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()

init_db()

class VerifyRequest(BaseModel):
    license_key: str
    hwid: str

@app.get("/")
def home():
    return {"status": "Server Running"}

@app.post("/verify")
def verify_license(data: VerifyRequest):
    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT hwid, is_active FROM licenses WHERE key = ?", (data.license_key,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid License Key")
        
    db_hwid, is_active = result
    
    if not is_active:
        conn.close()
        raise HTTPException(status_code=403, detail="License Expired or Disabled")
        
    if db_hwid is None:
        cursor.execute("UPDATE licenses SET hwid = ? WHERE key = ?", (data.hwid, data.license_key))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Device successfully bound"}
        
    if db_hwid == data.hwid:
        conn.close()
        return {"status": "success", "message": "Access Granted"}
    else:
        conn.close()
        raise HTTPException(status_code=401, detail="Key bound to another device")
