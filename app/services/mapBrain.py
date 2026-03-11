# Get distance & direction
import re

def clean_text(text):
    if not text:
        return ""
    # Looks for a word ending in a hyphen, a newline, and another word.
    # Replaces "word-\nword" with "wordword"
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    # 2. Now, normalize all other whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\n', " ")
    return text.strip()

def extract_distance(text: str):
    match = re.search(r'(\d+(?:\.\d+)?)\s*(km|m)\b', text, re.IGNORECASE)
    if match:
        value = float(match.group(1))
        unit = match.group(2).lower()
        return value, unit
    return None, None

def distance_in_meters(text):
    value, unit = extract_distance(text)
    if value is None:
        return None

    if unit == "km":
        return value * 1000
    return value

def extract_direction(text: str):
    text = text.lower()

    patterns = [
        ("u-turn", r"\b(u[- ]?turn)\b"),
        ("left", r"\b(left|turn left|keep left|slight left|sharp left)\b"),
        ("right", r"\b(right|turn right|keep right|slight right|sharp right)\b"),
        ("straight", r"\b(straight|continue|go straight|head straight)\b"),
    ]

    for direction, pattern in patterns:
        if re.search(pattern, text):
            return direction

    return None

