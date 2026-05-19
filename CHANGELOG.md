# CRIPT Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-19

### Added
- Initial release of CRIPT protocol implementation
- ECDSA signature generation and verification (SECP256R1)
- HKDF-SHA256 key derivation (RFC 5869)
- Signature ratcheting mechanism with forward secrecy
- Blind relay server for message routing
- Protocol client for network communication
- Comprehensive test suite (60+ test cases)
- Production-ready deployment guides
- Security audit documentation
- Full API documentation
- Network examples (localhost and Tailscale)
- CI/CD pipeline (GitHub Actions)

### Security
- Forward secrecy: Each message uses ephemeral keys
- Post-compromise security: Automatic ratcheting on each message
- ECDSA authentication: Only legitimate sender can create valid signatures
- Tamper detection: Invalid signatures rejected and alerted

### Documentation
- README with quick start guide
- Protocol technical specification
- Deployment guide for Ubuntu + Tailscale
- Security policy and considerations
- Contributing guidelines
- Architecture diagrams

## [2.0.0] - Planned

### Planned Features
- [ ] AES-256-GCM symmetric encryption
- [ ] Extended Key Exchange Protocol (EKEP)
- [ ] Multi-recipient group messaging
- [ ] Formal security verification
- [ ] Web-based dashboard
- [ ] Kubernetes deployment
- [ ] MLS (Messaging Layer Security) compatibility

### Roadmap
- Security audit by third party
- Performance benchmarks
- Platform-specific optimizations
- Additional test coverage

---

**Note**: This is an academic implementation based on research by Balbás, Collins, and Gajland.
For production use, additional security measures and third-party audits are recommended.
