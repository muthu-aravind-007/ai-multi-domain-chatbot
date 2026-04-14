import json
import re
import networkx as nx
from modules.llm.ollama import generate

ALLOWED_RELATIONS = {"uses", "contains", "depends_on", "part_of", "improves"}


def _clean_json_response(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else None


def extract_concepts(text):
    prompt = f"""
You are an expert AI researcher.

Extract a HIGH-QUALITY knowledge graph.

STRICT RULES:
- Main concept MUST be the topic
- 4–6 meaningful technical sub-concepts
- No long phrases (max 3 words each)
- Avoid generic terms like "system", "process"
- Relations must be meaningful

Allowed relations:
"uses", "contains", "depends_on", "part_of", "improves"

Return ONLY JSON:
{{
  "concepts": [...],
  "relations": [["A","B","uses"]]
}}

Text:
{text}
"""

    fallback_concepts = ["Artificial Intelligence", "Machine Learning", "Neural Networks", "NLP"]
    fallback_relations = [
        ["Artificial Intelligence", "Machine Learning", "contains"],
        ["Machine Learning", "Neural Networks", "uses"],
        ["Artificial Intelligence", "NLP", "uses"]
    ]

    try:
        response = generate(prompt)
        json_str = _clean_json_response(response)

        if not json_str:
            return fallback_concepts, fallback_relations

        data = json.loads(json_str)

        concepts = list(dict.fromkeys([c.strip() for c in data.get("concepts", [])]))[:6]

        relations = []
        for rel in data.get("relations", []):
            if isinstance(rel, list) and len(rel) == 3:
                src, tgt, label = rel
                if label in ALLOWED_RELATIONS:
                    relations.append([src.strip(), tgt.strip(), label])

        if len(concepts) < 2:
            return fallback_concepts, fallback_relations

        return concepts, relations if relations else fallback_relations

    except Exception as e:
        print("⚠️ Extraction failed:", e)
        return fallback_concepts, fallback_relations


def build_graph(concepts, relations):
    G = nx.DiGraph()
    for c in concepts:
        G.add_node(c)
    for rel in relations:
        if len(rel) == 3:
            src, tgt, label = rel
            if src in concepts and tgt in concepts:
                G.add_edge(src, tgt, label=label)
    return G