"""Message model for CRIPT protocol"""

from dataclasses import dataclass, asdict
from typing import Optional
import json
import base64


@dataclass
class CriptMessage:
    """
    Represents a CRIPT protocol message in the group messaging context.
    
    Attributes:
        sender_name: Identity of the sender
        ciphertext: Encrypted message content (base64)
        signature: Message authentication code (base64)
        next_spk: Optional ephemeral public key for next ratchet step (base64)
        sequence_number: Message counter for ordering
    """
    sender_name: str
    ciphertext: str
    signature: str
    next_spk: Optional[str] = None
    sequence_number: int = 0
    
    def to_json(self) -> str:
        """Serialize message to JSON for transmission."""
        return json.dumps(asdict(self))
    
    @staticmethod
    def from_json(json_str: str) -> 'CriptMessage':
        """Deserialize message from JSON."""
        data = json.loads(json_str)
        return CriptMessage(**data)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return asdict(self)
