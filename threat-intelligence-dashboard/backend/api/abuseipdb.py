import requests

class AbuseIPDBAPI:
    """AbuseIPDB API integration"""
    
    BASE_URL = 'https://api.abuseipdb.com/api/v2'
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'Key': api_key,
            'Accept': 'application/json'
        }
    
    def check_ip(self, ip_address):
        """Check IP address reputation"""
        try:
            url = f'{self.BASE_URL}/check'
            params = {
                'ipAddress': ip_address,
                'maxAgeInDays': '90',
                'verbose': ''
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                
                return {
                    'abuseConfidenceScore': data.get('abuseConfidenceScore', 0),
                    'totalReports': data.get('totalReports', 0),
                    'numDistinctUsers': data.get('numDistinctUsers', 0),
                    'isWhitelisted': data.get('isWhitelisted', False),
                    'countryCode': data.get('countryCode', 'Unknown'),
                    'domain': data.get('domain', 'Unknown'),
                    'isp': data.get('isp', 'Unknown'),
                    'usageType': data.get('usageType', 'Unknown')
                }
            else:
                return {'error': f'API error: {response.status_code}'}
                
        except Exception as e:
            return {'error': str(e)}
