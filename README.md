# Chromium History Parser

A Python script to extract and analyze browsing history from Chromium-based browsers (Chrome, Microsoft Edge, Brave, Opera, Vivaldi, etc.).

The script parses the `History` SQLite database and exports the data to a CSV file enriched with decoded navigation metadata and normalized timestamps.

---

## Description

This tool extracts browsing history artifacts from the `History` database used by Chromium-based browsers. It connects directly to the live SQLite database in **read-only mode**, making it suitable for:
- Live response and triage
- Incident response
- Behavioral analysis
- Timeline reconstruction
- Digital forensics investigations

The parser goes beyond basic URL extraction and includes contextual information such as:
- Visit chains (`visit_id` / `from_visit`)
- Visit duration
- Typed vs clicked URLs
- Navigation type and redirects (decoded from the `transition` field)
- ISO 8601 normalized timestamps

⚠️ **Note**:  
This script parses **only the browsing history** (`History` file).  
Other Chromium artifacts (Downloads, Login Data, Cookies, Bookmarks, etc.) are **not** included.

---

## Features

- Read-only access to live Chromium SQLite databases
- Chromium timestamp conversion (microseconds since 1601)
- Decoding of `transition` bitmask values
- CSV output suitable for Excel, pandas, Timesketch, Plaso, SIEM tools
- Compatible with most Chromium-based browsers

---

## Requirements

- Python 3.8+
- No external dependencies (uses Python standard library only)

---

## Usage

### Basic usage

```bash
python chromium_history_parser.py /path/to/History -o output.csv
```

## Disclaimer

This tool is intended for **legitimate forensic, security, and research purposes only**.  
Ensure you have proper authorization before analyzing browser data.
