"""
CRIPT: Cryptographic Ratcheting Implementation Protocol

A professional implementation of the Sender Keys Protocol with Signature Ratcheting
as described in:
Balbás, D., Collins, D., & Gajland, P. (2022). Analysis and Improvements of the 
Sender Keys Protocol for Group Messaging. XVII RECSI 2022, Santander, 25-30.

Author: Security Research Implementation
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Security Team"
__license__ = "MIT"

from .core.protocol import SenderKeysProtocol
from .crypto.ratchet import SignatureRatchet
from .crypto.keygen import generate_ecdsa_keypair

__all__ = [
    "SenderKeysProtocol",
    "SignatureRatchet",
    "generate_ecdsa_keypair",
]
