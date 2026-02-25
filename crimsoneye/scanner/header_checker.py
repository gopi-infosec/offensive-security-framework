import aiohttp
from typing import List, Dict

class HeaderChecker:
    """Check for missing security headers"""
    
    SECURITY_HEADERS = {
        'X-Frame-Options': 'Missing X-Frame-Options header',
        'X-Content-Type-Options': 'Missing X-Content-Type-Options header',
        'Strict-Transport-Security': 'Missing HSTS header',
        'Content-Security-Policy': 'Missing Content Security Policy',
        'X-XSS-Protection': 'Missing X-XSS-Protection header',
        'Referrer-Policy': 'Missing Referrer-Policy header',
        'Permissions-Policy': 'Missing Permissions-Policy header'
    }
    
    def __init__(self, target_url: str):
        self.target_url = target_url
    
    async def check(self) -> List[Dict]:
        """Check security headers"""
        vulnerabilities = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.target_url, timeout=10) as response:
                    headers = response.headers
                    
                    # Check for missing headers
                    for header, description in self.SECURITY_HEADERS.items():
                        if header not in headers:
                            severity = 'high' if header in ['X-Frame-Options', 'Content-Security-Policy'] else 'medium'
                            
                            vulnerabilities.append({
                                'title': description,
                                'severity': severity,
                                'description': f'The {header} header is not set, which may expose the application to security risks.',
                                'owasp': 'A05:2021 – Security Misconfiguration',
                                'affected': 'All pages',
                                'mitigation': f'Add "{header}" header with appropriate value.'
                            })
                    
                    # Check for server version disclosure
                    if 'Server' in headers and any(char.isdigit() for char in headers['Server']):
                        vulnerabilities.append({
                            'title': 'Server Version Disclosure',
                            'severity': 'low',
                            'description': f'Server header reveals version information: {headers["Server"]}',
                            'owasp': 'A05:2021 – Security Misconfiguration',
                            'affected': 'HTTP response headers',
                            'mitigation': 'Disable server version disclosure in web server configuration.'
                        })
        
        except Exception as e:
            print(f"Header check error: {e}")
        
        return vulnerabilities
