#!/usr/bin/env python3
"""VCD 波形查看器 — 把逻辑分析仪 VCD 画成专业波形图"""
import sys
import matplotlib.pyplot as plt
import numpy as np

def parse_vcd(path):
    """Parse VCD and return {signal_name: [(time_ns, value), ...]}"""
    signals = {}
    id_to_name = {}
    timescale = 1000  # default ps
    current_time = 0
    
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("$timescale"):
                parts = line.split()
                t = parts[1]
                if "us" in t: timescale = float(t.replace("us","")) * 1e6
                elif "ns" in t: timescale = float(t.replace("ns","")) * 1e3
                elif "ps" in t: timescale = float(t.replace("ps","")) * 1
            elif line.startswith("$var"):
                # $var wire 1 ! D0 $end
                parts = line.split()
                if len(parts) >= 4:
                    ident = parts[3]
                    name = parts[4]
                    id_to_name[ident] = name
                    signals[name] = []
            elif line.startswith("#"):
                # Format: #<time> <value><id> or #<time>
                rest = line[1:].strip()
                parts = rest.split()
                current_time = int(parts[0])
                if len(parts) >= 2:
                    val_id = parts[1]
                    if val_id and val_id[0] in "01xXzZ":
                        value = int(val_id[0]) if val_id[0] in "01" else 0
                        ident = val_id[1]
                        if ident in id_to_name:
                            name = id_to_name[ident]
                            signals[name].append((current_time * timescale / 1e9, value))
    
    return signals

def plot_vcd(path, output=None):
    signals = parse_vcd(path)
    if not signals:
        print("未找到信号")
        return
    
    fig, axes = plt.subplots(len(signals), 1, figsize=(14, 2.5 * len(signals)), sharex=True)
    if len(signals) == 1:
        axes = [axes]
    
    for ax, (name, edges) in zip(axes, signals.items()):
        # Convert edges to step plot
        times = [e[0] for e in edges]
        vals = [e[1] for e in edges]
        ax.step(times, vals, where='post', linewidth=1.5, color='#2196F3')
        ax.set_ylabel(name, fontsize=12, fontweight='bold')
        ax.set_ylim(-0.3, 1.5)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['LOW', 'HIGH'])
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    axes[-1].set_xlabel('Time (seconds)', fontsize=11)
    
    # Add duration annotation
    total = max(e[0] for e in signals[list(signals.keys())[0]])
    fig.suptitle(f'Logic Analyzer Capture — {total:.1f}s', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if output:
        plt.savefig(output, dpi=150, bbox_inches='tight')
        print(f"✅ 已保存: {output}")
    else:
        plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 view_wave.py capture.vcd [output.png]")
        sys.exit(1)
    plot_vcd(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
