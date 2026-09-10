"""Google search scraping logic."""

import random
import time
from urllib.parse import quote_plus

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from seleniumbase import SB

import config

# Google's organic-result container. "div.g" is the old (now-dead) markup;
# "div.yuRUbf" is current as of Aug 2026. Tried in order — first one that
# actually finds elements on the page wins, so this survives Google's
# markup shifting again without every caller needing to change.
RESULT_CONTAINER_SELECTORS = ["div.yuRUbf", "div.g"]


def _find_result_containers(sb):
    for selector in RESULT_CONTAINER_SELECTORS:
        containers = sb.find_elements(selector)
        if containers:
            return containers
    return []


def _is_captcha_page(sb):
    """Best-effort check for a Google CAPTCHA / "unusual traffic" page.

    Note: this only checks the URL for "recaptcha", not the page body —
    a body-text substring match on "recaptcha" false-positives on any
    page that merely embeds a reCAPTCHA widget for an unrelated reason.
    """
    try:
        url = sb.get_current_url().lower()
        if "/sorry/" in url or "recaptcha" in url:
            return True
        page = sb.get_page_source().lower()
        markers = ("unusual traffic", "captcha-form", "detected unusual traffic")
        return any(marker in page for marker in markers)
    except Exception:
        return False


def _fetch_results(sb, url):
    """Open the URL and pull result title/URL pairs off the page.

    Returns None if a CAPTCHA page was hit instead of real results.
    """
    sb.uc_open_with_reconnect(url, reconnect_time=4)
    sb.sleep(random.uniform(2, 4))

    if _is_captcha_page(sb):
        return None

    results = []
    containers = _find_result_containers(sb)
    for container in containers:
        try:
            title_el = container.find_element(By.CSS_SELECTOR, "h3")
            link_el = container.find_element(By.CSS_SELECTOR, "a")
            title = title_el.text.strip()
            link = link_el.get_attribute("href")
        except Exception:
            continue
        if title and link:
            results.append({"title": title, "url": link})

    sb.sleep(random.uniform(1, 2))
    return results


def _run_with_retries(fetch_page, log_label, max_retries=None):
    """Open a fresh browser session and call `fetch_page(sb)`, retrying on
    page-load failures and backing off longer on a detected CAPTCHA.

    `fetch_page` should return None to signal a CAPTCHA/block page was
    hit; any other value (including falsy ones like [] or "") is treated
    as a successful, final result. Returns None once retries are
    exhausted.
    """
    if max_retries is None:
        max_retries = config.MAX_RETRIES

    for attempt in range(1, max_retries + 1):
        user_agent = random.choice(config.USER_AGENTS)
        try:
            with SB(uc=True, headless=config.HEADLESS, agent=user_agent) as sb:
                result = fetch_page(sb)

            if result is None:
                print(f"[!] CAPTCHA detected for {log_label} (attempt {attempt}/{max_retries})")
                if attempt < max_retries:
                    time.sleep(config.CAPTCHA_PAUSE)
                    continue
                print(f"[!] Skipping {log_label} after repeated CAPTCHAs")
                return None

            return result

        except (WebDriverException, TimeoutException) as e:
            print(f"[!] Page load failed for {log_label} (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(random.uniform(3, 6))
                continue
            print(f"[!] Skipping {log_label} after repeated failures")
            return None

    return None


def search_google(query, max_retries=None):
    """Run one Google search query and extract result titles + URLs.

    Retries on page-load failures. On a detected CAPTCHA, backs off for a
    longer cooldown before retrying. Returns [] once attempts are
    exhausted rather than raising for either of these expected failure
    modes.
    """
    url = f"https://www.google.com/search?q={quote_plus(query)}"
    results = _run_with_retries(lambda sb: _fetch_results(sb, url), f"query {query!r}", max_retries)
    return results if results is not None else []


def run_searches(queries):
    """Run search_google for each query, rate-limited with a random delay.

    Returns a dict of {query: [ {"title", "url"}, ... ]}.
    """
    all_results = {}
    for i, query in enumerate(queries):
        all_results[query] = search_google(query)

        if i < len(queries) - 1:
            delay = random.uniform(config.MIN_QUERY_DELAY, config.MAX_QUERY_DELAY)
            time.sleep(delay)

    return all_results
