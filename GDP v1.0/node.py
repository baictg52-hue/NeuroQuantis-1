# ghostmesh/node.py
import asyncio
import logging
import json
from .config import Config
from .crypto import CryptoEngine
from .heartbeat import SubPulseHeartbeat
from .transport import NetworkTransport
from .router import RoutingTable

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GhostMesh.Node")

class GDPNode:
    def __init__(self, config: Config = None):
        self.config = config or Config()
        if self.config.node_id == "AUTO_GENERATE":
            self.config.node_id = CryptoEngine.generate_node_id()
        
        self.heartbeat = SubPulseHeartbeat(freq_hz=self.config.heartbeat_freq_hz)
        self.transport = NetworkTransport(port=8989)
        self.router = RoutingTable(node_id=self.config.node_id)

    async def _pulse_callback(self):
        """1.7 Hz 脉冲触发：向局域网广播自身心跳存活状态"""
        active_peers = self.router.get_active_peers()
        logger.debug(f"Node [{self.config.node_id[:12]}...] 脉冲触发 | 当前活跃邻居数: {len(active_peers)}")
        
        # 构造广播包
        payload = json.dumps({
            "sender_id": self.config.node_id,
            "action": "HEARTBEAT_PULSE"
        }).encode('utf-8')
        
        # 通过 UDP 广播至本地子网（可按需调整为多播或已知节点 IP）
        self.transport.send_packet(payload, ('255.255.255.255', 8989))

    def start_discovery(self):
        logger.info(f"[GhostMesh] 正在初始化节点，ID: {self.config.node_id}")
        logger.info(f"[GhostMesh] 加密模式: {self.config.encryption_mode} | 流量变形: {self.config.enable_traffic_morphing}")
        
        try:
            asyncio.run(self._run_async_loop())
        except KeyboardInterrupt:
            logger.info("[GhostMesh] 收到终止信号，节点正在安全离网...")
            self.stop()

    async def _run_async_loop(self):
        # 启动 UDP 传输服务器，并将入站数据包交由路由器处理
        await self.transport.start_server(self.router.handle_incoming_packet)
        # 并发运行 1.7 Hz 心跳广播
        await self.heartbeat.start(self._pulse_callback)

    def stop(self):
        self.heartbeat.stop()
        self.transport.stop()