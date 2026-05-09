# family-health

> Family health checkup management OpenClaw skill. Coexists with [pregnancy-care](https://github.com/VGEAREN/pregnancy-care).

## Features

- Auto-archive checkup reports / lab tests / imaging / specialist reports (per family member)
- Multi-year metric trend tracking
- Chronic-condition concern tracking (active / watching / resolved state machine)
- Comprehensive PDF report generation (per member)
- Coexists with pregnancy-care via one-way read-only `pregnancy/profile.md` (yield protocol)

## Data Layout

```
family-health/
├── members.md              ← member index + alias map
├── concerns.md             ← whole-family concerns overview
└── members/<displayName>/
    ├── profile.md
    ├── summary.md
    ├── records/            ← structured reports
    ├── reports/            ← raw PDF / images
    └── ocr_results/        ← OCR text
```

## Report Types

`checkup` annual / `lab` single-test / `imaging` (CT/MRI/US/...) / `specialist` (ECG/...)

## Install

```bash
pip3 install pymupdf reportlab
```

Then install via OpenClaw platform.

## Coexistence with pregnancy-care

- Symmetric yield protocol with pregnancy-care v1.1.0+:
  - family-health reads `pregnancy/profile.md`: pregnant person's reports + pregnancy-related signals yield to pregnancy-care
  - pregnancy-care reads `family-health/members.md`: checkup/imaging/lab signals yield to family-health
- User can override explicitly ("this is a checkup, not prenatal" / "file under pregnancy")
- Install order doesn't matter — when one side's index file is absent, that yield branch is skipped

## Test

```bash
python3 -m pytest tests/ -v
```

## Disclaimer

All analyses are for reference only. Not medical advice. Please consult a doctor.
