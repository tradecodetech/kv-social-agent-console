import random

CTAS = [
    "Need reliable lawn care? Visit our website.",
    "Local lawn care handled with consistency.",
    "We take care of the yard so you don’t have to.",
    "Dependable lawn service for your property.",
    "Book lawn care when you’re ready."
]

def maybe_add_cta(text: str, style_tags: list[str], probability: float = 0.33) -> str:
    if "cta-allowed" not in style_tags:
        return text

    if random.random() < probability:
        return f"{text}\n\n{random.choice(CTAS)}"

    return text
