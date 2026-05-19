"""ECDSA key generation utilities"""

from cryptography.hazmat.primitives.asymmetric import ec
from typing import Tuple


def generate_ecdsa_keypair() -> Tuple:
    """
    Generate an ECDSA keypair using SECP256R1 curve.
    
    Returns:
        Tuple[PrivateKey, PublicKey]: Private and public key pair
        
    Security:
        - Uses SECP256R1 (P-256) - NIST standardized elliptic curve
        - Suitable for signature generation and verification
    """
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key
