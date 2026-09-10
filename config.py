"""Project settings."""

# Job titles to search for
JOB_TITLES = [
    "Learning and Development Manager",
    "Training Manager",
    "Head of L&D",
    "Director of Training and Development",
    "Learning and Development Specialist",
    "Learning and Development Director",
    "L&D Business Partner",
    "Training and Development Manager",
]

# GCC countries to search for
COUNTRIES = [
    "UAE",
    "Saudi Arabia",
    "Qatar",
    "Kuwait",
    "Bahrain",
    "Oman",
]

# Where scraped results get written
OUTPUT_DIR = "output"
OUTPUT_FILE = "results.csv"

# Existing master list of known emails (single "Email" column) to
# de-duplicate against before saving new leads.
EXISTING_EMAILS_PATH = "existing_emails.csv"

# Company name -> email domain, filled in manually as domains are learned.
# Companies not listed here are saved with a blank Email.
COMPANY_DOMAINS = {
    # "Acme Corp": "acme.com",
}

# Browser / run behavior
HEADLESS = True
PAGE_LOAD_TIMEOUT = 30

# Rate limiting between search queries (seconds)
MIN_QUERY_DELAY = 5
MAX_QUERY_DELAY = 10

# Retry behavior
MAX_RETRIES = 3
CAPTCHA_PAUSE = 60  # cooldown before retrying after a CAPTCHA is detected

# SMTP verification settings
# Uses port 25, which is commonly blocked on cloud/ISP networks. Flip this
# to False to skip verification entirely and just use the first guessed
# email pattern, unverified.
ENABLE_SMTP_VERIFICATION = True
SMTP_TIMEOUT = 10  # seconds per connection attempt
SMTP_HELO_DOMAIN = "example.com"  # identify as during HELO/EHLO
SMTP_MAIL_FROM = "verify@example.com"  # sender used for the MAIL FROM probe

# User agents rotated between requests via SeleniumBase's `agent` option
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]
