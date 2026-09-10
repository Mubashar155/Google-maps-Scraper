"""Google search query generation for LinkedIn profile discovery."""

import config


def generate_search_queries():
    """Build one search query per (job title, country) combination."""
    queries = []
    for title in config.JOB_TITLES:
        for country in config.COUNTRIES:
            queries.append(f'site:linkedin.com/in "{title}" "{country}"')
    return queries
