# Hardware Lab — 嵌入式硬件设计

> 🔧 原理图设计、电路仿真、PCB 打样、器件资料
> 
> KiCad + Python/matplotlib + LTspice

---

## 📂 结构

```
hardware-lab/
├── schematics/          ← KiCad 原理图
│   └── rc-filter/       ← RC 滤波器
├── simulations/         ← 电路仿真（Python）
│   └── analog/          ← 模电仿真
├── pcb/                 ← PCB 设计
│   └── stm32-motor-driver/  ← STM32 电机驱动板
└── README.md
```

## 🔧 工具

| 工具 | 用途 | 路径 |
|------|------|------|
| KiCad 10 | 原理图 + PCB 设计 | `/opt/homebrew/bin/kicad-cli` |
| Python/matplotlib | 电路仿真 | `simulations/` |
| LTspice | SPICE 仿真 | `schematics/` |

## 📖 学习笔记

PCB 设计学习路径：[embedded-notes/notes/PCB设计学习路径-KiCad入门.md](https://github.com/finnyoun9/embedded-notes)

## 🔗 相关仓库

- 🔬 [theory-lab](https://github.com/finnyoun9/theory-lab) — 数电模电理论
- 📚 [embedded-notes](https://github.com/finnyoun9/embedded-notes)
- 🔵 [stm32-from-scratch](https://github.com/finnyoun9/stm32-from-scratch)
