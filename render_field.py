"""Render the real COMSOL heat-sink temperature field (exported CSV) into a
publication-style contour figure on a dark background."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "images")

def load_csv(name):
    rows = []
    with open(os.path.join(OUT, name), "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("%"):
                continue
            if line.startswith("X"):
                continue
            parts = line.split(",")
            if len(parts) >= 3:
                rows.append((float(parts[0]), float(parts[1]), float(parts[2])))
    a = np.array(rows)
    return a[:, 0], a[:, 1], a[:, 2]

x, y, t = load_csv("heatsink_field.csv")

tri = mtri.Triangulation(x, y)
fig, ax = plt.subplots(figsize=(7.6, 3.4))
ax.set_facecolor("#0d1117")
fig.patch.set_facecolor("#0d1117")
cf = ax.tricontourf(tri, t, levels=24, cmap="turbo")
cl = ax.tricontour(tri, t, levels=8, colors="white", linewidths=0.35, alpha=0.55)
cb = fig.colorbar(cf, ax=ax, pad=0.015, aspect=28)
cb.set_label("Temperature (K)", color="#e6edf3", fontsize=9)
cb.ax.tick_params(colors="#e6edf3", labelsize=8)
ax.set_xlabel("x (mm)", color="#e6edf3", fontsize=9)
ax.set_ylabel("y (mm)", color="#e6edf3", fontsize=9)
ax.tick_params(colors="#9aa4af", labelsize=8)
ax.set_aspect("equal")
ax.set_title("Steady-state temperature field \u2014 COMSOL Multiphysics",
             loc="left", color="#e6edf3", fontsize=10)
for s in ax.spines.values():
    s.set_color("#30363d")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "heatsink_contour.png"), dpi=170, bbox_inches="tight",
            facecolor="#0d1117")
print("max T:", round(t.max(), 2), "K  min T:", round(t.min(), 2), "K")
print("saved heatsink_contour.png")
