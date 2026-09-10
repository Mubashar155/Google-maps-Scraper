"""SMTP-based email verification (MX lookup + RCPT TO probe)."""

import smtplib
import socket

import dns.exception
import dns.resolver

import config


def _get_mx_host(domain, timeout):
    """Return the highest-priority MX hostname for a domain, or None."""
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=timeout)
        mx_records = sorted(answers, key=lambda r: r.preference)
        return str(mx_records[0].exchange).rstrip(".")
    except dns.exception.DNSException:
        return None


def verify_email_smtp(email, timeout=None, helo_domain=None, mail_from=None):
    """Check whether an email's mailbox likely exists via an SMTP probe.

    Looks up the domain's MX record, then connects to the mail server
    and runs HELO -> MAIL FROM -> RCPT TO, quitting before DATA so no
    message is ever actually sent.

    Returns:
        True  - the server accepted the recipient (mailbox likely exists).
        False - the server explicitly rejected the recipient, or the
                domain has no mail server at all.
        None  - inconclusive (Unknown): connection blocked, timed out, or
                the server gave an ambiguous/deferred response. Many mail
                servers refuse this kind of probing outright, so this is
                an expected outcome, not an error.
    """
    timeout = timeout or config.SMTP_TIMEOUT
    helo_domain = helo_domain or config.SMTP_HELO_DOMAIN
    mail_from = mail_from or config.SMTP_MAIL_FROM

    if not email or "@" not in email:
        return None

    domain = email.rsplit("@", 1)[1].strip().lower()
    if not domain:
        return None

    mx_host = _get_mx_host(domain, timeout)
    if mx_host is None:
        return False  # domain has no mail server at all

    smtp = None
    try:
        smtp = smtplib.SMTP(timeout=timeout)
        smtp.connect(mx_host, 25)
        smtp.helo(helo_domain)
        smtp.mail(mail_from)
        code, _ = smtp.rcpt(email)

        if code in (250, 251):
            return True
        if code in (550, 551, 553):
            return False
        return None  # e.g. 421/450/452 greylisting, or an unexpected code

    except (socket.timeout, smtplib.SMTPException, ConnectionError, OSError):
        return None
    finally:
        if smtp is not None:
            try:
                smtp.quit()
            except Exception:
                pass


def verify_best_guess(guesses, timeout=None, helo_domain=None, mail_from=None):
    """Verify a list of guessed emails in order, stopping early.

    Tries the first (most likely) guess; only moves on to the next one
    if the current guess is definitively rejected (False). A True or
    Unknown (None) result stops the search — there's no point probing
    further guesses once we have an answer, or once the server has shown
    it's blocking this kind of check.

    Returns {"email": ..., "status": True/False/None} for whichever
    guess was last tried, or None if `guesses` is empty.
    """
    if not guesses:
        return None

    result = None
    for guess in guesses:
        status = verify_email_smtp(guess, timeout=timeout, helo_domain=helo_domain, mail_from=mail_from)
        result = {"email": guess, "status": status}
        if status is not False:
            break

    return result
