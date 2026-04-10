# RFC 3463 Enhancement - Version 2

## Overview

Enhanced version of `process_bounces.py` that properly implements RFC 3463 status code parsing for bounce classification.

## What Changed

### v1 (Legacy)
- Keyword matching: `['550', '5.1.1', '5.7.1']`
- 9 hard codes, 7 soft codes
- Simple substring search in email body

### v2 (RFC 3463)
- Full RFC 3463 status code parsing: `X.Y.Z` format
- 7 classes × 8 subsystems × 10 detail codes
- DSN header parsing support
- Human-readable descriptions

## RFC 3463 Format

```
X.Y.Z
││└┴─ Detail code (0-9)
│└───── Subject code (0-7)
└─────── Class: 2=success, 4=soft, 5=hard
```

### Classes
| Class | Meaning | Action |
|-------|---------|--------|
| 2 | Success | N/A |
| 4 | Temporary | Retry later |
| 5 | Permanent | Remove from list |

### Common Codes

| Code | Meaning | Type |
|-----|---------|------|
| 5.1.1 | Bad destination mailbox | Hard |
| 5.2.2 | Mailbox full | Hard |
| 5.7.1 | Policy blocked | Hard |
| 5.7.26 | DMARC violation | Hard |
| 4.4.1 | Connection timeout | Soft |
| 4.4.7 | Delivery expired | Soft |
| 4.7.0 | Policy throttling | Soft |

## New Features

1. **RFC3463Status dataclass** - Parse code components
2. **STATUS_DESCRIPTIONS** - Human-readable meanings
3. **BOUNCE_ACTIONS** - Recommended handling per code
4. **parse_dsn_email()** - RFC 3464 DSN header parsing
5. **detect_bounce_from_body()** - Enhanced detection with RFC codes
6. **extract_recipient_from_bounce()** - Get failed recipient

## Output Format

```text
---GEMINI_EMAIL_SEPARATOR---
---GEMINI_DATE_SEPARATOR---2026-03-15 10:30:00
---RFC3463_STATUS---5.1.1
---BOUNCE_TYPE---hard_bounce
---BOUNCE_DESCRIPTION---Bad destination mailbox address
[Email body...]
```

## Usage

Same as v1:
```bash
python3 process_bounces_v2.py
```

## Dependencies

- Python 3.7+ (stdlib only, no external deps)

## Upgrade Path

Replace `process_bounces.py` with `process_bounces_v2.py` after testing:
```bash
mv process_bounces.py process_bounces_v1.py
mv process_bounces_v2.py process_bounces.py
```