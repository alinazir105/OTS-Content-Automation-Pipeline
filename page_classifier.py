# page_classifier.py

def classify_page(text: str) -> str:
    t = text.lower()

    if "activity" in t:
        return "activity"

    if "exercise" in t:
        return "exercise"

    if "q1" in t or "questions and answers" in t:
        return "qa"

    if "unit" in t and ("what is" in t or "learning objectives" in t):
        return "cover"

    # fallback
    return "concept"