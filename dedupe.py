"""De-duplication against an existing master email list."""

import csv
import os


def normalize_email(email):
    return email.strip().lower() if email else ""


def load_existing_emails(path):
    """Load a single-column "Email" CSV (~76k rows) into a set of
    normalized emails for fast membership checks.
    """
    emails = set()
    if not path or not os.path.exists(path):
        return emails

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return emails

        email_field = next(
            (c for c in reader.fieldnames if c.strip().lower() == "email"), None
        )
        if email_field is None:
            return emails

        for row in reader:
            normalized = normalize_email(row.get(email_field))
            if normalized:
                emails.add(normalized)

    return emails


def is_duplicate_email(email, existing_emails):
    """Check whether `email` is already present in `existing_emails`."""
    normalized = normalize_email(email)
    return bool(normalized) and normalized in existing_emails
