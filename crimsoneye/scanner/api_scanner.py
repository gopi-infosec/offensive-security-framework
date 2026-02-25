import aiohttp
from typing import List, Dict
from urllib.parse import urljoin, urlparse

class APIScanner:
    """Scan for exposed API endpoints and documentation"""
    
    COMMON_ENDPOINTS = [
        '/api',
        '/api/v1',
        '/api/v2',
        '/graphql',
        '/swagger',
        '/swagger.json',
        '/swagger-ui.html',
        '/api-docs',
        '/api/docs',
        '/openapi.json',
        '/redoc',
        '/docs',
        '/.well-known/openid-configuration',
        '/robots.txt',
        '/sitemap.xml',
        '/.env',
        '/.git/config',
        '/composer.json',
        '/package.json',
        '/api/health',
        '/api/status',
        '/admin',
        '/api/admin',
        '/debug',
        '/api/debug'
    ]
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        parsed = urlparse(target_url)
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    async def check(self) -> List[Dict]:
        """Scan for exposed endpoints"""
        vulnerabilities = []
        found_endpoints = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for endpoint in self.COMMON_ENDPOINTS:
                    url = urljoin(self.base_url, endpoint)
                    
                    try:
                        async with session.get(url, timeout=5, allow_redirects=False) as response:
                            if response.status == 200:
                                found_endpoints.append(endpoint)
                                
                                # Check for sensitive endpoints
                                if endpoint in ['/swagger', '/swagger.json', '/swagger-ui.html', '/api-docs', '/openapi.json']:
                                    vulnerabilities.append({
                                        'title': 'Exposed API Documentation',
                                        'severity': 'medium',
                                        'description': f'API documentation exposed at {endpoint}',
                                        'owasp': 'A05:2021 – Security Misconfiguration',
                                        'affected': endpoint,
                                        'mitigation': 'Restrict access to API documentation in production. Implement authentication.'
                                    })
                                
                                elif endpoint in ['/.env', '/.git/config']:
                                    vulnerabilities.append({
                                        'title': 'Sensitive File Exposure',
                                        'severity': 'critical',
                                        'description': f'Sensitive configuration file accessible at {endpoint}',
                                        'owasp': 'A05:2021 – Security Misconfiguration',
                                        'affected': endpoint,
                                        'mitigation': 'Remove or restrict access to sensitive files. Configure web server to deny access.'
                                    })
                                
                                elif '/admin' in endpoint:
                                    vulnerabilities.append({
                                        'title': 'Admin Interface Accessible',
                                        'severity': 'high',
                                        'description': f'Admin interface found at {endpoint}',
                                        'owasp': 'A01:2021 – Broken Access Control',
                                        'affected': endpoint,
                                        'mitigation': 'Restrict admin interface access. Implement strong authentication and IP whitelisting.'
                                    })
                    
                    except:
                        continue
                
                # Report found endpoints (info only)
                if found_endpoints and not vulnerabilities:
                    endpoint_list = '\n'.join(found_endpoints)
                    vulnerabilities.append({
                        'title': 'API Endpoints Discovered',
                        'severity': 'low',
                        'description': f'Discovered endpoints:\n{endpoint_list}',
                        'owasp': 'A05:2021 – Security Misconfiguration',
                        'affected': 'API surface',
                        'mitigation': 'Review exposed endpoints. Ensure proper authentication and authorization.'
                    })
        
        except Exception as e:
            print(f"API scan error: {e}")
        
        return vulnerabilities
