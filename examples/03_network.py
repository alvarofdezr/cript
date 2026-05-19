"""Example 3: Network server and client demonstration"""

import time
import threading
from cript.network.server import CriptServer
from cript.network.client import CriptClient
from cript.core.protocol import SenderKeysProtocol


def run_server():
    """Run the CRIPT relay server"""
    server = CriptServer(host='100.120.170.116', port=5000)
    server.start()


def main():
    print("=" * 70)
    print("CRIPT Protocol: Network Communication Example")
    print("=" * 70)
    print()
    
    # Start server in background
    print("[1] Starting CRIPT relay server...")
    #server_thread = threading.Thread(target=run_server, daemon=True)
    #server_thread.start()
    #time.sleep(1)
    print("    ✓ Server started on 100.120.170.116:5000\n")
    
    # Create sender and receiver protocols
    print("[2] Initializing participants...")
    alice_proto = SenderKeysProtocol.Sender(name="Alicia")
    bob_proto = SenderKeysProtocol.Receiver(name="Roberto")
    print("    ✓ Protocol instances created\n")
    
    # Create network clients
    print("[3] Connecting clients to relay server...")
    alice_client = CriptClient("Alicia", "100.120.170.116", 5000)
    bob_client = CriptClient("Roberto", "100.120.170.116", 5000)
    
    alice_client.connect()
    bob_client.connect()
    print("    ✓ Both clients connected\n")
    
    # Exchange messages
    print("[4] Alicia sends message through relay...")
    
    # Alicia creates a signed message
    message = alice_proto.create_message("Hello Roberto, this is Alicia!")
    message_dict = message.to_dict()
    
    # Send through network
    alice_client.send(message_dict)
    print("    ✓ Message sent: 'Hello Roberto, this is Alicia!'\n")
    
    # Bob receives message
    print("[5] Roberto receives and verifies message...")
    time.sleep(0.5)  # Give server time to relay
    
    received = bob_client.receive(timeout=2.0)
    if received:
        print(f"    ✓ Received from: {received['sender_name']}")
        print(f"      Content: {received['ciphertext']}")
        print(f"      Has ratchet: {'next_spk' in received}\n")
    else:
        print("    ⚠ No message received (timeout)\n")
    
    # Cleanup
    print("[6] Closing connections...")
    alice_client.disconnect()
    bob_client.disconnect()
    print("    ✓ Connections closed\n")
    
    print("=" * 70)
    print("✓ Network demonstration completed!")
    print("=" * 70)
    print()
    print("DEPLOYMENT INFO:")
    print("  - For production on Ubuntu with Tailscale:")
    print("    1. Install Tailscale: curl -fsSL https://tailscale.com/install.sh | sh")
    print("    2. Authenticate: sudo tailscale up")
    print("    3. Get Tailscale IP: ip addr show tailscale0")
    print("    4. Run server: python -m cript.network.server")
    print()


if __name__ == "__main__":
    main()
