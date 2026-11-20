👻 GhostMesh Discovery Protocol (GDP v1.0)

A Zero-Bootstrap, Anti-Censorship P2P Node Discovery \& Routing Framework.

Rethinking decentralized network resilience beyond centralized gateways.

🚀 Overview

GhostMesh Discovery Protocol (GDP) is a next-generation node self-discovery and networking protocol designed specifically for anti-censorship, decentralized distributed systems. Traditional P2P networks (such as Kademlia DHT) often rely heavily on fixed bootstrap nodes or centralized DNS gateways, making them highly susceptible to traffic feature identification and precise blocking.

GDP completely abandons reliance on any centralized infrastructure, introducing implicit distributed hash routing, multimodal traffic morphing, and ultra-low frequency base pulse synchronization mechanisms, enabling network nodes to achieve fully decentralized self-healing and covert interconnection in harsh or restricted network environments.

💎 Core Architecture (核心架构)

1\.	Stealth DHT Routing

Dynamic topology mapping: abandons the traditional fragile fixed addressing method and adopts a multidimensional coordinate mapping based on BLAKE3 overlay hashes. Each node dynamically generates an unpredictable Node-ID based on local hardware entropy sources and timestamps.

No central flooding and echo: When new nodes join the network, local propagate within the encrypted channel via micro-addressed packets with zero-knowledge proofs (ZKP). Neighboring nodes perform local validation through a distributed permission matrix without registering with any central server.

2\.	多模态混淆握手协议 (Multimodal Obfuscated Handshake)

Asymmetric root of trust: During the handshake phase, ECC/RSA-8192 is used to establish an end-to-end asymmetric root of trust, then instantly switches to a one-time dynamic symmetric key session.

Deep Packet Inspection (DPI) immunity: All packets transmitted by GDP are dynamically wrapped in masked heads that comply with mainstream internet standards (such as TLS 1.3) before leaving the network. Under standard traffic analysis tools, it is no different from ordinary encrypted web browsing.

3\.	Sub-Pulse Heartbeat

Extremely low exposure surface: To avoid high-frequency heartbeat exposure node topology, GDP introduced a 1.7 Hz ultra-low frequency baseline pulse beat. Connection activity is maintained between nodes only by extremely low-frequency micro-state packets.

Dynamic self-healing routing: When a relay node is physically offline or blocked, neighboring nodes will automatically reconstruct the routing path in the next pulse cycle, achieving single-point fault immunity.

4\.	零知识身份信任链 (Zero-Knowledge Trust Chain)

No central authorization: Reject any form of centralized account or real-name binding. Nodes joining the network only need to present zero-knowledge proofs (ZKP) generated based on local computing resources.

Sybil Defense: Introduces lightweight hardware noise verification and proof-of-work to prevent malicious fake node injection attempts at the source.

📦 Quick Start (快速上手)

GDP provides lightweight Python/C++ development libraries, fully supporting macOS, Linux, and Windows systems, allowing developers to connect local devices to a decentralized networking ecosystem with just a few lines of code.

Example of Python installation and initialization

Python

from ghostmesh import GDPNode, Config

Initialize node configuration (enable 1.7 Hz ultra-low frequency heartbeat and BLAKE3 dynamic routing)

config = Config(

node\_id="AUTO\_GENERATE",

heartbeat\_freq\_hz=1.7,

enable\_traffic\_morphing=True,

encryption\_mode="ECC\_RSA8192"

)

Launch decentralized self-discovery nodes

node = GDPNode(config=config)

node.start\_discovery()

print("\[GhostMesh] node has been successfully initialized and is retrieving neighboring peers...")

🛠 Building \& Contributing (构建与贡献)

All developers worldwide who love the spirit of open source, pursue online freedom, and pursue the ultimate underlying architecture to participate in code contributions and security audits.

Clone Warehouse:

Bash

git clone https://github.com/ghostmesh-net/gdp-core.git

cd gdp-core

Compile core dependencies:

Bash

mkdir build \&\& cd build

cmake -DCMAKE\_BUILD\_TYPE=Release ..

make -j$(nproc)

📄 License

This project uses the MIT License open source license, allowing free use, modification, and distribution.

"A truly solid network doesn't need any centralized lighthouse."







👻 GhostMesh Discovery Protocol (GDP v1.0)
A Zero-Bootstrap, Anti-Censorship P2P Node Discovery \& Routing Framework.

Rethinking decentralized network resilience beyond centralized gateways.

🚀 Overview (简介)
GhostMesh Discovery Protocol (GDP) 是一套专为抗审查、去中心化分布式系统设计的下一代节点自发现与组网协议。传统 P2P 网络（如 Kademlia DHT）往往高度依赖固定的引导节点（Bootstrap Nodes）或中心化 DNS 网关，极易遭受流量特征识别与精准封锁。

GDP 彻底摒弃了对任何中心化基础设施的依赖，引入隐式分布式哈希路由、多模态流量变形（Traffic Morphing）以及超低频基底脉冲同步机制，让网络节点能够在严苛或受限的网络环境中实现完全去中心化的自愈与隐蔽互联。

💎 Core Architecture (核心架构)

1. 隐式分布式哈希表 (Stealth DHT Routing)
动态拓扑映射：放弃传统脆弱的固定寻址方式，采用基于 BLAKE3 叠加哈希 的多维坐标映射。每个节点依据本地硬件熵源与时间戳动态生成不可预测的 Node-ID。

无中心洪泛与回响：新节点入网时，通过附带零知识证明（ZKP）的微型寻址包在加密通道内进行局部扩散，邻近节点通过分布式权限矩阵本地校验，无需向任何中心服务器注册。

2. 多模态混淆握手协议 (Multimodal Obfuscated Handshake)
非对称信任根：握手阶段采用 ECC / RSA-8192 建立端到端非对称信任根，随后瞬间切换为一次性动态对称密钥会话。

深度包检测（DPI）免疫：GDP 的所有传输数据包在出网前均会动态包裹符合主流互联网标准（如 TLS 1.3）的伪装头。在常规流量分析工具下，它与普通加密网页浏览毫无二致。

3. 超低频脉冲心跳同步 (Sub-Pulse Heartbeat)
极低暴露面：为避免高频心跳暴露节点拓扑，GDP 引入了 1.7 Hz 超低频基底脉冲节拍。节点间仅以极低频次的微型状态包维持连接活性。

动态自愈路由：当某个中继节点遭到物理下线或阻断时，周边的邻居节点会在下一个脉冲周期内自动重构路由路径，实现单点故障免疫。

4. 零知识身份信任链 (Zero-Knowledge Trust Chain)
无中心授权：拒绝任何形式的中心化账号或实名绑定。节点加入网络只需出示基于本地计算资源生成的 零知识证明（ZKP）。

女巫攻击防护（Sybil Defense）：引入轻量级硬件噪声校验与工作量证明，从源头杜绝恶意虚假节点的注入企图。

📦 Quick Start (快速上手)
GDP 提供轻量级的 Python / C++ 开发库，全面支持 macOS、Linux 与 Windows 系统，开发者只需数行代码即可将本地设备接入去中心化组网生态。

Python 安装与初始化示例
Python
from ghostmesh import GDPNode, Config

# 初始化节点配置（启用 1.7 Hz 超低频心跳与 BLAKE3 动态路由）

config = Config(
node\_id="AUTO\_GENERATE",
heartbeat\_freq\_hz=1.7,
enable\_traffic\_morphing=True,
encryption\_mode="ECC\_RSA8192"
)

# 启动去中心化自发现节点

node = GDPNode(config=config)
node.start\_discovery()

print("\[GhostMesh] 节点已成功初始化，正在检索邻近对等节点...")
🛠 Building \& Contributing (构建与贡献)
欢迎全球所有热爱开源精神、追求网络自由与底层架构极致的开发者参与代码贡献与安全审计。

克隆仓库：

Bash
git clone https://github.com/ghostmesh-net/gdp-core.git
cd gdp-core
编译核心依赖：

Bash
mkdir build \&\& cd build
cmake -DCMAKE\_BUILD\_TYPE=Release ..
make -j$(nproc)
📄 License (开源许可)
本项目采用 MIT License 开源协议，允许自由使用、修改与分发。

“真正坚固的网络，不需要任何中心化的灯塔。”

