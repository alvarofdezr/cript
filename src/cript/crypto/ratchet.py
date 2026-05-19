from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
from .keygen import generate_ecdsa_keypair
from .hkdf import derive_keys
from typing import Optional, Any


class SignatureRatchet:
    """
    Implements the Signature Ratcheting mechanism.
    
    The ratchet provides:
    1. Ephemeral signature keys that change per message
    2. Forward secrecy: compromising one key doesn't affect future keys
    3. Post-compromise security: Old messages remain secure even if current key is compromised
    
    Reference: Balbás et al. (2022) - Section on Signature Ratcheting
    """
    
    def __init__(self, initial_chain_key: Optional[bytes] = None):
        """
        Initialize the signature ratchet.
        
        Args:
            initial_chain_key: Initial 32-byte chain key (uses default if None)
        """
        self.chain_key = initial_chain_key or b"A" * 32
        self.ssk, self.spk = generate_ecdsa_keypair()  # Static Sender Key
        self.message_key = None
        
    def ratchet_forward(self) -> tuple:
        """
        Perform one ratchet step: advance the ephemeral key and derive new chain key.
        
        Returns:
            tuple: (current_public_key, new_chain_key)
            
        Security:
            - Generates new ephemeral keypair
            - Old keys are destroyed (forward secrecy)
            - Each call produces unique cryptographic material
        """
        # Derive keys from current chain key
        self.message_key, self.chain_key = derive_keys(self.chain_key)
        
        # Generate new ephemeral keypair
        new_ssk, new_spk = generate_ecdsa_keypair()
        current_spk = self.spk
        
        # Update for next iteration
        self.ssk, self.spk = new_ssk, new_spk
        
        return current_spk, self.chain_key
    
    def sign_message(self, message: bytes, key: Optional[Any] = None) -> bytes:
        """
        Sign a message with the current static sender key.
        
        Args:
            message: Message bytes to sign
            key: Optional custom key (uses self.ssk if None)
            
        Returns:
            bytes: ECDSA signature (DER encoded)
        """
        key_to_use = key or self.ssk
        signature: bytes = key_to_use.sign(message, ec.ECDSA(hashes.SHA256()))
        return signature
    
    def verify_signature(self, signature: bytes, message: bytes, public_key: Any) -> bool:
        """
        Verify a message signature against a public key.
        
        Args:
            signature: ECDSA signature to verify
            message: Original message
            public_key: Public key to verify against
            
        Returns:
            bool: True if signature is valid, raises InvalidSignature otherwise
            
        Security:
            - ECDSA verification with SHA256
            - Raises exception on invalid signature (fail-secure)
        """
        try:
            public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
            return True
        except InvalidSignature:
            raise
    
    def export_public_key(self, public_key: Any) -> bytes:
        """
        Export public key to DER format for transmission.
        
        Args:
            public_key: Public key object
            
        Returns:
            bytes: DER-encoded public key
        """
        der_bytes: bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        return der_bytes
    
    def import_public_key(self, der_bytes: bytes) -> Any:
        """
        Import public key from DER format.
        
        Args:
            der_bytes: DER-encoded public key bytes
            
        Returns:
            PublicKey: Imported public key object
        """
        return serialization.load_der_public_key(der_bytes)
