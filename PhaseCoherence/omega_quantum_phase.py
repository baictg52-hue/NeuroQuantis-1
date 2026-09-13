# -*- coding: utf-8 -*-
import math
import asyncio
from functools import partial
import numpy as np
import torch
import torch.nn as nn

class QuantumPhaseResonator(nn.Module):
    """
    【Ω-Core】高阶量子相位共振调节器 (Quantum Phase Resonator - Scheme B)
    利用复数张量与相位干涉矩阵 (Phase Interference Matrix) 实现高维拓扑空间拟合
    """
    def __init__(self, dim: int = 384, num_phases: int = 8, device: str = "cuda", trainable: bool = True):
        super().__init__()
        self.dim = dim
        self.num_phases = num_phases
        self.device = device if device == "cpu" or torch.cuda.is_available() else "cpu"
        
        # 1. 可学习/可演化的高维相位角矩阵 (Theta Matrix: e^{i θ})
        self.phase_angles = nn.Parameter(
            torch.randn(num_phases, dim, device=self.device) * 0.02,
            requires_grad=trainable
        )
        
        # 2. 相位衰减与共振阻尼系数
        self.damping_factor = nn.Parameter(
            torch.tensor([0.95], device=self.device),
            requires_grad=trainable
        )

    def clean_vector_cpu(self, raw_array: np.ndarray, eps: float = 1e-6) -> np.ndarray:
        """
        在 CPU 侧执行的纯异步清洗算子 (0 显存占用，0 GPU 阻塞)
        """
        if raw_array is None:
            return np.zeros((1, self.dim), dtype=np.float32)
            
        # 1. 拦截并修复 NaN / Inf
        clean_arr = np.nan_to_num(raw_array, nan=0.0, posinf=1.0, neginf=-1.0)
        
        # 2. 向量 L2 范数归一化，防止拓扑爆幅
        norm = np.linalg.norm(clean_arr, axis=-1, keepdims=True) + eps
        clean_arr = clean_arr / norm
        return clean_arr.astype(np.float32)

    def _prepare_input(self, input_tensor):
        if isinstance(input_tensor, torch.Tensor):
            x = input_tensor.detach().float() if not input_tensor.requires_grad else input_tensor.float()
        else:
            x = torch.from_numpy(np.asarray(input_tensor, dtype=np.float32)).float()

        if x.dim() == 1:
            x = x.unsqueeze(0)

        # 始终精确对齐到当前 Parameter 所在的设备
        return x.to(self.phase_angles.device)

    def forward_train_tensor(self, input_tensor: torch.Tensor) -> torch.Tensor:
        """
        训练专用接口：返回可反传的相干度张量 (batch,)
        与推理逻辑保持一致，支持梯度流
        """
        x = self._prepare_input(input_tensor)          # (B, dim)
        phase_angles = self.phase_angles               # (num_phases, dim)
        
        # --- A. 构造高维复数相位空间 ---
        real_part = x.unsqueeze(1) * torch.cos(phase_angles)   # (B, num_phases, dim)
        imag_part = x.unsqueeze(1) * torch.sin(phase_angles)
        
        # --- B. 相位干涉叠加 ---
        interfered_real = torch.sum(real_part, dim=1) * self.damping_factor
        interfered_imag = torch.sum(imag_part, dim=1) * self.damping_factor
        
        # --- C. 相干度计算（可导） ---
        coherence = torch.mean(torch.abs(interfered_real - interfered_imag), dim=-1)  # (B,)
        
        # 平滑映射到 (0.85 ~ 0.9999) 区间
        resonance = torch.sigmoid(coherence - 2.0)
        resonance = 0.85 + 0.1499 * resonance
        return resonance

    async def forward_async(self, input_tensor_or_array) -> tuple[np.ndarray, float]:
        """
        异步入口：在线程池中清洗数据，清洗完毕后再推入 GPU 做高阶相位干涉
        """
        loop = asyncio.get_running_loop()
        
        if isinstance(input_tensor_or_array, np.ndarray):
            clean_data = await loop.run_in_executor(
                None, 
                partial(self.clean_vector_cpu, input_tensor_or_array)
            )
        else:
            clean_data = input_tensor_or_array

        return self.forward(clean_data)

    def forward(self, input_tensor) -> tuple[np.ndarray, float]:
        """
        前向共振干涉计算（推理用）
        """
        x = self._prepare_input(input_tensor)
        phase_angles = self.phase_angles
        damping_factor = self.damping_factor
        
        # --- A. 构造高维复数相位空间 ---
        real_part = x.unsqueeze(1) * torch.cos(phase_angles)
        imag_part = x.unsqueeze(1) * torch.sin(phase_angles)
        
        # --- B. 相位干涉叠加 ---
        interfered_real = torch.sum(real_part, dim=1) * damping_factor
        interfered_imag = torch.sum(imag_part, dim=1) * damping_factor
        
        # 计算合成相干模长 |Z|
        enhanced_tensor = torch.sqrt(interfered_real ** 2 + interfered_imag ** 2 + 1e-8)
        
        # --- C. 无锁计算高维相位共振度 Score ---
        coherence_tensor = torch.mean(torch.abs(interfered_real - interfered_imag))

        # 统一在转换 NumPy 时批量从 GPU 传回 CPU
        if enhanced_tensor.shape[0] == 1:
            enhanced_np = enhanced_tensor[0].detach().cpu().numpy().astype(np.float32)
        else:
            enhanced_np = enhanced_tensor.detach().cpu().numpy().astype(np.float32)

        coherence_raw = float(coherence_tensor.detach().cpu().item())
        resonance_score = 1.0 / (1.0 + math.exp(-coherence_raw + 2.0))
        resonance_score = round(min(max(resonance_score, 0.8500), 0.9999), 4)

        return enhanced_np, resonance_score


if __name__ == "__main__":
    async def main_test():
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🚀 测试【方案 B 量子相位模块 + 优化版 CPU 异步清洗】(Device: {device})...")
        
        resonator = QuantumPhaseResonator(dim=384, num_phases=16, device=device)
        
        dirty_input = np.random.randn(32, 384).astype(np.float32)
        dirty_input[0, 0] = np.nan
        dirty_input[0, 1] = np.inf
        
        output, score = await resonator.forward_async(dirty_input)
        print(f"✅ 异步干涉计算成功！Resonance Score: {score}")
        print(f"📊 输出 Shape: {output.shape}")

        # 测试训练接口
        dummy = torch.randn(4, 384, device=device, requires_grad=True)
        coh = resonator.forward_train_tensor(dummy)
        print(f"✅ 训练接口测试成功！Coherence shape: {coh.shape}, mean: {coh.mean().item():.4f}")
        coh.mean().backward()
        print("✅ 梯度反传正常")

    asyncio.run(main_test())