#!/usr/bin/env python3
"""Extract CPAP summary data from ResMed STR.edf files into a CSV."""

import struct
import csv
import os
from datetime import datetime, timedelta

PROFILE_DIR = os.path.expanduser(
    "~/Documents/OSCAR_Data/Profiles/Tim Kilåker/ResMed_23222634969/Backup"
)
OUTPUT_CSV = os.path.expanduser("~/Documents/OSCAR_Data/cpap_complete.csv")

STR_FILES = ["STR 2.edf", "STR 3.edf", "STR.edf"]  # oldest first

KEY_COLS = [
    "date", "Duration", "OnDuration", "AHI", "HI", "AI", "OAI", "CAI", "UAI",
    "MaskPress.50", "MaskPress.95", "MaskPress.Max",
    "Leak.50", "Leak.95", "Leak.Max",
    "RespRate.50", "RespRate.95", "TidVol.50", "TidVol.95",
    "MinVent.50", "MinVent.95", "SpO2.50", "SpO2.95",
    "AmbHumidity.50", "CSR", "Mode",
    "S.EPR.Level", "S.AS.MinPress", "S.AS.MaxPress",
]


def read_edf_data(path):
    with open(path, "rb") as f:
        f.read(8)   # version
        f.read(80)  # patient
        f.read(80)  # recording
        start_date = f.read(8).decode("latin-1").strip()
        start_time = f.read(8).decode("latin-1").strip()
        header_bytes = int(f.read(8).decode("latin-1").strip())
        f.read(44)  # reserved
        num_records = int(f.read(8).decode("latin-1").strip())
        f.read(8)   # record_duration
        num_signals = int(f.read(4).decode("latin-1").strip())

        dd, mm, yy = start_date.split(".")
        hh, mi, ss = start_time.split(".")
        yy = int(yy)
        yy = yy + 2000 if yy < 85 else yy + 1900
        start_dt = datetime(yy, int(mm), int(dd), int(hh), int(mi), int(ss))

        ns = num_signals
        labels = [f.read(16).decode("latin-1").strip() for _ in range(ns)]
        f.read(80 * ns)  # transducers
        f.read(8 * ns)   # phys_dims

        def sf(b):
            try:
                return float(b.decode("latin-1").strip())
            except (ValueError, UnicodeDecodeError):
                return 0.0

        def si(b):
            try:
                return int(b.decode("latin-1").strip())
            except (ValueError, UnicodeDecodeError):
                return 0

        phys_mins = [sf(f.read(8)) for _ in range(ns)]
        phys_maxs = [sf(f.read(8)) for _ in range(ns)]
        dig_mins = [si(f.read(8)) for _ in range(ns)]
        dig_maxs = [si(f.read(8)) for _ in range(ns)]
        f.read(80 * ns)  # prefiltering
        samples_per_record = [si(f.read(8)) for _ in range(ns)]
        f.read(32 * ns)  # reserved

        gains = []
        offsets = []
        for i in range(ns):
            dr = dig_maxs[i] - dig_mins[i]
            pr = phys_maxs[i] - phys_mins[i]
            if dr == 0:
                gains.append(0)
                offsets.append(0)
            else:
                g = pr / dr
                gains.append(g)
                offsets.append(phys_mins[i] - g * dig_mins[i])

        f.seek(header_bytes)
        rows = []
        for rec in range(num_records):
            row = {"date": (start_dt + timedelta(days=rec)).strftime("%Y-%m-%d")}
            for sig in range(ns):
                n_samples = samples_per_record[sig]
                raw = struct.unpack(f"<{n_samples}h", f.read(n_samples * 2))
                phys = [r * gains[sig] + offsets[sig] for r in raw]
                label = labels[sig]
                if n_samples == 1:
                    row[label] = round(phys[0], 4)
                else:
                    row[label] = ";".join(str(round(v, 2)) for v in phys)
            rows.append(row)
        return rows


def main():
    all_data = {}
    for fname in STR_FILES:
        path = os.path.join(PROFILE_DIR, fname)
        if not os.path.exists(path):
            print(f"Skipping {fname} (not found)")
            continue
        rows = read_edf_data(path)
        for row in rows:
            all_data[row["date"]] = row
        print(f"{fname}: {len(rows)} records")

    used = {d: r for d, r in all_data.items() if r.get("Duration", 0) > 0}
    sorted_dates = sorted(used.keys())

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=KEY_COLS, extrasaction="ignore")
        writer.writeheader()
        for d in sorted_dates:
            writer.writerow(used[d])

    print(f"\nWrote {len(sorted_dates)} rows to {OUTPUT_CSV}")
    print(f"Date range: {sorted_dates[0]} to {sorted_dates[-1]}")


if __name__ == "__main__":
    main()
