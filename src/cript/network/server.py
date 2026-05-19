"""Server implementation for CRIPT message relay"""

import socket
import threading
import json
import logging
from typing import List

logger = logging.getLogger(__name__)


class CriptServer:
    """
    Blind relay server for CRIPT messages.
    
    Properties:
        - Does not inspect message contents
        - Routes messages to all connected clients
        - Runs on configurable host/port
        - Supports concurrent connections
    
    Deployment:
        - Runs on Ubuntu server
        - Behind Tailscale VPN tunnel
        - IPv4 address via Tailscale
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5000): # nosec B104
        """
        Initialize the CRIPT relay server.
        
        Args:
            host: Bind address (0.0.0.0 for all interfaces)
            port: Listening port
        """
        self.host = host
        self.port = port
        self.clients: List[socket.socket] = []
        self.lock = threading.Lock()
        self.running = False
        
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s: %(message)s'
        )
    
    def _handle_client(self, conn: socket.socket, addr: tuple):
        """
        Handle individual client connections.
        
        Args:
            conn: Client socket
            addr: Client address
        """
        logger.info(f"Node connected from: {addr}")
        
        try:
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break
                
                try:
                    payload = json.loads(data.decode('utf-8'))
                    sender = payload.get('sender_name', 'UNKNOWN')
                    has_ratchet = 'next_spk' in payload
                    
                    logger.info(f"Packet from '{sender}' - Ratchet: {'YES' if has_ratchet else 'NO'}")
                    
                    # Blind relay to other clients
                    with self.lock:
                        for client in self.clients:
                            if client != conn:
                                try:
                                    client.sendall(data)
                                except Exception as e:
                                    logger.error(f"Send error: {e}")
                                    if client in self.clients:
                                        self.clients.remove(client)
                
                except json.JSONDecodeError:
                    logger.warning("Received invalid JSON")
                    
        except ConnectionResetError:
            logger.warning(f"Connection reset by {addr}")
        finally:
            with self.lock:
                if conn in self.clients:
                    self.clients.remove(conn)
            conn.close()
            logger.info(f"Connection closed: {addr}")
    
    def start(self):
        """Start the relay server."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(10)
            self.running = True
            
            logger.info(f"CRIPT Server listening on {self.host}:{self.port}")
            
            while self.running:
                conn, addr = server_socket.accept()
                with self.lock:
                    self.clients.append(conn)
                
                thread = threading.Thread(
                    target=self._handle_client,
                    args=(conn, addr),
                    daemon=True
                )
                thread.start()
                
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.running = False
            server_socket.close()
            logger.info("Server stopped")
    
    def stop(self):
        """Stop the server."""
        self.running = False


if __name__ == "__main__":
    server = CriptServer()
    server.start()
