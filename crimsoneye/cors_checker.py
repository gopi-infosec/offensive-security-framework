import aiohttp
from typing import List, Dict

class CORSChecker:
    def __init__(self, target_url: str):
        self.target_url = target_url
    
    async def check(self) -> List[Dict]:
        vulnerabilities = []
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Origin': 'https://evil.com'}
                async with session.get(self.target_url, headers=headers, timeout=10) as response:
                    cors_header = response.headers.get('Access-Control-Allow-Origin', '')
                    if cors_header == '*':
                        vulnerabilities.append({
                            'title': 'CORS Misconfiguration',
                            'severity': 'medium',
                            'description': 'Access-Control-Allow-Origin set to wildcard (*)',
                            'owasp': 'A05:2021 – Security Misconfiguration',
                            'affected': '/api/*',
                            'mitigation': 'Set specific allowed origins. Never use wildcard.'
                        })
        except Exception as e:
            print(f"CORS check error: {e}")
        return vulnerabilities
