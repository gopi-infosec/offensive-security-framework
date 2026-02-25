import requests

class AlienVaultAPI:
    """AlienVault OTX API integration"""
    
    BASE_URL = 'https://otx.alienvault.com/api/v1'
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'X-OTX-API-KEY': api_key
        }
    
    def scan(self, target, scan_type):
        """Scan target using AlienVault OTX"""
        try:
            if scan_type == 'ip':
                return self._scan_ip(target)
            elif scan_type == 'domain':
                return self._scan_domain(target)
            elif scan_type == 'url':
                return self._scan_url(target)
            elif scan_type == 'hash':
                return self._scan_hash(target)
            else:
                return {'error': 'Unsupported scan type'}
        except Exception as e:
            return {'error': str(e)}
    
    def _scan_ip(self, ip):
        """Scan IP address"""
        url = f'{self.BASE_URL}/indicators/IPv4/{ip}/general'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Get pulse information
            pulse_url = f'{self.BASE_URL}/indicators/IPv4/{ip}/malware'
            pulse_response = requests.get(pulse_url, headers=self.headers)
            pulses = pulse_response.json() if pulse_response.status_code == 200 else {}
            
            return {
                'pulse_count': data.get('pulse_info', {}).get('count', 0),
                'reputation': data.get('reputation', 0),
                'country': data.get('country_name', 'Unknown'),
                'city': data.get('city', 'Unknown'),
                'asn': data.get('asn', 'Unknown'),
                'pulses': pulses.get('data', [])[:5]  # Top 5 pulses
            }
        else:
            return {'error': f'API error: {response.status_code}'}
    
    def _scan_domain(self, domain):
        """Scan domain"""
        url = f'{self.BASE_URL}/indicators/domain/{domain}/general'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                'pulse_count': data.get('pulse_info', {}).get('count', 0),
                'alexa_rank': data.get('alexa', 'Unknown'),
                'whois': data.get('whois', 'Unknown')
            }
        else:
            return {'error': f'API error: {response.status_code}'}
    
    def _scan_url(self, url):
        """Scan URL"""
        endpoint = f'{self.BASE_URL}/indicators/url/{url}/general'
        response = requests.get(endpoint, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                'pulse_count': data.get('pulse_info', {}).get('count', 0),
                'alexa_rank': data.get('alexa', 'Unknown')
            }
        else:
            return {'error': f'API error: {response.status_code}'}
    
    def _scan_hash(self, file_hash):
        """Scan file hash"""
        url = f'{self.BASE_URL}/indicators/file/{file_hash}/general'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                'pulse_count': data.get('pulse_info', {}).get('count', 0),
                'analysis': data.get('analysis', {})
            }
        else:
            return {'error': f'API error: {response.status_code}'}
