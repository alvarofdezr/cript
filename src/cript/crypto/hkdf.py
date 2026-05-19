"""HKDF-based key derivation for chain and message keys"""

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def derive_keys(chain_key: bytes) -> tuple:
    """
    Derive message key and new chain key using HKDF-SHA256.
    
    This implements the ratcheting mechanism from the Sender Keys Protocol:
    - Message Key (MK): Used for symmetric encryption
    - New Chain Key (CK): Used for next iteration's derivation
    
    Args:
        chain_key: Current chain key (32 bytes)
        
    Returns:
        tuple: (message_key, new_chain_key) both 32 bytes
        
    Security Properties:
        - Forward secrecy: Each new CK is independent
        - Post-compromise security: Cannot recover past keys from future CK
    """
    # Derive Message Key
    hkdf_mk = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"MessageKey"
    )
    message_key = hkdf_mk.derive(chain_key)
    
    # Derive new Chain Key
    hkdf_ck = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"ChainKey"
    )
    new_chain_key = hkdf_ck.derive(chain_key)
    
    return message_key, new_chain_key
