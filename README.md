# CRIPT - Cryptographic Ratcheting Implementation Protocol

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security: Cryptography](https://img.shields.io/badge/Security-Cryptography-red.svg)](https://cryptography.io/)

A professional implementation of the **Sender Keys Protocol with Signature Ratcheting** for secure group messaging, based on the academic research:

> **Balbás, D., Collins, D., & Gajland, P. (2022).** *Analysis and Improvements of the Sender Keys Protocol for Group Messaging.* XVII RECSI 2022, Santander, 25-30.

---

## 🔐 Overview

CRIPT provides a practical, production-ready implementation of the Sender Keys Protocol that enables:

- **Forward Secrecy**: Compromising one ephemeral key doesn't expose previous messages
- **Post-Compromise Security**: Even if the current key is compromised, past messages remain secure
- **Scalable Group Messaging**: Efficient protocol for multiple recipients
- **Signature Ratcheting**: Each message uses a derived ephemeral key for authentication

### Key Features

| Feature | Description |
|---------|-------------|
| **ECDSA Signatures** | Uses SECP256R1 (P-256) elliptic curve for signing |
| **HKDF Key Derivation** | HMAC-based Key Derivation Function (SHA256) for forward secrecy |
| **Blind Relay Server** | Server cannot read message contents, only routes packets |
| **Tailscale Integration** | Secure networking over VPN tunnel for private deployment |
| **Comprehensive Testing** | Unit and integration tests with security validation |
| **Production-Ready** | Proper error handling, logging, and security practices |

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### From Source

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/alvarofdezr/cript.git
cd cript

# Install with uv (creates virtual environment automatically)
uv sync

# With development tools
uv sync --group dev
```

### Using pip (Legacy)
```bash
pip install cript
```

---

## 🚀 Quick Start

### 1. **Sender: Create and Sign Messages**

```python
from cript.core.protocol import SenderKeysProtocol
from cript.crypto.ratchet import SignatureRatchet

# Initialize sender
sender = SenderKeysProtocol.Sender(name="Alicia")

# Create and sign message
message = sender.create_message("Hello, secure group!")
print(message.to_json())
```

### 2. **Receiver: Verify Messages**

```python
from cript.core.protocol import SenderKeysProtocol
from cryptography.exceptions import InvalidSignature

# Initialize receiver
receiver = SenderKeysProtocol.Receiver(name="Roberto")

# Register sender's initial public key (exchange happens out-of-band)
# In production, this comes from a key directory or manual verification

# Verify incoming message
try:
    is_valid = receiver.verify_message(message)
    if is_valid:
        content = receiver.get_decrypted_content(message)
        print(f"Authenticated content: {content}")
except InvalidSignature:
    print("⚠️ ALERT: Message signature invalid - possible forgery or tampering!")
```

### 3. **Run the Server**

```bash
python -m cript.network.server
# Output: CRIPT Server listening on 0.0.0.0:5000
```

---

## 🏗️ Architecture

```
CRIPT
├── src/cript/
│   ├── crypto/           # Cryptographic primitives
│   │   ├── keygen.py     # ECDSA key generation
│   │   ├── hkdf.py       # HKDF-SHA256 key derivation
│   │   └── ratchet.py    # Signature ratcheting mechanism
│   ├── core/             # Protocol logic
│   │   ├── protocol.py   # Sender Keys Protocol implementation
│   │   └── message.py    # Message serialization
│   └── network/          # Network layer
│       ├── server.py     # Blind relay server
│       └── client.py     # Protocol client
├── tests/                # Comprehensive test suite
├── examples/             # Usage examples
├── docs/                 # Technical documentation
└── pyproject.toml        # Project configuration
```

---

## 🔐 Security Properties

### Forward Secrecy (FS)
Each message uses an ephemeral signature key derived from a chain key. Compromising the current key does not expose past keys.

**Chain Key Derivation:**
```
CK_n = HKDF-SHA256(CK_{n-1}, info="ChainKey")
MK_n = HKDF-SHA256(CK_{n-1}, info="MessageKey")
```

### Post-Compromise Security (PCS)
After ratcheting, old ephemeral keys are destroyed. The protocol automatically advances to new keys with each message.

### Signature Authentication
- **Algorithm**: ECDSA with SHA256
- **Curve**: SECP256R1 (P-256) - NIST standardized
- **Key Recovery**: Impossible to derive private key from public key

---

## 📊 Protocol Flow

### Message Transmission

```
Sender (Alicia)                    Relay Server                   Receiver (Roberto)
        │                                 │                                │
        ├─ Generate ephemeral key       │                                │
        ├─ Sign message                 │                                │
        ├─ Package in CriptMessage      │                                │
        └──────── JSON over TCP ───────>│                                │
                                        │─────── Forward to all ────────>│
                                        │                          ├─ Verify signature
                                        │                          ├─ Update public key
                                        │                          └─ Extract content
                                        │                                │
                                        │                          [Ratchet advanced]
```

### Key Derivation Timeline

```
Initial Chain Key (CK_0)
        │
        ├─ Derive → Message Key 1, Chain Key 1
        │   └─ Sign Message 1 with SSK
        │   └─ Broadcast new ephemeral key
        │
        ├─ Derive → Message Key 2, Chain Key 2
        │   └─ Sign Message 2 with new SSK
        │   └─ Broadcast new ephemeral key
        │
        └─ Continue ratcheting for each message...
```

---

## 🧪 Testing

Run the comprehensive test suite with uv:

```bash
# First sync dependencies
uv sync --group dev

# Run all tests
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=src/cript --cov-report=html

# Specific test file
uv run pytest tests/test_protocol.py -v

# Run examples
uv run python examples/01_basic.py
uv run python examples/02_attacks.py
```

### Test Coverage
- Unit tests for cryptographic primitives
- Protocol state machine tests
- Attack simulation (tampering detection)
- Network layer tests

---

## 📖 Examples

### Basic Example

```python
# examples/basic_messaging.py
from cript.core.protocol import SenderKeysProtocol

sender = SenderKeysProtocol.Sender("Alice")
receiver = SenderKeysProtocol.Receiver("Bob")

# Send message
msg = sender.create_message("Hello, Bob!")
print(f"Sent: {msg.to_json()}")

# Receive and verify
if receiver.verify_message(msg):
    content = receiver.get_decrypted_content(msg)
    print(f"Received: {content}")
```

### Network Example

```python
# examples/network_demo.py
from cript.network.server import CriptServer
from cript.network.client import CriptClient

# Start server
server = CriptServer(port=5000)
# server.start()  # In production thread

# Connect clients
alice = CriptClient("Alicia", "localhost", 5000)
bob = CriptClient("Roberto", "localhost", 5000)

alice.connect()
bob.connect()

# Exchange messages
message = {...}  # CriptMessage as dict
alice.send(message)
received = bob.receive()
```

---

## 🛡️ Security Considerations

### ✅ What This Implementation Protects Against

- **Message Forgery**: Invalid signatures are rejected
- **Message Tampering**: Signature verification detects any modification
- **Replay Attacks**: Sequence numbers should be checked by application
- **Future Compromise**: Old messages remain secure after compromise

### ⚠️ Limitations & Future Work

- **Symmetric Encryption**: Currently uses placeholder; implement AES-GCM for production
- **Key Exchange**: Initial key distribution must use secure out-of-band channel
- **Metadata**: Server can see connection patterns (timing, volume)
- **Perfect Forward Secrecy for Groups**: Requires additional layer for multi-recipient scenarios

---

## 🔧 Deployment

### On Ubuntu Server with Tailscale

```bash
# 1. Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# 2. Authenticate
sudo tailscale up

# 3. Clone and setup CRIPT
git clone https://github.com/alvarofdezr/cript.git
cd cript
pip install .

# 4. Start server
python -m cript.network.server &

# 5. Verify listening on Tailscale IP
netstat -tuln | grep 5000
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install .
CMD ["python", "-m", "cript.network.server"]
```

---

## 📚 References

1. **Balbás, D., Collins, D., & Gajland, P. (2022).** Analysis and Improvements of the Sender Keys Protocol for Group Messaging. XVII RECSI 2022, Santander, 25-30.

2. **Signal Protocol**: https://signal.org/docs/
   - Reference implementation of Double Ratchet for 1-to-1 messaging

3. **NIST Cryptography Standards**: https://csrc.nist.gov/
   - ECDSA specification (FIPS 186-4)
   - SHA256 specification (FIPS 180-4)

4. **RFC 5869**: HMAC-based Extract-and-Expand Key Derivation Function (HKDF)
   - https://tools.ietf.org/html/rfc5869

---

## 📝 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 CRIPT Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
pip install -e ".[dev]"
pre-commit install
```

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/alvarofdezr/cript/issues)
- **Email**: your.email@example.com

---

## 🎯 Roadmap

- [ ] AES-GCM symmetric encryption layer
- [ ] Extended Key Exchange Protocol (EKEP) implementation
- [ ] Multi-recipient group messaging
- [ ] Key directory service
- [ ] Detailed security audit documentation
- [ ] Formal verification of protocol properties
- [ ] Kubernetes deployment guide
- [ ] Web dashboard for monitoring

---

**CRIPT** - Making group messaging cryptography accessible and secure. 🔐
