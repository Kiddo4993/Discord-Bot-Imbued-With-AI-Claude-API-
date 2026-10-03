import re

BANNED_WORDS = ['shit', 'fuck', 'cum', 'dick', 'ass', 'cock', 'bitch']

# Whole words only: a plain substring check also caught "class", "pass", "document"
# and the bot's own !assign command.
_BANNED = re.compile(r"\b(" + "|".join(map(re.escape, BANNED_WORDS)) + r")\b", re.IGNORECASE)


def contains_banned_word(text):
    return _BANNED.search(text) is not None
