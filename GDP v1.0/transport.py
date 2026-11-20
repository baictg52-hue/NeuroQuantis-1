# ghostmesh/transport.py
import asyncio
import logging
from .crypto import CryptoEngine

logger = logging.getLogger("GhostMesh.Transport")

class UDPTransportProtocol(asyncio.DatagramProtocol):
    def __init__(self, on_packet_received_callback):
        self.callback = on_packet_received_callback
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        # 1. 剥离或校验多模态流量变形外壳
        unwrapped_data = CryptoEngine.unwrap_traffic_morphing(data)
        if unwrapped_data:
            # 2. 触发上层路由与握手解析
            asyncio.create_task(self.callback(unwrapped_data, addr))

class NetworkTransport:
    def __init__(self, host: str = "0.0.0.0", port: int = 8989):
        self.host = host
        self.port = port
        self.transport = None

    async def start_server(self, callback):
        loop = asyncio.get_running_loop()
        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: UDPTransportProtocol(callback),
            local_addr=(self.host, self.port)
        )
        logger.info(f"[GDP-Transport] UDP 数据传输通道已在 {self.host}:{self.port} 成功开启")

    def send_packet(self, data: bytes, target_addr: tuple):
        if self.transport:
            morphed_packet = CryptoEngine.wrap_traffic_morphing(data)
            self.transport.sendto(morphed_packet, target_addr)

    def stop(self):
        if self.transport:
            self.transport.close()