from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime


class ScanRequest(BaseModel):
    """Request model for scan endpoint"""
    domain: str = Field(..., description="Target domain (e.g., example.com)")
    
    @validator('domain')
    def validate_domain(cls, v):
        """Validate domain format"""
        v = v.strip().lower()
        # Remove protocol if present
        v = v.replace('http://', '').replace('https://', '')
        # Remove trailing slash
        v = v.rstrip('/')
        # Remove www prefix for consistency
        v = v.replace('www.', '')
        
        if not v or ' ' in v:
            raise ValueError('Invalid domain format')
        
        return v


class ReconResults(BaseModel):
    """Reconnaissance results model"""
    domain: str
    timestamp: datetime = Field(default_factory=datetime.now)
    subdomains: List[str] = []
    live_hosts: List[str] = []
    open_ports: Dict[str, List[int]] = {}
    technologies: Dict[str, List[str]] = {}
    endpoints: List[str] = []
    directories: List[str] = []
    scan_duration: float = 0.0
    errors: List[str] = []


class AIAnalysis(BaseModel):
    """AI analysis results model"""
    attack_surface_summary: str
    possible_vulnerabilities: List[str]
    interesting_endpoints: List[str]
    security_recommendations: List[str]
    risk_level: str = Field(..., description="LOW, MEDIUM, HIGH, or CRITICAL")
    detailed_analysis: str


class ReportData(BaseModel):
    """Complete report data for PDF generation"""
    recon_results: ReconResults
    ai_analysis: AIAnalysis


class ScanResponse(BaseModel):
    """Response model for scan endpoint"""
    success: bool
    message: str
    data: Optional[ReconResults] = None
    scan_id: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model for analysis endpoint"""
    success: bool
    message: str
    data: Optional[AIAnalysis] = None
