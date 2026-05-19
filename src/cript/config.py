import os

# Server Configuration
SERVER_HOST = os.getenv('CRIPT_SERVER_HOST', '0.0.0.0') # nosec B104
SERVER_PORT = int(os.getenv('CRIPT_SERVER_PORT', 5000))
SERVER_BACKLOG = int(os.getenv('CRIPT_SERVER_BACKLOG', 10))

# Tailscale Configuration (for production)
TAILSCALE_ENABLED = os.getenv('CRIPT_TAILSCALE', 'false').lower() == 'true'
TAILSCALE_INTERFACE = 'tailscale0'

# Logging Configuration
LOG_LEVEL = os.getenv('CRIPT_LOG_LEVEL', 'INFO')
LOG_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'

# Crypto Configuration
ECDSA_CURVE = 'SECP256R1'
HASH_ALGORITHM = 'SHA256'
CHAIN_KEY_SIZE = 32  # bytes
MESSAGE_KEY_SIZE = 32  # bytes

# Network Configuration
SOCKET_TIMEOUT = float(os.getenv('CRIPT_SOCKET_TIMEOUT', 1.0))
MAX_MESSAGE_SIZE = int(os.getenv('CRIPT_MAX_MESSAGE_SIZE', 4096))

# Security Configuration
FAIL_SECURE = True  # Always reject on verification failure
ALLOW_COMPRESSION = False  # Avoid side-channel attacks
