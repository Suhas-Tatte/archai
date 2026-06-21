def detect_location(query, locations):
    query = query.lower()

    for loc in locations:
        if loc and loc.lower() in query:
            return loc

    return None


def detect_structure_type(query):
    q = query.lower()

    if "temple" in q:
        return "Temple"
    if "stepwell" in q:
        return "Stepwell"
    if "mosque" in q:
        return "Mosque"
    if "fort" in q:
        return "Fort"
    if "lake" in q:
        return "Lake"

    return None


def is_structure_query(query):
    keywords = ["structure", "temple", "stepwell", "mosque", "fort", "lake"]
    return any(k in query.lower() for k in keywords)


def extract_entity_phrase(query):
    words = query.lower().split()

    if "in" in words:
        idx = words.index("in")
        phrase = " ".join(words[idx + 1:])
        return phrase.title()

    return None