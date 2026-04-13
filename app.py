import streamlit as st
import threading
from PIL import Image

from modules.sentiment.sentiment import analyze_sentiment
from modules.rag.loader import load_all_documents
from modules.rag.retriever import VectorStore
from modules.routing.router import detect_intent, filter_docs_by_intent
from modules.llm.ollama import generate
from modules.multilingual import detect_language, translate_to_english, translate_from_english
from modules.rag.updater import auto_update
from modules.multimodal.gemini import analyze_image

# -----------------------------
# LOAD SYSTEM (CACHE)
# -----------------------------
@st.cache_resource
def initialize_system():
    docs = load_all_documents()
    vector_store = VectorStore(docs)
    return vector_store

vector_store = initialize_system()

# -----------------------------
# START AUTO UPDATE (SAFE)
# -----------------------------
if "updater_started" not in st.session_state:
    threading.Thread(target=auto_update, args=(vector_store,), daemon=True).start()
    st.session_state["updater_started"] = True

# -----------------------------
# UI CONFIG
# -----------------------------
st.set_page_config(page_title="AI Chatbot", layout="wide")
st.title("🤖 AI Multi-Domain Chatbot")

# -----------------------------
# SIDEBAR (RESEARCH SEARCH)
# -----------------------------
st.sidebar.header("📚 Research Explorer")

search_query = st.sidebar.text_input("Search research papers")

if search_query:
    results = vector_store.search(search_query)
    st.sidebar.write("Top Results:")
    for r in results[:5]:
        st.sidebar.markdown(f"- {r[:200]}...")

# -----------------------------
# IMAGE UPLOAD (REAL MULTIMODAL)
# -----------------------------
uploaded_file = st.file_uploader("📷 Upload an image", type=["png", "jpg", "jpeg"])

image_query = None

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Analyzing image using AI..."):
        image_description = analyze_image(image)

    st.success("✅ Image processed")
    st.write("🧠 Image Understanding:")
    st.write(image_description)

    image_query = image_description.strip()

# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# DISPLAY CHAT HISTORY
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# USER INPUT
# -----------------------------
user_input = st.chat_input("Ask something...")

final_input = image_query if image_query else user_input

if final_input:
    # Store user message
    st.session_state.messages.append({"role": "user", "content": final_input})

    with st.chat_message("user"):
        st.markdown(final_input)

    # -----------------------------
    # LANGUAGE DETECTION
    # -----------------------------
    lang = detect_language(final_input)
    query_en = translate_to_english(final_input) if lang != "en" else final_input

    # -----------------------------
    # SENTIMENT
    # -----------------------------
    sentiment = analyze_sentiment(query_en)

    # -----------------------------
    # INTENT
    # -----------------------------
    intent = detect_intent(query_en)

    # -----------------------------
    # RETRIEVAL
    # -----------------------------
    results = vector_store.search(query_en)
    filtered = filter_docs_by_intent(results, intent)

    context = "\n".join(filtered[:2])

    # -----------------------------
    # FOLLOW-UP MEMORY (IMPORTANT)
    # -----------------------------
    history = "\n".join([
        f"{m['role']}: {m['content']}"
        for m in st.session_state.messages[-5:]
    ])

    # -----------------------------
    # INSTRUCTION
    # -----------------------------
    if intent == "medical":
        instruction = "Give a clear and medically accurate answer."
    elif intent == "arxiv":
        instruction = "Explain the research concept clearly."
    else:
        instruction = "Answer clearly and concisely."

    # Sentiment adjustment
    if sentiment == "negative":
        instruction += " The user seems concerned. Respond in a supportive and empathetic tone."
    elif sentiment == "positive":
        instruction += " Respond in a friendly and encouraging tone."

    # -----------------------------
    # PROMPT
    # -----------------------------
    prompt = f"""
You are a professional AI assistant.

Conversation History:
{history}

{instruction}

STRICT RULES:
- Answer ONLY the question
- No extra stories or exercises
- Keep it concise

Context:
{context}

Question:
{query_en}

Answer:
"""

    # -----------------------------
    # GENERATE RESPONSE
    # -----------------------------
    response_en = generate(prompt)

    # Translate back
    response = translate_from_english(response_en, lang) if lang != "en" else response_en

    # -----------------------------
    # DISPLAY METADATA (BONUS)
    # -----------------------------
    st.caption(f"🌍 Language: {lang} | 😊 Sentiment: {sentiment}")

    # Store response
    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)