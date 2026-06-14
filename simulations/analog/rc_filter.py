#!/usr/bin/env python3
"""
Circuit Simulation — RC Low-Pass Filter
Analog Electronics Lesson 1: Frequency Response + Transient Response
"""
import numpy as np
import matplotlib.pyplot as plt

# ── Circuit Parameters ──
R = 1_000      # 1kΩ
C = 100e-9     # 100nF
fc = 1 / (2 * np.pi * R * C)  # cutoff frequency

# ── Frequency Response (AC Analysis) ──
freq = np.logspace(1, 5, 200)  # 10Hz ~ 100kHz
H = 1 / (1 + 1j * 2 * np.pi * freq * R * C)
gain_db = 20 * np.log10(np.abs(H))
phase = np.angle(H, deg=True)

# ── Transient Response (square wave input) ──
t = np.linspace(0, 0.005, 1000)  # 5ms
vin = 3.3 * (np.sign(np.sin(2 * np.pi * 1000 * t)) > 0)  # 1kHz square wave
vout = np.zeros_like(t)
for i in range(1, len(t)):
    dt = t[i] - t[i-1]
    vout[i] = vout[i-1] + (vin[i] - vout[i-1]) * (1 - np.exp(-dt/(R*C)))

# ── Plot ──
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle(f'RC Low-Pass Filter  |  R = {R/1000:.0f} kΩ  |  C = {C*1e9:.0f} nF  |  fc = {fc:.0f} Hz',
             fontsize=14, fontweight='bold')

# 1. Magnitude (Bode gain plot)
ax = axes[0, 0]
ax.semilogx(freq, gain_db, 'b-', linewidth=1.5)
ax.axvline(fc, color='r', linestyle='--', alpha=0.5, label=f'fc = {fc:.0f} Hz')
ax.axhline(-3, color='gray', linestyle=':', alpha=0.5, label='-3 dB')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Gain (dB)')
ax.set_title('A. Magnitude Response (Bode Gain)')
ax.grid(True, alpha=0.3)
ax.legend(loc='lower left')
ax.set_ylim(-40, 3)

# 2. Phase
ax = axes[0, 1]
ax.semilogx(freq, phase, 'r-', linewidth=1.5)
ax.axvline(fc, color='r', linestyle='--', alpha=0.5)
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Phase (deg)')
ax.set_title('B. Phase Response')
ax.grid(True, alpha=0.3)

# 3. Square wave response
ax = axes[1, 0]
ax.plot(t*1000, vin, 'gray', linewidth=1, alpha=0.5, label='Vin (square wave)')
ax.plot(t*1000, vout, 'b-', linewidth=1.5, label='Vout (RC filtered)')
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Voltage (V)')
ax.set_title('C. Step Response — 1 kHz Square Wave')
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_xlim(0, 3)

# 4. Charging curve detail
ax = axes[1, 1]
tau = R * C
t_detail = np.linspace(0, 5*tau, 200)
v_charge = 3.3 * (1 - np.exp(-t_detail/tau))
ax.plot(t_detail*1000, v_charge, 'b-', linewidth=2, label=f'Charge  (τ = {tau*1e6:.0f} µs)')
ax.axhline(3.3*0.632, color='r', linestyle='--', alpha=0.5, label=f'63.2% @ τ')
ax.axvline(tau*1000, color='r', linestyle=':', alpha=0.5)
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Voltage (V)')
ax.set_title('D. RC Charging Curve')
ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()
plt.savefig('simulations/analog/images/rc_filter.png', dpi=150)
print(f'Done -> simulations/analog/images/rc_filter.png')
print(f'Cutoff frequency  fc = {fc:.0f} Hz')
print(f'Time constant     τ  = {tau*1e6:.0f} µs')
