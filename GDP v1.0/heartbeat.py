# ghostmesh/heartbeat.py
import asyncio
import logging

logger = logging.getLogger("GhostMesh.Heartbeat")

class SubPulseHeartbeat:
    def __init__(self, freq_hz: float = 1.7):
        self.freq_hz = freq_hz
        self.interval = 1.0 / freq_hz if freq_hz > 0 else 0.588
        self._is_running = False

    async def start(self, callback):
        self._is_running = True
        logger.info(f"[GDP] 1.7 Hz 超低频脉冲心跳引擎已激活 (Interval: {self.interval:.3f}s)")
        while self._is_running:
            await asyncio.sleep(self.interval)
            try:
                await callback()
            except Exception as e:
                logger.error(f"[GDP] 心跳脉冲同步异常: {e}")

    def stop(self):
        self._is_running = False