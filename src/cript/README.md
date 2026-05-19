# CRIPT Source Code

This directory contains the main CRIPT implementation.

## Structure

```
cript/
├── crypto/          # Cryptographic primitives
│   ├── keygen.py    # ECDSA key generation
│   ├── hkdf.py      # HKDF key derivation
│   └── ratchet.py   # Signature ratcheting mechanism
├── core/            # Protocol logic
│   ├── protocol.py  # Sender Keys Protocol
│   └── message.py   # Message models
└── network/         # Network layer
    ├── server.py    # Relay server
    └── client.py    # Protocol client
```

## Quick Start

```python
from cript.core.protocol import SenderKeysProtocol

# Sender
sender = SenderKeysProtocol.Sender("Alice")
message = sender.create_message("Hello!")

# Receiver
receiver = SenderKeysProtocol.Receiver("Bob")
if receiver.verify_message(message):
    content = receiver.get_decrypted_content(message)
    print(f"Received: {content}")
```

See [../README.md](../README.md) for full documentation.
