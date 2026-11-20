# ghostmesh/config.py

class Config:
    def __init__(
        self,
        node_id: str = "AUTO_GENERATE",
        heartbeat_freq_hz: float = 1.7,
        enable_traffic_morphing: bool = True,
        encryption_mode: str = "ECC_RSA8192"
    ):
        self.node_id = node_id
        self.heartbeat_freq_hz = heartbeat_freq_hz
        self.enable_traffic_morphing = enable_traffic_morphing
        self.encryption_mode = encryption_mode

    def to_dict(self):
        return {
            "node_id": self.node_id,
            "heartbeat_freq_hz": self.heartbeat_freq_hz,
            "enable_traffic_morphing": self.enable_traffic_morphing,
            "encryption_mode": self.encryption_mode
        }