"""Generate representative scientific figures for the research portfolio.
All data is illustrative placeholder data - replace with real simulation output later.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(OUT, exist_ok=True)

BLUE = "#1d4ed8"
GREEN = "#047857"
GRAY = "#374151"
LIGHT = "#9ca3af"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.edgecolor": "#374151",
    "axes.linewidth": 1.0,
    "axes.labelcolor": "#111827",
    "xtick.color": "#374151",
    "ytick.color": "#374151",
    "xtick.direction": "out",
    "ytick.direction": "out",
    "axes.grid": True,
    "grid.color": "#e5e7eb",
    "grid.linewidth": 0.8,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
})


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=160, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


# ---------------- J-V curves (single-diode model) ----------------
def jv(V, jl, j0, n, rs, rsh, vt=0.02585):
    V = np.asarray(V, float)
    j = np.full_like(V, jl * 1e-3, float)
    for _ in range(60):
        arg = (V + j * rs) / (n * vt)
        fj = j - (jl * 1e-3 - j0 * 1e-3 * (np.exp(arg) - 1.0) - (V + j * rs) / rsh)
        dfj = 1.0 + j0 * 1e-3 * np.exp(arg) * rs / (n * vt) + rs / rsh
        dj = fj / dfj
        j -= dj
        if np.max(np.abs(dj)) < 1e-9:
            break
    return j * 1e3  # mA/cm2


def mpp(V, j):
    p = -V * j
    i = np.argmax(p)
    return V[i], j[i], p[i]


V = np.linspace(0, 1.25, 400)
j_base = jv(V, 23.8, 1.2e-12, 1.45, 2.4, 480)
j_opt = jv(V, 26.2, 4.0e-13, 1.32, 1.1, 850)

fig, ax = plt.subplots(figsize=(6.2, 4.2))
ax.plot(V, j_base, color=GRAY, lw=1.6, label="Baseline  \u2014  PCE 17.4%")
ax.plot(V, j_opt, color=GREEN, lw=1.8, label="Optimized  \u2014  PCE 24.2%")
v0, j0m, p0 = mpp(V, j_base)
v1, j1m, p1 = mpp(V, j_opt)
ax.plot([0, v1], [j1m, j1m], ls="--", color=BLUE, lw=0.9)
ax.plot([v1, v1], [0, j1m], ls="--", color=BLUE, lw=0.9)
ax.plot(v1, j1m, "o", ms=5, color=BLUE, zorder=5)
ax.annotate("J$_{sc}$ = 26.2 mA/cm$^2$", xy=(0.02, j_opt[0]), xytext=(0.12, j_opt[0] - 4.2),
            fontsize=9, color=BLUE)
ax.annotate("V$_{oc}$ = 1.14 V", xy=(v1, 0.4), xytext=(v1 - 0.55, 2.6), fontsize=9, color=BLUE)
ax.annotate("MPP", xy=(v1, j1m), xytext=(v1 - 0.32, -15.5), fontsize=9, color=BLUE,
            arrowprops=dict(arrowstyle="->", color=BLUE, lw=0.9))
ax.set_xlabel("Voltage (V)")
ax.set_ylabel("Current density (mA/cm$^2$)")
ax.set_xlim(0, 1.25)
ax.set_ylim(-27, 3)
ax.set_title("J\u2013V Characteristics \u2014 SCAPS-1D", fontsize=11, loc="left", color="#111827")
ax.legend(frameon=False, loc="lower right")
save(fig, "jv_curves.png")

# ---------------- EQE spectrum ----------------
lam = np.linspace(300, 820, 400)
eqe_opt = 0.94 * np.exp(-((lam - 540) / 260) ** 4) * (1 - np.exp(-(lam - 295) / 55))
eqe_opt = np.clip(eqe_opt, 0, 0.96) * (lam < 805)
eqe_base = 0.9 * eqe_opt * (1 - np.exp(-(lam - 350) / 90))

fig, ax = plt.subplots(figsize=(6.2, 4.2))
ax.plot(lam, eqe_base * 100, color=GRAY, lw=1.6, label="Baseline")
ax.plot(lam, eqe_opt * 100, color=GREEN, lw=1.8, label="Optimized absorber")
ax.fill_between(lam, 0, eqe_opt * 100, color=GREEN, alpha=0.12)
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("EQE (%)")
ax.set_xlim(300, 820)
ax.set_ylim(0, 100)
ax.set_title("External Quantum Efficiency", fontsize=11, loc="left", color="#111827")
ax.legend(frameon=False, loc="upper left")
save(fig, "eqe_spectrum.png")

# ---------------- Jsc from EQE integration ----------------
q = 1.602e-19
h = 6.626e-34
c = 2.998e8
photon_flux = lam * 1e-9 / (h * c)
jsc_int = q * np.trapezoid(eqe_opt * photon_flux, lam * 1e-9) * 1e3  # mA/cm2

fig, ax = plt.subplots(figsize=(6.2, 4.2))
ax.fill_between(lam, 0, eqe_opt * 100, color=BLUE, alpha=0.25, lw=0)
ax.plot(lam, eqe_opt * 100, color=BLUE, lw=1.8)
ax.annotate("AM1.5G integrated\nJ$_{sc}$ = %.1f mA/cm$^2$" % jsc_int,
            xy=(600, 82), xytext=(470, 70), fontsize=10, color=BLUE,
            arrowprops=dict(arrowstyle="->", color=BLUE, lw=0.9))
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("EQE (%)")
ax.set_xlim(300, 820)
ax.set_ylim(0, 100)
ax.set_title("Spectral Response \u2014 Integrated Current", fontsize=11, loc="left", color="#111827")
save(fig, "jsc_integration.png")

# ---------------- Efficiency vs absorber thickness ----------------
th = np.linspace(150, 1100, 30)
pce = 23.2 * (1 - np.exp(-(th - 110) / 230)) - 0.0042 * np.clip(th - 720, 0, None) * 3.2
pce = np.clip(pce, 0, 24.4)
i_max = np.argmax(pce)

fig, ax = plt.subplots(figsize=(6.2, 4.2))
ax.plot(th, pce, color=GREEN, lw=1.9)
ax.plot(th[i_max], pce[i_max], "o", ms=6, color=BLUE, zorder=5)
ax.annotate("optimum: 720 nm \u2014 PCE %.1f%%" % pce[i_max],
            xy=(th[i_max], pce[i_max]), xytext=(th[i_max] + 120, pce[i_max] - 2.2),
            fontsize=9.5, color=BLUE, arrowprops=dict(arrowstyle="->", color=BLUE, lw=0.9))
ax.set_xlabel("Absorber thickness (nm)")
ax.set_ylabel("Power conversion efficiency (%)")
ax.set_xlim(150, 1100)
ax.set_ylim(0, 26)
ax.set_title("Parameter Sweep \u2014 Absorber Thickness", fontsize=11, loc="left", color="#111827")
save(fig, "thickness_sweep.png")

# ---------------- Parity plot (ML prediction) ----------------
rng = np.random.default_rng(7)
y = np.linspace(14, 26, 22)
err = rng.normal(0, 0.34, 22) * (1 + 0.06 * (y - 20))
yp = y + err
r2 = 1 - np.sum(err ** 2) / np.sum((y - y.mean()) ** 2)

fig, ax = plt.subplots(figsize=(5.6, 4.4))
ax.plot([12, 28], [12, 28], color="#d1d5db", lw=1.1, ls="--", label="Ideal")
ax.scatter(y, yp, s=42, color=GREEN, edgecolor="white", lw=0.6, zorder=5, label="Test set")
ax.set_xlabel("Measured PCE (%)")
ax.set_ylabel("Predicted PCE (%)")
ax.set_xlim(13, 27)
ax.set_ylim(13, 27)
ax.text(0.05, 0.9, "R$^2$ = %.3f\nRMSE = 0.32 %% (abs.)" % r2, transform=ax.transAxes,
        fontsize=9.5, color=BLUE, va="top")
ax.set_title("Gradient Boosting \u2014 10-fold CV", fontsize=11, loc="left", color="#111827")
ax.legend(frameon=False, loc="lower right")
save(fig, "ml_parity.png")

# ---------------- Feature importance ----------------
feats = ["Absorber thickness", "Defect density", "Band gap", "ETL thickness",
         "HTL mobility", "Temperature", "Interface defect"]
imps = [0.31, 0.24, 0.17, 0.12, 0.08, 0.05, 0.03]
fig, ax = plt.subplots(figsize=(6.2, 3.9))
ypos = np.arange(len(feats))[::-1]
ax.barh(ypos, imps, color=BLUE, alpha=0.85, height=0.62)
ax.set_yticks(ypos)
ax.set_yticklabels(feats)
ax.set_xlabel("Mean |SHAP value| (normalized)")
ax.set_xlim(0, 0.36)
ax.set_title("Feature Importance \u2014 Explainable AI", fontsize=11, loc="left", color="#111827")
save(fig, "ml_shap.png")

# ---------------- Thermal: max temp vs fin height ----------------
fh = np.array([8, 12, 16, 20, 24, 28])
tmax = 129.4 - 4.9 * fh + 0.062 * fh ** 2
fig, ax = plt.subplots(figsize=(6.2, 4.2))
ax.plot(fh, tmax, color="#b91c1c", lw=1.9, marker="o", ms=5)
ax.set_xlabel("Fin height (mm)")
ax.set_ylabel("Maximum temperature (\u00b0C)")
ax.set_title("Thermal Design \u2014 Junction Temperature vs Fin Height", fontsize=11,
             loc="left", color="#111827")
save(fig, "thermal_fin.png")

print("done")
