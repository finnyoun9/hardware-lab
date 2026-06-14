#!/usr/bin/env python3
"""
Circuit Simulation — Diode I-V Characteristic Curve
Shockley equation:  I = Is * (exp(V / (n*Vt)) - 1)
"""
import numpy as np
import matplotlib.pyplot as plt

# ── Physical Constants ──
k = 1.38e-23     # Boltzmann constant
q = 1.6e-19      # electron charge
T = 300          # room temp (K)
Vt = k * T / q   # thermal voltage ≈ 25.85 mV

# ── 1N4148 Silicon Diode Parameters ──
Is_si = 2.5e-9   # saturation current
n_si  = 1.8      # ideality factor

# ── Ideal Diode for Comparison ──
Is_ideal = 1e-12
n_ideal  = 1.0

# ── Compute I-V ──
Vf = np.linspace(0, 0.85, 500)  # forward 0 ~ 0.85V
Vr = np.linspace(-5, 0, 300)    # reverse 0 ~ -5V
V_all = np.concatenate([Vr, Vf])

def diode_i(V, Is, n):
    return Is * (np.exp(V / (n * Vt)) - 1)

I_si = diode_i(V_all, Is_si, n_si)
I_ideal = diode_i(V_all, Is_ideal, n_ideal)

# ── Find "knee" voltage (where I = 1 mA) ──
V_knee = n_si * Vt * np.log(1e-3 / Is_si + 1)

# ── Plot ──
fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
fig.suptitle(f'1N4148 Diode I-V Characteristic  |  Is = {Is_si*1e9:.1f} nA  |  n = {n_si}  |  Vt = {Vt*1e3:.1f} mV',
             fontsize=13, fontweight='bold')

# A) Forward — Linear Scale
ax = axes[0]
ax.plot(Vf, I_si[300:]*1000, 'b-', linewidth=2, label='1N4148')
ax.plot(Vf, I_ideal[300:]*1000, 'gray', linewidth=1, linestyle='--', alpha=0.5, label='Ideal (n=1)')
ax.axvline(V_knee, color='r', linestyle='--', alpha=0.5, label=f'Knee ≈ {V_knee:.2f}V @ 1mA')
ax.set_xlabel('Forward Voltage Vf (V)')
ax.set_ylabel('Current If (mA)')
ax.set_title('A. Forward I-V (Linear)')
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_xlim(0, 0.85)
ax.set_ylim(0, 30)

# B) Forward — Semi-Log Scale (shows exponential)
ax = axes[1]
ax.semilogy(Vf, I_si[300:]*1000, 'b-', linewidth=2, label='1N4148')
ax.semilogy(Vf, I_ideal[300:]*1000, 'gray', linewidth=1, linestyle='--', alpha=0.5, label='Ideal')
ax.axvline(V_knee, color='r', linestyle='--', alpha=0.5)
ax.set_xlabel('Forward Voltage Vf (V)')
ax.set_ylabel('Current If (mA)')
ax.set_title('B. Forward I-V (Semi-Log) — straight line = exponential')
ax.grid(True, alpha=0.3, which='both')
ax.legend()
ax.set_xlim(0, 0.85)

# C) Full I-V with Reverse
ax = axes[2]
ax.plot(V_all, I_si*1e9, 'b-', linewidth=1.5)
ax.axhline(0, color='gray', linewidth=0.5)
ax.axvline(0, color='gray', linewidth=0.5)
# Annotate regions
ax.annotate('Reverse\n(~0 current)', xy=(-3, -0.02), fontsize=9, ha='center',
            bbox=dict(boxstyle='round', alpha=0.1))
ax.annotate('Forward\n(exponential)', xy=(0.5, 0.15), fontsize=9, ha='center',
            bbox=dict(boxstyle='round', alpha=0.1))
ax.annotate(f'Knee\n{V_knee:.2f}V', xy=(V_knee, 0.5), fontsize=9, ha='center',
            xytext=(V_knee+0.15, 2.5),
            arrowprops=dict(arrowstyle='->', color='r', alpha=0.5), color='r')
ax.set_xlabel('Voltage Vd (V)')
ax.set_ylabel('Current Id (nA)')
ax.set_title('C. Full I-V (Reverse + Forward)')
ax.grid(True, alpha=0.3)
ax.set_xlim(-5, 0.85)
ax.set_ylim(-0.1, 5)

plt.tight_layout()
plt.savefig('simulations/analog/images/diode_iv.png', dpi=150)
print(f'Done -> simulations/analog/images/diode_iv.png')
print(f'Thermal voltage  Vt = {Vt*1e3:.1f} mV')
print(f'Knee voltage     Vk = {V_knee:.2f} V  (where I = 1 mA)')
print(f'Saturation curr  Is = {Is_si*1e9:.1f} nA')
print(f'Ideality factor  n  = {n_si}')
