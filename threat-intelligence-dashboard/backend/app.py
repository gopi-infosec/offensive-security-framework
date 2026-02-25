from flask import Flask, request, jsonify
from flask_cors import CORS
from api.virustotal import VirusTotalAPI
from api.abuseipdb import AbuseIPDBAPI
from api.alienvault import AlienVaultAPI
from utils.validators import validate_input
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'TIT API'}), 200

@app.route('/api/scan', methods=['POST'])
def scan_target():
    """
    Scan a target (IP, domain, URL, or hash) across multiple threat intelligence sources
    """
    try:
        data = request.get_json()
        
        target = data.get('target')
        scan_type = data.get('type')
        api_keys = data.get('api_keys', {})
        
        # Validate input
        if not target or not scan_type:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        if not validate_input(target, scan_type):
            return jsonify({'error': 'Invalid input format'}), 400
        
        logger.info(f'Scanning {scan_type}: {target}')
        
        # Initialize API clients
        results = {}
        
        # VirusTotal
        if api_keys.get('virustotal'):
            try:
                vt_api = VirusTotalAPI(api_keys['virustotal'])
                vt_result = vt_api.scan(target, scan_type)
                results['virustotal'] = vt_result
            except Exception as e:
                logger.error(f'VirusTotal error: {e}')
                results['virustotal'] = {'error': str(e)}
        
        # AbuseIPDB (only for IPs)
        if scan_type == 'ip' and api_keys.get('abuseipdb'):
            try:
                abuse_api = AbuseIPDBAPI(api_keys['abuseipdb'])
                abuse_result = abuse_api.check_ip(target)
                results['abuseipdb'] = abuse_result
            except Exception as e:
                logger.error(f'AbuseIPDB error: {e}')
                results['abuseipdb'] = {'error': str(e)}
        
        # AlienVault OTX
        if api_keys.get('alienvault'):
            try:
                otx_api = AlienVaultAPI(api_keys['alienvault'])
                otx_result = otx_api.scan(target, scan_type)
                results['alienvault'] = otx_result
            except Exception as e:
                logger.error(f'AlienVault OTX error: {e}')
                results['alienvault'] = {'error': str(e)}
        
        # Add metadata
        results['metadata'] = {
            'target': target,
            'type': scan_type,
            'timestamp': str(logger.info)
        }
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f'Scan error: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/feeds', methods=['GET'])
def get_threat_feeds():
    """
    Get latest threat intelligence feeds
    """
    try:
        # This would fetch real-time threat feeds from various sources
        feeds = [
            {
                'title': 'New Ransomware Campaign Detected',
                'description': 'Multiple organizations report new ransomware variant',
                'severity': 'critical',
                'source': 'AlienVault OTX',
                'timestamp': '2 minutes ago'
            }
        ]
        
        return jsonify(feeds), 200
        
    except Exception as e:
        logger.error(f'Feed error: {e}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
