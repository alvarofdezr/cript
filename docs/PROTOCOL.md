# Technical Protocol Documentation

## Overview

CRIPT implements the **Sender Keys Protocol** with **Signature Ratcheting** for secure group messaging.

Reference: Balbás, D., Collins, D., & Gajland, P. (2022). Analysis and Improvements of the Sender Keys Protocol for Group Messaging. XVII RECSI 2022.

## Protocol Components

### 1. Elliptic Curve Cryptography (ECDSA)

**Curve**: SECP256R1 (P-256)
- NIST standardized
- 256-bit security level
- Suitable for both signatures and key agreement

**Operations**:
- Key Generation: `(sk, pk) = ECDSA-KeyGen(SECP256R1)`
- Signing: `σ = Sign(sk, m)`
- Verification: `Verify(pk, σ, m) → {True, False}`

### 2. Key Derivation (HKDF)

**Function**: HKDF-SHA256
**Specification**: RFC 5869

```
HKDF(IKM, salt, info, L):
  PRK = HMAC-Hash(salt, IKM)
  OKM = KDF(PRK, info, L)
  return OKM
```

In CRIPT:
```
CK_n = HKDF(CK_{n-1}, salt=∅, info="ChainKey", L=32)
MK_n = HKDF(CK_{n-1}, salt=∅, info="MessageKey", L=32)
```

### 3. Signature Ratcheting

The core mechanism providing forward secrecy.

**State**: `(CK, SSK, SPK)` where:
- `CK`: Chain Key (32 bytes)
- `SSK`: Static Sender Key (private)
- `SPK`: Static Sender Key public component

**Ratchet Operation**:

```
RatchetForward():
  (MK, CK) ← DeriveKeys(CK)
  (new_SSK, new_SPK) ← GenerateECDSAKeypair()
  σ ← Sign(SSK, message)
  SPK_to_send ← current_SPK
  (SSK, SPK) ← (new_SSK, new_SPK)
  return (SPK_to_send, σ, CK)
```

### 4. Message Structure

```json
{
  "sender_name": "Alicia",
  "ciphertext": "base64_encoded_encrypted_data",
  "signature": "base64_encoded_ecdsa_signature",
  "next_spk": "base64_encoded_next_ephemeral_pubkey",
  "sequence_number": 1
}
```

## Security Properties

### Forward Secrecy (FS)

**Definition**: Compromise of long-term keys does not expose past message keys.

**In CRIPT**: 
- Each message uses ephemeral key `SPK_n`
- After use, `SPK_n` is deleted
- Cannot derive `SPK_n` from `SPK_{n+1}`

**Proof Sketch**:
```
If attacker has CK_n, can compute:
  CK_n → MK_n (cannot reverse)
  CK_n → CK_{n+1} (forward direction only)
  
Cannot recover: CK_{n-1}, MK_{n-1}, SPK_{n-1}
```

### Post-Compromise Security (PCS)

**Definition**: After compromise recovery, future messages are secure even if attacker observed all past communication.

**In CRIPT**:
- Ratchet automatically updates on each message
- New `SPK` generated from random
- Old keys not derivable from new state

**Timeline**:
```
Before compromise:  SSK_1 → SSK_2 → SSK_3 ...
                    SPK_1 → SPK_2 → SPK_3 ...

Compromise at t=3: Attacker has SSK_3, CK_3

After compromise:   SSK_4 → SSK_5 ...
                    SPK_4 → SPK_5 ...
                    (Independent random generation)

Result: Messages from SSK_4+ are secure despite SSK_3 compromise
```

### Authentication

**Property**: Only sender with `SSK` can create valid signatures.

**Verification**:
```
Verify(SPK, σ, m):
  if ECDSA_Verify(SPK, σ, m) = True:
    accept message
  else:
    reject and alert (tampering/forgery)
```

## Attack Scenarios

### Scenario 1: Passive Eavesdropping

**Attack**: Attacker reads all traffic but cannot modify

**Protection**: ✓ CRIPT encrypts content (placeholder → implement AES-GCM)

### Scenario 2: Active Tampering

**Attack**: Attacker modifies message ciphertext

```
Original:  msg = (ct, σ)
Tampered:  msg' = (ct', σ)  [σ unchanged]
```

**Result**: Signature verification fails → message rejected

**Evidence**: 
```python
try:
    verify_message(msg')
except InvalidSignature:
    # ALERT: Tampering detected!
    logger.critical("Possible attack")
```

### Scenario 3: Message Forgery

**Attack**: Attacker creates fake message impersonating sender

```
Attacker generates: σ_fake = Sign(SK_attacker, msg_fake)
Claims: "From Alicia"
```

**Result**: Verification with Alicia's `SPK` fails

**Protection**: Only Alicia can create valid signatures with her `SSK`

### Scenario 4: Replay Attack

**Attack**: Attacker resends old message

```
Time 1: Alicia sends "msg1" with seq=1
Time 5: Attacker resends "msg1" with seq=1
```

**Mitigation**: Application checks `sequence_number` field

**Implementation**:
```python
if message.sequence_number <= last_received_sequence:
    raise ReplayAttackError()
last_received_sequence = message.sequence_number
```

### Scenario 5: Key Compromise

**Attack**: Attacker obtains `SSK_n`

**Scope of Compromise**:
- ✗ Can sign messages with `SSK_n`
- ✗ Can decrypt with `MK_n`
- ✓ Cannot recover `SSK_{n-1}` (destroyed)
- ✓ Cannot predict `SSK_{n+1}` (random)

**Recovery**: Continue protocol, automatic ratcheting on next message

## Cryptographic Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Curve | SECP256R1 | NIST standardized, 256-bit security |
| Hash | SHA-256 | FIPS 180-4, collision-resistant |
| Key Size | 256-bit | Protects against birthday attacks |
| HKDF Salt | None | Protocol design allows this |
| Sequence Counter | Uint32 | 4 billion messages per sender |

## Computational Complexity

| Operation | Time | Notes |
|-----------|------|-------|
| Key Generation | ~1-5ms | ECDSA keypair generation |
| Sign | ~1-5ms | ECDSA signature |
| Verify | ~1-5ms | ECDSA verification |
| HKDF Derive | ~0.1-0.5ms | SHA256 based |
| Ratchet Forward | ~5-15ms | Gen keypair + derive + sign |

## Protocol Flow

```
INITIALIZATION (Out-of-band):
  Alicia and Roberto exchange initial public keys
  Alicia generates: (CK_0, SSK_0, SPK_0)

MESSAGE EXCHANGE:

Round 1:
  Alicia: Ratchet → (SPK_0, σ_0, CK_1)
          Send(msg1, σ_0, next_spk=SPK_1)
  Roberto: Verify(SPK_0, σ_0, msg1) ✓
           Update: SPK_0 ← SPK_1

Round 2:
  Alicia: Ratchet → (SPK_1, σ_1, CK_2)
          Send(msg2, σ_1, next_spk=SPK_2)
  Roberto: Verify(SPK_1, σ_1, msg2) ✓
           Update: SPK_1 ← SPK_2

... (continues indefinitely)
```

## Implementation Considerations

### Thread Safety
- Chain key updates must be atomic
- Consider locks for concurrent senders

### Memory Management
- Destroyed keys should be overwritten (avoid string type)
- Consider using `os.urandom()` for secrets

### Constant-Time Operations
- Use cryptography library which provides constant-time verification
- Avoid early returns in verification

### Error Handling
- Never log sensitive material
- Fail-secure on verification failure
- Detailed logging for debugging only

## Future Enhancements

1. **Multi-Recipient**: Extend to true group messaging
2. **Forward Secrecy for Groups**: Per-group chain keys
3. **Perfect Forward Secrecy**: Ephemeral Diffie-Hellman component
4. **Key Transparency**: Commitment to public keys
5. **MLS Compatibility**: Align with IETF Messaging Layer Security

---

**Document Version**: 1.0  
**Last Updated**: May 2026  
**Protocol Version**: 1.0
