import re

IDENTIFIER_RE = re.compile("^[A-Za-z_][A-Za-z_\-0-9]*$")
def check_identifier(identifier: str, message_postfix: str):
    if not IDENTIFIER_RE.match(identifier):
        raise ValueError(f"{identifier:!r} is not a valid {message_postfix}")
