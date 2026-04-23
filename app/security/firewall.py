"""Firewall module for FitAct.

Detects attack indicators in request paths and query strings and
redirects to a blocked page if SQL injection, XSS, or path traversal
attempts are detected (NFR4).
"""

import re
from urllib.parse import unquote_plus

from flask import request, redirect, url_for

FIREWALL_INDICATORS = {
    "SQL Injection": [
        r"\bunion\b",
        r"\bselect\b",
        r"\binsert\b",
        r"\bdrop\b",
        r"\balter\b",
        r";",
        r"`",
        r"'",
    ],
    "XSS": [
        r"<\s*script\b",
        r"<\s*iframe\b",
        r"%3cscript%3e",
        r"%3ciframe%3e",
    ],
    "Path Traversal": [
        r"\.\./",
        r"\.\.",
        r"%2e%2e%2f",
        r"%2e%2e/",
        r"\.\.%2f",
    ],
}


def detect_attack(path_and_query):
    """Scan a combined path and query string for attack indicators.

    Checks both the raw and URL-decoded form of the string to catch
    encoded attack attempts.

    Args:
        path_and_query (str): The request path concatenated with the
                              query string.

    Returns:
        str | None: The attack type if an indicator is found,
                    otherwise None.
    """
    raw_text = path_and_query.lower()
    decoded_text = unquote_plus(path_and_query).lower()

    for attack_type, patterns in FIREWALL_INDICATORS.items():
        for pat in patterns:
            if re.search(pat, raw_text, re.IGNORECASE) or re.search(
                pat, decoded_text, re.IGNORECASE
            ):
                return attack_type
    return None


def firewall_check():
    """Global firewall check executed before every request.

    Skips static assets and the blocked page itself to avoid redirect
    loops. Redirects to the firewall blocked page if an attack indicator
    is detected in the request path or query string.
    """
    if request.endpoint in ("static", "main.firewall_blocked"):
        return None

    path = request.path or ""
    query = request.query_string.decode(errors="ignore")
    combined = f"{path}?{query}"

    attack_found = detect_attack(combined)
    if attack_found:
        return redirect(url_for("main.firewall_blocked", attack=attack_found))

    return None
