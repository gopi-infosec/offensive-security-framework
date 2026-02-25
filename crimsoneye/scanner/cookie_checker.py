import aiohttp
from typing import List, Dict

class CookieChecker:
    """Check cookie security flags"""
    
    def __init__(self, target_url: str):
        self.target_url = target_url
    
    async def check(self) -> List[Dict]:
        """Check cookie security"""
        vulnerabilities = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.target_url, timeout=10) as response:
                    cookies = response.cookies
                    
                    for cookie in cookies.values():
                        issues = []
                        
                        if not cookie.get('secure'):
                            issues.append('Secure flag missing')
                        if not cookie.get('httponly'):
                            issues.append('HttpOnly flag missing')
                        if not cookie.get('samesite'):
                            issues.append('SameSite attribute missing')
                        
                        if issues:
                            vulnerabilities.append({
                                'title': 'Insecure Cookie Configuration',
                                'severity': 'high',
                                'description': f'Cookie "{cookie.key}" has security issues: {", ".join(issues)}',
                                'owasp': 'A05:2021 – Security Misconfiguration',
                                'affected': f'{cookie.key} cookie',
                                'mitigation': 'Set Secure, HttpOnly, and SameSite=Strict flags on all cookies.'
                            })
        
        except Exception as e:
            print(f"Cookie check error: {e}")
        
        return vulnerabilities
