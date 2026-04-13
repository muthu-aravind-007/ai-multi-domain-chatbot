import requests
import xml.etree.ElementTree as ET
import json

def fetch_arxiv(category="cs.AI", max_results=50):
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

        if title is not None and summary is not None:
            papers.append({
                "title": title.text.strip(),
                "abstract": summary.text.strip(),
                "category": category
            })

    return papers


# Fetch multiple CS domains
all_papers = []
categories = ["cs.AI", "cs.CL", "cs.LG"]

for cat in categories:
    print(f"Fetching {cat}...")
    papers = fetch_arxiv(cat, max_results=40)
    all_papers.extend(papers)


# Save file
with open("data/arxiv.json", "w", encoding="utf-8") as f:
    json.dump(all_papers, f, indent=2)

print(f"✅ Saved {len(all_papers)} REAL arXiv papers")