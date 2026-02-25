import asyncio
from typing import AsyncGenerator, Dict, List
from datetime import datetime

from .header_checker import HeaderChecker
from .tls_checker import TLSChecker
from .cookie_checker import CookieChecker
from .cors_checker import CORSChecker
from .tech_fingerprint import TechFingerprint
from .sqli_scanner import SQLiScanner
from .xss_scanner import XSSScanner
from .redirect_checker import RedirectChecker
from .traversal_scanner import TraversalScanner
from .api_scanner import APIScanner
from .risk_scoring import RiskScorer

class ScanEngine:
    """Main scanning orchestrator"""
    
    def __init__(self, target_url: str, scan_mode: str):
        self.target_url = target_url
        self.scan_mode = scan_mode
        self.vulnerabilities = []
        self.logs = []
        
    async def scan(self) -> AsyncGenerator[Dict, None]:
        """Execute scan and yield progress updates"""
        
        # Passive scan modules (always executed)
        passive_modules = [
            (HeaderChecker, "Analyzing HTTP headers", 20),
            (TLSChecker, "Testing TLS/SSL configuration", 30),
            (CookieChecker, "Checking cookie security", 40),
            (CORSChecker, "Testing CORS configuration", 50),
            (TechFingerprint, "Fingerprinting technologies", 60),
            (APIScanner, "Scanning for exposed endpoints", 70),
        ]
        
        # Active scan modules (only if active mode)
        active_modules = [
            (SQLiScanner, "Testing SQL injection points", 75),
            (XSSScanner, "Checking XSS vulnerabilities", 80),
            (RedirectChecker, "Testing for open redirects", 85),
            (TraversalScanner, "Testing path traversal", 90),
        ]
        
        # Execute passive scans
        for module_class, description, progress in passive_modules:
            yield {
                "progress": progress,
                "current_step": description
            }
            
            module = module_class(self.target_url)
            results = await module.check()
            self.vulnerabilities.extend(results)
            await asyncio.sleep(0.5)  # Simulate processing time
        
        # Execute active scans if enabled
        if self.scan_mode == 'active':
            for module_class, description, progress in active_modules:
                yield {
                    "progress": progress,
                    "current_step": description
                }
                
                module = module_class(self.target_url)
                results = await module.check()
                self.vulnerabilities.extend(results)
                await asyncio.sleep(0.5)
        
        # Calculate risk scores
        yield {
            "progress": 95,
            "current_step": "Calculating risk scores"
        }
        
        scorer = RiskScorer()
        for vuln in self.vulnerabilities:
            vuln['cvss'] = scorer.calculate_cvss(vuln)
    
    def get_results(self) -> Dict:
        """Get final scan results"""
        
        summary = {
            'critical': len([v for v in self.vulnerabilities if v['severity'] == 'critical']),
            'high': len([v for v in self.vulnerabilities if v['severity'] == 'high']),
            'medium': len([v for v in self.vulnerabilities if v['severity'] == 'medium']),
            'low': len([v for v in self.vulnerabilities if v['severity'] == 'low']),
            'total': len(self.vulnerabilities)
        }
        
        return {
            'url': self.target_url,
            'scan_mode': self.scan_mode,
            'timestamp': datetime.utcnow().isoformat(),
            'summary': summary,
            'vulnerabilities': self.vulnerabilities
        }
