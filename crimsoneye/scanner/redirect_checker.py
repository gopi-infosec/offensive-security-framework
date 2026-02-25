
import aiohttp
from typing import List, Dict
from urllib.parse import urljoin, urlparse

class RedirectChecker:
    """Check for open redirect vulnerabilities"""
    
    REDIRECT_PAYLOADS = [
        "https://evil.com",
        "//evil.com",
        "///evil.com",
        "javascript:alert('XSS')",
        "data:text/html,<script>alert('XSS')</script>"
    ]
    
    def __init__(self, target_url: str):
        self.target_url = target_url
    
    async def check(self) -> List[Dict]:
        """Test for open redirect vulnerabilities"""
        vulnerabilities = []
        
        try:
            parsed = urlparse(self.target_url)
            
            # Common redirect parameters
            redirect_params = ['url', 'redirect', 'next', 'return', 'returnUrl', 'goto', 'target']
            
            async with aiohttp.ClientSession(allow_redirects=False) as session:
                for param in redirect_params:
                    for payload in self.REDIRECT_PAYLOADS:
                        test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{param}={payload}"
                        
                        try:
                            async with session.get(test_url, timeout=5) as response:
                                if response.status in [301, 302, 303, 307, 308]:
                                    location = response.headers.get('Location', '')
                                    
                                    # Check if redirecting to external domain
                                    if 'evil.com' in location or location.startswith('//'):
                                        vulnerabilities.append({
                                            'title': 'Open Redirect Vulnerability',
                                            'severity': 'medium',
                                            'description': f'The application redirects to user-controlled URLs via the {param} parameter.',
                                            'owasp': 'A01:2021 – Broken Access Control',
                                            'affected': f'?{param}= parameter',
                                            'mitigation': 'Validate and whitelist redirect destinations. Never redirect to arbitrary user input.'
                                        })
                                        return vulnerabilities
                        except:
                            continue
        
        except Exception as e:
            print(f"Redirect check error: {e}")
        
        return vulnerabilities
