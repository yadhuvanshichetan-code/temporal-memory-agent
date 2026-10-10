"""
Fact Extractor — Rule-based extraction of (subject, predicate, object)
from natural language sentences.

Handles:
  - Statements (facts to store)
  - Questions (queries to answer)
  - Historical queries (e.g., "what was alice's job in 2024?")
"""

import re


PREDICATE_PATTERNS = [
    # Contact info
    (r"\b(phone is|phone number is|number is)\b", "phone"),
    (r"\b(email is|email address is)\b", "email"),

    # Marital status (self)
    (r"\b(is|got|now|am)\s+(married|single|divorced|engaged|separated|widowed)\b",
     "marital_status_self"),

    # Job changes (promotion, becoming)
    (r"\b(got promoted to|promoted to|became|works as)\b", "job_change"),

    # Location
    (r"\b(lives in|moved to|is from|resides in|based in)\b", "location"),

    # Age
    (r"\b(is|turned)\s+\d+\s*(years old|yo)\b", "age"),

    # Preferences
    (r"\b(likes|prefers|favorite|favourite)\b", "preference"),

    # Possession
    (r"\b(owns|has|drives|bought)\b", "possession"),

    # Multi-word job titles (matched as the object)
    (r"\b(software engineer|staff engineer|senior engineer|"
     r"data scientist|product manager|project manager|"
     r"engineering manager|software developer|web developer|"
     r"product designer|ux designer|machine learning engineer)\b",
     "job_multiword"),

    # Single-word job titles with "is a/an"
    (r"\bis (a|an)\s+"
     r"(engineer|manager|doctor|teacher|student|designer|developer|"
     r"scientist|analyst|director|intern|lead|architect|consultant|"
     r"nurse|lawyer|chef|writer|artist)\b",
     "job_singleword"),

    # Generic "is a/an" fallback (LAST)
    (r"\bis (a|an)\b", "attribute"),
]


QUESTION_STARTERS = (
    "what", "where", "who", "when", "why", "how",
    "is", "are", "was", "were", "does", "do", "did", "can", "could"
)


def is_question(text: str) -> bool:
    """Return True if the sentence looks like a question."""
    t = text.strip().lower()
    if t.endswith("?"):
        return True
    return t.startswith(QUESTION_STARTERS)


def normalize(text: str) -> str:
    """Trim and lowercase a piece of text."""
    return text.strip().lower().rstrip(".").rstrip("?").rstrip("!")


def extract_fact(sentence: str):
    """Extract (subject, predicate, object) from a statement."""
    s = normalize(sentence)
    if not s:
        return None

    for pattern, tag in PREDICATE_PATTERNS:
        match = re.search(pattern, s)
        if not match:
            continue

        # Marital status: object IS the matched word
        if tag == "marital_status_self":
            status_word = match.group(2)
            subject = s[:match.start()].strip().replace("'s", "").strip()
            if subject:
                return {
                    "subject": subject,
                    "predicate": "marital_status",
                    "object": status_word,
                }
            continue

        # Multi-word job: object IS the matched phrase
        if tag == "job_multiword":
            job_word = match.group(1)
            subject = s[:match.start()].strip().replace("'s", "").strip()
            subject = re.sub(
                r"\s+(is a|is an|is|was a|was an|was|now|got|became)$",
                "", subject
            ).strip()
            if subject:
                return {
                    "subject": subject,
                    "predicate": "job_title",
                    "object": job_word,
                }
            continue

        # Job change: "dave got promoted to manager"
        if tag == "job_change":
            subject = s[:match.start()].strip().replace("'s", "").strip()
            obj = s[match.end():].strip()
            obj = re.sub(r"^(a|an|the|at|in|to|now)\s+", "", obj).strip()
            if subject and obj:
                return {
                    "subject": subject,
                    "predicate": "job_title",
                    "object": obj,
                }
            continue

        # Single-word job: "alice is a teacher"
        if tag == "job_singleword":
            subject = s[:match.start()].strip().replace("'s", "").strip()
            job_word = match.group(2)
            if subject:
                return {
                    "subject": subject,
                    "predicate": "job_title",
                    "object": job_word,
                }
            continue

        # Generic patterns (location, phone, preference, etc.)
        subject = s[:match.start()].strip().replace("'s", "").strip()
        obj = s[match.end():].strip()
        obj = re.sub(r"^(a|an|the|at|in|to|now)\s+", "", obj).strip()
        obj = obj.rstrip(".,!?").strip()

        if subject and obj:
            return {
                "subject": subject,
                "predicate": tag,
                "object": obj,
            }

    return None


def extract_query(sentence: str):
    """
    Extract a query hint (subject + predicate + optional as_of year)
    from a question.

    Examples:
      "what is alice job?"          → {'subject': 'alice', 'predicate': 'job_title', 'as_of_year': None}
      "what was alice job in 2024?" → {'subject': 'alice', 'predicate': 'job_title', 'as_of_year': 2024}
    """
    s = normalize(sentence)
    if not s:
        return None

    hint_words = {
        "job": "job_title",
        "work": "job_title",
        "role": "job_title",
        "title": "job_title",
        "position": "job_title",
        "live": "location",
        "location": "location",
        "city": "location",
        "where": "location",
        "phone": "phone",
        "number": "phone",
        "email": "email",
        "age": "age",
        "old": "age",
        "favorite": "preference",
        "favourite": "preference",
        "like": "preference",
        "married": "marital_status",
        "single": "marital_status",
    }

    predicate = None
    for word, pred in hint_words.items():
        if word in s:
            predicate = pred
            break

    # ---- Detect year in query (e.g., "in 2024") ----
    as_of_year = None
    year_match = re.search(r"\b(19|20)\d{2}\b", s)
    if year_match:
        as_of_year = int(year_match.group(0))

    # ---- Extract subject ----
    cleaned = re.sub(
        r"^(what|where|who|when|is|are|was|were|does|do|did|how)\s+",
        "", s
    )
    cleaned = re.sub(r"\b(19|20)\d{2}\b", "", cleaned)  # remove the year
    cleaned = re.sub(
        r"\b(is|are|was|were|does|do|did|the|a|an|s|in|at|on)\b",
        " ", cleaned
    )
    tokens = [t for t in cleaned.split() if t]

    subject = tokens[0] if tokens else None

    return {
        "subject": subject,
        "predicate": predicate,
        "as_of_year": as_of_year,
    }


# --- Quick test ---
if __name__ == "__main__":
    tests = [
        "alice is a software engineer",
        "bob lives in new york",
        "carol's phone is 555-1234",
        "dave got promoted to manager",
        "alice got promoted to staff engineer",
        "eve is married",
        "frank drives a tesla",
        "what is alice job?",
        "where does bob live?",
        "what is carol phone?",
        "what was alice job in 2024?",
        "what was alice's job in 2023?",
    ]

    for t in tests:
        if is_question(t):
            print(f"QUERY: {t}")
            print(f"   → {extract_query(t)}")
        else:
            print(f"FACT:  {t}")
            print(f"   → {extract_fact(t)}")
        print()