from pathlib import Path
import json

def load_general_docs(path="data/general.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return [f"[GENERAL] {line.strip()}" for line in f.readlines() if line.strip()]


def load_medical_docs(path="data/medical.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs = []
    for item in data:
        q = item.get("question", "")
        a = item.get("answer", "")
        docs.append(f"[MEDICAL] Q: {q} A: {a}")

    return docs


def load_arxiv_docs(path="data/arxiv.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs = []
    for item in data:
        title = item.get("title", "")
        abstract = item.get("abstract", "")
        category = item.get("category", "")

        docs.append(f"[ARXIV][{category}] {title}: {abstract}")

    return docs


def load_all_documents():
    docs = []
    docs.extend(load_general_docs())
    docs.extend(load_medical_docs())
    docs.extend(load_arxiv_docs())
    return docs