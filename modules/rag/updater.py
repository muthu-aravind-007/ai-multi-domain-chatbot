import json

# -----------------------------
# LOAD MEDICAL DATA
# -----------------------------
def load_medical_data(file_path="data/medical.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs = []
    for item in data:
        question = item.get("question", "")
        answer = item.get("answer", "")
        docs.append(f"[MEDICAL] Q: {question} A: {answer}")

    return docs


# -----------------------------
# LOAD ARXIV DATA
# -----------------------------
def load_arxiv_data(file_path="data/arxiv.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs = []
    for item in data:
        title = item.get("title", "")
        abstract = item.get("abstract", "")
        category = item.get("category", "")

        docs.append(f"[ARXIV][{category}] {title}: {abstract}")

    return docs


# -----------------------------
# UPDATE VECTOR STORE (KEY PART)
# -----------------------------
def update_vector_store(vector_store, new_docs):
    if not new_docs:
        return

    # Encode new docs
    new_embeddings = vector_store.model.encode(new_docs)

    # Append to existing
    vector_store.embeddings = list(vector_store.embeddings) + list(new_embeddings)
    vector_store.documents.extend(new_docs)

    print(f"✅ Added {len(new_docs)} new documents to knowledge base")


# -----------------------------
# AUTO UPDATE LOOP (SIMULATION)
# -----------------------------
def auto_update(vector_store, interval=3600):
    import time

    while True:
        print("🔄 Updating knowledge base...")

        # Reload datasets (simulate new data)
        new_arxiv_docs = load_arxiv_data()
        new_medical_docs = load_medical_data()

        new_docs = new_arxiv_docs + new_medical_docs

        update_vector_store(vector_store, new_docs)

        print("✅ Knowledge base updated")

        time.sleep(interval)  # every 1 hour