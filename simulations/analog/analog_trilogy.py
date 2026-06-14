#!/usr/bin/env python3
"""
Analog Electronics Trilogy:
  1. BJT Common-Emitter Amplifier (2N2222)
  2. Op-Amp Circuits (LM358)
  3. LDO Linear Voltage Regulator
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# ═══════════════════════════════════════════════════════════
# PART 1: BJT Common-Emitter Amplifier
# ═══════════════════════════════════════════════════════════

# Circuit: fixed bias common-emitter
#         Vcc = 12V
#          │
#         Rc (2.2k)
#          ├── Vout
#         Q1 (2N2222, β≈200)
#          │
#         Rb (100k)
#          │
#         Vin (AC + DC bias)

# Transistor model (simplified Ebers-Moll / load-line analysis)
beta = 200        # current gain
Vbe_on = 0.7      # base-emitter turn-on
Vcc = 12.0        # supply
Rc = 2200         # collector resistor
Rb = 100_000      # base resistor
Vbb = 2.0         # base bias voltage (from divider or signal DC offset)

# DC operating point (Q-point)
Ib = max(0, (Vbb - Vbe_on) / Rb)
Ic = beta * Ib
Vce = Vcc - Ic * Rc

# Load line
Ic_max = Vcc / Rc
Vce_range = np.linspace(0, Vcc, 200)
Ic_loadline = (Vcc - Vce_range) / Rc

# AC small-signal: Vin = Vbb + 50mV*sin(2π*1kHz*t), 5 cycles
Vt = 0.02585  # thermal voltage
gm = Ic / Vt  # transconductance
rpi = beta / gm
Av = -gm * Rc  # voltage gain (negative = inverting!)

t = np.linspace(0, 5e-3, 500)
vin = Vbb + 0.05 * np.sin(2 * np.pi * 1000 * t)
ib = np.maximum(0, (vin - Vbe_on) / Rb)
ic = beta * ib
vout = Vcc - ic * Rc

# ═══════════════════════════════════════════════════════════
# PART 2: Op-Amp Circuits
# ═══════════════════════════════════════════════════════════

t_opamp = np.linspace(0, 4e-3, 400)
vin_sine = 0.5 * np.sin(2 * np.pi * 500 * t_opamp)

# A) Inverting amplifier:  Vo = -(Rf/Ri) * Vin
# Ri=10k, Rf=22k → gain = -2.2
Ri, Rf = 10_000, 22_000
gain_inv = -Rf/Ri
vout_inv = gain_inv * vin_sine

# B) Non-inverting amplifier:  Vo = (1 + Rf/Ri) * Vin
gain_noninv = 1 + Rf/Ri
vout_noninv = gain_noninv * vin_sine

# C) Comparator (open-loop, no feedback)
vref = 0.1  # reference voltage
vout_comp = np.where(vin_sine > vref, 3.3, 0)

# D) Voltage follower (buffer): Vo = Vin
vout_buf = vin_sine

# ═══════════════════════════════════════════════════════════
# PART 3: LDO Linear Regulator
# ═══════════════════════════════════════════════════════════

#   Vin(5-12V) → TIP122(series pass) → Vout(target 3.3V)
#                      ↑
#                LM358(error amp)←──┬── Vout
#                      ↑           R1 (divider)
#                 Vref(1.25V)       │
#                                   R2
#                                   GND

Vout_target = 3.3
Vref = 1.25
R1_ldo, R2_ldo = 10_000, 6_100  # Vout = Vref*(1+R1/R2) ≈ 3.3V

def ldo_vout(Vin, Iload=0.1, Vdropout=0.8):
    """Simulate LDO: output follows target until dropout"""
    if Vin < Vout_target + Vdropout:
        return Vin - Vdropout
    else:
        return Vout_target * (1 - 0.001 * Iload * 10)  # tiny load regulation

Vin_sweep = np.linspace(2, 10, 200)
vout_ldo = [ldo_vout(v) for v in Vin_sweep]
vout_ldo_heavy = [ldo_vout(v, Iload=0.5) for v in Vin_sweep]

# ═══════════════════════════════════════════════════════════
# PLOT
# ═══════════════════════════════════════════════════════════

fig = plt.figure(figsize=(16, 12))
gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.35)

# ── Row 1: BJT Amplifier ──
fig.suptitle('Analog Electronics: BJT Amplifier  ·  Op-Amp  ·  LDO Regulator',
             fontsize=15, fontweight='bold', y=0.98)

# 1A: Load line + Q-point
ax = fig.add_subplot(gs[0, 0])
ax.plot(Vce_range, Ic_loadline*1000, 'orange', linewidth=1.5, label='Load line')
ax.plot(Vce, Ic*1000, 'ro', markersize=8, label=f'Q ({Vce:.1f}V, {Ic*1000:.1f}mA)')
ax.set_xlabel('Vce (V)')
ax.set_ylabel('Ic (mA)')
ax.set_title(f'A. DC Load Line & Q-Point  |  β={beta}')
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_xlim(0, Vcc)
ax.set_ylim(0, Ic_max*1000*1.1)

# 1B: AC amplifier waveforms
ax = fig.add_subplot(gs[0, 1])
ax.plot(t*1000, vin, 'gray', linewidth=1, alpha=0.6, label='Vin (DC + 50mV AC)')
ax.plot(t*1000, vout, 'b-', linewidth=1.5, label='Vout (amplified & inverted)')
# Annotate: ΔVin vs ΔVout
ax.annotate('50mV swing\ninput', xy=(1.25, Vbb+0.02), fontsize=8, color='gray')
ax.annotate(f'{abs(Av*50):.0f}mV swing\noutput (Gain={abs(Av):.1f}x)',
            xy=(1.25, Vce-Av*0.05*0.7), fontsize=8, color='blue')
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Voltage (V)')
ax.set_title(f'B. AC Amplification  |  Av = {Av:.1f}x  (inverting)')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=8)
ax.set_xlim(0, 3)

# 1C: Gain vs frequency (idealized - single pole from Miller)
ax = fig.add_subplot(gs[0, 2])
freq_bode = np.logspace(1, 8, 200)
# Simplified single-pole: ft = 300MHz for 2N2222
ft = 300e6
Av_freq = Av / np.sqrt(1 + (freq_breadth := freq_bode / (ft/abs(Av)))**2)
# Actually simpler:
pole = ft / abs(Av)
Av_mag = abs(Av) / np.sqrt(1 + (freq_bode/pole)**2)
ax.semilogx(freq_bode, 20*np.log10(Av_mag), 'b-', linewidth=1.5)
ax.axhline(20*np.log10(abs(Av)), color='gray', linestyle=':', alpha=0.5, label=f'Mid-band {abs(Av):.1f}x')
ax.axhline(-3 + 20*np.log10(abs(Av)), color='r', linestyle='--', alpha=0.5, label=f'{pole/1e6:.0f} MHz BW')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Gain (dB)')
ax.set_title('C. Frequency Response (simplified)')
ax.grid(True, alpha=0.3, which='both')
ax.legend(fontsize=8)
ax.set_ylim(-20, 20*np.log10(abs(Av))+5)

# ── Row 2: Op-Amp Circuits ──

# 2A: Inverting vs Non-inverting
ax = fig.add_subplot(gs[1, 0])
ax.plot(t_opamp*1000, vin_sine, 'gray', linewidth=1, alpha=0.5, label=f'Vin (±0.5V)')
ax.plot(t_opamp*1000, vout_inv, 'r-', linewidth=1.5, label=f'Inverting (G={gain_inv:.1f})')
ax.plot(t_opamp*1000, vout_noninv, 'b-', linewidth=1.5, label=f'Non-Invert (G={gain_noninv:.1f})')
ax.axhline(0, color='gray', linewidth=0.5)
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Voltage (V)')
ax.set_title(f'D. Inverting vs Non-Inverting Amp')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=7.5)
ax.set_xlim(0, 4)

# 2B: Comparator
ax = fig.add_subplot(gs[1, 1])
ax.plot(t_opamp*1000, vin_sine, 'gray', linewidth=1, alpha=0.5, label=f'Vin')
ax.plot(t_opamp*1000, vout_comp, 'r-', linewidth=1.5, drawstyle='steps-post', label=f'Comparator')
ax.axhline(vref, color='g', linestyle='--', alpha=0.5, label=f'Vref = {vref}V')
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Voltage (V)')
ax.set_title(f'E. Comparator (open-loop)')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=8)
ax.set_xlim(0, 4)
ax.set_ylim(-0.2, 3.6)

# 2C: Circuit symbols comparison
ax = fig.add_subplot(gs[1, 2])
ax.axis('off')
circuits = """
Op-Amp Building Blocks:

INVERTING:          NON-INVERTING:
   Rf(22k)             Rf(22k)
  ┌──/\\/\\──┐          ┌──/\\/\\──┐
  │  ┌───┐ │          │  ┌───┐ │
Vi─R1─┤-  ├─Vo     Vi─┤+  ├─Vo
 10k  │   │            │   │
GND───┤+  │         ┌─┤-  │
      └───┘         │ └───┘
                    R1(10k)→GND

Vo/Vi = -Rf/Ri      Vo/Vi = 1+Rf/Ri
     = -2.2x             = 3.2x

COMPARATOR (no Rf):  FOLLOWER (Rf=0):
Vi──┤+  ├─Vo(rail)   Vi──┤+  ├─Vo=Vi
    │   │                │   │
Vref┤-  │             ┌──┤-  │
    └───┘             │  └───┘
                      └──Vo──┘
"""
ax.text(0.05, 0.95, circuits, transform=ax.transAxes, fontsize=8,
        fontfamily='monospace', verticalalignment='top',
        bbox=dict(boxstyle='round', alpha=0.05))

# ── Row 3: LDO Regulator ──

# 3A: LDO output vs input
ax = fig.add_subplot(gs[2, 0])
ax.plot(Vin_sweep, vout_ldo, 'b-', linewidth=1.5, label='Light load (100mA)')
ax.plot(Vin_sweep, vout_ldo_heavy, 'r--', linewidth=1.5, label='Heavy load (500mA)')
ax.axhline(Vout_target, color='g', linestyle=':', alpha=0.5, label=f'{Vout_target}V target')
dropout = Vout_target + 0.8
ax.axvline(dropout, color='orange', linestyle='--', alpha=0.5, label=f'Dropout ≈ {dropout:.1f}V')
# Region labels
ax.fill_between([2, dropout], 0, 5, alpha=0.05, color='red')
ax.text(2.5, 4.5, 'Dropout\nRegion', fontsize=9, ha='center', color='red', alpha=0.6)
ax.fill_between([dropout, 10], 0, 5, alpha=0.05, color='green')
ax.text(7, 4.5, 'Regulation\nRegion', fontsize=9, ha='center', color='green', alpha=0.6)
ax.set_xlabel('Input Voltage Vin (V)')
ax.set_ylabel('Output Voltage Vout (V)')
ax.set_title('G. LDO: Line Regulation')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=7.5)
ax.set_xlim(2, 10)
ax.set_ylim(0, 5)

# 3B: LDO block diagram
ax = fig.add_subplot(gs[2, 1])
ax.axis('off')
ldo_diagram = """
SERIES LINEAR REGULATOR (LDO)

 Vin ──────┬──[ TIP122 ]──┬── Vout
           │  Pass Trans   │
           │     ↑         │
           │  [LM358]      ├── R1 ──┬── Vfb
           │  Error Amp    │         │
           │     ↑         │         R2
           │  Vref=1.25V   │         │
           │  (Zener 5.1V  │        GND
           │   + divider)  │
           │               │
          GND             GND

  Vout = Vref × (1 + R1/R2)
       = 1.25 × (1 + 10k/6.1k)
       ≈ 3.3V

  Line Regulation:  ΔVout/ΔVin ≈ 0.1%
  Load Regulation:  ΔVout/ΔIload ≈ 1mV/mA
  Dropout Voltage:  ~0.8V (TIP122)
"""
ax.text(0.05, 0.95, ldo_diagram, transform=ax.transAxes, fontsize=8,
        fontfamily='monospace', verticalalignment='top',
        bbox=dict(boxstyle='round', alpha=0.05))

# 3C: Applications summary
ax = fig.add_subplot(gs[2, 2])
ax.axis('off')
apps = """
WHERE THESE CIRCUITS ARE USED:

BJT AMPLIFIER:
  • Audio pre-amp (mic → speaker)
  • Sensor signal conditioning
  • RF front-end (LNA)

OP-AMP:
  • Instrumentation amplifier
    (ECG, strain gauge, thermocouple)
  • Active filters (anti-aliasing)
  • PID controller
  • ADC driver

LDO REGULATOR:
  • Every MCU board (3.3V rail)
  • Battery-powered devices
  • Clean analog supply
  • Post-switcher ripple cleanup
"""
ax.text(0.05, 0.95, apps, transform=ax.transAxes, fontsize=8.5,
        fontfamily='monospace', verticalalignment='top',
        bbox=dict(boxstyle='round', alpha=0.05))

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('simulations/analog/images/analog_trilogy.png', dpi=150)
print('Done -> simulations/analog/images/analog_trilogy.png')
print(f'\nBJT Amp: Q-point Vce={Vce:.1f}V Ic={Ic*1000:.1f}mA  Av={Av:.1f}x')
print(f'Op-Amp:  Inverting G={gain_inv:.1f}x  Non-Inv G={gain_noninv:.1f}x')
print(f'LDO:     Vout={Vout_target}V  Dropout=0.8V  Vref={Vref}V')
