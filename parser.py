"""Parsing of LinkedIn search result titles."""


def parse_linkedin_title(raw_title):
    """Parse a LinkedIn result title into name/title/company parts.

    Expected format: "First Last - Job Title - Company Name | LinkedIn"

    Always returns a dict with first_name, last_name, title, company,
    and complete (True only if all four fields were extracted). Malformed
    input is filled in on a best-effort basis rather than raising.
    """
    result = {
        "first_name": None,
        "last_name": None,
        "title": None,
        "company": None,
        "complete": False,
    }

    if not raw_title or not isinstance(raw_title, str):
        return result

    text = raw_title.strip()

    # Drop the trailing " | LinkedIn" (or similar) suffix, if present.
    if "|" in text:
        text = text.rsplit("|", 1)[0].strip()

    parts = [p.strip() for p in text.split(" - ") if p.strip()]

    if not parts:
        return result

    name_parts = parts[0].split(" ", 1)
    result["first_name"] = name_parts[0] or None
    result["last_name"] = name_parts[1].strip() if len(name_parts) > 1 and name_parts[1].strip() else None

    if len(parts) >= 2:
        result["title"] = parts[1] or None

    if len(parts) >= 3:
        # Anything after title is treated as company, even if it
        # itself contains " - " (e.g. "Company - Region").
        result["company"] = " - ".join(parts[2:]).strip() or None

    result["complete"] = all(
        [result["first_name"], result["last_name"], result["title"], result["company"]]
    )

    return result
