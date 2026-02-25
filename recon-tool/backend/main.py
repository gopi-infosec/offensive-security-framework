from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import uuid
from typing import Dict

from backend.models import (
    ScanRequest, ScanResponse, AnalysisResponse,
    ReconResults, AIAnalysis, ReportData
)
from backend.services.recon_service import ReconService
from backend.services.ai_service import AIService
from backend.services.pdf_service import PDFService
from backend.config import get_settings

settings = get_settings()

# In-memory storage for scan results
scan_storage: Dict[str, ReconResults] = {}
analysis_storage: Dict[str, AIAnalysis] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    print("[*] Starting AI-Powered Recon Tool...")
    print(f"[*] Server: http://{settings.host}:{settings.port}")
    print("[*] Perplexity API configured")
    yield
    # Shutdown
    print("[*] Shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Recon Tool",
    description="Web and API reconnaissance tool with AI-powered security analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
recon_service = ReconService()
ai_service = AIService()
pdf_service = PDFService()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI-Powered Recon Tool API",
        "version": "1.0.0",
        "endpoints": {
            "scan": "/scan",
            "analyze": "/analyze/{scan_id}",
            "report": "/report/{scan_id}"
        }
    }


@app.post("/scan", response_model=ScanResponse)
async def scan_domain(request: ScanRequest):
    """
    Perform reconnaissance scan on target domain
    
    Args:
        request: ScanRequest with target domain
        
    Returns:
        ScanResponse with scan results and scan_id
    """
    try:
        print(f"\n[*] New scan request for domain: {request.domain}")
        
        # Perform reconnaissance
        results = await recon_service.perform_full_scan(request.domain)
        
        # Generate unique scan ID
        scan_id = str(uuid.uuid4())
        
        # Store results
        scan_storage[scan_id] = results
        
        return ScanResponse(
            success=True,
            message="Scan completed successfully",
            data=results,
            scan_id=scan_id
        )
        
    except Exception as e:
        print(f"[!] Scan error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Scan failed: {str(e)}"
        )


@app.post("/analyze/{scan_id}", response_model=AnalysisResponse)
async def analyze_results(scan_id: str):
    """
    Analyze reconnaissance results using AI
    
    Args:
        scan_id: Scan identifier
        
    Returns:
        AnalysisResponse with AI analysis
    """
    try:
        # Retrieve scan results
        if scan_id not in scan_storage:
            raise HTTPException(
                status_code=404,
                detail="Scan ID not found"
            )
        
        recon_results = scan_storage[scan_id]
        
        print(f"\n[*] Analyzing results for scan: {scan_id}")
        
        # Perform AI analysis
        analysis = await ai_service.analyze_recon_results(recon_results)
        
        # Store analysis
        analysis_storage[scan_id] = analysis
        
        return AnalysisResponse(
            success=True,
            message="Analysis completed successfully",
            data=analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[!] Analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/report/{scan_id}")
async def generate_report(scan_id: str):
    """
    Generate and download PDF report
    
    Args:
        scan_id: Scan identifier
        
    Returns:
        StreamingResponse with PDF file
    """
    try:
        # Retrieve scan results and analysis
        if scan_id not in scan_storage:
            raise HTTPException(
                status_code=404,
                detail="Scan ID not found"
            )
        
        if scan_id not in analysis_storage:
            raise HTTPException(
                status_code=400,
                detail="Analysis not performed yet. Call /analyze first."
            )
        
        recon_results = scan_storage[scan_id]
        analysis = analysis_storage[scan_id]
        
        print(f"\n[*] Generating PDF report for scan: {scan_id}")
        
        # Create report data
        report_data = ReportData(
            recon_results=recon_results,
            ai_analysis=analysis
        )
        
        # Generate PDF
        pdf_buffer = pdf_service.generate_report(report_data)
        
        # Create filename
        filename = f"recon_report_{recon_results.domain}_{recon_results.timestamp.strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[!] Report generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "scans_in_memory": len(scan_storage),
        "analyses_in_memory": len(analysis_storage)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
