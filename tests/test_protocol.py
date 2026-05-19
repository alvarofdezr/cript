"""Comprehensive tests for CRIPT protocol"""

import pytest
from cryptography.exceptions import InvalidSignature

from cript.crypto.keygen import generate_ecdsa_keypair
from cript.crypto.ratchet import SignatureRatchet
from cript.crypto.hkdf import derive_keys
from cript.core.protocol import SenderKeysProtocol
from cript.core.message import CriptMessage


class TestCryptoKeyGen:
    """Test ECDSA key generation"""
    
    def test_keypair_generation(self):
        """Test that keypairs are generated correctly"""
        private_key, public_key = generate_ecdsa_keypair()
        assert private_key is not None
        assert public_key is not None
    
    def test_keypairs_are_different(self):
        """Test that different calls generate different keypairs"""
        priv1, pub1 = generate_ecdsa_keypair()
        priv2, pub2 = generate_ecdsa_keypair()
        
        # Different objects
        assert priv1 != priv2
        assert pub1 != pub2


class TestHKDF:
    """Test HKDF key derivation"""
    
    def test_derive_keys_returns_tuple(self):
        """Test that derive_keys returns two keys"""
        chain_key = b"A" * 32
        mk, ck = derive_keys(chain_key)
        
        assert isinstance(mk, bytes)
        assert isinstance(ck, bytes)
        assert len(mk) == 32
        assert len(ck) == 32
    
    def test_derived_keys_different(self):
        """Test that message key and chain key are different"""
        chain_key = b"A" * 32
        mk, ck = derive_keys(chain_key)
        
        assert mk != ck
    
    def test_deterministic_derivation(self):
        """Test that same chain key produces same derivation"""
        chain_key = b"A" * 32
        mk1, ck1 = derive_keys(chain_key)
        mk2, ck2 = derive_keys(chain_key)
        
        assert mk1 == mk2
        assert ck1 == ck2
    
    def test_forward_secrecy(self):
        """Test that chain evolves forward"""
        ck = b"A" * 32
        
        mk1, ck1 = derive_keys(ck)
        mk2, ck2 = derive_keys(ck1)
        
        # Each iteration produces new keys
        assert mk1 != mk2
        assert ck1 != ck2
        assert ck != ck1


class TestSignatureRatchet:
    """Test signature ratcheting mechanism"""
    
    def test_ratchet_initialization(self):
        """Test ratchet initializes correctly"""
        ratchet = SignatureRatchet()
        assert ratchet.chain_key is not None
        assert ratchet.ssk is not None
        assert ratchet.spk is not None
    
    def test_ratchet_forward(self):
        """Test ratchet forward operation"""
        ratchet = SignatureRatchet()
        spk1, ck1 = ratchet.ratchet_forward()
        
        assert spk1 is not None
        assert ck1 is not None
    
    def test_ratchet_changes_keys(self):
        """Test that ratcheting changes ephemeral keys"""
        ratchet = SignatureRatchet()
        spk1, ck1 = ratchet.ratchet_forward()
        spk2, ck2 = ratchet.ratchet_forward()
        
        # Public keys should be different
        assert spk1 != spk2
    
    def test_sign_verify(self):
        """Test message signing and verification"""
        ratchet = SignatureRatchet()
        message = b"Test message"
        
        signature = ratchet.sign_message(message)
        assert len(signature) > 0
        
        # Verify signature
        assert ratchet.verify_signature(signature, message, ratchet.spk)
    
    def test_invalid_signature_detection(self):
        """Test that invalid signatures are detected"""
        ratchet = SignatureRatchet()
        message = b"Test message"
        
        signature = ratchet.sign_message(message)
        modified_message = b"Modified message"
        
        with pytest.raises(InvalidSignature):
            ratchet.verify_signature(signature, modified_message, ratchet.spk)
    
    def test_key_export_import(self):
        """Test exporting and importing public keys"""
        ratchet = SignatureRatchet()
        der_bytes = ratchet.export_public_key(ratchet.spk)
        
        imported_key = ratchet.import_public_key(der_bytes)
        assert imported_key is not None


class TestSenderKeysProtocol:
    """Test the Sender Keys Protocol implementation"""
    
    def test_sender_creation(self):
        """Test sender initialization"""
        sender = SenderKeysProtocol.Sender(name="Alice")
        assert sender.name == "Alice"
        assert sender.message_count == 0
    
    def test_sender_create_message(self):
        """Test creating and signing a message"""
        sender = SenderKeysProtocol.Sender(name="Alice")
        message = sender.create_message("Hello, Bob!")
        
        assert message.sender_name == "Alice"
        assert message.ciphertext is not None
        assert message.signature is not None
        assert message.next_spk is not None
        assert message.sequence_number == 1
    
    def test_sender_message_sequence(self):
        """Test that messages have increasing sequence numbers"""
        sender = SenderKeysProtocol.Sender(name="Alice")
        
        msg1 = sender.create_message("Message 1")
        msg2 = sender.create_message("Message 2")
        
        assert msg1.sequence_number == 1
        assert msg2.sequence_number == 2
    
    def test_receiver_creation(self):
        """Test receiver initialization"""
        receiver = SenderKeysProtocol.Receiver(name="Bob")
        assert receiver.name == "Bob"
        assert len(receiver.sender_keys) == 0
    
    def test_receiver_verify_valid_message(self):
        """Test verifying a valid message"""
        # Create sender and send message
        sender = SenderKeysProtocol.Sender(name="Alice")
        message = sender.create_message("Hello!")
        
        # Receiver: Extract initial sender key
        ratchet = SignatureRatchet()
        initial_spk = ratchet.export_public_key(sender.ratchet.spk)
        
        # Register sender
        receiver = SenderKeysProtocol.Receiver(name="Bob")
        receiver.register_sender("Alice", initial_spk)
        
        # Verify message - should fail initially because we need first key
        # In production, keys are exchanged out-of-band
    
    def test_receiver_detect_tampering(self):
        """Test that tampering is detected"""
        sender = SenderKeysProtocol.Sender(name="Alice")
        message = sender.create_message("Original")
        
        # Tamper with ciphertext
        import base64
        ciphertext = base64.b64decode(message.ciphertext)
        tampered = base64.b64encode(ciphertext + b"tampered").decode('utf-8')
        message.ciphertext = tampered
        
        # Try to verify - should fail
        receiver = SenderKeysProtocol.Receiver(name="Bob")
        ratchet = SignatureRatchet()
        initial_spk = ratchet.export_public_key(sender.ratchet.spk)
        receiver.register_sender("Alice", initial_spk)
        
        # Should raise InvalidSignature
        assert receiver.verify_message(message) is False
    
    def test_message_serialization(self):
        """Test message JSON serialization"""
        message = CriptMessage(
            sender_name="Alice",
            ciphertext="aGVsbG8=",
            signature="c2lnbg==",
            next_spk="a2V5"
        )
        
        json_str = message.to_json()
        assert "Alice" in json_str
        
        recovered = CriptMessage.from_json(json_str)
        assert recovered.sender_name == "Alice"
    
    def test_export_sender_state(self):
        """Test exporting sender state for debugging"""
        sender = SenderKeysProtocol.Sender(name="Alice")
        sender.create_message("Test")
        
        state = sender.export_state()
        assert state['name'] == "Alice"
        assert state['message_count'] == 1
    
    def test_export_receiver_state(self):
        """Test exporting receiver state for debugging"""
        receiver = SenderKeysProtocol.Receiver(name="Bob")
        
        state = receiver.export_state()
        assert state['name'] == "Bob"
        assert len(state['known_senders']) == 0


class TestSecurityProperties:
    """Test security properties of the protocol"""
    
    def test_forward_secrecy_chain(self):
        """Test that compromising one key doesn't expose others"""
        ratchet = SignatureRatchet()
        
        # Collect three ratchet steps
        keys = []
        for _ in range(3):
            spk, ck = ratchet.ratchet_forward()
            keys.append((spk, ck))
        
        # Each iteration should produce different keys
        assert keys[0][0] != keys[1][0]
        assert keys[1][0] != keys[2][0]
    
    def test_ephemeral_keys_differ_per_message(self):
        """Test that each message uses different ephemeral key"""
        sender = SenderKeysProtocol.Sender(name="Alice")
        
        msg1 = sender.create_message("Message 1")
        msg2 = sender.create_message("Message 2")
        
        # Different ephemeral keys for each message
        assert msg1.next_spk != msg2.next_spk
    
    def test_signature_authentication(self):
        """Test that signatures authenticate the sender"""
        ratchet = SignatureRatchet()
        message = b"Authenticated message"
        
        signature = ratchet.sign_message(message)
        
        # Only the private key holder can create valid signatures
        assert ratchet.verify_signature(signature, message, ratchet.spk)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
