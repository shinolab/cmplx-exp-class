import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent.parent / "slides" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "figure.dpi": 160,
        "savefig.dpi": 160,
        "savefig.bbox": "tight",
        "savefig.facecolor": "white",
        "font.size": 15,
        "axes.titlesize": 17,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "lines.linewidth": 2.2,
    }
)

ACCENT = "#2e9e5b"
ACCENT_D = "#1f7a45"
INK = "#22303a"
RED = "#d2433a"
IRC = "#7a4fd0"
MUTED = "#6b7780"


def ppg_ac(t, hr=72.0):
    f = hr / 60.0
    phase = (t * f) % 1.0
    systolic = np.exp(-((phase - 0.20) ** 2) / (2 * 0.045 ** 2))
    dicrotic = 0.38 * np.exp(-((phase - 0.50) ** 2) / (2 * 0.07 ** 2))
    ac = systolic + dicrotic
    return ac / ac.max()


def fig_ppg_dc_ac():
    from matplotlib.gridspec import GridSpec
    from matplotlib.patches import ConnectionPatch

    fs = 250
    t = np.linspace(0, 2.5, int(fs * 2.5))
    ac = ppg_ac(t)
    DC, AC_FRAC = 1.0, 0.01
    received = DC - AC_FRAC * ac

    fig = plt.figure(figsize=(10, 4.0))
    gs = GridSpec(1, 2, figure=fig, width_ratios=[2, 1], wspace=0.35)
    a1  = fig.add_subplot(gs[0, 0])
    ins = fig.add_subplot(gs[0, 1])

    a1.plot(t, received, color=INK)
    a1.set_ylim(0, 1.08)
    a1.set_ylabel("PPG signal (a.u.)")
    a1.set_xlabel("Time [s]")

    ZX0, ZX1 = 0.8, 1.7
    ZY0, ZY1 = 0.988, 1.0005
    YMAX = 1.08
    BAND_BOTTOM = 0.9
    BAND_BOTTOM_AX = BAND_BOTTOM / YMAX
    a1.axvspan(ZX0, ZX1, ymin=BAND_BOTTOM_AX, color=ACCENT, alpha=0.15, zorder=0)
    for xv in [ZX0, ZX1]:
        a1.axvline(xv, ymin=BAND_BOTTOM_AX, color=ACCENT, lw=1.2, alpha=0.6, zorder=2)

    ins.plot(t, received, color="#202289")
    ins.set_xlim(ZX0, ZX1)
    ins.set_ylim(ZY0, ZY1)
    ins.set_xlabel("Time [s]", fontsize=10)
    ins.tick_params(labelsize=8)
    ins.grid(alpha=0.3)
    ins.annotate("systolic\npeak", xy=(1.0, 0.990), xytext=(1.05, 0.9928),
                 arrowprops=dict(arrowstyle="->"), fontsize=12)
    ins.annotate("dicrotic\nnotch", xy=(1.112, 0.99965), xytext=(1.17, 1.0000),
                 arrowprops=dict(arrowstyle="->"), fontsize=12)
    ins.annotate("diastolic\npeak", xy=(1.25, 0.9962), xytext=(1.30, 0.9942),
                 arrowprops=dict(arrowstyle="->"), fontsize=12)

    for ya, (xb, yb) in [(YMAX, (0, 1)), (BAND_BOTTOM, (0, 0))]:
        fig.add_artist(ConnectionPatch(
            xyA=(ZX1, ya), coordsA="data", axesA=a1,
            xyB=(xb, yb), coordsB="axes fraction", axesB=ins,
            color=ACCENT, lw=1.0, linestyle="--", alpha=0.7,
        ))

    fig.tight_layout()
    return _save(fig, "ppg_dc_ac")


def fig_ppg_cardiac():
    hr = 72.0
    fs = 250
    t = np.linspace(0, 2, fs * 3)
    ac = ppg_ac(t, hr=hr)

    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.plot(t, ac, color=ACCENT)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("PPG (a.u.)")

    T = 60.0 / hr 
    p1, p2 = 0.20 / (hr / 60.0), 0.20 / (hr / 60.0) + T
    ax.annotate(
        "", xy=(p2, 1.06), xytext=(p1, 1.06),
        arrowprops=dict(arrowstyle="<->", color=INK, lw=1.8),
   )
    ax.text((p1 + p2) / 2, 1.10, f"T = {T:.2f}s  →  HR = 60/T ≈ {hr:.0f} bpm",
            ha="center", fontsize=13, color=INK)
    ax.set_ylim(-0.05, 1.25)
    for pk in [p1, p2]:
        ax.axvline(pk, color=MUTED, ls=":", lw=1)
    fig.tight_layout()
    return _save(fig, "ppg_cardiac")


def fig_absorption_spectra():
    from scipy.interpolate import PchipInterpolator

    w = np.array([450, 500, 540, 560, 576, 600, 660, 700,
                  760, 805, 850, 905, 940, 1000])
    hbo2 = np.array([62000, 20000, 53000, 44000, 51000, 3200, 320, 290,
                     600, 800, 1058, 1190, 1214, 1100])
    hb = np.array([45000, 20000, 53000, 53000, 45000, 16000, 3226, 1794,
                   1390, 800, 780, 740, 693, 900])

    ww = np.linspace(450, 1000, 600)
    fo = np.power(10, PchipInterpolator(w, np.log10(hbo2))(ww))
    fh = np.power(10, PchipInterpolator(w, np.log10(hb))(ww))

    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.semilogy(ww, fo, color=RED, label="HbO₂ (oxygenated)")
    ax.semilogy(ww, fh, color=INK, label="Hb (deoxygenated)")

    ax.axvspan(520, 560, color="#2e9e5b", alpha=0.18)
    ax.axvspan(650, 670, color=RED, alpha=0.12)
    ax.axvspan(930, 950, color=IRC, alpha=0.12)
    ax.text(540, 75000, "Green\n(HR)", ha="center", color="#1f7a45", fontsize=12)
    ax.text(660, 75000, "Red", ha="center", color=RED, fontsize=12)
    ax.text(940, 75000, "IR", ha="center", color=IRC, fontsize=12)
    ax.text(800, 75000, "(SpO₂ uses Red+IR)", ha="center",
            color=MUTED, fontsize=11)

    ax.set_xlabel("Wavelength [nm]")
    ax.set_ylabel("Molar extinction [cm$^{-1}$/M] (approx.)")
    ax.set_xlim(450, 1000)
    ax.set_ylim(100, 1.2e5)
    ax.legend(loc="lower left", fontsize=12)
    fig.tight_layout()
    return _save(fig, "absorption_spectra")


def fig_adc_sampling():
    t = np.linspace(0, 1, 1000)
    analog = 0.5 + 0.42 * np.sin(2 * np.pi * 2 * t) * np.exp(-0.3 * t)

    fs_n = 16 
    ts = np.linspace(0, 1, fs_n, endpoint=False) + 0.5 / fs_n
    samp = 0.5 + 0.42 * np.sin(2 * np.pi * 2 * ts) * np.exp(-0.3 * ts)

    levels = 8 
    q = 1.0 / levels
    quant = np.round(samp / q) * q

    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.plot(t, analog, color=MUTED, lw=2, label="Analog (continuous)")
    for lv in np.arange(0, 1.001, q):
        ax.axhline(lv, color="#cdd6d0", lw=0.8, zorder=0)
    ax.step(np.append(ts, 1.0), np.append(quant, quant[-1]),
            where="post", color=ACCENT, lw=2.2, label="Sampled + quantized")
    ax.plot(ts, quant, "o", color=ACCENT_D, ms=6, zorder=5)
    ax.vlines(ts, [min(a, b) for a, b in zip(samp, quant)],
              [max(a, b) for a, b in zip(samp, quant)],
              color=RED, lw=1, alpha=0.6)

    for tx in [ts[0], ts[1]]:
        ax.plot([tx, tx], [-0.11, 1.05], color=INK, lw=1.0, alpha=0.35,
                linestyle="--", clip_on=False)
    ax.annotate("", xy=(ts[1], -0.09), xytext=(ts[0], -0.09),
                arrowprops=dict(arrowstyle="<->", color=INK))
    ax.text((ts[0] + ts[1]) / 2, -0.16, r"$\Delta t = 1/f_s$",
            ha="center", fontsize=12)

    Q_LO, Q_HI = 2 * q, 3 * q
    ax.annotate("", xy=(1.03, Q_HI), xytext=(1.03, Q_LO),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=1.5))
    ax.text(1.045, (Q_LO + Q_HI) / 2, "LSB", fontsize=11, color=INK, va="center")
    for yq in [Q_LO, Q_HI]:
        ax.plot([1.0, 1.038], [yq, yq], color=INK, lw=1.2, clip_on=False)

    ax.set_xlabel("Time")
    ax.set_ylabel("Voltage")
    ax.set_ylim(-0.22, 1.05)
    ax.set_xlim(0, 1.14)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.legend(loc="upper right", fontsize=11)
    fig.tight_layout()
    return _save(fig, "adc_sampling")


def fig_led_resistor():
    try:
        import schemdraw
        import schemdraw.elements as elm
    except Exception as e:  # noqa: BLE001
        return f"schemdraw unavailable: {e}"
    d = schemdraw.Drawing()
    d.config(unit=2.4)
    d += elm.Dot().label("3.3 V", loc="top")
    d += elm.Resistor().down().label("220 Ω")
    d += elm.LED().down().label("LED")
    d += elm.Ground()
    return _save_sd(d, "led_resistor")


def fig_led_loadline():
    Vg = 3.3                        
    Vt = 0.07                       
    Is = 0.02 / np.exp(1.95 / Vt)   
    I_LED = lambda V: Is * (np.exp(V / Vt) - 1.0)  

    def operating_point(R):
        V = np.linspace(0, Vg, 400000)
        k = np.argmin(np.abs(I_LED(V) - (Vg - V) / R))
        return V[k], I_LED(V[k]) * 1e3        

    Vop0, Iop0 = operating_point(20)           
    Vop1, Iop1 = operating_point(220)          

    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    Vcurve = np.linspace(0, 2.15, 600)
    ax.plot(Vcurve, I_LED(Vcurve) * 1e3, color=INK, lw=2.6, label="LED I–V")

    Vline = np.array([0.0, Vg])
    ax.plot(Vline, (Vg - Vline) / 20 * 1e3, color=RED, lw=2.4,
            label="No resistor (slope −1/R$_{On}$)")
    ax.plot(Vline, (Vg - Vline) / 220 * 1e3, color=ACCENT, lw=2.2, ls="--",
            label="With 220 Ω")

    ax.axhline(20, color=MUTED, lw=1.3, ls=":")
    ax.text(3.45, 21.5, "LED max ≈ 20 mA", color=MUTED, fontsize=11,
            va="bottom", ha="right")

    ax.plot(Vop0, Iop0, "o", color=RED, ms=10, zorder=5)
    ax.annotate(f"operating point\n≈ {Iop0:.0f} mA → overload!",
                xy=(Vop0, Iop0), xytext=(2.25, 69),
                color=RED, fontsize=12, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.6))
    ax.plot(Vop1, Iop1, "o", color=ACCENT_D, ms=8, zorder=5)
    ax.annotate(f"≈ {Iop1:.0f} mA",
                xy=(Vop1, Iop1), xytext=(2.2, 12),
                color=ACCENT_D, fontsize=11,
                arrowprops=dict(arrowstyle="->", color=ACCENT_D, lw=1.4))

    ax.plot(Vg, 0, "o", color=INK, ms=6, clip_on=False, zorder=5)
    ax.annotate("3.3 V", xy=(Vg, 0), xytext=(Vg - 0.05, 9),
                ha="center", color=INK, fontsize=11)

    ax.set_xlabel("Voltage  V [V]")
    ax.set_ylabel("Current  I [mA]")
    ax.set_xlim(0, 3.5)
    ax.set_ylim(0, 80)
    ax.legend(loc="upper left", fontsize=11)
    fig.tight_layout()
    return _save(fig, "led_loadline")


def fig_voltage_divider():
    try:
        import schemdraw
        import schemdraw.elements as elm
    except Exception as e:  # noqa: BLE001
        return f"schemdraw unavailable: {e}"
    d = schemdraw.Drawing()
    d.config(unit=2.6)
    d += elm.Vdd().label("3.3 V")
    pot = elm.Potentiometer().down()
    d += pot
    d += elm.Ground()
    d += elm.Line().right().at(pot.tap).length(2.6)
    d += elm.Dot(open=True).label("→ ADC", loc="right")
    return _save_sd(d, "voltage_divider")



def _save(fig, name):
    p = OUT / f"{name}.png"
    fig.savefig(p)
    plt.close(fig)
    return p


def _save_sd(d, name):
    p = OUT / f"{name}.png"
    d.save(str(p), dpi=200)
    return p


def _synth_raw(seed=3):
    rng = np.random.default_rng(seed)
    fs = 100
    t = np.linspace(0, 8, fs * 8)
    pulse = ppg_ac(t, hr=72)
    baseline = 0.6 * np.sin(2 * np.pi * 0.25 * t + 1.0)    
    motion = np.zeros_like(t)
    for c, amp in [(2.4, 1.7), (5.6, 1.3)]:                
        env = np.exp(-((t - c) ** 2) / (2 * 0.18 ** 2))
        motion += amp * env * np.sin(2 * np.pi * 6 * (t - c))
    noise = 0.05 * rng.standard_normal(t.size)
    raw = 0.35 * pulse + baseline + motion + noise + 1.0   
    return t, fs, pulse, raw


def fig_noisy_signal():
    t, fs, clean, raw = _synth_raw()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 5), sharex=True)
    a1.plot(t, clean, color=ACCENT)
    a1.set_title("What we want: the clean pulse")
    a1.set_ylabel("PPG (a.u.)")
    a2.plot(t, raw, color=INK)
    a2.set_title("What we actually measure (raw)")
    a2.set_ylabel("Voltage (a.u.)")
    a2.set_xlabel("Time [s]")
    a2.annotate("motion artifact", xy=(2.4, raw[int(2.4 * fs)]),
                xytext=(3.0, raw.max() * 0.96),
                arrowprops=dict(arrowstyle="->", color=RED), color=RED, fontsize=12)
    a2.annotate("baseline wander\n(ambient / breathing)",
                xy=(7.0, raw[int(7.0 * fs)]), xytext=(4.6, raw.min() + 0.05),
                arrowprops=dict(arrowstyle="->", color=MUTED), color=MUTED,
                fontsize=11)
    fig.tight_layout()
    return _save(fig, "noisy_signal")


def fig_filtering():
    from scipy.signal import butter, filtfilt, find_peaks
    t, fs, clean, raw = _synth_raw()
    b, a = butter(3, [0.5, 5], btype="band", fs=fs)
    filt = filtfilt(b, a, raw)
    peaks, _ = find_peaks(filt, distance=int(fs * 0.4), prominence=0.1)

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 5), sharex=True)
    a1.plot(t, raw, color=INK)
    a1.set_title("Raw (messy)")
    a1.set_ylabel("a.u.")
    a2.plot(t, filt, color=ACCENT)
    a2.plot(t[peaks], filt[peaks], "v", color=RED, ms=10)
    a2.set_title("After 0.5–5 Hz band-pass — pulses recovered")
    a2.set_xlabel("Time [s]")
    a2.set_ylabel("a.u.")
    if len(peaks) > 1:
        hr = 60 * fs / np.mean(np.diff(peaks))
        a2.text(0.015, 0.86, f"detected ≈ {hr:.0f} bpm",
                transform=a2.transAxes, color=ACCENT_D, fontsize=13)
    fig.tight_layout()
    return _save(fig, "filtering")


def fig_i2c_timing():
    fs = 2000
    x = np.linspace(-1.4, 10.6, int((10.6 + 1.4) * fs))
    scl = np.ones_like(x)
    sda = np.ones_like(x)
    for i in range(9):                       
        scl[(x >= i) & (x < i + 0.5)] = 0
    bits = [1, 0, 1, 0, 1, 1, 1, 0, 0]         
    sda[x >= -0.5] = 0                          
    for i, b in enumerate(bits):
        sda[(x >= i) & (x < i + 1)] = b
    sda[x >= 9] = 0
    sda[x >= 9.5] = 1                         

    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.plot(x, scl, color=INK, lw=2)
    ax.plot(x, sda + 2.4, color=ACCENT, lw=2)
    ax.text(-2.1, 0.4, "SCL", color=INK, fontsize=14, weight="bold")
    ax.text(-2.1, 2.8, "SDA", color=ACCENT_D, fontsize=14, weight="bold")
    for i, lab in enumerate(["1", "0", "1", "0", "1", "1", "1", "R/W", "ACK"]):
        ax.text(i + 0.5, 3.65, lab, ha="center", fontsize=11, color=MUTED)
    ax.annotate("START", xy=(-0.5, 3.4), xytext=(-1.3, 4.15),
                arrowprops=dict(arrowstyle="->", color=RED), fontsize=12, color=RED)
    ax.annotate("STOP", xy=(9.5, 3.4), xytext=(9.5, 4.15),
                arrowprops=dict(arrowstyle="->", color=RED), fontsize=12, color=RED)
    ax.text(3.5, -0.8, "Address 0x57  ( + R/W bit)", ha="center",
            fontsize=12, color=INK)
    ax.set_ylim(-1.1, 4.6)
    ax.set_xlim(-2.3, 10.6)
    ax.axis("off")
    ax.set_title("I²C: one frame on SDA / SCL")
    fig.tight_layout()
    return _save(fig, "i2c_timing")


def fig_phototransistor_frontend():
    try:
        import schemdraw
        import schemdraw.elements as elm
    except Exception as e:  # noqa: BLE001
        return f"schemdraw unavailable: {e}"
    d = schemdraw.Drawing()
    d.config(unit=2.2)
    d += elm.Vdd().label("3.3 V")
    Q = elm.BjtNpn().anchor("collector").label("photo-\ntransistor", loc="left")
    d += Q
    for dy in (0.55, 0.0):                   
        d += (elm.Arrow()
              .at((Q.base[0] - 1.8, Q.base[1] + 1.1 + dy))
              .to((Q.base[0] - 0.25, Q.base[1] + 0.25 + dy))
              .color("#caa000"))
    d += (node := elm.Line().down().at(Q.emitter).length(0.9).dot())
    d += elm.Line().right().length(2.3).label("→ ADC (GP26)", loc="right")
    d += elm.Dot(open=True)
    d += elm.Resistor().down().at(node.end).label("10 kΩ\n(load)")
    d += elm.Ground()
    return _save_sd(d, "phototransistor_frontend")


FIGS = {
    "ppg_dc_ac": fig_ppg_dc_ac,
    "ppg_cardiac": fig_ppg_cardiac,
    "absorption_spectra": fig_absorption_spectra,
    "adc_sampling": fig_adc_sampling,
    "led_resistor": fig_led_resistor,
    "led_loadline": fig_led_loadline,
    "voltage_divider": fig_voltage_divider,
    "noisy_signal": fig_noisy_signal,
    "filtering": fig_filtering,
    "i2c_timing": fig_i2c_timing,
    "phototransistor_frontend": fig_phototransistor_frontend,
}

if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for name in want:
        fn = FIGS.get(name)
        if fn is None:
            print(f"[skip] unknown figure: {name}")
            continue
        print(f"[{name}] -> {fn()}")
