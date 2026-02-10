import sqlite3
import csv
from datetime import datetime, timedelta
import os
import argparse
import shutil
import tempfile
import sys

# =========================
# TIMESTAMP CONVERSION
# =========================


def chrome_time_to_datetime(chrome_time):
    if chrome_time is None or chrome_time == 0:
        return None
    epoch_start = datetime(1601, 1, 1)
    return epoch_start + timedelta(microseconds=chrome_time)


# =========================
# TRANSITION DECODING
# =========================

TRANSITION_CORE = {
    0: "LINK",
    1: "TYPED",
    2: "AUTO_BOOKMARK",
    3: "AUTO_SUBFRAME",
    4: "MANUAL_SUBFRAME",
    5: "GENERATED",
    6: "START_PAGE",
    7: "FORM_SUBMIT",
    8: "RELOAD",
    9: "KEYWORD",
    10: "KEYWORD_GENERATED",
}

TRANSITION_QUALIFIERS = {
    0x01000000: "FORWARD_BACK",
    0x02000000: "FROM_ADDRESS_BAR",
    0x04000000: "HOME_PAGE",
    0x08000000: "CHAIN_START",
    0x10000000: "CHAIN_END",
    0x20000000: "CLIENT_REDIRECT",
    0x40000000: "SERVER_REDIRECT",
}


def decode_transition(transition):
    if transition is None:
        return None

    core = transition & 0xFF
    core_desc = TRANSITION_CORE.get(core, f"UNKNOWN({core})")

    qualifiers = []
    for bitmask, desc in TRANSITION_QUALIFIERS.items():
        if transition & bitmask:
            qualifiers.append(desc)

    if qualifiers:
        return f"{core_desc} ({', '.join(qualifiers)})"
    return core_desc


# =========================
# DATABASE EXTRACTION
# =========================


def extract_history(db_path, output_csv):
    if not os.path.exists(db_path):
        print(f"[!] File not found: {db_path}")
        return

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=5)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        print(f"[!] Error opening SQLite database (live mode): {e}")
        return

    query = """
        SELECT
            urls.id,
            urls.url,
            urls.title,
            urls.visit_count,
            urls.typed_count,
            urls.last_visit_time,
            visits.id AS visit_id,
            visits.from_visit,
            visits.visit_time,
            visits.visit_duration,
            visits.transition
        FROM urls
        JOIN visits ON urls.id = visits.url
        ORDER BY visits.visit_time DESC
    """

    try:
        rows = cursor.execute(query).fetchall()
    except sqlite3.Error as e:
        print(f"[!] SQL query error: {e}")
        conn.close()
        return

    conn.close()

    # CSV writing
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "url_id",
                "url",
                "title",
                "visit_count",
                "typed_count",
                "last_visit_time",
                "visit_id",
                "from_visit",
                "visit_time",
                "visit_duration_sec",
                "transition_raw",
                "transition_decoded",
            ]
        )

        for row in rows:
            (
                url_id,
                url,
                title,
                visit_count,
                typed_count,
                last_visit_time,
                visit_id,
                from_visit,
                visit_time,
                visit_duration,
                transition,
            ) = row

            last_visit_dt = chrome_time_to_datetime(last_visit_time)
            visit_dt = chrome_time_to_datetime(visit_time)

            writer.writerow(
                [
                    url_id,
                    url,
                    title,
                    visit_count,
                    typed_count,
                    last_visit_dt.isoformat(sep=" ", timespec="seconds")
                    if last_visit_dt
                    else None,
                    visit_id,
                    from_visit,
                    visit_dt.isoformat(sep=" ", timespec="seconds")
                    if visit_dt
                    else None,
                    round(visit_duration / 1_000_000, 2) if visit_duration else None,
                    transition,
                    decode_transition(transition),
                ]
            )

    print("[+] Extraction completed successfully")
    print(f"[+] CSV file generated: {output_csv}")


# =========================
# MAIN
# =========================


def main():
    parser = argparse.ArgumentParser(
        description="Forensic-ready extraction of browsing history from Chromium-based browsers (Chrome, Edge, Brave, Opera, etc.)"
    )

    parser.add_argument(
        "history_file", help="Path to the Chromium History SQLite database"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="chromium_history_forensic.csv",
        help="Output CSV file name (default: chromium_history_forensic.csv)",
    )

    args = parser.parse_args()
    extract_history(args.history_file, args.output)


if __name__ == "__main__":
    main()
