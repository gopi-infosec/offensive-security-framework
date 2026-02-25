import requests
import time

class VirusTotalAPI:
    """VirusTotal API integration"""
    
    BASE_URL = 'https://www.virustotal.com/api/v3'
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'x-apikey': api_key
        }
    
    def scan(self, target, scan_type):
        """Scan target using VirusTotal"""
        try:
            if scan_type == 'ip':
                return self._scan_ip(target)
            elif scan_type == 'domain':
                return self._scan_domain(target)
            elif scan_type == 'url':
                return self._scan_url(target)
            elif scan_type == 'hash':
                return self._scan_file(target)
            else:
                return {'error': 'Unsupported scan type'}
        except Exception as e:
            return {'error': str(e)}
    
    def _scan_ip(self, ip):
        """Scan IP address"""
        url = f'{self.BASE_URL}/ip_addresses/{ip}'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            attributes = data.get('data', {}).get('attributes', {})
            stats = attributes.get('last_analysis_stats', {})
            
            return {
                'malicious': stats.get('malicious', 0),
                'suspicious': stats.get('suspicious', 0),
                'harmless': stats.get('harmless', 0),
                'total': sum(stats.values()),
                'country': attributes.get('country', 'Unknown'),
                'asn': attributes.get('asn', 'Unknown')
            }
        else:
            return {'error': f'API error: {response.status_code}'}
    
    def _scan_domain(self, domain):
        """Scan domain"""
        url = f'{self.BASE_URL}/domains/{domain}'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            attributes = data.get('data', {}).get('attributes', {})
            stats = attributes.get('last_analysis_stats', {})
            
            return {
                'malicious': stats.get('malicious', 0),
                'suspicious': stats.get('suspicious', 0),
                'harmless': stats.get('harmless', 0),
                'total': sum(stats.values()),
                'categories': attributes.get('categories', {})
            }
        else:
            return {'error': f'API error: {response.status_code}'}
    
    def _scan_url(self, url):
        """Scan URL"""
        # Submit URL for analysis
        submit_url = f'{self.BASE_URL}/urls'
        data = {'url': url}
        response = requests.post(submit_url, headers=self.headers, data=data)
        
        if response.status_code == 200:
            analysis_id = response.json().get('data', {}).get('id')
            
            # Wait and get results
            time.sleep(2)
            result_url = f'{self.BASE_URL}/analyses/{analysis_id}'
            result_response = requests.get(result_url, headers=self.headers)
            
            if result_response.status_code == 200:
                data = result_response.json()
                stats = data.get('data', {}).get('attributes', {}).get('stats', {})
                
                return {
                    'malicious': stats.get('malicious', 0),
                    'suspicious': stats.get('suspicious', 0),
                    'harmless': stats.get('harmless', 0),
                    'total': sum(stats.values())
                }
        
        return {'error': 'URL scan failed'}
    
    def _scan_file(self, file_hash):
        """Scan file hash"""
        url = f'{self.BASE_URL}/files/{file_hash}'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            attributes = data.get('data', {}).get('attributes', {})
            stats = attributes.get('last_analysis_stats', {})
            
            return {
                'malicious': stats.get('malicious', 0),
                'suspicious': stats.get('suspicious', 0),
                'harmless': stats.get('harmless', 0),
                'total': sum(stats.values()),
                'type_description': attributes.get('type_description', 'Unknown')
            }
        else:
            return {'error': f'API error: {response.status_code}'}
