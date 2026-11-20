# ghostmesh/router.py
import json
import logging
import time

logger = logging.getLogger("GhostMesh.Router")

class RoutingTable:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.routes = {}  # 结构: { peer_id: {"addr": (ip, port), "last_seen": timestamp, "session_key": ...} }

    def update_route(self, peer_id: str, addr: tuple):
        """注册或更新邻居节点路由信息"""
        if peer_id == self.node_id:
            return  # 忽略自身
        
        is_new = peer_id not in self.routes
        self.routes[peer_id] = {
            "addr": addr,
            "last_seen": time.time(),
            "status": "SECURE_CONNECTED"
        }
        
        if is_new:
            logger.info(f"[GDP-Router] 发现并注册新邻居节点 ➔ ID: {peer_id[:16]}... | 地址: {addr}")
        else:
            logger.debug(f"[GDP-Router] 刷新邻居路由心跳 ➔ ID: {peer_id[:16]}...")

    async def handle_incoming_packet(self, raw_data: bytes, addr: tuple):
        """解析入站的分布式协议数据包"""
        try:
            packet = json.loads(raw_data.decode('utf-8'))
            sender_id = packet.get("sender_id")
            action = packet.get("action")

            if action in ["HEARTBEAT_PULSE", "HANDSHAKE_INIT"]:
                self.update_route(sender_id, addr)
                
        except Exception as e:
            logger.error(f"[GDP-Router] 无法解析入站数据包: {e}")

    def get_active_peers(self):
        """获取当前所有活跃邻居节点"""
        current_time = time.time()
        # 清理超过 3 秒未响应的死链接
        self.routes = {pid: info for pid, info in self.routes.items() if current_time - info["last_seen"] < 3.0}
        return self.routes