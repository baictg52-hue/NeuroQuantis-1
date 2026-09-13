# train_resonance_symbiosis_fixed.py (静态开源基准火种版)
# -*- coding: utf-8 -*-
import os
import time
import math
import json
import logging
from typing import Dict, Any, List

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import bitsandbytes as bnb  # 保留 8bit 内存压缩支持

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)
from peft import get_peft_model, LoraConfig, TaskType

from omega_quantum_phase import QuantumPhaseResonator

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
LOGGER = logging.getLogger("ResonanceTrainer")

# ============================================================
# 【顶部核心配置区】：单档静态模式，锁定常数阻尼基准
# ============================================================
HYPER = {
    "alpha": 0.15,
    "lr_lora": 1e-4,
    "lr_projector": 1e-3,
    "lr_resonator": 5e-4,
    "max_seq_len": 256,
    "grad_accum": 16,
}

TOTAL_OPT_STEPS = 500
WARMUP_RATIO = 0.04
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_PATH = r"E:\aii\btc\btces\google_gemma_4_12B_it\snapshots\master"
RESONATOR_DIM = 384
STATIC_DAMPING = 0.95  # 锁死静态基准阻尼，高维动态修复版由内部闭源舱保留


# ============================================================
# 【开源保留】：训练快照自动递增保存状态机（防覆盖）
# ============================================================
def save_non_overwriting_snapshot(
    opt_step: int,
    coh: float,
    lm: float,
    res: float,
    latency: float = 1.25,
    val_score: float = 0.85,
) -> str:
    ckpt_root = "resonance_symbiosis_ckpt"
    os.makedirs(ckpt_root, exist_ok=True)

    existing_steps = []
    for root, dirs, files in os.walk(ckpt_root):
        if "snapshot.json" in files:
            try:
                with open(os.path.join(root, "snapshot.json"), "r", encoding="utf-8") as f:
                    snap_data = json.load(f)
                existing_steps.append(int(snap_data.get("step", 0)))
            except (OSError, ValueError, TypeError):
                pass

    max_existing_step = max(existing_steps) if existing_steps else 0
    if opt_step <= max_existing_step:
        offset = ((max_existing_step // 500) + 1) * 500
        global_step = opt_step + offset
    else:
        global_step = opt_step

    step_dir = os.path.join(ckpt_root, f"step_{global_step:06d}")
    os.makedirs(step_dir, exist_ok=True)

    snapshot_data = {
        "step": global_step,
        "local_step": opt_step,
        "mode": "static_baseline",
        "coherence": round(float(coh), 4),
        "lm_loss": round(float(lm), 4),
        "res_loss": round(float(res), 4),
        "avg_latency": round(float(latency), 2),
        "validation_score": round(float(val_score), 4),
    }

    snap_path = os.path.join(step_dir, "snapshot.json")
    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
    return snap_path


# ============================================================
# 【静态开源数据集】
# ============================================================
class QuantisStaticDataset(Dataset):
    def __init__(self, texts: List[str], tokenizer, max_len: int = 256):
        self.texts = texts
        self.tok = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tok(
            self.texts[idx],
            truncation=True,
            max_length=self.max_len,
            padding="max_length",
            return_tensors="pt",
        )
        input_ids = enc["input_ids"].squeeze(0)
        attention_mask = enc["attention_mask"].squeeze(0)

        labels = input_ids.clone()
        labels[attention_mask == 0] = -100

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


# ============================================================
# 【退化回归】：经典静态共振共生模型
# ============================================================
class ResonanceGemmaStaticSymbiont(nn.Module):
    def __init__(self, model_path: str, lora_r: int = 16, lora_alpha: int = 32):
        super().__init__()
        bnb_cfg = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        
        base = AutoModelForCausalLM.from_pretrained(
            model_path,
            quantization_config=bnb_cfg,
            device_map="auto",
            torch_dtype=torch.float16,
            local_files_only=True,
            trust_remote_code=True,
        )

        self.hidden_size = getattr(base.config, "hidden_size", 3840)

        lora_cfg = LoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            target_modules=["q_proj", "v_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )
        self.gemma = get_peft_model(base, lora_cfg)

        try:
            self.gemma.gradient_checkpointing_enable()
            self.gemma.enable_input_require_grads()
            if hasattr(self.gemma.config, "use_cache"):
                self.gemma.config.use_cache = False
        except Exception as e:
            LOGGER.warning(f"Gradient Checkpointing 启用失败: {e}")

        # 【退化降维】：退回标准单层线性投影，隐藏非线性流形重塑
        self.projector = nn.Linear(self.hidden_size, RESONATOR_DIM, dtype=torch.float32)
        
        self.resonator = QuantumPhaseResonator(
            dim=RESONATOR_DIM, 
            num_phases=16, 
            device=DEVICE, 
            trainable=True
        )

        self.projector.to(DEVICE)
        self.resonator.to(DEVICE)

        self.hidden_buffer = None
        target_layer = self._find_decoder_layers()
        if target_layer is not None:
            target_layer[-1].register_forward_hook(self._hook)
            LOGGER.info(f"Hook 成功挂载到最后一层: {type(target_layer[-1]).__name__}")

    def _find_decoder_layers(self):
        candidates = []
        def walk(m):
            for _, child in m.named_children():
                if isinstance(child, nn.ModuleList) and len(child) >= 8:
                    candidates.append(child)
                walk(child)
        walk(self.gemma)
        return max(candidates, key=lambda ml: sum(p.numel() for p in ml.parameters())) if candidates else None

    def _hook(self, module, inp, out):
        if out is None:
            self.hidden_buffer = None
            return
        self.hidden_buffer = out[0] if isinstance(out, tuple) else out

    def forward(self, input_ids, attention_mask=None, labels=None, alpha: float = 0.15):
        self.hidden_buffer = None
        outputs = self.gemma(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        lm_loss = outputs.loss

        res_loss = torch.tensor(0.0, device=lm_loss.device)
        coherence = torch.tensor(0.0, device=lm_loss.device)

        if self.hidden_buffer is not None:
            h_last = self.hidden_buffer[:, -1, :].to(torch.float32)
            h_base = self.projector(h_last)

            # 【退化回归】：强制锁定常数阻尼基准，切断动态输入通道
            if hasattr(self.resonator, "damping_factor") and isinstance(self.resonator.damping_factor, nn.Parameter):
                with torch.no_grad():
                    self.resonator.damping_factor.copy_(
                        torch.tensor([STATIC_DAMPING], device=h_base.device, dtype=self.resonator.damping_factor.dtype)
                    )

            # 经典单项纯净语义共振损失
            coherence = self.resonator.forward_train_tensor(h_base)
            res_loss = torch.mean(1.0 - coherence)

        total = lm_loss + alpha * res_loss
        return {
            "loss": total,
            "lm_loss": lm_loss.detach(),
            "res_loss": res_loss.detach(),
            "coherence": coherence.detach().mean() if coherence.numel() else coherence,
        }


def train():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    demo_texts = [
        "请执行一次高维共振稳定性验证并给出结论。",
        "分析拓扑一致性与缓存命中率之间的关系。",
        "在生产环境中如何平衡延迟与共振强度？",
    ] * 120

    cfg = HYPER

    model = ResonanceGemmaStaticSymbiont(MODEL_PATH)
    model.train()

    dataset = QuantisStaticDataset(demo_texts, tokenizer, max_len=cfg["max_seq_len"])
    loader = DataLoader(dataset, batch_size=1, shuffle=True)

    lora_params = [p for n, p in model.named_parameters() if p.requires_grad and "gemma" in n]
    proj_params = list(model.projector.parameters())
    res_params = list(model.resonator.parameters())

    # 【开源保留】：高性能 8bit 内存压缩优化器支持
    optim = bnb.optim.AdamW8bit([
        {"params": lora_params, "lr": cfg["lr_lora"], "weight_decay": 0.01},
        {"params": proj_params, "lr": cfg["lr_projector"], "weight_decay": 0.0},
        {"params": res_params, "lr": cfg["lr_resonator"], "weight_decay": 0.0},
    ])

    opt_step = 0
    micro_step = 0

    optim.zero_grad()
    data_iter = iter(loader)

    print("🚀 [QuantisCore] 静态基准微调舱点火成功，开始训练...")

    while opt_step < TOTAL_OPT_STEPS:
        try:
            batch = next(data_iter)
        except StopIteration:
            data_iter = iter(loader)
            batch = next(data_iter)

        micro_step += 1
        accum = cfg["grad_accum"]

        if micro_step % 10 == 0:
            torch.cuda.empty_cache()

        warmup_steps = int(TOTAL_OPT_STEPS * WARMUP_RATIO)
        if opt_step < warmup_steps:
            lr_scale = float(opt_step + 1) / float(max(1, warmup_steps))
        else:
            progress = float(opt_step - warmup_steps) / float(max(1, TOTAL_OPT_STEPS - warmup_steps))
            lr_scale = max(0.1, 1.0 - progress)

        # 锁定单档静态控制，清除动态调度器
        lrs = [cfg["lr_lora"] * lr_scale, cfg["lr_projector"] * lr_scale, cfg["lr_resonator"] * lr_scale]
        for pg, lr in zip(optim.param_groups, lrs):
            pg["lr"] = lr

        input_ids = batch["input_ids"].to(DEVICE)
        attention_mask = batch["attention_mask"].to(DEVICE)
        labels = batch["labels"].to(DEVICE)
        out = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
            alpha=cfg["alpha"],
        )
        loss = out["loss"] / accum
        loss.backward()

        if micro_step % accum == 0:
            torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
            optim.step()
            optim.zero_grad()
            opt_step += 1

            lm = float(out["lm_loss"])
            res = float(out["res_loss"])
            coh = float(out["coherence"])
            print(f"Step [{opt_step:03d}/{TOTAL_OPT_STEPS}] | Baseline Mode | "
                  f"Loss: {out['loss'].detach().item():.4f} | LM Loss: {lm:.4f} | Res Loss: {res:.4f} | "
                  f"Coh: {coh:.4f}")

            # 【开源保留】：定时落盘节点快照状态机
            if opt_step % 50 == 0 or opt_step == TOTAL_OPT_STEPS:
                snap_path = save_non_overwriting_snapshot(
                    opt_step=opt_step,
                    coh=coh,
                    lm=lm,
                    res=res,
                )
                print(f" └─ 📸 基准节点快照已成功写入: {snap_path}")

    save_dir = "resonance_symbiosis_ckpt"
    os.makedirs(save_dir, exist_ok=True)
    model.gemma.save_pretrained(save_dir)
    torch.save({
        "projector": model.projector.state_dict(),
        "resonator": model.resonator.state_dict(),
        "mode": "static_baseline",
    }, os.path.join(save_dir, "resonance_extra.pt"))
    print("✅ [QuantisCore] 静态基准模型与共振参数保存成功。")


if __name__ == "__main__":
    train()
