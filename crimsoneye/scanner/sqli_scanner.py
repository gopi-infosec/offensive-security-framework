import aiohttp
from typing import List, Dict
from urllib.parse import urljoin, urlparse, parse_qs

class SQLiScanner:
    """Test for SQL injection vulnerabilities"""
    
    PAYLOADS = [
        "'",
        "' OR '1'='1",
        "' OR '1'='1' --",
        "' OR '1'='1' /*",
        "admin' --",
        "' UNION SELECT NULL--",
        "1' AND '1'='2"
    ]
    
    ERROR_PATTERNS = [
        "sql syntax",
        "mysql_fetch",
        "warning: mysql",
        "unclosed quotation",
        "quoted string not properly terminated",
        "ora-01756",
        "sqlserver",
        "odbc driver"
    ]
    
    def __init__(self, target_url: str):
        self.target_url = target_url
    
    async def check(self) -> List[Dict]:
        """Test for SQL injection"""
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
                                text_lower = text.lower()
                                
                                for error in self.ERROR_PATTERNS:
                                    if error in text_lower:
                                        vulnerabilities.append({
                                            'title': 'SQL Injection Vulnerability',
                                            'severity': 'critical',
                                            'description': f'Potential SQL injection in parameter: {param_name}',
                                            'owasp': 'A03:2021 – Injection',
                                            'affected': f'{param_name} parameter',
                                            'mitigation': 'Use parameterized queries or prepared statements.'
                                        })
                                        return vulnerabilities  # Found vulnerability, stop testing
                        
                        except:
                            continue
        
        except Exception as e:
            print(f"SQLi scan error: {e}")
        
        return vulnerabilities
