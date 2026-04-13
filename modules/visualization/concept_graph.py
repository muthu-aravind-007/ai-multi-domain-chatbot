import networkx as nx

def extract_concepts(text):
    """
    Simple concept extractor (can be improved later)
    """
    keywords = [
        "AI", "Machine Learning", "Deep Learning",
        "Neural Network", "Transformer", "Attention",
        "NLP", "Model", "Algorithm"
    ]

    found = []

    for k in keywords:
        if k.lower() in text.lower():
            found.append(k)

    return found


def build_graph(concepts):
    G = nx.Graph()

    for i in range(len(concepts)):
        for j in range(i + 1, len(concepts)):
            G.add_edge(concepts[i], concepts[j])

    return G