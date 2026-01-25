import os
import csv
import numpy as np

# =========================
# Configuration
# =========================
rows = 8
cols = 12
rounds = 32

row_labels = [chr(i) for i in range(65, 65 + rows)]
base_path = "plate_test_rounds_native"
os.makedirs(base_path, exist_ok=True)

# =========================
# Curve generator
# =========================
def generate_curve(max_val, rise):
    t = np.arange(rounds)
    midpoint = rounds * 0.4

    # Logistic rise
    curve = max_val / (1 + np.exp(-rise * (t - midpoint)))

    # Plateau
    curve[t > rounds * 0.7] = curve[int(rounds * 0.7)]

    # Gentle falloff
    fall_mask = t > rounds * 0.85
    curve[fall_mask] *= np.linspace(1, 0.7, fall_mask.sum())

    # Noise
    noise = np.random.normal(0, max_val * 0.02, size=rounds)
    return (curve + noise).clip(min=0)

# =========================
# Generate unique wells
# =========================
plate = {}

for r in row_labels:
    for c in range(1, cols + 1):
        well = f"{r}{c}"

        # Unique per-well parameters
        od_max = np.random.uniform(0.3, 1.3)
        rfu_max = np.random.uniform(300, 1300)
        rise = np.random.uniform(0.5, 1.5)

        od = generate_curve(od_max, rise)
        rfu = generate_curve(rfu_max, rise)

        plate[well] = {
            "sample": f"Well_{well}",
            "od": od,
            "rfu": rfu
        }

# =========================
# Write one CSV per round
# =========================
for rnd in range(rounds):
    fname = f"plate_data_round_{rnd + 1:02d}.csv"
    path = os.path.join(base_path, fname)

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)

        # Header
        header = [str(i + 1) for i in range(cols)]
        writer.writerow([""] + header)

        # Data rows
        for r in row_labels:
            row_vals = []
            for c in range(1, cols + 1):
                well = f"{r}{c}"
                cell = (
                    f"{plate[well]['sample']}|"
                    f"{plate[well]['od'][rnd]:.3f}|"
                    f"{plate[well]['rfu'][rnd]:.1f}"
                )
                row_vals.append(cell)

            writer.writerow([r] + row_vals)

print(f"✅ 32-round test CSVs created in folder '{base_path}'")
