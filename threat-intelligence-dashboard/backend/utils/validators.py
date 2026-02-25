import re

def validate_input(value, input_type):
    """Validate input based on type"""
    
    patterns = {
        'ip': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
        'domain': r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$',
        'url': r'^https?://.+',
        'hash': r'^[a-fA-F0-9]{32,64}$'
    }
    
    if input_type not in patterns:
        return False
    
    pattern = re.compile(patterns[input_type])
    return bool(pattern.match(value))
