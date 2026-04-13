def detect_intent(query):
    q = query.lower()

    # Medical keywords
    if any(word in q for word in [
        "fever", "pain", "disease", "symptom", "medicine",
        "treatment", "headache", "diabetes"
    ]):
        return "medical"

    # Research / arXiv keywords
    elif any(word in q for word in [
        "paper", "research", "model", "transformer",
        "neural", "learning", "algorithm", "study"
    ]):
        return "arxiv"

    # Default
    return "general"


def filter_docs_by_intent(docs, intent):
    if intent == "medical":
        return [d for d in docs if "[MEDICAL]" in d]

    elif intent == "arxiv":
        return [d for d in docs if "[ARXIV]" in d]

    return docs