from typing import Dict

class RiskScorer:
    """Calculate CVSS scores for vulnerabilities"""
    
    # CVSS base scores by severity
    SEVERITY_SCORES = {
        'critical': {
            'min': 9.0,
            'max': 10.0
        },
        'high': {
            'min': 7.0,
            'max': 8.9
        },
        'medium': {
            'min': 4.0,
            'max': 6.9
        },
        'low': {
            'min': 0.1,
            'max': 3.9
        }
    }
    
    # Specific vulnerability scores
    VULN_SCORES = {
        'SQL Injection': 9.8,
        'Reflected XSS': 7.1,
        'Stored XSS': 8.8,
        'Path Traversal': 9.1,
        'Open Redirect': 4.7,
        'Missing X-Frame-Options': 6.5,
        'Missing CSP': 5.9,
        'Insecure Cookie': 6.1,
        'CORS Misconfiguration': 4.3,
        'Weak TLS': 5.3,
        'No HTTPS': 9.8,
        'Server Version Disclosure': 3.1,
        'Exposed API Documentation': 5.3,
        'Sensitive File Exposure': 9.8,
        'Admin Interface Accessible': 7.5,
        'Missing HSTS': 5.4,
        'Missing X-Content-Type-Options': 4.8,
        'Missing Referrer-Policy': 3.7,
        'Technology Fingerprinting': 2.6,
        'API Endpoints Discovered': 3.2
    }
    
    def calculate_cvss(self, vulnerability: Dict) -> str:
        """Calculate CVSS score for a vulnerability"""
        
        title = vulnerability.get('title', '')
        severity = vulnerability.get('severity', 'low')
        
        # Check for exact match
        for vuln_name, score in self.VULN_SCORES.items():
            if vuln_name.lower() in title.lower():
                return f"{score:.1f}"
        
        # Use severity-based scoring
        score_range = self.SEVERITY_SCORES.get(severity, self.SEVERITY_SCORES['low'])
        
        # Calculate middle of range
        score = (score_range['min'] + score_range['max']) / 2
        
        return f"{score:.1f}"
    
    def get_risk_level(self, cvss_score: float) -> str:
        """Get risk level from CVSS score"""
        
        if cvss_score >= 9.0:
            return 'Critical'
        elif cvss_score >= 7.0:
            return 'High'
        elif cvss_score >= 4.0:
            return 'Medium'
        else:
            return 'Low'
