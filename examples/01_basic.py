"""Example 1: Basic sender and receiver demonstration"""

from cript.core.protocol import SenderKeysProtocol
from cript.crypto.ratchet import SignatureRatchet
from cryptography.exceptions import InvalidSignature


def main():
    print("=" * 60)
    print("CRIPT Protocol: Basic Sender-Receiver Example")
    print("=" * 60)
    print()
    
    # 1. Initialize sender
    print("[1] Initializing Sender (Alicia)...")
    sender = SenderKeysProtocol.Sender(name="Alicia")
    print(f"    ✓ Sender ready: {sender.export_state()}")
    print()
    
    # 2. Initialize receiver
    print("[2] Initializing Receiver (Roberto)...")
    receiver = SenderKeysProtocol.Receiver(name="Roberto")
    print(f"    ✓ Receiver ready: {receiver.export_state()}")
    print()
    
    # 3. Create and sign messages
    print("[3] Alicia sends messages...")
    messages = []
    for i in range(3):
        content = f"Secure message #{i+1} from Alicia"
        msg = sender.create_message(content)
        messages.append(msg)
        print(f"    ✓ Message {i+1} created and signed")
        print(f"      - Sequence: {msg.sequence_number}")
        print(f"      - Signature length: {len(msg.signature)}")
        print()
    
    # 4. Register sender at receiver
    print("[4] Roberto registers Alicia...")
    ratchet = SignatureRatchet()
    initial_spk_der = ratchet.export_public_key(sender.ratchet.spk)
    receiver.register_sender("Alicia", initial_spk_der)
    print(f"    ✓ Alicia registered. State: {receiver.export_state()}")
    print()
    
    # 5. Verify messages
    print("[5] Roberto verifies incoming messages...")
    for i, msg in enumerate(messages):
        try:
            is_valid = receiver.verify_message(msg)
            if is_valid:
                content = receiver.get_decrypted_content(msg)
                print(f"    ✓ Message {i+1} verified: {content}")
            else:
                print(f"    ✗ Message {i+1} verification failed")
        except InvalidSignature:
            print(f"    ✗ Message {i+1} INVALID SIGNATURE - TAMPERING DETECTED!")
    
    print()
    print("=" * 60)
    print("✓ Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
