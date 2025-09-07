import re
import time
import logging
from datetime import datetime

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('darkweb_intel.log'),
            logging.StreamHandler()
        ]
    )

def validate_onion_url(url):
    """Validate an onion URL"""
    onion_pattern = r'^https?://[a-z2-7]{16,56}\.onion(/.*)?$'
    return re.match(onion_pattern, url) is not None

def validate_i2p_url(url):
    """Validate an I2P URL"""
    i2p_pattern = r'^https?://[a-zA-Z0-9-]+\.i2p(/.*)?$'
    return re.match(i2p_pattern, url) is not None

def format_timestamp(timestamp=None):
    """Format a timestamp for display"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def calculate_risk_score(content):
    """Calculate a risk score based on content"""
    