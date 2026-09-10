"""Email pattern guessing for leads."""


def _clean(name_part):
    """Lowercase, strip, and drop internal spaces from a name part."""
    if not name_part:
        return ""
    return name_part.strip().lower().replace(" ", "")


def generate_email_guesses(first_name, last_name, domain):
    """Generate likely email guesses for a lead, given a known domain.

    Patterns (in order): firstname.lastname@domain, firstname@domain,
    f.lastname@domain. Patterns needing last_name are skipped if it's
    missing. Returns [] if first_name or domain is missing entirely.
    """
    first = _clean(first_name)
    last = _clean(last_name)
    domain = domain.strip().lower().lstrip("@") if domain else ""

    if not first or not domain:
        return []

    guesses = []
    if last:
        guesses.append(f"{first}.{last}@{domain}")
    guesses.append(f"{first}@{domain}")
    if last:
        guesses.append(f"{first[0]}.{last}@{domain}")

    return guesses
