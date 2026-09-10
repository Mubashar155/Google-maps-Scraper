"""Writing parsed leads to the output CSV."""

import csv
import os

import config
from dedupe import normalize_email

CSV_COLUMNS = ["First Name", "Last Name", "Title", "Email", "Company", "Email Verification Status"]


def _lead_to_row(lead):
    return (
        lead.get("first_name") or "",
        lead.get("last_name") or "",
        lead.get("title") or "",
        lead.get("email") or "",
        lead.get("company") or "",
        lead.get("email_status") or "",
    )


def _read_header(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return None
    with open(path, "r", newline="", encoding="utf-8") as f:
        return next(csv.reader(f), None)


def _read_existing_rows(path):
    seen = set()
    if not os.path.exists(path):
        return seen
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            seen.add(tuple(row))
    return seen


def append_leads_to_csv(leads, output_path=None, known_emails=None):
    """Append parsed leads to the output CSV, skipping exact duplicate rows.

    Each lead is a dict with first_name, last_name, title, company, and
    (optionally, once guessed) email keys. Writes the header only if the
    file doesn't already exist or is empty. Returns the number of rows
    actually appended.

    known_emails, if given, is a set of normalized emails (e.g. from
    dedupe.load_existing_emails) to check a lead's guessed email against
    before adding it — any lead whose email is already in the set is
    skipped. Newly written emails are added to the set in place, so it
    also catches duplicates across multiple calls within the same run.
    """
    if output_path is None:
        output_path = os.path.join(config.OUTPUT_DIR, config.OUTPUT_FILE)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    existing_header = _read_header(output_path)
    if existing_header is not None and existing_header != CSV_COLUMNS:
        print(
            f"[!] Warning: {output_path} has columns {existing_header}, "
            f"expected {CSV_COLUMNS}. New rows may not align — consider "
            "migrating or renaming the old file."
        )

    needs_header = existing_header is None
    seen = _read_existing_rows(output_path)

    appended = 0
    with open(output_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if needs_header:
            writer.writerow(CSV_COLUMNS)

        for lead in leads:
            if not isinstance(lead, dict):
                continue

            email = normalize_email(lead.get("email"))
            if known_emails is not None and email and email in known_emails:
                continue

            row = _lead_to_row(lead)
            if row in seen:
                continue

            writer.writerow(row)
            seen.add(row)
            if known_emails is not None and email:
                known_emails.add(email)
            appended += 1

    return appended
