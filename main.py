"""Entry point for the scraper pipeline."""

import os
import random
import time

import config
from dedupe import load_existing_emails
from email_guesser import generate_email_guesses
from export import append_leads_to_csv
from parser import parse_linkedin_title
from queries import generate_search_queries
from scraper import search_google
from smtp_verifier import verify_best_guess


def _status_label(status):
    if status is True:
        return "True"
    if status is False:
        return "False"
    return "Unknown"


def build_lead(result):
    """Turn one raw search result into a lead dict, or None if unusable
    (including when SMTP verification confirms every guessed email is
    invalid).
    """
    url = result.get("url", "")
    if "linkedin.com/in" not in url.lower():
        return None  # not a profile page (e.g. a stray Google box)

    parsed = parse_linkedin_title(result.get("title", ""))
    if not parsed["first_name"]:
        return None  # nothing usable to build a lead from

    lead = dict(parsed)
    lead["email"] = None
    lead["email_status"] = "No Domain"

    domain = config.COMPANY_DOMAINS.get(parsed["company"]) if parsed["company"] else None
    if not domain:
        return lead  # no domain known yet -> save with a blank email

    guesses = generate_email_guesses(parsed["first_name"], parsed["last_name"], domain)
    if not guesses:
        return lead

    if not config.ENABLE_SMTP_VERIFICATION:
        lead["email"] = guesses[0]
        lead["email_status"] = "Unverified"
        return lead

    verification = verify_best_guess(guesses)
    if verification is None:
        return lead

    if verification["status"] is False:
        # Every guessed pattern was confirmed rejected by the mail
        # server — nothing usable to save for this lead.
        return None

    lead["email"] = verification["email"]
    lead["email_status"] = _status_label(verification["status"])
    return lead


def main():
    queries = generate_search_queries()
    total_queries = len(queries)
    print(f"Generated {total_queries} search queries")

    existing_emails = load_existing_emails(config.EXISTING_EMAILS_PATH)
    print(f"Loaded {len(existing_emails)} known emails for de-duplication")

    output_path = os.path.join(config.OUTPUT_DIR, config.OUTPUT_FILE)
    total_leads_saved = 0

    for i, query in enumerate(queries, start=1):
        print(f"[{i}/{total_queries}] Searching: {query}")

        results = search_google(query)
        print(f"  -> {len(results)} raw results")

        leads = [lead for r in results if (lead := build_lead(r)) is not None]

        saved = append_leads_to_csv(leads, output_path=output_path, known_emails=existing_emails)
        total_leads_saved += saved

        print(f"Processed query {i}/{total_queries}, found {total_leads_saved} leads so far")

        if i < total_queries:
            delay = random.uniform(config.MIN_QUERY_DELAY, config.MAX_QUERY_DELAY)
            time.sleep(delay)

    print(f"Done. {total_leads_saved} new leads saved to {output_path}")


if __name__ == "__main__":
    main()
