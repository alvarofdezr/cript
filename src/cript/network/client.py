"""Client implementation for CRIPT protocol"""

import socket
import json
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class CriptClient:
    """
    Client for communicating through the CRIPT relay.
    
    Usage:
        client = CriptClient("alicia", "100.120.170.116", 5000)
        message = {...}  # CriptMessage as dict
        client.send(message)
        received = client.receive()
    """
    
    def __init__(self, name: str, server_host: str, server_port: int = 5000):
        """
        Initialize a CRIPT client.
        
        Args:
            name: Client identity
            server_host: Server IP address (Tailscale IP for remote)
            server_port: Server port
        """
        self.name = name
        self.server_host = server_host
        self.server_port = server_port
        self.socket: Optional[socket.socket] = None
        
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s: %(message)s'
        )
    
    def connect(self) -> bool:
        """
        Connect to the CRIPT server.
        
        Returns:
            bool: True if connection successful
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            logger.info(f"[{self.name}] Connected to {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            logger.error(f"[{self.name}] Connection failed: {e}")
            return False
    
    def send(self, message: dict) -> bool:
        """
        Send a message through the relay.
        
        Args:
            message: Message dictionary (CriptMessage)
            
        Returns:
            bool: True if sent successfully
        """
        if not self.socket:
            logger.error(f"[{self.name}] Not connected")
            return False
        
        try:
            payload = json.dumps(message)
            self.socket.sendall(payload.encode('utf-8'))
            logger.info(f"[{self.name}] Message sent")
            return True
        except Exception as e:
            logger.error(f"[{self.name}] Send failed: {e}")
            return False
    
    def receive(self, timeout: float = 1.0) -> Optional[dict]:
        """
        Receive a message from the relay.
        
        Args:
            timeout: Receive timeout in seconds
            
        Returns:
            dict: Message dictionary or None if timeout
        """
        if not self.socket:
            logger.error(f"[{self.name}] Not connected")
            return None
        
        try:
            self.socket.settimeout(timeout)
            data = self.socket.recv(4096)
            
            if data:
                message = json.loads(data.decode('utf-8'))
                logger.info(f"[{self.name}] Message received from {message.get('sender_name')}")
                return message
            
            return None
            
        except socket.timeout:
            return None
        except Exception as e:
            logger.error(f"[{self.name}] Receive error: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from server."""
        if self.socket:
            self.socket.close()
            logger.info(f"[{self.name}] Disconnected")
