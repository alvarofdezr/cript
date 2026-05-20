import base64
from cryptography.exceptions import InvalidSignature
from ..crypto.ratchet import SignatureRatchet
from .message import CriptMessage
from typing import Optional, Dict, Any


class SenderKeysProtocol:
    """
    Implements the Sender Keys Protocol with Signature Ratcheting.
    
    Reference:
        Balbás, D., Collins, D., & Gajland, P. (2022). Analysis and Improvements 
        of the Sender Keys Protocol for Group Messaging. XVII RECSI 2022.
    
    Components:
        1. Sender: Creates and signs messages using signature ratcheting
        2. Receiver: Validates messages and detects manipulation attempts
        3. Server: Blind relay of messages (doesn't read content)
    """
    
    class Sender:
        """Sender side of the protocol"""
        
        def __init__(self, name: str, initial_chain_key: Optional[bytes] = None):
            """
            Initialize a sender.
            
            Args:
                name: Sender identity
                initial_chain_key: Optional initial chain key
            """
            self.name = name
            self.ratchet = SignatureRatchet(initial_chain_key)
            self.message_count = 0
        
        def create_message(self, plaintext: str) -> CriptMessage:
            """
            Create and sign a message with ratcheting.
            
            Args:
                plaintext: Message content
                
            Returns:
                CriptMessage: Signed and ratcheted message
            """
            signing_key = self.ratchet.ssk
            
            self.ratchet.ratchet_forward()
            
            ciphertext = f"Cifrado({plaintext})".encode('utf-8')
            
            signature = self.ratchet.sign_message(ciphertext, key=signing_key)
            
            next_spk_der = self.ratchet.export_public_key(self.ratchet.spk)
            next_spk_b64 = base64.b64encode(next_spk_der).decode('utf-8')
            
            self.message_count += 1
            
            return CriptMessage(
                sender_name=self.name,
                ciphertext=base64.b64encode(ciphertext).decode('utf-8'),
                signature=base64.b64encode(signature).decode('utf-8'),
                next_spk=next_spk_b64,
                sequence_number=self.message_count
            )
        
        def export_state(self) -> dict:
            """Export sender state (for debugging/testing)"""
            return {
                'name': self.name,
                'message_count': self.message_count,
            }
    
    class Receiver:
        """Receiver side of the protocol"""
        
        def __init__(self, name: str):
            """
            Initialize a receiver.
            
            Args:
                name: Receiver identity
            """
            self.name = name
            self.sender_keys: Dict[str, Any] = {}
            self.message_count: Dict[str, int] = {} 
        
        def register_sender(self, sender_name: str, spk_der: bytes):
            """
            Register a sender's initial public key.
            
            Args:
                sender_name: Sender identity
                spk_der: DER-encoded public key
            """
            ratchet = SignatureRatchet()
            public_key = ratchet.import_public_key(spk_der)
            self.sender_keys[sender_name] = public_key
            self.message_count[sender_name] = 0
        
        def verify_message(self, message: CriptMessage) -> bool:
            """
            Verify an incoming message.
            
            Args:
                message: CriptMessage to verify
                
            Returns:
                bool: True if valid and authentic
                
            Raises:
                ValueError: If sender unknown
                InvalidSignature: If signature invalid (message tampered or forged)
            """
            if message.sender_name not in self.sender_keys:
                raise ValueError(f"Unknown sender: {message.sender_name}")
            
            ciphertext = base64.b64decode(message.ciphertext)
            signature = base64.b64decode(message.signature)
            public_key = self.sender_keys[message.sender_name]
            
            # Verify signature
            try:
                ratchet = SignatureRatchet()
                ratchet.verify_signature(signature, ciphertext, public_key)
                
                # Update public key if ratchet info provided
                if message.next_spk:
                    next_spk_der = base64.b64decode(message.next_spk)
                    self.sender_keys[message.sender_name] = ratchet.import_public_key(next_spk_der)
                
                self.message_count[message.sender_name] += 1
                return True
                
            except InvalidSignature:
                return False
        
        def get_decrypted_content(self, message: CriptMessage) -> str:
            """
            Get decrypted message content (placeholder - AES-GCM in production).
            
            Args:
                message: Verified message
                
            Returns:
                str: Decrypted content
            """
            ciphertext = base64.b64decode(message.ciphertext)
            return ciphertext.decode('utf-8')
        
        def export_state(self) -> dict:
            """Export receiver state (for debugging/testing)"""
            return {
                'name': self.name,
                'known_senders': list(self.sender_keys.keys()),
                'message_counts': self.message_count,
            }
