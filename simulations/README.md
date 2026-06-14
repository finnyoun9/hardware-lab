# Simulations

理论仿真脚本，用 Python + matplotlib 可视化电路行为。

## analog/

| 脚本 | 内容 | 输出 |
|------|------|------|
| `rc_filter.py` | RC 低通滤波器：幅频/相频/瞬态/充电曲线 | ![](images/rc_filter.png) |
| `diode_iv.py` | 1N4148 二极管伏安特性曲线 | ![](images/diode_iv.png) |
| `analog_trilogy.py` | BJT 放大 + 运放电路 + LDO 稳压器 | ![](images/analog_trilogy.png) |

### 运行

```bash
cd ~/Projects/embedded-learning
python3 simulations/analog/rc_filter.py
python3 simulations/analog/diode_iv.py
python3 simulations/analog/analog_trilogy.py
```

输出图片保存在 `simulations/analog/images/`。

### 理论背景

- **RC 低通**：截止频率 fc = 1/(2πRC)，-20dB/decade 滚降，时间常数 τ=RC
- **二极管 I-V**：Shockley 方程 I = Is(e^(V/nVt)−1)，膝点电压 ~0.6V
- **BJT 放大**：共射放大器，Q 点偏置，负载线分析，增益 Av = -gm×Rc
- **运放**：反相/同相/比较器/跟随器四种基本拓扑
- **LDO**：串联稳压，Vout = Vref×(1+R1/R2)，线调整率 <0.1%

## view_wave.py

逻辑分析仪 VCD → PNG 波形图工具。

```bash
sigrok-cli -d fx2lafw --samples 2M -c samplerate=1M --channels D0 -o capture.sr
sigrok-cli -i capture.sr -O vcd -o capture.vcd
python3 simulations/view_wave.py capture.vcd capture.png
```
