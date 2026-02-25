import ssl
import socket
from urllib.parse import urlparse
from typing import List, Dict

class TLSChecker:
    """Check SSL/TLS configuration"""
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        parsed = urlparse(target_url)
        self.hostname = parsed.hostname
        self.port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    
    async def check(self) -> List[Dict]:
        """Check TLS configuration"""
        vulnerabilities = []
        
        if not self.target_url.startswith('https://'):
            vulnerabilities.append({
                'title': 'No HTTPS Enabled',
                'severity': 'critical',
                'description': 'The website does not use HTTPS encryption.',
                'owasp': 'A02:2021 – Cryptographic Failures',
                'affected': 'Entire site',
                'mitigation': 'Enable HTTPS with a valid SSL/TLS certificate.'
            })
            return vulnerabilities
        
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((self.hostname, self.port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    # Check TLS version
                    if version in ['TLSv1', 'TLSv1.1']:
                        vulnerabilities.append({
                            'title': 'Weak TLS Configuration',
                            'severity': 'medium',
                            'description': f'Server supports deprecated protocol: {version}',
                            'owasp': 'A02:2021 – Cryptographic Failures',
                            'affected': 'HTTPS endpoint',
                            'mitigation': 'Disable TLS 1.0 and 1.1. Only support TLS 1.2 and TLS 1.3.'
                        })
        
        except Exception as e:
            print(f"TLS check error: {e}")
        
        return vulnerabilities
