# SECURITY.md - CRIPT Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in CRIPT, please report it by emailing:
**security@cript-project.dev** (or your actual security contact)

**DO NOT** open a public GitHub issue for security vulnerabilities.

Please provide:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge your report within 48 hours and work to resolve it promptly.

## Security Considerations

### ✅ Secure By Default

- **ECDSA Signatures**: Uses standardized SECP256R1 (P-256) elliptic curve
- **SHA256 Hashing**: Cryptographically secure hash function (FIPS-approved)
- **HKDF Derivation**: Following RFC 5869 specifications
- **Forward Secrecy**: Each message uses ephemeral keys
- **Post-Compromise Security**: Old keys destroyed after ratcheting

### ⚠️ Known Limitations

1. **Symmetric Encryption**: Currently uses placeholder encryption
   - **ACTION**: Implement AES-256-GCM for production deployment
   - **Reference**: NIST SP 800-38D

2. **Key Exchange**: Initial sender keys must be exchanged via secure out-of-band channel
   - **ACTION**: Use X3DH (Extended Triple Diffie-Hellman) for key agreement
   - **Reference**: Signal Protocol documentation

3. **Metadata**: Server can observe connection patterns
   - **MITIGATION**: Deploy over Tailscale or similar VPN for network-level privacy
   - **MITIGATION**: Use onion routing for complete anonymity if required

4. **Replay Attack**: Protocol requires application-level sequence number checks
   - **ACTION**: Implement Lamport timestamps or incrementing counters
   - **VALIDATION**: Check `sequence_number` field in each message

5. **Group Management**: No secure group membership protocol
   - **ROADMAP**: Implement MLS (Messaging Layer Security) subset

### 🔒 Cryptographic Parameters

| Component | Algorithm | Key Size | Notes |
|-----------|-----------|----------|-------|
| Signatures | ECDSA | 256-bit | SECP256R1 curve |
| Hash | SHA-256 | 256-bit | FIPS 180-4 |
| Key Derivation | HKDF | 256-bit | RFC 5869 |
| Symmetric Enc | AES | 256-bit | ⚠️ TODO: Implement |

### 🛡️ Threat Model

#### Adversary Capabilities
- Can read/modify network traffic (unless using Tailscale)
- Can send arbitrary messages
- Can compromise current ephemeral keys

#### Security Guarantees
- **Forward Secrecy**: ✓ Yes (ephemeral keys destroyed)
- **Post-Compromise Security**: ✓ Yes (automatic ratcheting)
- **Message Authentication**: ✓ Yes (ECDSA signatures)
- **Message Confidentiality**: ⚠️ Partial (needs symmetric encryption)
- **Perfect Forward Secrecy**: ⚠️ Partial (with PCS)

### 📋 Security Best Practices

1. **Key Management**
   ```python
   # ✓ DO: Secure key storage
   from cryptography.hazmat.primitives.asymmetric import ec
   private_key = ec.generate_private_key(ec.SECP256R1())
   
   # ✗ DON'T: Hardcode keys
   PRIVATE_KEY = b"super-secret-key"
   ```

2. **Message Verification**
   ```python
   # ✓ DO: Always verify signatures
   from cryptography.exceptions import InvalidSignature
   try:
       receiver.verify_message(message)
   except InvalidSignature:
       # REJECT message - possible tampering
       logger.error("TAMPERING DETECTED")
   
   # ✗ DON'T: Skip verification
   process_message(message)  # INSECURE!
   ```

3. **Sequence Checking**
   ```python
   # ✓ DO: Check sequence numbers
   if message.sequence_number <= last_received:
       # REJECT - potential replay
       raise ReplayAttackError()
   
   # ✗ DON'T: Accept all messages
   process_message(message)  # Vulnerable to replay
   ```

4. **Deployment**
   ```bash
   # ✓ DO: Use Tailscale for secure transport
   sudo tailscale up
   python -m cript.network.server
   
   # ✗ DON'T: Expose server on public internet
   # Server needs TLS/HTTPS in addition to CRIPT
   ```

### 🔄 Security Audit Checklist

- [ ] Code review completed
- [ ] Cryptographic parameters verified
- [ ] Edge cases tested
- [ ] Error handling reviewed
- [ ] Logging doesn't expose secrets
- [ ] Dependencies updated
- [ ] Vulnerability scanning passed

### 📚 References

- **NIST SP 800-186**: Recommendations for Discrete Logarithm-based Cryptography
- **RFC 5869**: HMAC-based Extract-and-Expand Key Derivation Function (HKDF)
- **FIPS 186-4**: Digital Signature Standard (DSS)
- **Signal Protocol**: https://signal.org/docs/
- **Balbás et al. (2022)**: Analysis and Improvements of the Sender Keys Protocol

### 🚨 Security Incident Response

If a security incident occurs:

1. **Immediate Actions**
   - Revoke compromised keys
   - Alert all users
   - Preserve evidence
   - Post-incident review

2. **Communication**
   - Transparency with users
   - Timeline of events
   - Mitigation steps
   - Prevention measures

3. **Recovery**
   - Deploy patched version
   - Key rotation process
   - Verification procedures

---

**Last Updated**: May 2026
**Version**: 1.0.0
