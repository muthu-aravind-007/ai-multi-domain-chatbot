import streamlit as st 
import threading
from PIL import Image
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import os
import re

from modules.sentiment.sentiment import analyze_sentiment
from modules.rag.loader import load_all_documents
from modules.rag.retriever import VectorStore
from modules.routing.router import detect_intent, filter_docs_by_intent
from modules.llm.ollama import generate
from modules.multilingual.translate import detect_language, translate_to_english, translate_from_english
from modules.rag.updater import auto_update
from modules.multimodal.gemini import analyze_image
from modules.visualization.concept_graph import extract_concepts, build_graph


# ---------------- UI CONFIG ---------------- #
st.set_page_config(
    page_title="AI Research Assistant",
    layout="wide",
    page_icon="🧠"
)

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}
.chat-box {
    background-color: #0E1117;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
}
.graph-card {
    background-color: #111827;
    padding: 15px;
    border-radius: 12px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 AI Research Assistant")
st.caption("Explain complex concepts • Explore research • Visualize knowledge")


# ---------------- INIT SYSTEM ---------------- #
@st.cache_resource
def initialize_system():
    docs = load_all_documents()
    return VectorStore(docs)

vector_store = initialize_system()

if "updater_started" not in st.session_state:
    threading.Thread(target=auto_update, args=(vector_store,), daemon=True).start()
    st.session_state["updater_started"] = True


# ---------------- SIDEBAR ---------------- #
st.sidebar.header("📚 Research Explorer")
search_query = st.sidebar.text_input("Search papers")

if search_query:
    results = vector_store.search(search_query)
    for r in results[:5]:
        st.sidebar.markdown(f"• {r[:120]}...")


# ---------------- IMAGE INPUT ---------------- #
uploaded_file = st.file_uploader("📷 Upload an image", type=["png", "jpg", "jpeg"])
image_query = None

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", width=300)

    with st.spinner("🔍 Understanding image..."):
        image_description = analyze_image(image)

    st.success("✅ Image processed")
    st.write(image_description)
    image_query = image_description.strip()


# ---------------- SESSION ---------------- #
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- GRAPH HELPERS ---------------- #

def wrap_text(text, width=18):
    words = text.split()
    lines = []
    line = ""

    for word in words:
        if len(line + word) < width:
            line += word + " "
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())

    return "\n".join(lines)


def draw_research_graph_pyvis(graph, query):
    net = Network(
        height="700px",
        width="100%",
        directed=True,
        bgcolor="#0E1117",
        font_color="white",
        notebook=False,
        cdn_resources="in_line"
    )

    net.barnes_hut(
        gravity=-20000,
        central_gravity=0.3,
        spring_length=180,
        spring_strength=0.04,
        damping=0.2
    )

    net.set_options("""
    var options = {
      "nodes": {
        "shape": "box",
        "font": {
          "size": 16,
          "multi": true
        },
        "borderWidth": 2,
        "margin": 10
      },
      "edges": {
        "smooth": { "type": "dynamic" },
        "font": { "size": 13, "align": "middle" },
        "arrows": { "to": { "enabled": true } },
        "color": "#AAAAAA"
      },
      "physics": { "stabilization": true }
    }
    """)

    # 🔥 Find center node (most connected)
    degrees = dict(graph.degree())
    center = max(degrees, key=degrees.get) if degrees else None

    # ---------------- ADD NODES ---------------- #
    for node in graph.nodes():
        label_clean = node.strip()

        # prevent long paragraph nodes
        if len(label_clean) > 50:
            label_clean = label_clean[:50] + "..."

        net.add_node(
            node,
            label=wrap_text(label_clean),
            title=node,
            color="#1B4F72" if node == center else "#AED6F1",
            size=40 if node == center else 25,
            shape="box"
        )

    # ---------------- ADD EDGES ---------------- #
    connected_nodes = set()

    for u, v, d in graph.edges(data=True):
        label = d.get("label", "")

        net.add_edge(u, v, label=label, arrows="to")

        connected_nodes.add(u)
        connected_nodes.add(v)

    # 🔥 Fix disconnected nodes
    for node in graph.nodes():
        if node not in connected_nodes and node != center:
            net.add_edge(center, node, label="related", arrows="to")

    return net


def render_pyvis_graph(graph, query_en):
    net = draw_research_graph_pyvis(graph, query_en)

    html = net.generate_html()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
        f.write(html)
        path = f.name

    with open(path, "r", encoding="utf-8") as f:
        html_content = f.read()

    os.remove(path)

    components.html(html_content, height=750, scrolling=True)


# ---------------- CHAT HISTORY ---------------- #
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant" and msg.get("graph"):
            st.markdown("### 📊 Concept Visualization")
            graph = build_graph(*msg["graph"])
            render_pyvis_graph(graph, msg["content"])


# ---------------- USER INPUT ---------------- #
user_input = st.chat_input("Ask anything about AI, ML, research...")
final_input = image_query if image_query else user_input

if final_input:
    st.session_state.messages.append({"role": "user", "content": final_input})

    with st.chat_message("user"):
        st.markdown(final_input)

    with st.spinner("🤖 Thinking..."):
        lang = detect_language(final_input)
        query_en = translate_to_english(final_input) if lang != "en" else final_input

        sentiment = analyze_sentiment(query_en)
        intent = detect_intent(query_en)

        results = vector_store.search(query_en)
        context = "\n".join(filter_docs_by_intent(results, intent)[:1])

        prompt = f"""
    You are an expert AI professor.

    Explain the concept: "{query_en}"

    STRICT RULES:
    - First line: 1-line simple definition
    - Then: bullet points (clear & short)
    - Then: real-world examples
    - Avoid long paragraphs
    - Avoid repetition
    - Max 120 words

    Make it crisp, modern, and easy to understand.

    Context:
    {context}
    """

        response_en = generate(prompt)
        response = translate_from_english(response_en, lang) if lang != "en" else response_en

        graph_data = None
        if "explain" in query_en.lower() or intent == "arxiv":
            concepts, relations = extract_concepts(response_en)

            concepts = concepts[:7]
            relations = relations[:10]

            if len(concepts) > 1:
                graph_data = (concepts, relations)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "graph": graph_data
    })

    with st.chat_message("assistant"):
        st.markdown(response)
        st.caption(f"🌍 {lang} | 😊 {sentiment}")

        if graph_data:
            st.markdown("### 📊 Concept Visualization")
            graph = build_graph(*graph_data)
            render_pyvis_graph(graph, query_en)