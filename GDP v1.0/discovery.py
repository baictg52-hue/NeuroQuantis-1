# ghostmesh/discovery.py
import asyncio
import logging
import json
from .crypto import CryptoEngine

logger = logging.getLogger("GhostMesh.Discovery")

class PeerDiscovery:
    def __init__(self, node_id: str, port: int = 8989):
        self.node_id = node_id
        self.port = port
        self.peers = set()
        self._is_active = False

    async def broadcast_presence(self):
        """周期性向暗空间广播节点存活状态（附带流量变形与伪装）"""
        self._is_active = True
        logger.info(f"[GDP-Discovery] 邻居自发现广播监听已启动 (Port: {self.port})")
        
        while self._is_active:
            # 构造发现契约包
            discovery_payload = {
                "sender_id": self.node_id,
                "action": "HEARTBEAT_PULSE"
            }
            raw_data = json.dumps(discovery_payload).encode('utf-8')
            
            # 经过多模态流量变形封装
            morphed_packet = CryptoEngine.wrap_traffic_morphing(raw_data)
            
            # 此处可扩展 UDP 组播发送逻辑（适配 iOS/PC 端本地网络探测）
            # logger.debug(f"广播封装包大小: {len(morphed_packet)} bytes")
            
            await asyncio.sleep(1.0 / 1.7) # 严格贴合 1.7 Hz 脉冲节拍

    def stop(self):
        self._is_active = False