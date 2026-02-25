from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Dict, List, Optional
import uuid
import asyncio
from datetime import datetime

from scanner.engine import ScanEngine

app = FastAPI(title="CrimsonEye Scanner API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
scan_results: Dict[str, dict] = {}
scan_status: Dict[str, dict] = {}

class ScanRequest(BaseModel):
    target_url: HttpUrl
    scan_mode: str  # 'passive' or 'active'
    permission_confirmed: bool

class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str

@app.get("/")
async def root():
    return {
        "service": "CrimsonEye Scanner API",
        "version": "1.0.0",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/scan", response_model=ScanResponse)
async def initiate_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks
):
    """Initiate a new vulnerability scan"""
    
    if not request.permission_confirmed:
        raise HTTPException(
            status_code=400,
            detail="Permission confirmation required"
        )
    
    if request.scan_mode not in ['passive', 'active']:
        raise HTTPException(
            status_code=400,
            detail="Invalid scan mode. Use 'passive' or 'active'"
        )
    
    # Generate unique scan ID
    scan_id = str(uuid.uuid4())
    
    # Initialize scan status
    scan_status[scan_id] = {
        "status": "queued",
        "progress": 0,
        "current_step": "Initializing",
        "started_at": datetime.utcnow().isoformat()
    }
    
    # Start scan in background
    background_tasks.add_task(
        run_scan,
        scan_id,
        str(request.target_url),
        request.scan_mode
    )
    
    return ScanResponse(
        scan_id=scan_id,
        status="queued",
        message=f"Scan initiated for {request.target_url}"
    )

@app.get("/scan/status/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get current status of a scan"""
    
    if scan_id not in scan_status:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return scan_status[scan_id]

@app.get("/scan/results/{scan_id}")
async def get_scan_results(scan_id: str):
    """Get scan results"""
    
    if scan_id not in scan_results:
        # Check if scan is still in progress
        if scan_id in scan_status:
            status = scan_status[scan_id]["status"]
            if status in ["queued", "running"]:
                return {"status": status, "message": "Scan in progress"}
        raise HTTPException(status_code=404, detail="Results not found")
    
    return scan_results[scan_id]

async def run_scan(scan_id: str, target_url: str, scan_mode: str):
    """Execute the vulnerability scan"""
    
    try:
        # Update status to running
        scan_status[scan_id].update({
            "status": "running",
            "progress": 10,
            "current_step": "Initializing scanner modules"
        })
        
        # Initialize scan engine
        engine = ScanEngine(target_url, scan_mode)
        
        # Execute scan with progress updates
        async for progress in engine.scan():
            scan_status[scan_id].update(progress)
        
        # Get final results
        results = engine.get_results()
        
        # Store results
        scan_results[scan_id] = results
        
        # Update final status
        scan_status[scan_id].update({
            "status": "completed",
            "progress": 100,
            "current_step": "Scan completed",
            "completed_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        scan_status[scan_id].update({
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
