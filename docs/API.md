"""
API Reference for CRIPT Protocol

Core Classes and Functions
"""

# Crypto Primitives
from cript.crypto.keygen import generate_ecdsa_keypair
from cript.crypto.ratchet import SignatureRatchet
from cript.crypto.hkdf import derive_keys

# Protocol
from cript.core.protocol import SenderKeysProtocol
from cript.core.message import CriptMessage

# Network
from cript.network.server import CriptServer
from cript.network.client import CriptClient

__all__ = [
    # Crypto
    "generate_ecdsa_keypair",
    "SignatureRatchet",
    "derive_keys",
    
    # Protocol
    "SenderKeysProtocol",
    "CriptMessage",
    
    # Network
    "CriptServer",
    "CriptClient",
]

# Documentation
"""
QUICK API OVERVIEW

1. SENDER KEYS PROTOCOL
========================

Sender:
  sender = SenderKeysProtocol.Sender("Alicia")
  message = sender.create_message("Hello!")
  
  Properties:
    - message.sender_name: "Alicia"
    - message.ciphertext: base64 encoded
    - message.signature: ECDSA signature
    - message.next_spk: Ephemeral public key
    - message.sequence_number: 1

Receiver:
  receiver = SenderKeysProtocol.Receiver("Roberto")
  receiver.register_sender("Alicia", public_key_der)
  
  if receiver.verify_message(message):
      content = receiver.get_decrypted_content(message)

2. CRYPTOGRAPHIC PRIMITIVES
============================

Key Generation:
  private_key, public_key = generate_ecdsa_keypair()

Signature Ratcheting:
  ratchet = SignatureRatchet()
  public_key, chain_key = ratchet.ratchet_forward()
  signature = ratchet.sign_message(data)
  ratchet.verify_signature(signature, data, public_key)

Key Derivation:
  message_key, chain_key = derive_keys(initial_chain_key)

3. NETWORK
==========

Server:
  server = CriptServer("0.0.0.0", 5000)
  server.start()

Client:
  client = CriptClient("Alice", "100.120.170.116", 5000)
  client.connect()
  client.send(message_dict)
  received = client.receive()
  client.disconnect()

4. MESSAGES
===========

Create:
  msg = CriptMessage(
      sender_name="Alice",
      ciphertext="base64_data",
      signature="base64_sig",
      next_spk="base64_key"
  )

Serialize:
  json_str = msg.to_json()
  msg = CriptMessage.from_json(json_str)
  dict_repr = msg.to_dict()
"""
