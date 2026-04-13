import requests
import xml.etree.ElementTree as ET
import json
import os

DATA_FILE = "data/arxiv.json"


# -----------------------------
# FETCH FROM ARXIV API
# -----------------------------
def fetch_arxiv(category="cs.AI", max_results=20):
    url = f"http://export.arxiv.org/api/query?search_query=cat:{category}&start=0&max_results={max_results}"

    response = requests.get(url)

    if response.status_code != 200:
        print("❌ Failed to fetch data")
        return []

    root = ET.fromstring(response.content)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}

    papers = []

    for entry in root.findall("atom:entry", namespace):
        title = entry.find("atom:title", namespace)
        summary = entry.find("atom:summary", namespace)
        paper_id = entry.find("atom:id", namespace)

        if title is not None and summary is not None:
            papers.append({
                "id": paper_id.text.strip() if paper_id is not None else title.text.strip(),
                "title": title.text.strip(),
                "abstract": summary.text.strip(),
                "category": category
            })

    return papers


# -----------------------------
# LOAD EXISTING DATA
# -----------------------------
def load_existing_data():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------
# SAVE DATA (MERGE WITHOUT DUPLICATES)
# -----------------------------
def save_data(new_papers):
    existing = load_existing_data()

    existing_ids = {p.get("id") for p in existing}

    added = 0

    for paper in new_papers:
        if paper["id"] not in existing_ids:
            existing.append(paper)
            added += 1

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

    print(f"✅ Added {added} new papers | Total: {len(existing)}")


# -----------------------------
# MAIN EXECUTION
# -----------------------------
def run_fetch():
    categories = ["cs.AI", "cs.CL", "cs.LG"]

    all_new_papers = []

    for cat in categories:
        print(f"📡 Fetching {cat}...")
        papers = fetch_arxiv(cat, max_results=20)
        all_new_papers.extend(papers)

    save_data(all_new_papers)


# -----------------------------
# RUN SCRIPT
# -----------------------------
if __name__ == "__main__":
    run_fetch()