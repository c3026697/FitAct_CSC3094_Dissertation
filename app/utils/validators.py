"""Password validation utilities for FitAct.

Enforces the strong password policy applied during user registration (NFR4).
Rules are defined once here and reused by both the backend route and
the frontend checklist to ensure consistency.
"""

import re

# Password policy constants
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 15


def validate_password(password):
    """Validate a password against the FitAct strong password policy.

    Rules:
        - Between 8 and 15 characters in length.
        - At least 1 uppercase letter.
        - At least 1 lowercase letter.
        - At least 1 digit.
        - At least 1 special (non-word) character.

    Args:
        password (str): The plain-text password to validate.

    Returns:
        list[str]: A list of error messages. Empty list means the password
                   is valid and passes all rules.
    """
    errors = []

    if not (PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH):
        errors.append(
            f"Password must be between {PASSWORD_MIN_LENGTH} "
            f"and {PASSWORD_MAX_LENGTH} characters."
        )
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least 1 uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least 1 lowercase letter.")
    if not re.search(r"\d", password):
        errors.append("Password must contain at least 1 digit.")
    if not re.search(r"\W", password):
        errors.append("Password must contain at least 1 special character.")

    return errors
