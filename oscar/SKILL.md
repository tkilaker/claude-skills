---
name: oscar
description: Query CPAP/sleep data from OSCAR (ResMed). Triggers on "cpap", "sleep data", "oscar", "ahi", "apnea", "sleep quality", "cpap pressure", "sleep coaching".
---

# OSCAR CPAP Data Analysis

Parse and query Tim's CPAP data from the OSCAR app (ResMed AutoSet).

## Data Sources

- **Raw EDF files**: `~/Documents/OSCAR_Data/Profiles/Tim Kilåker/ResMed_23222634969/Backup/STR*.edf`
  - `STR 2.edf`: Mar 2024 - Jan 2025
  - `STR 3.edf`: Mar 2024 - Jun 2025
  - `STR.edf`: Mar 2025 - present (most recent)
- **Pre-extracted CSV**: `~/Documents/OSCAR_Data/cpap_complete.csv` (may be stale)
- **Apple Note**: "CPAP Sleep Analysis - Tim" has full context, history, and coaching notes

## Re-extracting Fresh Data

The CSV may be outdated if new nights have been recorded. Re-extract by running:

```bash
python3 ~/dev/claude-skills/oscar/scripts/extract_edf.py
```

This parses all 3 STR.edf files and writes a fresh `cpap_complete.csv`.

## Available Signals (per night)

| Signal | Description |
|--------|-------------|
| Duration | Total mask-on time (minutes) |
| OnDuration | Time machine was on (minutes) |
| AHI | Apnea-Hypopnea Index (events/hour) |
| HI, AI, OAI, CAI, UAI | Hypopnea, Apnea, Obstructive, Central, Unclassified indices |
| MaskPress.50/.95/.Max | Mask pressure percentiles (cmH2O) |
| Leak.50/.95/.Max | Leak rate percentiles (L/s) |
| RespRate.50/.95 | Respiratory rate (breaths/min) |
| TidVol.50/.95 | Tidal volume (L) |
| MinVent.50/.95 | Minute ventilation (L/min) |
| SpO2.50/.95 | Oxygen saturation (%) |
| AmbHumidity.50 | Ambient humidity (%) |
| CSR | Cheyne-Stokes respiration (minutes) |
| S.EPR.Level | EPR setting (1-3) |
| S.AS.MinPress/.MaxPress | AutoSet pressure range |
| Mode | Device mode |

## Key Context

- Tim uses a ResMed AutoSet, serial 23222634969
- On Wegovy since 2024: 107 kg -> 85 kg (ongoing weight loss)
- Apnea is structural (AHI ~15 without CPAP even at lower weight)
- History of aerophagia requiring pressure reductions
- Current settings (Feb 2026): Min 6, Max 8, EPR 2
- Main concern: sleep duration declining since mid-2025 (~8.6h -> ~7.3h)
- AHI is excellently controlled (avg 1.2, never above 5.0)

## Querying

Load the CSV with pandas or plain csv module. Example:

```python
import csv
from datetime import datetime

rows = []
with open("/Users/tim/Documents/OSCAR_Data/cpap_complete.csv") as f:
    for r in csv.DictReader(f):
        r = {k: float(v) if v and k != 'date' else v for k, v in r.items()}
        r['hours'] = r['Duration'] / 60
        rows.append(r)
```

## When Advising

- Always re-extract fresh data before analysis (run the extract script)
- Read the Apple Note "CPAP Sleep Analysis - Tim" for historical context
- Compare current metrics to established baselines in the note
- Flag if pressure headroom is shrinking (max setting - Press.95 < 1.0)
- Duration trend is the primary coaching concern, not AHI
