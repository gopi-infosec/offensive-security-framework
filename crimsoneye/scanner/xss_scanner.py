import aiohttp
from typing import List, Dict
from urllib.parse import urljoin, urlparse, parse_qs

class XSSScanner:
    """Test for XSS vulnerabilities"""
    
    PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg/onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src=javascript:alert('XSS')>",
        "<body onload=alert('XSS')>"
    ]
    
    def __init__(self, target_url: str):
        self.target_url = target_url
    
    async def check(self) -> List[Dict]:
        """Test for XSS"""
        vulnerabilities = []
        
        try:
            parsed = urlparse(self.target_url)
            params = parse_qs(parsed.query)
            
            if not params:
                return vulnerabilities
            
            async with aiohttp.ClientSession() as session:
                for param_name in params.keys():
                    for payload in self.PAYLOADS:
                        test_params = params.copy()
                        test_params[param_name] = [payload]
                        
                        test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                        
                        try:
                            async with session.get(test_url, params=test_params, timeout=5) as response:
                                text = await response.text()
                                
                                # Check if payload is reflected
                                if payload in text:
                                    vulnerabilities.append({
                                        'title': 'Reflected XSS Vulnerability',
                                        'severity': 'critical',
                                        'description': f'User input reflected without sanitization in parameter: {param_name}',
                                        'owasp': 'A03:2021 – Injection',
                                        'affected': f'{param_name} parameter',
                                        'mitigation': 'Encode all user-supplied data. Implement Content Security Policy (CSP).'
                                    })
                                    return vulnerabilities
                        
                        except:
                            continue
        
        except Exception as e:
            print(f"XSS scan error: {e}")
        
        return vulnerabilities
