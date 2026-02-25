import aiohttp
import re
from typing import List, Dict
from bs4 import BeautifulSoup

class TechFingerprint:
    """Fingerprint web technologies"""
    
    def __init__(self, target_url: str):
        self.target_url = target_url
    
    async def check(self) -> List[Dict]:
        """Fingerprint technologies"""
        vulnerabilities = []
        detected_tech = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.target_url, timeout=10) as response:
                    headers = response.headers
                    text = await response.text()
                    
                    # Server detection
                    if 'Server' in headers:
                        server = headers['Server']
                        detected_tech.append(f"Server: {server}")
                    
                    # X-Powered-By detection
                    if 'X-Powered-By' in headers:
                        powered_by = headers['X-Powered-By']
                        detected_tech.append(f"Powered by: {powered_by}")
                    
                    # Parse HTML for technology signatures
                    soup = BeautifulSoup(text, 'html.parser')
                    
                    # WordPress detection
                    if 'wp-content' in text or 'wp-includes' in text:
                        detected_tech.append("CMS: WordPress")
                        
                        # Check WordPress version
                        meta_gen = soup.find('meta', {'name': 'generator'})
                        if meta_gen and 'WordPress' in str(meta_gen):
                            version = re.search(r'WordPress (\d+\.\d+\.\d+)', str(meta_gen))
                            if version:
                                detected_tech.append(f"WordPress version: {version.group(1)}")
                    
                    # Joomla detection
                    if 'joomla' in text.lower():
                        detected_tech.append("CMS: Joomla")
                    
                    # Drupal detection
                    if 'drupal' in text.lower() or 'sites/default/files' in text:
                        detected_tech.append("CMS: Drupal")
                    
                    # Framework detection
                    if 'django' in text.lower():
                        detected_tech.append("Framework: Django")
                    
                    if 'Laravel' in text or 'laravel_session' in str(response.cookies):
                        detected_tech.append("Framework: Laravel")
                    
                    if 'X-AspNet-Version' in headers:
                        detected_tech.append(f"Framework: ASP.NET {headers['X-AspNet-Version']}")
                    
                    # JavaScript library detection
                    if 'jquery' in text.lower():
                        jquery_version = re.search(r'jquery[/-](\d+\.\d+\.\d+)', text.lower())
                        if jquery_version:
                            detected_tech.append(f"Library: jQuery {jquery_version.group(1)}")
                        else:
                            detected_tech.append("Library: jQuery")
                    
                    if 'react' in text.lower():
                        detected_tech.append("Library: React")
                    
                    if 'angular' in text.lower():
                        detected_tech.append("Library: Angular")
                    
                    if 'vue' in text.lower():
                        detected_tech.append("Library: Vue.js")
                    
                    # CDN detection
                    if 'cloudflare' in str(headers).lower():
                        detected_tech.append("CDN: Cloudflare")
                    
                    if 'akamai' in str(headers).lower():
                        detected_tech.append("CDN: Akamai")
                    
                    # Report detected technologies
                    if detected_tech:
                        tech_list = '\n'.join(detected_tech)
                        vulnerabilities.append({
                            'title': 'Technology Fingerprinting',
                            'severity': 'low',
                            'description': f'Detected technologies:\n{tech_list}',
                            'owasp': 'A05:2021 – Security Misconfiguration',
                            'affected': 'Server configuration',
                            'mitigation': 'Remove version information from headers. Minimize technology disclosure.'
                        })
        
        except Exception as e:
            print(f"Fingerprint error: {e}")
        
        return vulnerabilities
